from django.db.models import QuerySet

from graphql import GraphQLError

from hct_mis_api.apps.payment.models import CashPlanPaymentVerification
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


def get_payment_records(cash_plan, verification_channel) -> QuerySet:
    if verification_channel == CashPlanPaymentVerification.VERIFICATION_CHANNEL_RAPIDPRO:
        return cash_plan.available_payment_records(extra_validation=does_payment_record_have_right_hoh_phone_number)
    return cash_plan.available_payment_records()


class VerificationPlanCrudServices:
    @classmethod
    def create(cls, cash_plan, input_data) -> CashPlanPaymentVerification:
        verifier = PaymentVerificationArgumentVerifier(input_data)
        verifier.verify("sampling")
        verifier.verify("verification_channel")

        cash_plan_verification = CashPlanPaymentVerification()
        cash_plan_verification.cash_plan = cash_plan
        cash_plan_verification.verification_channel = input_data.get("verification_channel")

        payment_records = get_payment_records(
            cash_plan_verification.cash_plan, cash_plan_verification.verification_channel
        )
        sampling = Sampling(input_data, cash_plan, payment_records)
        cash_plan_verification, payment_records = sampling.process_sampling(cash_plan_verification)
        ProcessVerification(input_data, cash_plan_verification).process()
        cash_plan_verification.save()

        CreatePaymentVerifications(cash_plan_verification, payment_records).create()

        return cash_plan_verification

    @classmethod
    def update(cls, cash_plan_verification, input_data) -> CashPlanPaymentVerification:
        verifier = PaymentVerificationArgumentVerifier(input_data)
        verifier.verify("sampling")
        verifier.verify("verification_channel")

        if cash_plan_verification.status != CashPlanPaymentVerification.STATUS_PENDING:
            raise GraphQLError("You can only edit PENDING Cash Plan Verification")

        payment_records = get_payment_records(
            cash_plan_verification.cash_plan, cash_plan_verification.verification_channel
        )
        sampling = Sampling(input_data, cash_plan_verification.cash_plan, payment_records)
        cash_plan_verification, payment_records = sampling.process_sampling(cash_plan_verification)
        ProcessVerification(input_data, cash_plan_verification).process()
        cash_plan_verification.save()

        CreatePaymentVerifications(cash_plan_verification, payment_records).create()

        return cash_plan_verification

    @classmethod
    def delete(cls, cash_plan_verification) -> None:
        if cash_plan_verification.status != CashPlanPaymentVerification.STATUS_PENDING:
            raise GraphQLError("You can delete only PENDING verification")

        cash_plan_verification.delete()
