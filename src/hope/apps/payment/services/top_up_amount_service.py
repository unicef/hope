from decimal import Decimal
from typing import IO, TYPE_CHECKING
from zipfile import BadZipFile

from django.core.exceptions import ValidationError
import openpyxl
from openpyxl.utils.exceptions import InvalidFileException
from openpyxl.worksheet.worksheet import Worksheet

from hope.apps.payment.utils import to_decimal
from hope.apps.payment.xlsx.xlsx_payment_list_base_service import XlsxPaymentListBaseService
from hope.apps.payment.xlsx.xlsx_payment_list_export_service import XlsxPaymentListExportService

if TYPE_CHECKING:
    from hope.models import Payment, PaymentList


class TopUpAmountTemplateService(XlsxPaymentListExportService):
    """Blank amount template listing the payments eligible for a payment plan's Top-Up or Amendment.

    One sheet for every source payment list of the payment plan. Same sheet shape as the entitlement export
    operators already know, with two differences: the rows are each plan's
    ``eligible_payments_for_child_plan()`` rather than every eligible payment, and the entitlement
    columns ship empty. Empty is deliberate — prefilling the source amount invites the operator to
    submit it unchanged, which would silently repeat the original payment instead of topping it up.
    The payment lists of one payment plan share a programme, so the first one sets the columns.
    """

    def __init__(self, source_payment_lists: list["PaymentList"]) -> None:
        super().__init__(source_payment_lists[0])
        self.source_payment_lists = source_payment_lists

    def _add_payment_list(self) -> None:
        for source_payment_list in self.source_payment_lists:
            qs = (
                source_payment_list.eligible_payments_for_child_plan()
                .select_related("household_snapshot", "currency", "delivery_type", "financial_service_provider")
                .order_by("unicef_id")
            )
            for payment in qs.iterator(chunk_size=self.batch_size):
                self._add_payment_row(payment)

    def _payment_row(self, payment: "Payment") -> list:
        # Blank the amounts before the row reaches the sheet: reading them back out of openpyxl
        # costs a full-sheet scan per row, which turns a 10k export into minutes.
        row = super()._payment_row(payment)
        for column_name in (self.COLUMN_ENTITLEMENT_QUANTITY, "entitlement_quantity_usd"):
            row[self.headers.index(column_name)] = None
        return row


def _open_amount_sheet(file: IO[bytes]) -> Worksheet:
    try:
        workbook = openpyxl.load_workbook(file, data_only=True)
    except (InvalidFileException, BadZipFile, OSError):
        raise ValidationError("The uploaded file could not be read as an XLSX workbook.")
    sheet_name = XlsxPaymentListBaseService.payment_sheet_name(workbook.sheetnames)
    if sheet_name is None:
        raise ValidationError(f"Sheet '{XlsxPaymentListBaseService.TITLE}' not found in the uploaded file.")
    return workbook[sheet_name]


def _row_amount(raw_amount: object, payment_id: str) -> Decimal | None:
    """Amount for one row, or ``None`` when the row funds nobody (blank or zero)."""
    if raw_amount is None or str(raw_amount).strip() == "":
        return None
    amount = to_decimal(str(raw_amount))  # returns None for anything non-numeric
    if amount is None:
        raise ValidationError(f"Invalid amount '{raw_amount}' for payment {payment_id}.")
    if amount < 0:
        raise ValidationError(f"Negative amount '{raw_amount}' for payment {payment_id}.")
    return amount or None


def parse_top_up_amount_file(source_payment_lists: list["PaymentList"], file: IO[bytes]) -> dict[str, Decimal]:
    """Read a filled-in Top-Up amount template into ``{payment unicef_id: amount}``.

    Only funded rows are returned: a row left empty or set to zero means the beneficiary is not
    part of the Top-Up at all, which is how the operator narrows it down. Raises when the file is
    unreadable, references payments outside the source plans' eligible sets, carries a negative or
    non-numeric amount, or funds nobody.
    """
    worksheet = _open_amount_sheet(file)
    headers = [cell.value for cell in worksheet[1]]
    required_columns = (
        XlsxPaymentListBaseService.COLUMN_PAYMENT_ID,
        XlsxPaymentListBaseService.COLUMN_ENTITLEMENT_QUANTITY,
    )
    missing = [column for column in required_columns if column not in headers]
    if missing:
        raise ValidationError(f"Column '{missing[0]}' is required in the amount file.")

    payment_id_index = headers.index(XlsxPaymentListBaseService.COLUMN_PAYMENT_ID)
    amount_index = headers.index(XlsxPaymentListBaseService.COLUMN_ENTITLEMENT_QUANTITY)
    eligible_ids = {
        unicef_id
        for source_payment_list in source_payment_lists
        for unicef_id in source_payment_list.eligible_payments_for_child_plan().values_list("unicef_id", flat=True)
    }

    amounts: dict[str, Decimal] = {}
    # Tracked separately from ``amounts``, which a blank or zero row never reaches: checking there
    # would let a duplicate through or not depending on which of its rows carries the amount.
    seen_payment_ids: set[str] = set()
    for row in worksheet.iter_rows(min_row=2):
        raw_payment_id = row[payment_id_index].value
        if raw_payment_id is None:
            continue
        payment_id = str(raw_payment_id).strip()
        if payment_id not in eligible_ids:
            raise ValidationError(f"Payment {payment_id} is not eligible for a Top-Up of this Payment Plan.")
        if payment_id in seen_payment_ids:
            raise ValidationError(f"Payment {payment_id} appears more than once in the amount file.")
        seen_payment_ids.add(payment_id)
        if (amount := _row_amount(row[amount_index].value, payment_id)) is not None:
            amounts[payment_id] = amount

    if not amounts:
        raise ValidationError("The amount file funds nobody — set an amount above zero for at least one beneficiary.")
    return amounts
