import logging
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING

from django.contrib.admin.options import get_content_type_for_model
from django.core.files import File

import openpyxl

from hct_mis_api.apps.core.models import FileTemp
from hct_mis_api.apps.payment.models import (
    FinancialServiceProviderXlsxTemplate,
    Payment,
    PaymentPlan,
)
from hct_mis_api.apps.payment.xlsx.base_xlsx_export_service import XlsxExportBaseService
from hct_mis_api.apps.payment.xlsx.xlsx_payment_plan_base_service import (
    XlsxPaymentPlanBaseService,
)

if TYPE_CHECKING:
    from hct_mis_api.apps.account.models import User

logger = logging.getLogger(__name__)


class XlsxPaymentPlanExportService(XlsxPaymentPlanBaseService, XlsxExportBaseService):
    def __init__(self, payment_plan: PaymentPlan):
        self.batch_size = 5000
        self.payment_plan = payment_plan

    def _add_payment_row(self, payment: Payment) -> None:
        payment_row = [
            FinancialServiceProviderXlsxTemplate.get_column_value_from_payment(payment, column_name)
            for column_name in self.HEADERS
        ]
        self.ws_export_list.append(payment_row)

    def _add_payment_list(self) -> None:
        qs = (
            self.payment_plan.eligible_payments.all()
            .select_related(
                "household_snapshot",
                "delivery_type",
                "financial_service_provider",
            )
            .order_by("unicef_id")
        )
        for payment in qs.iterator(chunk_size=self.batch_size):
            self._add_payment_row(payment)

    def generate_workbook(self) -> openpyxl.Workbook:
        self._create_workbook()
        self._add_headers()
        self._add_payment_list()
        self._adjust_column_width_from_col(ws=self.ws_export_list)
        self._add_col_bgcolor(
            [
                self.HEADERS.index("entitlement_quantity") + 1,
            ],
        )
        return self.wb

    def save_xlsx_file(self, user: "User") -> None:
        filename = f"payment_plan_payment_list_{self.payment_plan.unicef_id or self.payment_plan.id}.xlsx"
        self.generate_workbook()
        with NamedTemporaryFile() as tmp:
            xlsx_obj = FileTemp(
                object_id=str(self.payment_plan.pk),
                content_type=get_content_type_for_model(self.payment_plan),
                created_by=user,
            )
            self.wb.save(tmp.name)
            tmp.seek(0)
            xlsx_obj.file.save(filename, File(tmp))
            self.payment_plan.export_file_entitlement = xlsx_obj
            self.payment_plan.save()
