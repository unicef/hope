from typing import List, Tuple, Dict

import openpyxl
from django.core.exceptions import ValidationError

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
        self.payment_record_verifications = (
            self.cashplan_payment_verification.payment_record_verifications.all()
        )
        self.payment_record_ids = [
            str(x.payment_record_id) for x in self.payment_record_verifications
        ]
        self.payment_record_verifications_dict = {
            str(x.payment_record_id): x
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
            raise ValidationError("You can't import verifications with errors.")
        if not self.was_validation_run:
            raise ValidationError("Run validation before import.")
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
            raise ValidationError(
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

    def _validate_rows(self):
        for row in self.ws_verifications.iter_rows(min_row=2):
            self._validate_row_types(row)
            self._validate_payment_record_id(row)
            self._validate_row_status(row)
