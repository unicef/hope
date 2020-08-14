from decimal import Decimal

import openpyxl
from graphql import GraphQLError

from payment.models import PaymentVerification
from payment.xlsx.XlsxVerificationExportService import (
    XlsxVerificationExportService,
)


class XlsxVerificationImportService:
    TYPES_READABLE_MAPPING = {"s": "text", "n": "number"}
    COLUMNS_TYPES = ("s", "s", "s", "s", "n", "n")

    PAYMENT_VERIFICATION_STATUSES = [
        x[0] for x in PaymentVerification.STATUS_CHOICES
    ]

    def __init__(self, cashplan_payment_verification, file):
        self.file = file
        self.cashplan_payment_verification = cashplan_payment_verification
        self.payment_record_verifications = (
            cashplan_payment_verification.payment_record_verifications.all()
        )
        self.current_row = 0
        self.errors = []
        self.cashplan_payment_verification = cashplan_payment_verification
        self.payment_record_verifications = self.cashplan_payment_verification.payment_record_verifications.all().prefetch_related(
            "payment_record"
        )
        self.payment_record_ids = [
            str(x.payment_record_id) for x in self.payment_record_verifications
        ]
        self.payment_record_verifications_dict = {
            str(x.payment_record_id): x
            for x in self.payment_record_verifications
        }
        self.payment_records_dict = {
            str(x.payment_record_id): x.payment_record
            for x in self.payment_record_verifications
        }
        self.payment_verifications_to_save = []
        self.was_validation_run = False

    def open_workbook(self) -> openpyxl.Workbook:
        wb = openpyxl.load_workbook(self.file)
        self.wb = wb
        self.ws_verifications = wb[
            XlsxVerificationExportService.VERIFICATION_SHEET
        ]
        return wb

    def validate(self):
        self._check_version()
        self._validate_headers()
        self._validate_rows()
        self.was_validation_run = True

    def import_verifications(self):
        if len(self.errors):
            raise GraphQLError("You can't import verifications with errors.")
        if not self.was_validation_run:
            raise GraphQLError("Run validation before import.")
        for row in self.ws_verifications.iter_rows(min_row=2):
            self._import_row(row)
        PaymentVerification.objects.bulk_update(
            self.payment_verifications_to_save, ("status", "received_amount")
        )

    def _check_version(self):
        ws_meta = self.wb[XlsxVerificationExportService.META_SHEET]
        version_cell_name = ws_meta[
            XlsxVerificationExportService.VERSION_CELL_NAME_COORDINATES
        ].value
        version = ws_meta[
            XlsxVerificationExportService.VERSION_CELL_COORDINATES
        ].value

        if (
            version_cell_name != XlsxVerificationExportService.VERSION_CELL_NAME
            or version != XlsxVerificationExportService.VERSION
        ):
            raise GraphQLError(
                f"Unsupported file version ({version}). Only version: {XlsxVerificationExportService.VERSION} is supported"
            )

    def _validate_headers(self):
        headers_row = self.ws_verifications[1]
        accepted_headers = XlsxVerificationExportService.HEADERS
        if len(headers_row) != len(accepted_headers):
            self.errors.append(
                (
                    "Payment Verifications",
                    None,
                    f"Different count of headers. Acceptable headers count in file version {XlsxVerificationExportService.VERSION}: {len(accepted_headers)}",
                )
            )
        column = 0
        for header in headers_row:
            if column >= len(accepted_headers):
                self.errors.append(
                    (
                        "Payment Verifications",
                        header.coordinate,
                        f"Unexpected header {header.value}",
                    )
                )
            elif header.value != accepted_headers[column]:
                self.errors.append(
                    (
                        "Payment Verifications",
                        header.coordinate,
                        f"Unexpected header {header.value} expected {accepted_headers[column]}",
                    )
                )
            column += 1

    def _validate_row_types(self, row):
        column = 0
        for cell in row:

            if (
                cell.data_type
                != XlsxVerificationImportService.COLUMNS_TYPES[column]
            ):
                self.errors.append(
                    (
                        "Payment Verifications",
                        cell.coordinate,
                        f"Wrong type off cell"
                        f" {XlsxVerificationImportService.TYPES_READABLE_MAPPING[XlsxVerificationImportService.COLUMNS_TYPES[column]]}"
                        f" expected, {XlsxVerificationImportService.TYPES_READABLE_MAPPING[cell.data_type]} given.",
                    )
                )
            column += 1

    def _validate_payment_record_id(self, row):
        cell = row[0]
        if cell.value not in self.payment_record_ids:
            self.errors.append(
                (
                    "Payment Verifications",
                    cell.coordinate,
                    f"This payment record id {cell.value} is not in Cash Plan Payment Record Verification",
                )
            )

    def _validate_row_status(self, row):
        cell = row[1]
        if (
            cell.value
            not in XlsxVerificationImportService.PAYMENT_VERIFICATION_STATUSES
        ):
            self.errors.append(
                (
                    "Payment Verifications",
                    cell.coordinate,
                    f"The status of this payment verification is not correct: {cell.value} should be one of: {XlsxVerificationImportService.PAYMENT_VERIFICATION_STATUSES}",
                )
            )

    def _validate_status_to_received_amount(self, row):
        payment_record_id = row[0].value
        payment_record = self.payment_records_dict.get(payment_record_id)
        if payment_record is None:
            return
        delivered_amount = payment_record.delivered_quantity
        received_amount = row[5].value
        if received_amount is not None:
            received_amount = Decimal(format(round(received_amount, 2), '.2f'))
        status_cell = row[1]
        status = status_cell.value
        if (
            status == PaymentVerification.STATUS_PENDING
            and received_amount is not None
        ):
            self.errors.append(
                (
                    "Payment Verifications",
                    status_cell.coordinate,
                    f"Wrong status {PaymentVerification.STATUS_PENDING} when received_amount ({received_amount}) is not empty",
                )
            )
        elif (
            status == PaymentVerification.STATUS_NOT_RECEIVED
            and received_amount is not None
            and received_amount != Decimal(0)
        ):
            self.errors.append(
                (
                    "Payment Verifications",
                    status_cell.coordinate,
                    f"Wrong status {PaymentVerification.STATUS_NOT_RECEIVED} when received_amount ({received_amount}) is not 0 or empty",
                )
            )
        elif status == PaymentVerification.STATUS_RECEIVED_WITH_ISSUES and (
            received_amount is None or received_amount == Decimal(0)
        ):
            self.errors.append(
                (
                    "Payment Verifications",
                    status_cell.coordinate,
                    f"Wrong status {PaymentVerification.STATUS_RECEIVED_WITH_ISSUES} when received_amount ({received_amount}) is 0 or empty",
                )
            )
        elif (
            status == PaymentVerification.STATUS_RECEIVED
            and received_amount != delivered_amount
        ):
            received_amount_text = (
                "None" if received_amount is None else received_amount
            )
            self.errors.append(
                (
                    "Payment Verifications",
                    status_cell.coordinate,
                    f"Wrong status {PaymentVerification.STATUS_RECEIVED} when received_amount ({received_amount_text}) ≠ delivered_amount ({delivered_amount})",
                )
            )

    def _validate_rows(self):
        for row in self.ws_verifications.iter_rows(min_row=2):
            self._validate_row_types(row)
            self._validate_payment_record_id(row)
            self._validate_row_status(row)
            self._validate_status_to_received_amount(row)

    def _import_row(self, row):
        payment_record_id = row[0].value
        status = row[1].value
        received_amount = row[5].value
        payment_verification = self.payment_record_verifications_dict[
            payment_record_id
        ]
        payment_verification.status = status
        if received_amount is not None and received_amount != "":
            payment_verification.received_amount = received_amount
        self.payment_verifications_to_save.append(payment_verification)
