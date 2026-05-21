import logging
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING

from django.contrib.admin.options import get_content_type_for_model
from django.core.files import File
from django.db import transaction
import openpyxl

from hope.apps.payment.xlsx.base_xlsx_export_service import XlsxExportBaseService
from hope.apps.payment.xlsx.xlsx_payment_plan_export_per_fsp_service import XlsxPaymentPlanExportPerFspService
from hope.models import FileTemp, FinancialServiceProviderXlsxTemplate, FspXlsxTemplatePerDeliveryMechanism, PaymentPlan

if TYPE_CHECKING:
    from hope.models import PaymentPlanGroup, User

logger = logging.getLogger(__name__)


class XlsxPaymentPlanGroupExportPerFspService(XlsxExportBaseService):
    """Export every ACCEPTED/FINISHED payment plan of a group into one xlsx with a single sheet.

    The sheet header is the union of the columns of every FSP XLSX template used by the
    selected payment plans. Each payment row only fills the columns defined by its own FSP
    template; columns belonging to other FSPs are left blank.
    """

    TITLE = "Payment Plan Group - Payment List"
    batch_size = 2000

    def __init__(self, payment_plan_group: "PaymentPlanGroup") -> None:
        self.payment_plan_group = payment_plan_group
        self.payment_plans = list(
            payment_plan_group.payment_plans.filter(
                status__in=[PaymentPlan.Status.ACCEPTED, PaymentPlan.Status.FINISHED]
            ).order_by("unicef_id")
        )

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

    def generate_workbook(self) -> openpyxl.Workbook:
        self._create_workbook()

        union_headers: list[str] = []
        seen_columns: set[str] = set()
        prepared_services: list[XlsxPaymentPlanExportPerFspService] = []

        for payment_plan in self.payment_plans:
            template = self._resolve_template(payment_plan)
            if template is None:
                logger.warning(
                    f"Skipping Payment Plan {payment_plan.unicef_id}: no FSP XLSX Template for its FSP "
                    f"and delivery mechanism."
                )
                continue
            per_fsp_service = XlsxPaymentPlanExportPerFspService(payment_plan)
            per_fsp_service.prepare_headers(template)
            for column_name in per_fsp_service.header_list:
                if column_name not in seen_columns:
                    seen_columns.add(column_name)
                    union_headers.append(column_name)
            prepared_services.append(per_fsp_service)

        self.ws_export_list.append(union_headers)

        column_index = {name: index for index, name in enumerate(union_headers)}
        for per_fsp_service in prepared_services:
            payments = per_fsp_service.payment_plan.eligible_payments.select_related(
                "household_snapshot", "currency", "delivery_type", "financial_service_provider", "parent"
            ).order_by("unicef_id")
            for payment in payments.iterator(chunk_size=self.batch_size):
                values = per_fsp_service.get_payment_row(payment)
                row: list = [""] * len(union_headers)
                for column_name, value in zip(per_fsp_service.header_list, values, strict=True):
                    row[column_index[column_name]] = value
                self.ws_export_list.append(row)

        self._adjust_column_width_from_col(ws=self.ws_export_list)
        return self.wb

    def save_xlsx_file(self, user: "User") -> None:
        group = self.payment_plan_group
        filename = f"payment_plan_group_payment_list_{group.unicef_id or group.id}.xlsx"
        self.generate_workbook()
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
                group.delivery_export_file = file_temp
                group.save(update_fields=["delivery_export_file", "updated_at"])
