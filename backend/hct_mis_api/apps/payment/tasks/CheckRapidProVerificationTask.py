import logging

from hct_mis_api.apps.payment.models import PaymentVerification, PaymentVerificationPlan
from hct_mis_api.apps.payment.services.rapid_pro.api import RapidProAPI
from hct_mis_api.apps.payment.utils import calculate_counts, from_received_to_status
from hct_mis_api.apps.utils.phone_number import is_right_phone_number_format

logger = logging.getLogger(__name__)


def does_payment_record_have_right_hoh_phone_number(record):
    hoh = record.head_of_household
    if not hoh:
        logging.warning("Payment record has no head of household")
        return False
    return hoh.phone_no_valid or hoh.phone_no_alternative_valid


class CheckRapidProVerificationTask:
    def execute(self):
        active_rapidpro_verifications = PaymentVerificationPlan.objects.filter(
            verification_channel=PaymentVerificationPlan.VERIFICATION_CHANNEL_RAPIDPRO,
            status=PaymentVerificationPlan.STATUS_ACTIVE,
        )
        for payment_verification_plan in active_rapidpro_verifications:
            try:
                self._verify_cashplan_payment_verification(payment_verification_plan)
            except Exception as e:
                logger.exception(e)

    def _verify_cashplan_payment_verification(self, payment_verification_plan: PaymentVerificationPlan):
        payment_record_verifications = payment_verification_plan.payment_record_verifications.prefetch_related(
            "payment_obj__head_of_household"
        )
        business_area = payment_verification_plan.payment_plan_obj.business_area

        payment_record_verifications_phone_number_dict = {
            str(payment_verification.payment_obj.head_of_household.phone_no): payment_verification
            for payment_verification in payment_record_verifications
        }
        api = RapidProAPI(business_area.slug)
        rapid_pro_results = api.get_mapped_flow_runs(payment_verification_plan.rapid_pro_flow_start_uuids)
        payment_record_verification_to_update = self._get_payment_record_verification_to_update(
            rapid_pro_results, payment_record_verifications_phone_number_dict
        )
        PaymentVerification.objects.bulk_update(payment_record_verification_to_update, ("status", "received_amount"))
        calculate_counts(payment_verification_plan)
        payment_verification_plan.save()

    def _get_payment_record_verification_to_update(self, results, phone_numbers):
        output = []
        for rapid_pro_result in results:
            payment_record_verification = self._rapid_pro_results_to_payment_record_verification(
                phone_numbers, rapid_pro_result
            )
            if payment_record_verification:
                output.append(payment_record_verification)
        return output

    def _rapid_pro_results_to_payment_record_verification(
        self, payment_record_verifications_phone_number_dict, rapid_pro_result
    ):
        received = rapid_pro_result.get("received")
        received_amount = rapid_pro_result.get("received_amount")
        phone_number = rapid_pro_result.get("phone_number")
        if not phone_number or not is_right_phone_number_format(phone_number):
            return None
        payment_record_verification = payment_record_verifications_phone_number_dict.get(phone_number)
        if not payment_record_verification:
            return None
        delivered_amount = payment_record_verification.get_payment.delivered_quantity
        payment_record_verification.status = from_received_to_status(received, received_amount, delivered_amount)
        payment_record_verification.received_amount = received_amount
        return payment_record_verification
