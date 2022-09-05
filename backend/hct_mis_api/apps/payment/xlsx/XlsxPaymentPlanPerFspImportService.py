import openpyxl

from hct_mis_api.apps.payment.xlsx.BaseXlsxImportService import XlsxImportBaseService


class XlsxPaymentPlanImportPerFspService(XlsxImportBaseService):
    def __init__(self, payment_plan, file):
        self.payment_plan = payment_plan
        self.file = file
        self.errors = []

    def open_workbook(self) -> openpyxl.Workbook:
        wb = openpyxl.load_workbook(self.file, data_only=True)
        self.wb = wb
        return wb

    def validate(self):
        # TODO
        # self._validate_headers()
        # self._validate_rows()
        # self._validate_imported_file()
        pass

    def import_payment_list(self):
        print("TODO")
