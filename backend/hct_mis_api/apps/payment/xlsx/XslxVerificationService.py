from typing import List, Tuple, Dict

import openpyxl


class XslxVerificationService:
    def __init__(self, cashplan_payment_verification):
        self.cashplan_payment_verification = cashplan_payment_verification
        self.payment_record_verifications = (
            cashplan_payment_verification.payment_record_verifications.all()
        )

    def _create_workbook(self) -> openpyxl.Workbook:
        wb = openpyxl.Workbook()
        ws_verifications = wb.active
        ws_verifications.title = "Payment Verifications"
        self.wb = wb
        self.ws_verifications = ws_verifications
        return wb

    def _add_headers(self):
        headers_row = (
            "payment_record_id",
            "verification_status",
            "head_of_household",
            "household_id",
            "delivered_amount",
            "received_amount",
        )
        self.ws_verifications.append(headers_row)

    def _add_payment_record_verification_row(self, payment_record_verification):

        payment_record_verification_row = (
            str(payment_record_verification.payment_record.id),
            payment_record_verification.status,
            str(
                payment_record_verification.payment_record.household.head_of_household_id
            ),
            str(payment_record_verification.payment_record.household_id),
            payment_record_verification.payment_record.delivered_quantity,
            payment_record_verification.received_amount,
        )
        self.ws_verifications.append(payment_record_verification_row)

    def _add_payment_record_verifications(self):
        for payment_record_verification in self.payment_record_verifications:
            self._add_payment_record_verification_row(
                payment_record_verification
            )

    def generate_workbook(self):
        self._create_workbook()
        self._add_headers()
        self._add_payment_record_verifications()
        return self.wb

    def generate_file(self, filename):
        self.generate_workbook()
        self.wb.save(filename=filename)
