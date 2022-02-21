from hct_mis_api.apps.household.models import Individual
from hct_mis_api.apps.payment.models import CashPlanPaymentVerification
from hct_mis_api.apps.payment.services.rapid_pro.api import RapidProAPI


class ActivatePaymentVerificationPlanService:
    def __init__(self, payment_verification: CashPlanPaymentVerification):
        self.payment_verification = payment_verification

    def execute(self) -> CashPlanPaymentVerification:
        if self.payment_verification.status != CashPlanPaymentVerification.STATUS_PENDING:
            raise ValueError("You can activate only PENDING verification")

        if self.can_activate_via_rapidpro():
            self.activate_rapidpro()

        self.payment_verification.activate()
        self.payment_verification.save()

        return self.payment_verification

    def can_activate_via_rapidpro(self):
        return self.payment_verification.verification_method == CashPlanPaymentVerification.VERIFICATION_METHOD_RAPIDPRO

    def activate_rapidpro(self):
        business_area_slug = self.payment_verification.business_area.slug
        api = RapidProAPI(business_area_slug)
        pv_id = self.payment_verification.id
        phone_numbers = list(
            Individual.objects.filter(
                heading_household__payment_records__verifications__cash_plan_payment_verification=pv_id
            ).values_list("phone_no", flat=True)
        )
        flow_start_info = api.start_flow(self.payment_verification.rapid_pro_flow_id, phone_numbers)
        self.payment_verification.rapid_pro_flow_start_uuid = flow_start_info.get("uuid")
