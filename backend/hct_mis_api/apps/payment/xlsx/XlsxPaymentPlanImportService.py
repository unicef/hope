from decimal import Decimal

import openpyxl

from hct_mis_api.apps.payment.utils import float_to_decimal
from hct_mis_api.apps.payment.xlsx.XlsxPaymentPlanExportService import XlsxPaymentPlanExportService


class XlsxPaymentPlanImportService:
    TYPES_READABLE_MAPPING = {
        "s": "text",
        "n": "number",
        "f": "formula",
        "b": "bool",
        "inlineStr": "inlineStr",
        "e": "error",
        "str": "text",
    }

    ENTITLEMENT_COLUMN_INDEX = 0

    def __int__(self, payment_plan, file):
        self.payment_plan = payment_plan
        self.payment_list = payment_plan.all_active_payments
        self.file = file
        self.errors = []
        self.payments_dict = {}

        self.payments_to_save = []
        self.was_validation_run = False

    def open_workbook(self) -> openpyxl.Workbook:
        file = ""
        wb = openpyxl.load_workbook(file, data_only=True)
        self.wb = wb
        self.ws_payments = wb[XlsxPaymentPlanExportService.TITLE]
        return wb

    def validate(self):
        self._validate_headers()
        self._validate_rows()
        self.was_validation_run = True

    def import_payment_list(self):
        pass

    def _validate_headers(self):
        headers_row = self.ws_payments[1]
        accepted_headers = XlsxPaymentPlanExportService.HEADERS
        if len(headers_row) != len(accepted_headers):
            self.errors.append(
                (
                    "Payment Plan",
                    None,
                    f"Different count of headers. Acceptable headers are: [{accepted_headers}]",
                )
            )
        column = 0
        for header in headers_row:
            if column >= len(accepted_headers):
                self.errors.append(
                    (
                        "Payment Plan",
                        header.coordinate,
                        f"Unexpected header {header.value}",
                    )
                )
            elif header.value != accepted_headers[column]:
                self.errors.append(
                    (
                        "Payment Plan",
                        header.coordinate,
                        f"Unexpected header {header.value} expected {accepted_headers[column]}",
                    )
                )
            column += 1

    def _validate_row_types(self, row):
        column = 0
        for cell in row:
            if cell.value is None:
                column += 1
                continue
            if cell.data_type != XlsxPaymentPlanImportService.COLUMNS_TYPES[column]:
                readable_cell_error = XlsxPaymentPlanImportService.TYPES_READABLE_MAPPING[
                    XlsxPaymentPlanImportService.COLUMNS_TYPES[column]
                ]
                self.errors.append(
                    (
                        "Payment Plan",
                        cell.coordinate,
                        f"Wrong type off cell {readable_cell_error} "
                        f"expected, {XlsxPaymentPlanImportService.TYPES_READABLE_MAPPING[cell.data_type]} given.",
                    )
                )
            column += 1

    def _validate_payment_record_id(self, row):
        cell = row[0]
        if cell.value not in self.ws_payments:
            self.errors.append(
                (
                    "Payment Plan",
                    cell.coordinate,
                    f"This payment id {cell.value} is not in Payment Plan Payment List",
                )
            )

    def _validate_entitlement_and_payment_chanel(self, row):
        payment_id = row[0].value
        payment = self.payments_dict.get(payment_id)
        if payment is None:
            return
        entitlement_amount = row[XlsxPaymentPlanImportService.ENTITLEMENT_COLUMN_INDEX].value
        if entitlement_amount is not None:
            if not isinstance(entitlement_amount, float) and not isinstance(entitlement_amount, int):
                return
            entitlement_amount = Decimal(format(round(entitlement_amount, 2), ".2f"))

        # TODO: add validation if wrong value

    def _validate_rows(self):
        for row in self.ws_payment_list.iter_rows(min_row=2):
            if not any([cell.value for cell in row]):
                continue
            self._validate_row_types(row)
            self._validate_payment_record_id(row)
            self._validate_entitlement_and_usd_entitlement(row)

    def _import_row(self, row):
        payment_id = row[XlsxPaymentPlanImportService.ID_COLUMN_INDEX].value
        entitlement_amount = row[XlsxPaymentPlanImportService.ENTITLEMENT_COLUMN_INDEX].value
        usd_entitlement_amount = row[XlsxPaymentPlanImportService.USD_ENTITLEMENT_COLUMN_INDEX].value
        payment = self.payments_dict[payment_id]

        if entitlement_amount is not None and entitlement_amount != "":
            payment.entitlement_quantity = float_to_decimal(entitlement_amount)
        if usd_entitlement_amount is not None and usd_entitlement_amount != "":
            payment.entitlement_quantity_usd = float_to_decimal(usd_entitlement_amount)

        self.payments_to_save.append(payment)
