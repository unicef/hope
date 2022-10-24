import abc
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from django.db.models import QuerySet

from hct_mis_api.apps.core.filters import filter_age
from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.payment.utils import get_number_of_samples

from ..models import Message


class BaseSampling(abc.ABC):
    def __init__(self, arguments: dict):
        self.confidence_interval = arguments.get("confidence_interval")
        self.margin_of_error = arguments.get("margin_of_error")
        self.sex = arguments.get("sex")
        self.age = arguments.get("age")
        self.excluded_admin_areas = arguments.get("excluded_admin_areas", [])
        self.administrative_level = arguments.get("administrative_level")
        self.excluded_admin_areas_decoded = [decode_id_string(x) for x in self.excluded_admin_areas if x and x.strip()]
        self.sample_size = 0
        self.households: Optional[QuerySet[Household]] = None

    @abc.abstractmethod
    def data(self) -> dict:
        pass

    @abc.abstractmethod
    def calc_sample_size(self, sample_count: int) -> int:
        pass

    @abc.abstractmethod
    def sampling(self, households: QuerySet[Household]) -> None:
        pass


class FullListSampling(BaseSampling):
    def calc_sample_size(self, sample_count: int) -> int:
        return sample_count

    def sampling(self, households: QuerySet[Household]):
        self.households = households.exclude(
            head_of_household__phone_no__isnull=False, admin_area__id__in=self.excluded_admin_areas_decoded
        )
        self.sample_size = self.calc_sample_size(households.count())

    def data(self) -> dict:
        return {
            "excluded_admin_areas": self.excluded_admin_areas_decoded,
        }


class RandomSampling(BaseSampling):
    def calc_sample_size(self, sample_count: int) -> int:
        return get_number_of_samples(sample_count, self.confidence_interval, self.margin_of_error)

    def sampling(self, households: QuerySet[Household]):
        if self.sex and isinstance(self.sex, str):
            households = households.filter(head_of_household__sex=self.sex)

        if self.age and isinstance(self.age, dict):
            households = filter_age(
                "head_of_household__birth_date",
                households,
                self.age.get("min"),
                self.age.get("max"),
            )
        self.households = households.exclude(
            head_of_household__phone_no__isnull=False, admin_area__id__in=self.excluded_admin_areas_decoded
        )
        self.sample_size = self.calc_sample_size(households.count())

    def data(self) -> dict:
        return {
            "excluded_admin_areas": self.excluded_admin_areas_decoded,
            "confidence_interval": self.confidence_interval,
            "margin_of_error": self.margin_of_error,
            "age": self.age,
            "sex": self.sex,
        }


@dataclass
class ResultSampling:
    sample_size: int
    full_list_arguments: Optional[Dict]
    random_sampling_arguments: Optional[Dict]
    number_of_recipients: int
    households: QuerySet[Household]


class Sampling:
    def __init__(self, input_data, households: QuerySet[Household]):
        self.input_data = input_data
        self.households = households

    def process_sampling(self) -> ResultSampling:
        sampling_type = self.input_data["sampling_type"]
        sampling = self._get_sampling()
        sampling.sampling(self.households)
        sample_size = sampling.sample_size
        sampling_data = sampling.data()

        self.households = sampling.households
        number_of_recipients = self.households.count()

        if self.households and sampling_type == Message.SamplingChoices.RANDOM:
            self.households = self.households.order_by("?")[: sampling.sample_size]

        return ResultSampling(
            sample_size=sample_size,
            full_list_arguments=sampling_data if sampling_type == Message.SamplingChoices.FULL_LIST else None,
            random_sampling_arguments=sampling_data if sampling_type == Message.SamplingChoices.RANDOM else None,
            number_of_recipients=number_of_recipients,
            households=self.households,
        )

    def generate_sampling(self) -> Tuple[int, int]:
        recipients_count = self.households.count()
        sampling = self._get_sampling()
        sampling.sampling(self.households)

        return recipients_count, sampling.sample_size

    def _get_sampling(self) -> BaseSampling:
        if self.input_data["sampling_type"] == Message.SamplingChoices.FULL_LIST:
            return FullListSampling(self.input_data.get("full_list_arguments"))
        return RandomSampling(self.input_data.get("random_sampling_arguments"))
