from typing import List, Tuple

from django.db.models import Q

from hct_mis_api.apps.core.filters import filter_age
from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.payment.models import CashPlanPaymentVerification, PaymentRecord
from hct_mis_api.apps.payment.utils import get_number_of_samples


class Sampling:
    def __init__(self, input_data, cash_plan):
        self.input_data = input_data
        self.cash_plan = cash_plan

    def process_sampling(
        self, cash_plan_verification: CashPlanPaymentVerification
    ) -> Tuple[CashPlanPaymentVerification, List[PaymentRecord]]:
        sampling = self.input_data.get("sampling")
        excluded_admin_areas = []
        sex = None
        age = None
        confidence_interval = None
        margin_of_error = None
        payment_records = self.cash_plan.available_payment_records()

        if not payment_records:
            raise ValueError("There are no payment records that could be assigned to a new verification plan.")

        if sampling == CashPlanPaymentVerification.SAMPLING_FULL_LIST:
            excluded_admin_areas = self.input_data.get("full_list_arguments").get("excluded_admin_areas", [])
        elif sampling == CashPlanPaymentVerification.SAMPLING_RANDOM:
            random_sampling_arguments = self.input_data.get("random_sampling_arguments")
            confidence_interval = random_sampling_arguments.get("confidence_interval")
            margin_of_error = random_sampling_arguments.get("margin_of_error")
            sex = random_sampling_arguments.get("sex")
            age = random_sampling_arguments.get("age")
            excluded_admin_areas = random_sampling_arguments.get("excluded_admin_areas", [])

            if sex is not None:
                payment_records = payment_records.filter(household__head_of_household__sex=sex)
            if age is not None:
                payment_records = filter_age(
                    "household__head_of_household__birth_date",
                    payment_records,
                    age.get("min"),
                    age.get("max"),
                )
        excluded_admin_areas_decoded = [decode_id_string(x) for x in excluded_admin_areas]

        payment_records = payment_records.filter(~(Q(household__admin_area__id__in=excluded_admin_areas_decoded)))
        payment_records_sample_count = payment_records.count()

        if sampling == CashPlanPaymentVerification.SAMPLING_RANDOM:
            payment_records_sample_count = get_number_of_samples(
                payment_records_sample_count,
                confidence_interval,
                margin_of_error,
            )
            payment_records = payment_records.order_by("?")[:payment_records_sample_count]

        cash_plan_verification.confidence_interval = confidence_interval
        cash_plan_verification.margin_of_error = margin_of_error
        cash_plan_verification.sample_size = payment_records_sample_count
        cash_plan_verification.sampling = sampling
        cash_plan_verification.sex_filter = sex
        cash_plan_verification.age_filter = age
        cash_plan_verification.excluded_admin_areas_filter = excluded_admin_areas

        return cash_plan_verification, payment_records
