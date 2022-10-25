from typing import List

from django.contrib.admin.options import get_content_type_for_model
from django.utils import timezone

from hct_mis_api.apps.payment.models import (
    PaymentRecord,
    PaymentVerification,
    PaymentVerificationPlan,
)


class CreatePaymentVerifications:
    def __init__(self, payment_verification_plan: PaymentVerificationPlan, payment_records: List[PaymentRecord]):
        self.payment_verification_plan = payment_verification_plan
        self.payment_records = payment_records

    def create(self):
        payment_record_verifications_to_create = []
        for payment_record in self.payment_records:
            payment_record_verification = PaymentVerification(
                status_date=timezone.now(),
                payment_verification_plan=self.payment_verification_plan,
                payment_content_type=get_content_type_for_model(payment_record),
                payment_object_id=payment_record.pk,
            )
            payment_record_verifications_to_create.append(payment_record_verification)
        PaymentVerification.objects.bulk_create(payment_record_verifications_to_create)
