from typing import Iterable

from django.utils import timezone

from hope.models import Payment, PaymentVerification, PaymentVerificationPlan


class CreatePaymentVerifications:
    BATCH_SIZE = 2000

    def __init__(
        self,
        payment_verification_plan: PaymentVerificationPlan,
        payment_records: Iterable[Payment],
    ) -> None:
        self.payment_verification_plan = payment_verification_plan
        self.payment_records = payment_records

    def create(self) -> None:
        payment_record_verifications_to_create = []
        now = timezone.now()

        for payment_id in self.payment_records.values_list("id", flat=True).iterator():
            payment_record_verifications_to_create.append(
                PaymentVerification(
                    status_date=now,
                    payment_verification_plan=self.payment_verification_plan,
                    payment_id=payment_id,
                    received_amount=None,
                )
            )
            if len(payment_record_verifications_to_create) >= self.BATCH_SIZE:
                PaymentVerification.objects.bulk_create(
                    payment_record_verifications_to_create, batch_size=self.BATCH_SIZE
                )
                payment_record_verifications_to_create.clear()

        if payment_record_verifications_to_create:
            PaymentVerification.objects.bulk_create(payment_record_verifications_to_create, batch_size=self.BATCH_SIZE)
