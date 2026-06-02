import logging
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING

from django.contrib.admin.options import get_content_type_for_model
from django.core.files import File
from django.db import transaction
from django.db.models import Max
import openpyxl

from hope.apps.payment.xlsx.base_xlsx_export_service import XlsxExportBaseService
from hope.apps.payment.xlsx.xlsx_payment_plan_delivery_export_service import XlsxPaymentPlanDeliveryExportService
from hope.models import FileTemp, FinancialServiceProviderXlsxTemplate, FspXlsxTemplatePerDeliveryMechanism, PaymentPlan

if TYPE_CHECKING:
    from hope.models import PaymentPlanGroup, User

logger = logging.getLogger(__name__)


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

    def __init__(self, payment_plan_group: "PaymentPlanGroup") -> None:
        self.payment_plan_group = payment_plan_group
        self.payment_plans = list(
            payment_plan_group.payment_plans.filter(
                status__in=[PaymentPlan.Status.ACCEPTED, PaymentPlan.Status.FINISHED],
                plan_type=PaymentPlan.PlanType.REGULAR,
                export_tag__isnull=True,
            ).order_by("unicef_id")
        )
        self.exported_plan_ids: list = []

    @staticmethod
    def _resolve_template(payment_plan: PaymentPlan) -> FinancialServiceProviderXlsxTemplate | None:
        fsp = payment_plan.financial_service_provider
        delivery_mechanism = payment_plan.delivery_mechanism
        if not fsp or not delivery_mechanism:
            return None
        mapping = FspXlsxTemplatePerDeliveryMechanism.objects.filter(
            financial_service_provider=fsp,
            delivery_mechanism=delivery_mechanism,
        ).first()
        return mapping.xlsx_template if mapping else None

    def _next_export_tag(self) -> int:
        current_max = self.payment_plan_group.payment_plans.aggregate(max_tag=Max("export_tag"))["max_tag"]
        return (current_max or 0) + 1

    def generate_workbook(self) -> openpyxl.Workbook:
        self._create_workbook()

        header: list[str] = []
        prepared_services: list[XlsxPaymentPlanDeliveryExportService] = []
        self.exported_plan_ids = []

        for payment_plan in self.payment_plans:
            template = self._resolve_template(payment_plan)
            if template is None:
                logger.warning(
                    f"Skipping Payment Plan {payment_plan.unicef_id}: no FSP XLSX Template for its FSP "
                    f"and delivery mechanism."
                )
                continue
            per_fsp_service = XlsxPaymentPlanDeliveryExportService(payment_plan)
            per_fsp_service.prepare_headers(template)
            if not header:
                header = per_fsp_service.header_list
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
        next_tag = self._next_export_tag()
        if not self.exported_plan_ids:
            return
        filename = f"payment_plan_group_{group.unicef_id or group.id}_payment_list_batch_{next_tag}.xlsx"
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
                exported_plans = list(self.payment_plans)
                first_plan = next(plan for plan in exported_plans if plan.id in self.exported_plan_ids)
                first_plan.group_export_file = file_temp
                first_plan.export_tag = next_tag
                first_plan.save(update_fields=["group_export_file", "export_tag", "updated_at"])
                other_ids = [pk for pk in self.exported_plan_ids if pk != first_plan.id]
                if other_ids:
                    PaymentPlan.objects.filter(id__in=other_ids).update(export_tag=next_tag)
