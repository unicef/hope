from typing import Iterable

from django.utils import timezone

from hct_mis_api.apps.payment.models import (
    PaymentRecord,
    PaymentVerification,
    PaymentVerificationPlan,
)


class CreatePaymentVerifications:
    def __init__(
        self, payment_verification_plan: PaymentVerificationPlan, payment_records: Iterable[PaymentRecord]
    ) -> None:
        self.payment_verification_plan = payment_verification_plan
        self.payment_records = payment_records

    def create(self) -> None:
        payment_record_verifications_to_create = []
        for payment_record in self.payment_records:
            payment_record_verification = PaymentVerification(
                status_date=timezone.now(),
                payment_verification_plan=self.payment_verification_plan,
                payment_obj=payment_record,
                received_amount=None,
            )
            payment_record_verifications_to_create.append(payment_record_verification)
        PaymentVerification.objects.bulk_create(payment_record_verifications_to_create)
