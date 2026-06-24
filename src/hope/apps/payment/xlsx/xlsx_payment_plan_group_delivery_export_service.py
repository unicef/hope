import logging
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING

from django.contrib.admin.options import get_content_type_for_model
from django.core.files import File
from django.db import transaction
from django.db.models import Max
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
import openpyxl
import pyzipper

from hope.apps.payment.xlsx.base_xlsx_export_service import XlsxExportBaseService
from hope.apps.payment.xlsx.xlsx_payment_plan_delivery_export_service import XlsxPaymentPlanDeliveryExportService
from hope.models import FileTemp, FinancialServiceProviderXlsxTemplate, FspXlsxTemplatePerDeliveryMechanism, PaymentPlan

if TYPE_CHECKING:
    from hope.models import PaymentPlanGroup, Program, User

logger = logging.getLogger(__name__)


class EmptyDeliveryExportError(Exception):
    """Raised when an export batch would produce no rows because every payment plan was skipped."""

    MESSAGE = "Nothing to export: no payment plan is currently exportable."

    def __init__(self, skipped_reasons: list[str]) -> None:
        self.skipped_reasons = skipped_reasons
        super().__init__(self.MESSAGE)


class XlsxPaymentPlanGroupDeliveryExportService(XlsxExportBaseService):
    """Export one batch of a group's payment plans into a single-sheet xlsx.

    A group is bound to a single FSP, so every exported payment plan shares the same FSP XLSX
    template and the sheet has a single, flat header.

    Each export is a batch: only ACCEPTED/FINISHED, REGULAR (no follow-ups / top-ups) plans that
    have not been exported yet (``export_tag`` is null) are included. On success the exported plans
    are stamped with the next sequential ``export_tag`` so they are
    excluded from the next export.
    """

    TITLE = "Payment Plan Group - Payment List"
    batch_size = 2000

    def __init__(
        self,
        payment_plan_group: "PaymentPlanGroup",
        fsp_xlsx_template_id: str | None = None,
        export_tag: int | None = None,
    ) -> None:
        self.payment_plan_group = payment_plan_group
        self.export_tag = export_tag
        self.applied_export_tag: int | None = None
        self.payment_generate_token_and_order_numbers = True
        self.allow_export_fsp_auth_code = False
        if export_tag is not None:
            plan_qs = payment_plan_group.payment_plans.filter(export_tag=export_tag)
        else:
            plan_qs = payment_plan_group.payment_plans.filter(
                status__in=[PaymentPlan.Status.ACCEPTED, PaymentPlan.Status.FINISHED],
                plan_type=PaymentPlan.PlanType.REGULAR,
                export_tag__isnull=True,
            )
        self.payment_plans = list(plan_qs.order_by("unicef_id"))
        self.exported_plan_ids: list = []
        self.skipped_reasons: list[str] = []
        self.fsp_xlsx_template: FinancialServiceProviderXlsxTemplate | None = (
            get_object_or_404(FinancialServiceProviderXlsxTemplate, pk=fsp_xlsx_template_id)
            if fsp_xlsx_template_id
            else None
        )

    def _resolve_template(self, payment_plan: PaymentPlan) -> FinancialServiceProviderXlsxTemplate | None:
        if self.fsp_xlsx_template is not None:
            return self.fsp_xlsx_template
        fsp = payment_plan.financial_service_provider
        delivery_mechanism = payment_plan.delivery_mechanism
        if not fsp or not delivery_mechanism:
            return None
        mapping = FspXlsxTemplatePerDeliveryMechanism.objects.filter(
            financial_service_provider=fsp,
            delivery_mechanism=delivery_mechanism,
        ).first()
        return mapping.xlsx_template if mapping else None

    def _skip_reason(
        self, payment_plan: PaymentPlan, template: FinancialServiceProviderXlsxTemplate | None
    ) -> str | None:
        """Return why `payment_plan` would be left out of the export, or None if it would be included."""
        if template is None:
            return f"Payment Plan {payment_plan.unicef_id}: no FSP XLSX Template for its FSP and delivery mechanism."
        if (
            payment_plan.is_payment_gateway
            and "fsp_auth_code" in template.columns
            and not payment_plan.is_payment_gateway_and_all_sent_to_fsp
        ):
            return (
                f"Payment Plan {payment_plan.unicef_id}: template requires fsp_auth_code "
                f"but not all payments have been sent to the payment gateway yet."
            )
        return None

    def preview_export(self) -> list:
        """Return the ids of plans that would be exported (empty if every plan would be skipped)."""
        return [
            payment_plan.id
            for payment_plan in self.payment_plans
            if self._skip_reason(payment_plan, self._resolve_template(payment_plan)) is None
        ]

    def generate_token_and_order_numbers(self, program: "Program") -> None:
        from hope.models import Payment

        all_eligible = Payment.objects.filter(parent__in=self.payment_plans).eligible()
        XlsxPaymentPlanDeliveryExportService.generate_token_and_order_numbers(all_eligible, program)

    def get_email_context(self, user: "User") -> dict:
        group = self.payment_plan_group
        tag = self.applied_export_tag
        link = reverse("download-payment-plan-group-batch", args=[str(group.id), tag])
        return {
            "first_name": getattr(user, "first_name", ""),
            "last_name": getattr(user, "last_name", ""),
            "email": getattr(user, "email", ""),
            "message": (
                f"Payment Plan Group {group.unicef_id} Batch {tag} Payment List xlsx file "
                "was generated and below you have the link to download this file."
            ),
            "link": link or "",
            "title": f"Payment Plan Group {group.unicef_id} Batch {tag} Payment List Generated",
        }

    def _next_export_tag(self) -> int:
        current_max = self.payment_plan_group.payment_plans.aggregate(max_tag=Max("export_tag"))["max_tag"]
        return (current_max or 0) + 1

    def generate_workbook(self) -> openpyxl.Workbook:
        self._create_workbook()

        header: list[str] = []
        prepared_services: list[XlsxPaymentPlanDeliveryExportService] = []
        self.exported_plan_ids = []
        self.skipped_reasons = []

        shared_lookups = XlsxPaymentPlanDeliveryExportService.build_shared_lookups()

        for payment_plan in self.payment_plans:
            template = self._resolve_template(payment_plan)
            reason = self._skip_reason(payment_plan, template)
            if reason:
                logger.warning(f"Skipping {reason}")
                self.skipped_reasons.append(reason)
                continue
            per_fsp_service = XlsxPaymentPlanDeliveryExportService(payment_plan, shared_lookups=shared_lookups)
            per_fsp_service.prepare_headers(template)
            if not header:
                header = per_fsp_service.header_list
                self.allow_export_fsp_auth_code = per_fsp_service.allow_export_fsp_auth_code
            prepared_services.append(per_fsp_service)
            self.exported_plan_ids.append(payment_plan.id)

        self.ws_export_list.append(header)

        for per_fsp_service in prepared_services:
            payments = per_fsp_service.payment_plan.eligible_payments.select_related(
                "household_snapshot", "currency", "delivery_type", "financial_service_provider", "parent"
            ).order_by("unicef_id")
            for payment in payments.iterator(chunk_size=self.batch_size):
                self.ws_export_list.append(per_fsp_service.get_payment_row(payment))

        self._adjust_column_width_from_col(ws=self.ws_export_list)
        return self.wb

    def save_xlsx_file(self, user: "User") -> None:
        group = self.payment_plan_group
        self.generate_workbook()
        if not self.exported_plan_ids:
            raise EmptyDeliveryExportError(self.skipped_reasons)
        if self.export_tag is not None:
            tag = self.export_tag
        else:
            tag = self._next_export_tag()
        self.applied_export_tag = tag

        if self.allow_export_fsp_auth_code:
            self._save_xlsx_file_with_auth_code(group, tag, user)
        else:
            self._save_plain_xlsx_file(group, tag, user)

    def _save_plain_xlsx_file(self, group: "PaymentPlanGroup", tag: int, user: "User") -> None:
        filename = f"payment_plan_group_{group.unicef_id}_payment_list_batch_{tag}.xlsx"
        with NamedTemporaryFile() as tmp:
            file_temp = FileTemp(
                object_id=str(group.pk),
                content_type=get_content_type_for_model(group),
                created_by=user,
            )
            self.wb.save(tmp.name)
            tmp.seek(0)
            file_temp.file.save(filename, File(tmp))
            with transaction.atomic():
                # bump updated_at so the payment-plan list cache invalidates
                if self.export_tag is not None:
                    PaymentPlan.objects.filter(id__in=self.exported_plan_ids).update(
                        export_file_delivery=file_temp, updated_at=timezone.now()
                    )
                else:
                    PaymentPlan.objects.filter(id__in=self.exported_plan_ids).update(
                        export_tag=tag, export_file_delivery=file_temp, updated_at=timezone.now()
                    )

    def _save_xlsx_file_with_auth_code(self, group: "PaymentPlanGroup", tag: int, user: "User") -> None:
        zip_password = get_random_string(12)
        xlsx_password = get_random_string(12)
        zip_filename = f"payment_plan_group_{group.unicef_id}_payment_list_batch_{tag}.zip"
        xlsx_filename = f"payment_plan_group_{group.unicef_id}_payment_list_batch_{tag}.xlsx"

        with NamedTemporaryFile(suffix=".zip") as tmp_zip:
            with pyzipper.AESZipFile(
                tmp_zip, mode="w", compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES
            ) as zf:
                zf.setpassword(zip_password.encode("utf-8"))
                XlsxPaymentPlanDeliveryExportService.save_workbook(zf, self.wb, xlsx_filename, xlsx_password)

            file_temp = FileTemp(
                object_id=str(group.pk),
                content_type=get_content_type_for_model(group),
                created_by=user,
                password=zip_password,
                xlsx_password=xlsx_password,
            )
            tmp_zip.seek(0)
            file_temp.file.save(zip_filename, File(tmp_zip))
            with transaction.atomic():
                # bump updated_at so the payment-plan list cache invalidates
                if self.export_tag is not None:
                    PaymentPlan.objects.filter(id__in=self.exported_plan_ids).update(
                        export_file_delivery=file_temp, updated_at=timezone.now()
                    )
                else:
                    PaymentPlan.objects.filter(id__in=self.exported_plan_ids).update(
                        export_tag=tag, export_file_delivery=file_temp, updated_at=timezone.now()
                    )
