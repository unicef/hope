import logging
from django.contrib.admin.options import get_content_type_for_model
from django.core.files import File
from tempfile import NamedTemporaryFile

from hct_mis_api.apps.payment.models import (
    Payment,
    PaymentPlan,
    FinancialServiceProviderXlsxTemplate,
)
from hct_mis_api.apps.payment.xlsx.BaseXlsxExportService import XlsxExportBaseService
from hct_mis_api.apps.core.models import FileTemp


logger = logging.getLogger(__name__)


class XlsxPaymentPlanExportService(XlsxExportBaseService):
    TITLE = "Payment Plan - Payment List"
    HEADERS = FinancialServiceProviderXlsxTemplate.DEFAULT_COLUMNS

    def __init__(self, payment_plan: PaymentPlan):
        self.payment_plan = payment_plan
        self.payment_list = payment_plan.not_excluded_payments.select_related(
            "household", "collector", "financial_service_provider", "assigned_payment_channel"
        ).order_by("unicef_id")

    def _add_payment_row(self, payment: Payment):
        payment_row = [
            FinancialServiceProviderXlsxTemplate.get_column_value_from_payment(payment, column_name) or ""
            for column_name in self.HEADERS
        ]
        self.ws_export_list.append(payment_row)

    def _add_payment_list(self):
        for payment in self.payment_list:
            self._add_payment_row(payment)

    def generate_workbook(self):
        self._create_workbook()
        self._add_headers()
        self._add_payment_list()
        self._adjust_column_width_from_col(ws=self.ws_export_list, max_col=len(self.HEADERS))
        self._add_col_bgcolor(
            [
                self.HEADERS.index("payment_channel") + 1,
                self.HEADERS.index("entitlement_quantity") + 1,
            ]
        )
        return self.wb

    def save_xlsx_file(self, user):
        filename = f"payment_plan_payment_list_{self.payment_plan.unicef_id or self.payment_plan.id}.xlsx"
        self.generate_workbook()
        with NamedTemporaryFile() as tmp:
            xlsx_obj = FileTemp(
                object_id=self.payment_plan.pk,
                content_type=get_content_type_for_model(self.payment_plan),
                created_by=user,
            )
            self.wb.save(tmp.name)
            tmp.seek(0)
            xlsx_obj.file.save(filename, File(tmp))
            self.payment_plan.export_file = xlsx_obj
            self.payment_plan.save()
