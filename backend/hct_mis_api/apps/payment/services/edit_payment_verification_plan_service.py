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


class EditPaymentVerificationPlanService:
    def __init__(self, input_data, cash_plan_verification: CashPlanPaymentVerification):
        self.input_data = input_data
        self.cash_plan_verification = cash_plan_verification

    def execute(self) -> CashPlanPaymentVerification:
        verifier = PaymentVerificationArgumentVerifier(self.input_data)
        verifier.verify("sampling")
        verifier.verify("verification_channel")

        if self.cash_plan_verification.status != CashPlanPaymentVerification.STATUS_PENDING:
            raise GraphQLError("You can only edit PENDING Cash Plan Verification")

        sampling = Sampling(self.input_data, self.cash_plan_verification.cash_plan)
        cash_plan_verification, payment_records = sampling.process_sampling(self.cash_plan_verification)
        cash_plan_verification.save()

        CreatePaymentVerifications(cash_plan_verification, payment_records).create()
        ProcessVerification(self.input_data, cash_plan_verification).process()

        return cash_plan_verification
