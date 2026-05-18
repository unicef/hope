from collections.abc import Iterable
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING, Any

from django.contrib.admin.options import get_content_type_for_model
from django.core.files import File
import openpyxl

from hope.apps.payment.xlsx.xlsx_payment_plan_base_service import XlsxPaymentPlanBaseService
from hope.models import DocumentType, FileTemp, FinancialServiceProviderXlsxTemplate, Payment, PaymentPlan

if TYPE_CHECKING:
    from hope.models import User


class XlsxPaymentPlanExportBaseService(XlsxPaymentPlanBaseService):
    batch_size = 5000
    FILENAME_PREFIX: str
    EXPORT_FILE_FIELD: str

    def __init__(self) -> None:
        self.admin_areas_dict = FinancialServiceProviderXlsxTemplate.get_areas_dict()
        self.all_document_types = DocumentType.get_all_doc_types()
        self.headers = list(self.HEADERS)
        if self.is_social_worker_program:
            self.headers.remove("household_size")
            self.headers.remove("household_id")
            self.headers.remove("collector_id")
        else:
            self.headers.remove("individual_id")

    @property
    def is_social_worker_program(self) -> bool:
        raise NotImplementedError

    def _payment_plans(self) -> Iterable[PaymentPlan]:
        raise NotImplementedError

    def _export_instance(self) -> Any:
        raise NotImplementedError

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
        for payment_plan in self._payment_plans():
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
        instance = self._export_instance()
        filename = f"{self.FILENAME_PREFIX}_{instance.unicef_id or instance.id}.xlsx"
        self.generate_workbook()
        with NamedTemporaryFile() as tmp:
            xlsx_obj = FileTemp(
                object_id=str(instance.pk),
                content_type=get_content_type_for_model(instance),
                created_by=user,
            )
            self.wb.save(tmp.name)
            tmp.seek(0)
            xlsx_obj.file.save(filename, File(tmp))
            setattr(instance, self.EXPORT_FILE_FIELD, xlsx_obj)
            instance.save()
