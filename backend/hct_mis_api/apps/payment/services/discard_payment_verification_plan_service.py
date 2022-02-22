from graphql import GraphQLError

from hct_mis_api.apps.payment.models import (
    CashPlanPaymentVerification,
    PaymentVerification,
)


class DiscardPaymentVerificationPlanService:
    def __init__(self, cash_plan_verification: CashPlanPaymentVerification):
        self.cash_plan_verification = cash_plan_verification

    def execute(self) -> CashPlanPaymentVerification:
        if self.cash_plan_verification.status != CashPlanPaymentVerification.STATUS_ACTIVE:
            raise GraphQLError("You can discard only ACTIVE verification")

        self.cash_plan_verification.set_pending()
        self.cash_plan_verification.save()

        # payment verifications to reset
        payment_record_verifications = self.cash_plan_verification.payment_record_verifications.all()
        for payment_record_verification in payment_record_verifications:
            payment_record_verification.set_pending()

        PaymentVerification.objects.bulk_update(
            payment_record_verifications, ["status_date", "status", "received_amount"]
        )

        return self.cash_plan_verification
