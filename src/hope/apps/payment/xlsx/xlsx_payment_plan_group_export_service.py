import logging
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING

from django.contrib.admin.options import get_content_type_for_model
from django.core.files import File
import openpyxl
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.dimensions import ColumnDimension, DimensionHolder

from hope.apps.payment.xlsx.xlsx_payment_plan_base_service import XlsxPaymentPlanBaseService
from hope.models import DocumentType, FileTemp, FinancialServiceProviderXlsxTemplate

if TYPE_CHECKING:
    from openpyxl.worksheet.worksheet import Worksheet

    from hope.models import Payment, PaymentPlanGroup, User

logger = logging.getLogger(__name__)


class XlsxPaymentPlanGroupExportService(XlsxPaymentPlanBaseService):
    BATCH_SIZE = 5000
    SHEET_TITLE = "Payments"

    def __init__(self, payment_plan_group: "PaymentPlanGroup") -> None:
        self.payment_plan_group = payment_plan_group
        self.admin_areas_dict = FinancialServiceProviderXlsxTemplate.get_areas_dict()
        self.all_document_types = DocumentType.get_all_doc_types()

    def _headers_for(self, is_social_worker_program: bool) -> list[str]:
        headers = list(self.HEADERS)
        if is_social_worker_program:
            headers.remove("household_size")
            headers.remove("household_id")
            headers.remove("collector_id")
        else:
            headers.remove("individual_id")
        return headers

    def _build_row(self, payment: "Payment", headers: list[str]) -> list:
        # `collector_id` is missing from the shared template mapping, so resolve it here
        # from the snapshot's collector data instead of letting the template return
        # "wrong_column_name".
        snapshot_data = payment.household_snapshot.snapshot_data
        primary_collector = snapshot_data.get("primary_collector", {})
        alternate_collector = snapshot_data.get("alternate_collector", {})
        collector_data = alternate_collector if payment.collector_is_alternate else primary_collector

        row = []
        for column_name in headers:
            if column_name == "collector_id":
                row.append(collector_data.get("unicef_id", ""))
            else:
                row.append(
                    FinancialServiceProviderXlsxTemplate.get_column_value_from_payment(
                        payment,
                        column_name,
                        self.admin_areas_dict,
                        self.all_document_types,
                    )
                )
        return row

    def generate_workbook(self) -> openpyxl.Workbook:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = self.SHEET_TITLE

        payment_plans = list(self.payment_plan_group.payment_plans.order_by("unicef_id"))
        if not payment_plans:
            return wb

        headers = self._headers_for(payment_plans[0].is_social_worker_program)
        ws.append(headers)

        for payment_plan in payment_plans:
            qs = (
                payment_plan.eligible_payments.filter(household_snapshot__isnull=False)
                .select_related(
                    "household_snapshot",
                    "currency",
                    "delivery_type",
                    "financial_service_provider",
                )
                .order_by("unicef_id")
            )
            for payment in qs.iterator(chunk_size=self.BATCH_SIZE):
                ws.append(self._build_row(payment, headers))

        self._adjust_column_width(ws)
        return wb

    @staticmethod
    def _adjust_column_width(ws: "Worksheet") -> None:
        dim_holder = DimensionHolder(worksheet=ws)
        for col in range(ws.min_column, ws.max_column + 1):
            dim_holder[get_column_letter(col)] = ColumnDimension(ws, min=col, max=col, width=20)
        ws.column_dimensions = dim_holder

    def save_xlsx_file(self, user: "User") -> None:
        group = self.payment_plan_group
        filename = f"payment_plan_group_{group.unicef_id or group.pk}.xlsx"
        wb = self.generate_workbook()
        with NamedTemporaryFile() as tmp:
            wb.save(tmp.name)
            tmp.seek(0)
            xlsx_obj = FileTemp(
                object_id=str(group.pk),
                content_type=get_content_type_for_model(group),
                created_by=user,
            )
            xlsx_obj.file.save(filename, File(tmp))
        group.export_file = xlsx_obj
        group.save(update_fields=["export_file", "updated_at"])
