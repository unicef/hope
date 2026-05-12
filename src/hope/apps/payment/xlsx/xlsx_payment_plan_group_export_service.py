import logging
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING

from django.contrib.admin.options import get_content_type_for_model
from django.core.files import File
import openpyxl

from hope.apps.payment.xlsx.base_xlsx_export_service import XlsxExportBaseService
from hope.apps.payment.xlsx.xlsx_payment_plan_base_service import XlsxPaymentPlanBaseService
from hope.models import DocumentType, FileTemp, FinancialServiceProviderXlsxTemplate, Payment

if TYPE_CHECKING:
    from hope.models import PaymentPlanGroup, User

logger = logging.getLogger(__name__)


class XlsxPaymentPlanGroupExportService(XlsxPaymentPlanBaseService, XlsxExportBaseService):
    TITLE = "Payment Plan Group - Payment List"

    def __init__(self, payment_plan_group: "PaymentPlanGroup") -> None:
        self.batch_size = 5000
        self.payment_plan_group = payment_plan_group
        self.payment_plans = list(payment_plan_group.payment_plans.order_by("unicef_id"))
        self.admin_areas_dict = FinancialServiceProviderXlsxTemplate.get_areas_dict()
        self.all_document_types = DocumentType.get_all_doc_types()
        self.headers = list(self.HEADERS)
        is_social_worker_program = self.payment_plan_group.cycle.program.is_social_worker_program
        if is_social_worker_program:
            self.headers.remove("household_size")
            self.headers.remove("household_id")
            self.headers.remove("collector_id")
        else:
            self.headers.remove("individual_id")

    def _add_payment_row(self, payment: Payment) -> None:
        payment_row = [
            FinancialServiceProviderXlsxTemplate.get_column_value_from_payment(
                payment,
                column_name,
                self.admin_areas_dict,
                self.all_document_types,
            )
            for column_name in self.headers
        ]
        self.ws_export_list.append(payment_row)

    def _add_payment_list(self) -> None:
        for payment_plan in self.payment_plans:
            qs = (
                payment_plan.eligible_payments.all()
                .select_related(
                    "household_snapshot",
                    "currency",
                    "delivery_type",
                    "financial_service_provider",
                )
                .order_by("unicef_id")
            )
            for payment in qs.iterator(chunk_size=self.batch_size):
                self._add_payment_row(payment)

    def _add_headers(self) -> None:
        self.ws_export_list.append(self.headers)

    def generate_workbook(self) -> openpyxl.Workbook:
        self._create_workbook()
        self._add_headers()
        self._add_payment_list()
        self._adjust_column_width_from_col(ws=self.ws_export_list)
        self._add_col_bgcolor(
            [
                self.headers.index("entitlement_quantity") + 1,
            ],
        )
        return self.wb

    def save_xlsx_file(self, user: "User") -> None:
        filename = f"payment_plan_group_{self.payment_plan_group.unicef_id}.xlsx"
        self.generate_workbook()
        with NamedTemporaryFile() as tmp:
            xlsx_obj = FileTemp(
                object_id=str(self.payment_plan_group.pk),
                content_type=get_content_type_for_model(self.payment_plan_group),
                created_by=user,
            )
            self.wb.save(tmp.name)
            tmp.seek(0)
            xlsx_obj.file.save(filename, File(tmp))
            self.payment_plan_group.export_file = xlsx_obj
            self.payment_plan_group.save(update_fields=["export_file", "updated_at"])
