from typing import IO, TYPE_CHECKING, Dict, List, Optional

from django.db.models import QuerySet

import openpyxl
from xlwt import Row

from hct_mis_api.apps.payment.models import (
    FinancialServiceProviderXlsxTemplate,
    Payment,
)
from hct_mis_api.apps.payment.utils import float_to_decimal, get_quantity_in_usd
from hct_mis_api.apps.payment.xlsx.base_xlsx_import_service import XlsxImportBaseService

if TYPE_CHECKING:
    from hct_mis_api.apps.payment.models import FinancialServiceProvider, PaymentPlan


class XlsxPaymentPlanImportPerFspService(XlsxImportBaseService):
    HEADERS = FinancialServiceProviderXlsxTemplate.DEFAULT_COLUMNS

    def __init__(self, payment_plan: "PaymentPlan", file: IO) -> None:
        self.payment_plan = payment_plan
        self.payment_list: QuerySet["Payment"] = payment_plan.not_excluded_payments
        self.file = file
        self.errors: List = []
        self.payments_dict: Dict = {str(x.unicef_id): x for x in self.payment_list}
        self.payment_ids: List = list(self.payments_dict.keys())
        self.payments_to_save: List = []
        self.fsp: Optional["FinancialServiceProvider"] = None
        self.expected_columns: List[str] = []
        self.is_updated: bool = False

    def _set_fsp_expected_columns(self) -> None:
        first_payment_row = self.ws_payments[2]
        payment_id = first_payment_row[self.HEADERS.index("payment_id")].value
        payment = self.payments_dict[payment_id]

        self.fsp = payment.financial_service_provider
        self.expected_columns = (self.fsp.fsp_xlsx_template and self.fsp.fsp_xlsx_template.columns) or self.HEADERS

    def open_workbook(self) -> openpyxl.Workbook:
        wb = openpyxl.load_workbook(self.file, data_only=True)
        self.wb = wb
        self.ws_payments = wb[wb.sheetnames[0]]
        self._set_fsp_expected_columns()

        return wb

    def _validate_headers(self) -> None:
        headers_row = self.ws_payments[1]

        if len(headers_row) != len(self.expected_columns):
            self.errors.append(
                (
                    self.fsp.name,
                    None,
                    f"Provided headers {[header.value for header in headers_row]}"
                    f" do not match expected headers {self.expected_columns}, "
                    f"please use exported Template File to import data.",
                )
            )
            return

        for header, expected_column in zip(headers_row, self.expected_columns):
            if header.value != expected_column:
                self.errors.append(
                    (
                        self.fsp.name,
                        header.coordinate,
                        f"Unexpected header {header.value}, expected {expected_column}, "
                        f"please use exported Template File to import data.",
                    )
                )

    def _validate_payment_id(self, row: Row) -> None:
        cell = row[self.expected_columns.index("payment_id")]
        if cell.value not in self.payment_ids:
            self.errors.append(
                (
                    self.fsp.name,
                    cell.coordinate,
                    f"This payment id {cell.value} is not in Payment Plan Payment List",
                )
            )

    def _validate_fsp(self, row: Row) -> None:
        cell = row[self.expected_columns.index("payment_id")]
        if cell.value not in self.payment_ids:
            self.errors.append(
                (
                    self.fsp.name,
                    cell.coordinate,
                    f"This payment id {cell.value} is not in Payment Plan Payment List",
                )
            )

    def _validate_delivered_quantity(self, row: Row) -> None:
        payment_id = row[self.expected_columns.index("payment_id")].value
        payment = self.payments_dict.get(payment_id)
        if payment is None:
            return

        cell = row[self.expected_columns.index("delivered_quantity")]
        delivered_quantity = cell.value
        if delivered_quantity is not None and delivered_quantity != "":

            delivered_quantity = float_to_decimal(delivered_quantity)
            if delivered_quantity != payment.delivered_quantity:

                if delivered_quantity == payment.entitlement_quantity:
                    self.is_updated = True
                else:
                    # TODO should we allow delivered_quantity == 0
                    # TODO should we allow and create grievance ticket for these cases
                    self.errors.append(
                        (
                            self.fsp.name,
                            cell.coordinate,
                            f"Payment {payment_id}: Delivered quantity {delivered_quantity} is not equal "
                            f"Entitlement quantity {payment.entitlement_quantity}",
                        )
                    )

    def _validate_rows(self) -> None:
        for row in self.ws_payments.iter_rows(min_row=2):
            if not any([cell.value for cell in row]):
                continue

            self._validate_payment_id(row)
            self._validate_fsp(row)
            self._validate_delivered_quantity(row)

    def _validate_imported_file(self) -> None:
        if not self.is_updated:
            self.errors.append(
                (
                    self.fsp.name,
                    None,
                    "There aren't any updates in imported file, please add changes and try again",
                )
            )

    def validate(self) -> None:
        self._validate_headers()
        self._validate_rows()
        self._validate_imported_file()

    def import_payment_list(self) -> None:
        exchange_rate = self.payment_plan.get_exchange_rate()

        for row in self.ws_payments.iter_rows(min_row=2):
            self._import_row(row, exchange_rate)

        Payment.objects.bulk_update(self.payments_to_save, ("delivered_quantity", "delivered_quantity_usd", "status"))

    def _import_row(self, row: Row, exchange_rate: float) -> None:
        payment_id = row[self.expected_columns.index("payment_id")].value
        payment = self.payments_dict[payment_id]
        delivered_quantity = row[self.expected_columns.index("delivered_quantity")].value

        if delivered_quantity is not None and delivered_quantity != "":
            delivered_quantity = float_to_decimal(delivered_quantity)
            if delivered_quantity != payment.delivered_quantity:
                payment.delivered_quantity = delivered_quantity
                payment.delivered_quantity_usd = get_quantity_in_usd(
                    amount=delivered_quantity,
                    currency=self.payment_plan.currency,
                    exchange_rate=exchange_rate,
                    currency_exchange_date=self.payment_plan.currency_exchange_date,
                )

                payment.status = Payment.STATUS_DISTRIBUTION_SUCCESS
                self.payments_to_save.append(payment)
