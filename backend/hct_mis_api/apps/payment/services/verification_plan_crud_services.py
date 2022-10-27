from typing import Union

from django.contrib.admin.options import get_content_type_for_model

from graphql import GraphQLError

from hct_mis_api.apps.payment.models import PaymentVerificationPlan, PaymentPlan, CashPlan
from hct_mis_api.apps.payment.services.create_payment_verifications import (
    CreatePaymentVerifications,
)
from hct_mis_api.apps.payment.services.process_verification import ProcessVerification
from hct_mis_api.apps.payment.services.sampling import Sampling
from hct_mis_api.apps.payment.services.verifiers import (
    PaymentVerificationArgumentVerifier,
)
from hct_mis_api.apps.payment.tasks.CheckRapidProVerificationTask import (
    does_payment_record_have_right_hoh_phone_number,
)


def get_payment_records(payment_plan, verification_channel):
    payment_plan_type = payment_plan.__class__.__name__
    if verification_channel == PaymentVerificationPlan.VERIFICATION_CHANNEL_RAPIDPRO:
        return payment_plan.available_payment_records(
            class_name=payment_plan_type, extra_validation=does_payment_record_have_right_hoh_phone_number
        )
    return payment_plan.available_payment_records(class_name=payment_plan_type)


class VerificationPlanCrudServices:
    @classmethod
    def create(cls, payment_plan: Union[PaymentPlan, CashPlan], input_data: dict) -> PaymentVerificationPlan:
        verifier = PaymentVerificationArgumentVerifier(input_data)
        verifier.verify("sampling")
        verifier.verify("verification_channel")

        payment_verification_plan = PaymentVerificationPlan()
        payment_verification_plan.payment_plan_content_type = get_content_type_for_model(payment_plan)
        payment_verification_plan.payment_plan_object_id = payment_plan.pk

        payment_verification_plan.verification_channel = input_data.get("verification_channel")

        payment_records = get_payment_records(payment_plan, payment_verification_plan.verification_channel)
        sampling = Sampling(input_data, payment_plan, payment_records)
        payment_verification_plan, payment_records = sampling.process_sampling(payment_verification_plan)
        ProcessVerification(input_data, payment_verification_plan).process()
        payment_verification_plan.save()

        CreatePaymentVerifications(payment_verification_plan, payment_records).create()

        return payment_verification_plan

    @classmethod
    def update(cls, payment_verification_plan, input_data) -> PaymentVerificationPlan:
        verifier = PaymentVerificationArgumentVerifier(input_data)
        verifier.verify("sampling")
        verifier.verify("verification_channel")

        if payment_verification_plan.status != PaymentVerificationPlan.STATUS_PENDING:
            raise GraphQLError("You can only edit PENDING Cash/Payment Plan Verification")

        payment_records = get_payment_records(
            payment_verification_plan.payment_plan, payment_verification_plan.verification_channel
        )
        sampling = Sampling(input_data, payment_verification_plan.payment_plan, payment_records)
        payment_verification_plan, payment_records = sampling.process_sampling(payment_verification_plan)
        ProcessVerification(input_data, payment_verification_plan).process()
        payment_verification_plan.save()

        CreatePaymentVerifications(payment_verification_plan, payment_records).create()

        return payment_verification_plan

    @classmethod
    def delete(cls, payment_verification_plan):
        if payment_verification_plan.status != PaymentVerificationPlan.STATUS_PENDING:
            raise GraphQLError("You can delete only PENDING verification")

        payment_verification_plan.delete()
