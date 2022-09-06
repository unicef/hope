import openpyxl

from hct_mis_api.apps.payment.xlsx.BaseXlsxImportService import XlsxImportBaseService
from hct_mis_api.apps.payment.models import Payment
from hct_mis_api.apps.payment.xlsx.XlsxPaymentPlanExportService import XlsxPaymentPlanExportService


class XlsxPaymentPlanImportPerFspService(XlsxImportBaseService):
    def __init__(self, payment_plan, file):
        self.payment_plan = payment_plan
        self.payment_list = payment_plan.all_active_payments
        self.file = file
        self.errors = []
        self.payments_dict = {str(x.unicef_id): x for x in self.payment_list}
        self.payments_to_save = []

    def open_workbook(self) -> openpyxl.Workbook:
        wb = openpyxl.load_workbook(self.file, data_only=True)
        self.wb = wb
        self.ws_payments = wb[wb.sheetnames[0]]
        return wb

    def validate(self):
        # TODO
        # self._validate_headers()
        # self._validate_rows()
        # self._validate_imported_file()
        pass

    def import_payment_list(self):
        for row in self.ws_payments.iter_rows(min_row=2):
            self._import_row(row)

        Payment.objects.bulk_update(self.payments_to_save, ("delivered_quantity",))

    def _import_row(self, row):
        payment_id = row[XlsxPaymentPlanExportService.ID_COLUMN_INDEX].value
        payment = self.payments_dict[payment_id]
        payment.delivered_quantity = row[7].value
        self.payments_to_save.append(payment)
