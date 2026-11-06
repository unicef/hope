from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING, cast

from django.contrib.admin.options import get_content_type_for_model
from django.core.files import File
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
import openpyxl
import pyzipper

from hope.apps.activity_log.utils import copy_model_object
from hope.apps.payment.api.caches import invalidate_payment_list_list_cache
from hope.apps.payment.utils import bulk_log_payment_changes, get_link, inactive_currency_reason
from hope.apps.payment.xlsx.base_xlsx_export_service import XlsxExportBaseService
from hope.apps.payment.xlsx.xlsx_payment_list_delivery_export_service import (
    XlsxPaymentListDeliveryExportService,
)
from hope.models import (
    FileTemp,
    FinancialServiceProviderXlsxTemplate,
    FspXlsxTemplatePerDeliveryMechanism,
    Payment,
    PaymentList,
)

if TYPE_CHECKING:
    from hope.models import PaymentPlan, Program, User


class UnexportablePaymentListsError(Exception):
    """Raised when at least one payment list of the payment plan cannot go into the export file.

    The export is all or nothing: the FSP receives one file for the whole payment plan.
    """

    MESSAGE = "Export refused: not every payment list in the payment plan can be exported."

    def __init__(self, skipped_reasons: list[str]) -> None:
        self.skipped_reasons = skipped_reasons
        super().__init__(self.MESSAGE)


class XlsxPaymentPlanDeliveryExportService(XlsxExportBaseService):
    """Export every payment list of a payment plan into one single-sheet xlsx.

    A payment plan is bound to a single FSP, so every exported payment list shares the same FSP XLSX
    template and the sheet has a single, flat header. Exporting again replaces the payment plan's file.
    """

    TITLE = "Payment Plan - Payment List"
    batch_size = 2000

    def __init__(
        self,
        payment_plan: "PaymentPlan",
        fsp_xlsx_template_id: str | None = None,
    ) -> None:
        self.payment_plan = payment_plan
        self.payment_generate_token_and_order_numbers = True
        self.allow_export_fsp_auth_code = False
        self.payment_lists = list(
            payment_plan.payment_lists.select_related(
                "payment_plan__financial_service_provider", "payment_plan__currency", "delivery_mechanism"
            ).order_by("unicef_id")
        )
        self.plan_type: str = payment_plan.plan_type
        self.exported_plan_ids: list = []
        self.payments_to_mark_sent: list[Payment] = []
        self.skipped_reasons: list[str] = []
        self.fsp_xlsx_template: FinancialServiceProviderXlsxTemplate | None = (
            get_object_or_404(FinancialServiceProviderXlsxTemplate, pk=fsp_xlsx_template_id)
            if fsp_xlsx_template_id
            else None
        )
        self._template_map: dict[tuple, FinancialServiceProviderXlsxTemplate] | None = None
        self._plans_with_blocking_payments: set | None = None

    def _get_template_map(self) -> dict[tuple, FinancialServiceProviderXlsxTemplate]:
        """Resolve every plan's (fsp, delivery_mechanism) -> xlsx_template in a single query."""
        if self._template_map is None:
            pairs = {
                (pp.payment_plan.financial_service_provider_id, pp.delivery_mechanism_id)
                for pp in self.payment_lists
                if pp.payment_plan.financial_service_provider_id and pp.delivery_mechanism_id
            }
            mappings = FspXlsxTemplatePerDeliveryMechanism.objects.filter(
                financial_service_provider_id__in={fsp_id for fsp_id, _ in pairs},
                delivery_mechanism_id__in={dm_id for _, dm_id in pairs},
            ).select_related("xlsx_template")
            self._template_map = {
                (m.financial_service_provider_id, m.delivery_mechanism_id): m.xlsx_template
                for m in mappings
                if (m.financial_service_provider_id, m.delivery_mechanism_id) in pairs
            }
        return self._template_map

    def _get_plans_with_blocking_payments(self) -> set:
        """Plan ids that still have eligible payments not yet sent to the payment gateway.

        Equivalent to PaymentList.is_payment_gateway_and_all_sent_to_fsp.
        """
        if self._plans_with_blocking_payments is None:
            self._plans_with_blocking_payments = set(
                Payment.objects.filter(parent__in=self.payment_lists)
                .eligible()
                .filter(status__in=(Payment.STATUS_PENDING, Payment.STATUS_SENT_TO_PG))
                .values_list("parent_id", flat=True)
                .distinct()
            )
        return self._plans_with_blocking_payments

    def _resolve_template(self, payment_list: PaymentList) -> FinancialServiceProviderXlsxTemplate | None:
        if self.fsp_xlsx_template is not None:
            return self.fsp_xlsx_template
        fsp_id = payment_list.payment_plan.financial_service_provider_id
        if not fsp_id or not payment_list.delivery_mechanism_id:
            return None
        return self._get_template_map().get((fsp_id, payment_list.delivery_mechanism_id))

    def _skip_reason(
        self, payment_list: PaymentList, template: FinancialServiceProviderXlsxTemplate | None
    ) -> str | None:
        """Return why `payment_list` would be left out of the export, or None if it would be included."""
        if reason := inactive_currency_reason(payment_list):
            return reason
        if template is None:
            return f"Payment List {payment_list.unicef_id}: no FSP XLSX Template for its FSP and delivery mechanism."
        if (
            payment_list.is_payment_gateway
            and "fsp_auth_code" in template.columns
            and payment_list.id in self._get_plans_with_blocking_payments()
        ):
            return (
                f"Payment List {payment_list.unicef_id}: template requires fsp_auth_code "
                f"but not all payments have been sent to the payment gateway yet."
            )
        return None

    def unexportable_reasons(self) -> list[str]:
        """One reason per payment list that would keep the export from running; empty when it can run."""
        return [
            reason
            for payment_list in self.payment_lists
            if (reason := self._skip_reason(payment_list, self._resolve_template(payment_list))) is not None
        ]

    def generate_token_and_order_numbers(self, program: "Program") -> None:
        all_eligible = Payment.objects.filter(parent__in=self.payment_lists).eligible()
        XlsxPaymentListDeliveryExportService.generate_token_and_order_numbers(all_eligible, program)

    def _filename_suffix(self) -> str:
        if self.plan_type == PaymentList.PlanType.REGULAR:
            return ""
        return f"_{self.plan_type.lower()}"

    def get_email_context(self, user: "User") -> dict:
        payment_plan = self.payment_plan
        link = get_link(reverse("download-payment-plan-xlsx", args=[str(payment_plan.id)]))
        return {
            "first_name": getattr(user, "first_name", ""),
            "last_name": getattr(user, "last_name", ""),
            "email": getattr(user, "email", ""),
            "message": (
                f"Payment Plan {payment_plan.unicef_id} Payment List xlsx file "
                "was generated and below you have the link to download this file."
            ),
            "link": link or "",
            "title": f"Payment Plan {payment_plan.unicef_id} Payment List Generated",
        }

    def _invalidate_list_cache(self) -> None:
        program = self.payment_plan.cycle.program
        invalidate_payment_list_list_cache(program.business_area.slug, program.code)

    def generate_workbook(self) -> openpyxl.Workbook:
        self._create_workbook()

        header: list[str] = []
        prepared_services: list[XlsxPaymentListDeliveryExportService] = []
        self.exported_plan_ids = []
        self.payments_to_mark_sent = []
        self.skipped_reasons = []

        shared_lookups = XlsxPaymentListDeliveryExportService.build_shared_lookups()
        payment_plan_fsp_extra_fields_headers = XlsxPaymentListDeliveryExportService.get_fsp_extra_fields_headers(
            Payment.objects.filter(parent__in=self.payment_lists).eligible().only("extras")
        )

        for payment_list in self.payment_lists:
            template = self._resolve_template(payment_list)
            reason = self._skip_reason(payment_list, template)
            if reason:
                self.skipped_reasons.append(reason)
                continue
            per_fsp_service = XlsxPaymentListDeliveryExportService(
                payment_list,
                shared_lookups=shared_lookups,
                fsp_extra_fields_headers=payment_plan_fsp_extra_fields_headers,
            )
            per_fsp_service.prepare_headers(cast("FinancialServiceProviderXlsxTemplate", template))
            header.extend(column for column in per_fsp_service.header_list if column not in header)
            prepared_services.append(per_fsp_service)
            self.exported_plan_ids.append(payment_list.id)
        # Every list writes its own auth codes into the shared header, so one such list protects the file.
        self.allow_export_fsp_auth_code = any(service.allow_export_fsp_auth_code for service in prepared_services)

        self.ws_export_list.append(header)

        for per_fsp_service in prepared_services:
            payments = per_fsp_service.payment_list.eligible_payments.select_related(
                "household_snapshot", "currency", "delivery_type", "financial_service_provider", "parent"
            ).order_by("unicef_id")
            for payment in payments.iterator(chunk_size=self.batch_size):
                payment_row = dict(
                    zip(
                        per_fsp_service.header_list,
                        per_fsp_service.get_payment_row(payment),
                        strict=True,
                    )
                )
                self.ws_export_list.append([payment_row.get(column, "") for column in header])
                if (
                    not per_fsp_service.payment_list.is_payment_gateway
                    and payment.status == Payment.STATUS_PENDING
                    and payment.delivered_quantity is None
                ):
                    self.payments_to_mark_sent.append(payment)

        self._adjust_column_width_from_col(ws=self.ws_export_list)
        return self.wb

    def save_xlsx_file(self, user: "User") -> None:
        payment_plan = self.payment_plan
        self.generate_workbook()
        if self.skipped_reasons or not self.exported_plan_ids:
            raise UnexportablePaymentListsError(self.skipped_reasons)

        if self.allow_export_fsp_auth_code:
            self._save_xlsx_file_with_auth_code(payment_plan, user)
        else:
            self._save_plain_xlsx_file(payment_plan, user)

    def _mark_exported_payments_as_sent(self, user: "User") -> None:
        if not self.payments_to_mark_sent:
            return

        status_date = timezone.now()
        old_new_pairs: list[tuple[Payment | None, Payment]] = []
        for payment in self.payments_to_mark_sent:
            old_payment = cast("Payment", copy_model_object(payment))
            payment.status = Payment.STATUS_SENT_TO_FSP
            payment.status_date = status_date
            payment.sent_to_fsp_date = status_date
            old_new_pairs.append((old_payment, payment))

        Payment.signature_manager.bulk_update_with_signature(
            self.payments_to_mark_sent,
            ("status", "status_date", "sent_to_fsp_date"),
            batch_size=self.batch_size,
        )
        bulk_log_payment_changes(old_new_pairs, user)

    def _attach_file(self, payment_plan: "PaymentPlan", file_temp: FileTemp, user: "User") -> None:
        with transaction.atomic():
            payment_plan.remove_export_file_delivery()
            payment_plan.export_file_delivery = file_temp
            payment_plan.save(update_fields=["export_file_delivery", "updated_at"])
            self._mark_exported_payments_as_sent(user)
            self._invalidate_list_cache()

    def _save_plain_xlsx_file(self, payment_plan: "PaymentPlan", user: "User") -> None:
        filename = f"payment_plan_{payment_plan.unicef_id}_payment_list{self._filename_suffix()}.xlsx"
        with NamedTemporaryFile() as tmp:
            file_temp = FileTemp(
                object_id=str(payment_plan.pk),
                content_type=get_content_type_for_model(payment_plan),
                created_by=user,
            )
            self.wb.save(tmp.name)
            tmp.seek(0)
            file_temp.file.save(filename, File(tmp))
            self._attach_file(payment_plan, file_temp, user)

    def _save_xlsx_file_with_auth_code(self, payment_plan: "PaymentPlan", user: "User") -> None:
        zip_password = get_random_string(12)
        xlsx_password = get_random_string(12)
        zip_filename = f"payment_plan_{payment_plan.unicef_id}_payment_list{self._filename_suffix()}.zip"
        xlsx_filename = f"payment_plan_{payment_plan.unicef_id}_payment_list{self._filename_suffix()}.xlsx"

        with NamedTemporaryFile(suffix=".zip") as tmp_zip:
            with pyzipper.AESZipFile(
                tmp_zip, mode="w", compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES
            ) as zf:
                zf.setpassword(zip_password.encode("utf-8"))
                XlsxPaymentListDeliveryExportService.save_workbook(zf, self.wb, xlsx_filename, xlsx_password)

            file_temp = FileTemp(
                object_id=str(payment_plan.pk),
                content_type=get_content_type_for_model(payment_plan),
                created_by=user,
                password=zip_password,
                xlsx_password=xlsx_password,
            )
            tmp_zip.seek(0)
            file_temp.file.save(zip_filename, File(tmp_zip))
            self._attach_file(payment_plan, file_temp, user)
