from hct_mis_api.apps.payment.models import CashPlanPaymentVerification


class ProcessVerification:
    def __init__(self, input_data, cash_plan_payment_verification: CashPlanPaymentVerification) -> None:
        self.input_data = input_data
        self.cash_plan_payment_verification = cash_plan_payment_verification

    def process(self) -> None:
        verification_channel = self.cash_plan_payment_verification.verification_channel
        if verification_channel == CashPlanPaymentVerification.VERIFICATION_CHANNEL_RAPIDPRO:
            flow_id = self.input_data["rapid_pro_arguments"]["flow_id"]
            self.cash_plan_payment_verification.rapid_pro_flow_id = flow_id
