from typing import Dict

from hct_mis_api.apps.payment.models import PaymentVerificationPlan


class ProcessVerification:
    def __init__(self, input_data: Dict, payment_verification_plan: PaymentVerificationPlan) -> None:
        self.input_data = input_data
        self.payment_verification_plan = payment_verification_plan

    def process(self) -> None:
        verification_channel = self.payment_verification_plan.verification_channel
        if verification_channel == PaymentVerificationPlan.VERIFICATION_CHANNEL_RAPIDPRO:
            flow_id = self.input_data["rapid_pro_arguments"]["flow_id"]
            self.payment_verification_plan.rapid_pro_flow_id = flow_id
