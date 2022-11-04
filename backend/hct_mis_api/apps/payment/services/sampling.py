import abc
from typing import Optional, Tuple

from django.db.models import Q, QuerySet

from graphql import GraphQLError

from hct_mis_api.apps.core.filters import filter_age
from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.payment.models import CashPlanPaymentVerification
from hct_mis_api.apps.payment.utils import get_number_of_samples


class Sampling:
    def __init__(self, input_data, cash_plan, payment_records: QuerySet):
        self.input_data = input_data
        self.cash_plan = cash_plan
        self.payment_records: Optional[QuerySet] = payment_records

    def process_sampling(
        self, cash_plan_verification: CashPlanPaymentVerification
    ) -> Tuple[CashPlanPaymentVerification, Optional[QuerySet]]:
        if not self.payment_records:
            raise GraphQLError("There are no payment records that could be assigned to a new verification plan.")

        sampling: BaseSampling = self._get_sampling()
        sampling.sampling(self.payment_records)

        cash_plan_verification.sampling = sampling.sampling_type
        cash_plan_verification.sex_filter = sampling.sex
        cash_plan_verification.age_filter = sampling.age
        cash_plan_verification.confidence_interval = sampling.confidence_interval
        cash_plan_verification.margin_of_error = sampling.margin_of_error
        cash_plan_verification.excluded_admin_areas_filter = sampling.excluded_admin_areas
        cash_plan_verification.sample_size = sampling.sample_size

        self.payment_records = sampling.payment_records

        if sampling.sampling_type == CashPlanPaymentVerification.SAMPLING_RANDOM:
            self.payment_records = self.payment_records.order_by("?")[: sampling.sample_size]

        return cash_plan_verification, self.payment_records

    def generate_sampling(self) -> Tuple[int, int]:
        payment_record_count = self.payment_records.count()
        sampling = self._get_sampling()
        sampling.sampling(self.payment_records)

        return payment_record_count, sampling.sample_size

    def _get_sampling(self) -> "BaseSampling":
        sampling_type = self.input_data.get("sampling")
        if sampling_type == CashPlanPaymentVerification.SAMPLING_FULL_LIST:
            arguments = self.input_data.get("full_list_arguments")
            return FullListSampling(arguments, sampling_type)
        else:
            arguments = self.input_data.get("random_sampling_arguments")
            return RandomSampling(arguments, sampling_type)


class BaseSampling(abc.ABC):
    def __init__(self, arguments, sampling_type: str):
        self.sampling_type = sampling_type
        self.arguments = arguments
        self.confidence_interval = self.arguments.get("confidence_interval")
        self.margin_of_error = self.arguments.get("margin_of_error")
        self.sex = self.arguments.get("sex")
        self.age = self.arguments.get("age")
        self.excluded_admin_areas = self.arguments.get("excluded_admin_areas", [])
        self.excluded_admin_areas_decoded = [decode_id_string(x) for x in self.excluded_admin_areas]
        self.sample_size = 0
        self.payment_records: Optional[QuerySet] = None

    def calc_sample_size(self, sample_count: int) -> int:
        if self.sampling_type == CashPlanPaymentVerification.SAMPLING_FULL_LIST:
            return sample_count
        else:
            return get_number_of_samples(sample_count, self.confidence_interval, self.margin_of_error)

    @abc.abstractmethod
    def sampling(self, payment_records: QuerySet):
        pass


class RandomSampling(BaseSampling):
    def sampling(self, payment_records: QuerySet):
        if self.sex is not None:
            payment_records = payment_records.filter(household__head_of_household__sex=self.sex)

        if self.age is not None:
            payment_records = filter_age(
                "household__head_of_household__birth_date",
                payment_records,
                self.age.get("min"),
                self.age.get("max"),
            )

        self.payment_records = payment_records.filter(
            ~(Q(household__admin_area__id__in=self.excluded_admin_areas_decoded))
        )
        self.sample_size = self.calc_sample_size(payment_records.count())


class FullListSampling(BaseSampling):
    def sampling(self, payment_records: QuerySet):
        self.payment_records = payment_records.filter(
            ~(Q(household__admin_area__id__in=self.excluded_admin_areas_decoded))
        )
        self.sample_size = self.calc_sample_size(payment_records.count())
