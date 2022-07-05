import logging
import phonenumbers

from hct_mis_api.apps.payment.models import (
    CashPlanPaymentVerification,
    PaymentVerification,
)
from hct_mis_api.apps.payment.services.rapid_pro.api import RapidProAPI
from hct_mis_api.apps.payment.utils import calculate_counts, from_received_to_status, get_payment_records_for_dashboard

logger = logging.getLogger(__name__)


def is_right_phone_number_format(phone_number):
    # from phonenumbers.parse method description:
    # This method will throw a NumberParseException if the number is not
    # considered to be a possible number.
    #
    # so if `parse` does not throw, we may assume it's ok
    try:
        phonenumbers.parse(phone_number)
    except phonenumbers.NumberParseException:
        logging.warning(f"'{phone_number}' is not a valid phone number")
        return False
    return True


def does_payment_record_have_right_hoh_phone_number(record):
    hoh = record.head_of_household
    if not hoh:
        logging.warning("Payment record has no head of household")
        return False
    number = hoh.phone_no
    if not number:
        logging.warning("Head of household has no phone number")
        return False
    return is_right_phone_number_format(str(number))


class CheckRapidProVerificationTask:
    def execute(self):
        active_rapidpro_verifications = CashPlanPaymentVerification.objects.filter(
            verification_channel=CashPlanPaymentVerification.VERIFICATION_CHANNEL_RAPIDPRO,
            status=CashPlanPaymentVerification.STATUS_ACTIVE,
        )
        for cashplan_payment_verification in active_rapidpro_verifications:
            try:
                self._verify_cashplan_payment_verification(cashplan_payment_verification)
            except Exception as e:
                logger.exception(e)

    def _verify_cashplan_payment_verification(self, cashplan_payment_verification):
        payment_record_verifications = cashplan_payment_verification.payment_record_verifications.prefetch_related(
            "payment_record__head_of_household"
        )
        payment_record_verification_to_update = []
        business_area = cashplan_payment_verification.cash_plan.business_area
        payment_record_verifications_phone_number_dict = {
            str(x.payment_record.head_of_household.phone_no): x for x in payment_record_verifications
        }
        api = RapidProAPI(business_area.slug)
        rapid_pro_results = api.get_mapped_flow_runs(cashplan_payment_verification.rapid_pro_flow_start_uuid)
        payment_record_verification_to_update = self._get_payment_record_verification_to_update(
            rapid_pro_results, payment_record_verifications_phone_number_dict
        )
        PaymentVerification.objects.bulk_update(payment_record_verification_to_update, ("status", "received_amount"))
        calculate_counts(cashplan_payment_verification)
        cashplan_payment_verification.save()

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
        delivered_amount = payment_record_verification.payment_record.delivered_quantity
        payment_record_verification.status = from_received_to_status(received, received_amount, delivered_amount)
        payment_record_verification.received_amount = received_amount
        return payment_record_verification
