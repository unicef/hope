from typing import TYPE_CHECKING, Any

from django.db.models import QuerySet

from rest_framework.exceptions import ValidationError

from hope.apps.payment.models import PaymentVerificationPlan
from hope.apps.payment.services.create_payment_verifications import (
    CreatePaymentVerifications,
)
from hope.apps.payment.services.process_verification import ProcessVerification
from hope.apps.payment.services.sampling import Sampling
from hope.apps.payment.services.verifiers import (
    PaymentVerificationArgumentVerifier,
)
from hope.apps.payment.tasks.CheckRapidProVerificationTask import (
    does_payment_record_have_right_hoh_phone_number,
)

if TYPE_CHECKING:
    from hope.apps.payment.models import PaymentPlan  # pragma: no cover


def get_payment_records(payment_plan: "PaymentPlan", verification_channel: Any | None) -> QuerySet:
    if verification_channel == PaymentVerificationPlan.VERIFICATION_CHANNEL_RAPIDPRO:
        return payment_plan.available_payment_records(extra_validation=does_payment_record_have_right_hoh_phone_number)
    return payment_plan.available_payment_records()


class VerificationPlanCrudServices:
    @classmethod
    def create(cls, payment_plan: "PaymentPlan", input_data: dict) -> PaymentVerificationPlan:
        verifier = PaymentVerificationArgumentVerifier(input_data)
        verifier.verify("sampling")
        verifier.verify("verification_channel")

        payment_verification_plan = PaymentVerificationPlan()
        payment_verification_plan.payment_plan = payment_plan

        payment_verification_plan.verification_channel = input_data.get("verification_channel")

        payment_records = get_payment_records(payment_plan, payment_verification_plan.verification_channel)
        sampling = Sampling(input_data, payment_plan, payment_records)
        payment_verification_plan, payment_records_qs = sampling.process_sampling(payment_verification_plan)
        ProcessVerification(input_data, payment_verification_plan).process()
        payment_verification_plan.save()

        CreatePaymentVerifications(payment_verification_plan, payment_records_qs).create()

        return payment_verification_plan

    @classmethod
    def update(cls, payment_verification_plan: PaymentVerificationPlan, input_data: dict) -> PaymentVerificationPlan:
        verifier = PaymentVerificationArgumentVerifier(input_data)
        verifier.verify("sampling")
        verifier.verify("verification_channel")

        if payment_verification_plan.status != PaymentVerificationPlan.STATUS_PENDING:  # pragma: no cover
            raise ValidationError("You can only edit PENDING Payment Plan Verification")

        payment_records = get_payment_records(
            payment_verification_plan.payment_plan, payment_verification_plan.verification_channel
        )
        sampling = Sampling(input_data, payment_verification_plan.payment_plan, payment_records)
        pv_plan, payment_records_qs = sampling.process_sampling(payment_verification_plan)
        ProcessVerification(input_data, pv_plan).process()
        pv_plan.save()

        CreatePaymentVerifications(pv_plan, payment_records_qs).create()

        return pv_plan

    @classmethod
    def delete(cls, payment_verification_plan: PaymentVerificationPlan) -> None:
        if payment_verification_plan.status != PaymentVerificationPlan.STATUS_PENDING:
            raise ValidationError("You can delete only PENDING verification")

        payment_verification_plan.delete()
