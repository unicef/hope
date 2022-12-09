from typing import List

from django.utils import timezone

from hct_mis_api.apps.payment.models import (
    CashPlanPaymentVerification,
    PaymentRecord,
    PaymentVerification,
)


class CreatePaymentVerifications:
    def __init__(
        self, cash_plan_verification: CashPlanPaymentVerification, payment_records: List[PaymentRecord]
    ) -> None:
        self.cash_plan_verification = cash_plan_verification
        self.payment_records = payment_records

    def create(self) -> None:
        payment_record_verifications_to_create = []
        for payment_record in self.payment_records:
            payment_record_verification = PaymentVerification(
                status_date=timezone.now(),
                cash_plan_payment_verification=self.cash_plan_verification,
                payment_record=payment_record,
            )
            payment_record_verifications_to_create.append(payment_record_verification)
        PaymentVerification.objects.bulk_create(payment_record_verifications_to_create)
