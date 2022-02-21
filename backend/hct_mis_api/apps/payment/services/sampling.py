from typing import List, Tuple

from django.db.models import Q

from graphql import GraphQLError

from hct_mis_api.apps.core.filters import filter_age
from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.payment.models import CashPlanPaymentVerification, PaymentRecord


class Sampling:
    def __init__(self, input_data, cash_plan):
        self.input_data = input_data
        self.cash_plan = cash_plan

    def process_sampling(
        self, cash_plan_verification: CashPlanPaymentVerification
    ) -> Tuple[CashPlanPaymentVerification, List[PaymentRecord]]:
        cash_plan_verification.sampling = self.input_data.get("sampling")
        payment_records = self.cash_plan.available_payment_records()

        if not payment_records:
            raise GraphQLError("There are no payment records that could be assigned to a new verification plan.")

        if cash_plan_verification.sampling == CashPlanPaymentVerification.SAMPLING_FULL_LIST:
            sampling = FullListSampling(self.input_data.get("full_list_arguments"))
        else:
            sampling = RandomSampling(self.input_data.get("random_sampling_arguments"))
        payment_records = sampling.sampling(cash_plan_verification, payment_records)

        return cash_plan_verification, payment_records


class RandomSampling:
    def __init__(self, arguments):
        self.arguments = arguments

    def sampling(self, cash_plan_verification, payment_records):
        confidence_interval = self.arguments.get("confidence_interval")
        margin_of_error = self.arguments.get("margin_of_error")
        sex = self.arguments.get("sex")
        age = self.arguments.get("age")
        excluded_admin_areas = self.arguments.get("excluded_admin_areas", [])

        if sex is not None:
            payment_records = payment_records.filter(household__head_of_household__sex=sex)
            cash_plan_verification.sex_filter = sex

        if age is not None:
            payment_records = filter_age(
                "household__head_of_household__birth_date",
                payment_records,
                age.get("min"),
                age.get("max"),
            )
            cash_plan_verification.age_filter = age

        excluded_admin_areas_decoded = [decode_id_string(x) for x in excluded_admin_areas]
        payment_records = payment_records.filter(~(Q(household__admin_area__id__in=excluded_admin_areas_decoded)))

        cash_plan_verification.confidence_interval = confidence_interval
        cash_plan_verification.margin_of_error = margin_of_error
        cash_plan_verification.excluded_admin_areas_filter = excluded_admin_areas
        cash_plan_verification.set_sample_size(payment_records.count())

        payment_records = payment_records.order_by("?")[: cash_plan_verification.sample_size]

        return payment_records


class FullListSampling:
    def __init__(self, arguments):
        self.arguments = arguments

    def sampling(self, cash_plan_verification, payment_records):
        excluded_admin_areas = self.arguments.get("excluded_admin_areas", [])
        excluded_admin_areas_decoded = [decode_id_string(x) for x in excluded_admin_areas]
        payment_records = payment_records.filter(~(Q(household__admin_area__id__in=excluded_admin_areas_decoded)))
        cash_plan_verification.excluded_admin_areas_filter = excluded_admin_areas
        cash_plan_verification.set_sample_size(payment_records.count())

        return payment_records
