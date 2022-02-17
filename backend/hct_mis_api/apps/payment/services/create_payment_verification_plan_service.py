from hct_mis_api.apps.payment.models import CashPlanPaymentVerification
from hct_mis_api.apps.payment.services.create_payment_verifications import (
    CreatePaymentVerifications,
)
from hct_mis_api.apps.payment.services.process_verification import ProcessVerification
from hct_mis_api.apps.payment.services.sampling import Sampling
from hct_mis_api.apps.payment.services.verifiers import (
    PaymentVerificationArgumentVerifier,
)


class CreatePaymentVerificationPlanService:
    def __init__(self, input_data, cash_plan):
        self.input_data = input_data
        self.cash_plan = cash_plan

    def execute(self) -> CashPlanPaymentVerification:
        verifier = PaymentVerificationArgumentVerifier(self.input_data)
        verifier.verify("sampling")
        verifier.verify("verification_channel")

        cash_plan_verification = CashPlanPaymentVerification()
        cash_plan_verification.cash_plan = self.cash_plan
        cash_plan_verification.verification_method = self.input_data.get("verification_channel")

        sampling = Sampling(self.input_data, self.cash_plan)
        cash_plan_verification, payment_records = sampling.process_sampling(cash_plan_verification)
        cash_plan_verification.save()

        CreatePaymentVerifications(cash_plan_verification, payment_records).create()
        ProcessVerification(self.input_data, cash_plan_verification).process()

        return cash_plan_verification
