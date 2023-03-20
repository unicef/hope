import abc
from typing import TYPE_CHECKING, Any, Dict, Tuple, Union

from django.db.models import Q, QuerySet

from graphql import GraphQLError

from hct_mis_api.apps.core.filters import filter_age
from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.payment.models import PaymentVerificationPlan
from hct_mis_api.apps.payment.utils import get_number_of_samples

if TYPE_CHECKING:
    from hct_mis_api.apps.payment.models import CashPlan, PaymentPlan, PaymentRecord


class Sampling:
    def __init__(
        self, input_data: Dict, payment_plan: Union["CashPlan", "PaymentPlan"], payment_records: QuerySet
    ) -> None:
        self.input_data = input_data
        self.payment_plan = payment_plan
        self.payment_records: QuerySet = payment_records

    def process_sampling(
        self, payment_verification_plan: PaymentVerificationPlan
    ) -> Tuple[PaymentVerificationPlan, QuerySet]:
        if not self.payment_records:
            raise GraphQLError("There are no payment records that could be assigned to a new verification plan.")

        sampling: BaseSampling = self._get_sampling()
        sampling.sampling(self.payment_records)

        payment_verification_plan.sampling = sampling.sampling_type
        payment_verification_plan.sex_filter = sampling.sex
        payment_verification_plan.age_filter = sampling.age
        payment_verification_plan.confidence_interval = sampling.confidence_interval
        payment_verification_plan.margin_of_error = sampling.margin_of_error
        payment_verification_plan.excluded_admin_areas_filter = sampling.excluded_admin_areas
        payment_verification_plan.sample_size = sampling.sample_size

        self.payment_records = sampling.payment_records  # type: ignore # FIXME: Incompatible types in assignment (expression has type "Optional[_QuerySet[Any, Any]]", variable has type "_QuerySet[Any, Any]")

        if sampling.sampling_type == PaymentVerificationPlan.SAMPLING_RANDOM:
            self.payment_records = self.payment_records.order_by("?")[: sampling.sample_size]

        return payment_verification_plan, self.payment_records

    def generate_sampling(self) -> Tuple[int, int]:
        payment_record_count = self.payment_records.count()
        sampling = self._get_sampling()
        sampling.sampling(self.payment_records)

        return payment_record_count, sampling.sample_size

    def _get_sampling(self) -> "BaseSampling":
        sampling_type: str = self.input_data.get("sampling", "")
        if sampling_type == PaymentVerificationPlan.SAMPLING_FULL_LIST:
            arguments = self.input_data["full_list_arguments"]
            return FullListSampling(arguments, sampling_type)
        else:
            arguments = self.input_data["random_sampling_arguments"]
            return RandomSampling(arguments, sampling_type)


class BaseSampling(abc.ABC):
    def __init__(self, arguments: Dict, sampling_type: str) -> None:
        self.sampling_type = sampling_type
        self.arguments = arguments
        self.confidence_interval = self.arguments.get("confidence_interval", 0)
        self.margin_of_error = self.arguments.get("margin_of_error", 0)
        self.sex = self.arguments.get("sex")
        self.age = self.arguments.get("age")
        self.excluded_admin_areas = self.arguments.get("excluded_admin_areas", [])
        self.excluded_admin_areas_decoded = [decode_id_string(x) for x in self.excluded_admin_areas]
        self.sample_size = 0
        self.payment_records: Any = None

    def calc_sample_size(self, sample_count: int) -> int:
        if self.sampling_type == PaymentVerificationPlan.SAMPLING_FULL_LIST:
            return sample_count
        else:
            return get_number_of_samples(sample_count, self.confidence_interval, self.margin_of_error)  # type: ignore # FIXME: args 2 and 3 are opt, func def required non-opt

    @abc.abstractmethod
    def sampling(self, payment_records: QuerySet["PaymentRecord"]) -> None:
        pass


class RandomSampling(BaseSampling):
    def sampling(self, payment_records: QuerySet["PaymentRecord"]) -> None:
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
    def sampling(self, payment_records: QuerySet["PaymentRecord"]) -> None:
        self.payment_records = payment_records.filter(
            ~(Q(household__admin_area__id__in=self.excluded_admin_areas_decoded))
        )
        self.sample_size = self.calc_sample_size(payment_records.count())
