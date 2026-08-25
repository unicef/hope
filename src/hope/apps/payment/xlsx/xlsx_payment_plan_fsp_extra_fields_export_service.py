from typing import TYPE_CHECKING

from django.db.models import QuerySet
import openpyxl
from openpyxl import Workbook

from hope.apps.payment.xlsx.base_xlsx_export_service import XlsxExportBaseService
from hope.models import Payment, PaymentPlan

if TYPE_CHECKING:
    from openpyxl.worksheet.worksheet import Worksheet


class XlsxPaymentPlanFspExtraFieldsExportService(XlsxExportBaseService):
    TITLE = "Payment Plan - FSP Extra Fields"
    PAYMENT_ID_COLUMN = "payment_id"
    BATCH_SIZE = 2000

    def __init__(self, payment_plan: PaymentPlan) -> None:
        self.payment_plan = payment_plan
        self.headers = [self.PAYMENT_ID_COLUMN, *self._fsp_extra_fields_headers()]

    def _payments(self) -> QuerySet[Payment]:
        return self.payment_plan.eligible_payments.order_by("unicef_id").only("unicef_id", "extras")

    def _fsp_extra_fields_headers(self) -> list[str]:
        headers: set[str] = set()
        for payment in self._payments().iterator(chunk_size=self.BATCH_SIZE):
            headers.update(payment.fsp_extra_fields)
        return sorted(headers)

    def generate_workbook(self) -> Workbook:
        workbook = openpyxl.Workbook()
        worksheet: Worksheet = workbook.active
        worksheet.title = self.TITLE
        worksheet.append(self.headers)

        custom_headers = self.headers[1:]
        for payment in self._payments().iterator(chunk_size=self.BATCH_SIZE):
            worksheet.append(
                [
                    str(payment.unicef_id),
                    *(payment.fsp_extra_fields.get(header, "") for header in custom_headers),
                ]
            )

        self._adjust_column_width_from_col(worksheet)
        return workbook

    @property
    def filename(self) -> str:
        identifier = self.payment_plan.unicef_id or self.payment_plan.id
        return f"payment_plan_{identifier}_fsp_extra_fields.xlsx"
