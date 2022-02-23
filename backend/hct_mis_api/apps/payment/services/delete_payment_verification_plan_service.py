from graphql import GraphQLError

from hct_mis_api.apps.payment.models import CashPlanPaymentVerification


class DeletePaymentVerificationPlanService:
    def __init__(self, cash_plan_verification: CashPlanPaymentVerification):
        self.cash_plan_verification = cash_plan_verification

    def execute(self):
        if self.cash_plan_verification.status != CashPlanPaymentVerification.STATUS_PENDING:
            raise GraphQLError("You can delete only PENDING verification")

        self.cash_plan_verification.delete()
