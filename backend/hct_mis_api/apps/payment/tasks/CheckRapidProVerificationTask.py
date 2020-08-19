from payment.models import CashPlanPaymentVerification, PaymentVerification
from payment.rapid_pro.api import RapidProAPI


class CheckRapidProVerificationTask:
    def execute(self):
        active_rapidpro_verifications = CashPlanPaymentVerification.objects.filter(
            verification_method=CashPlanPaymentVerification.VERIFICATION_METHOD_RAPIDPRO,
            status=CashPlanPaymentVerification.STATUS_ACTIVE,
        )
        for cashplan_payment_verification in active_rapidpro_verifications:
            self._verify_cashplan_payment_verification(
                cashplan_payment_verification
            )

    def _verify_cashplan_payment_verification(
        self, cashplan_payment_verification
    ):
        payment_record_verifications = cashplan_payment_verification.payment_record_verifications.prefetch_related(
            "payment_record__household__head_of_household"
        )
        payment_record_verification_to_update = []
        business_area = cashplan_payment_verification.cash_plan.business_area
        payment_record_verifications_phone_number_dict = {
            str(x.payment_record.household.head_of_household.phone_no): x
            for x in payment_record_verifications
        }
        api = RapidProAPI(business_area.slug)
        rapid_pro_results = api.get_mapped_flow_runs(
            cashplan_payment_verification.rapid_pro_flow_start_uuid
        )
        for rapid_pro_result in rapid_pro_results:
            payment_record_verification = self._rapid_pro_results_to_payment_record_verification(
                payment_record_verifications_phone_number_dict, rapid_pro_result
            )
            if payment_record_verification:
                payment_record_verification_to_update.append(
                    payment_record_verification
                )
        PaymentVerification.objects.bulk_update(
            payment_record_verification_to_update, ("status", "received_amount")
        )

    def _rapid_pro_results_to_payment_record_verification(
        self, payment_record_verifications_phone_number_dict, rapid_pro_result
    ):
        received = rapid_pro_result.get("received")
        received_amount = rapid_pro_result.get("received_amount")
        phone_number = rapid_pro_result.get("phone_number")
        if not phone_number:
            return None
        payment_record_verification = payment_record_verifications_phone_number_dict.get(
            phone_number
        )
        if not payment_record_verification:
            return None
        delivered_amount = (
            payment_record_verification.payment_record.delivered_quantity
        )
        status = payment_record_verification.status
        if received:
            if received_amount == delivered_amount:
                status = PaymentVerification.STATUS_RECEIVED
            else:
                status = PaymentVerification.STATUS_RECEIVED_WITH_ISSUES
        else:
            status = PaymentVerification.STATUS_NOT_RECEIVED
        payment_record_verification.status = status
        payment_record_verification.received_amount = received_amount
        return payment_record_verification
