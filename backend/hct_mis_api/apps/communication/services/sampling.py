import abc
from typing import Optional, Tuple

from django.db.models import QuerySet

from hct_mis_api.apps.core.filters import filter_age
from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.payment.utils import get_number_of_samples

from ..models import Message


class BaseSampling(abc.ABC):
    def __init__(self, sampling_type: str, arguments: dict):
        self.sampling_type = sampling_type
        data = self._get_sampling_data(arguments)
        self.confidence_interval = data.get("confidence_interval")
        self.margin_of_error = data.get("margin_of_error")
        self.sex = data.get("sex")
        self.age = data.get("age")
        self.excluded_admin_areas = data.get("excluded_admin_areas", [])
        self.administrative_level = data.get("administrative_level")
        self.excluded_admin_areas_decoded = [decode_id_string(x) for x in self.excluded_admin_areas if x]
        self.sample_size = 0
        self.households: Optional[QuerySet[Household]] = None

    def _get_sampling_data(self, arguments: dict) -> dict:
        return arguments.get(
            "full_list_arguments"
            if self.sampling_type == Message.SamplingChoices.FULL_LIST
            else "random_sampling_arguments",
            {},
        )

    def calc_sample_size(self, sample_count: int) -> int:
        if self.sampling_type == Message.SamplingChoices.FULL_LIST:
            return sample_count
        return get_number_of_samples(sample_count, self.confidence_interval, self.margin_of_error)

    def data(self) -> dict:
        data = {
            "excluded_admin_areas": self.excluded_admin_areas_decoded,
        }
        if self.sampling_type == Message.SamplingChoices.RANDOM:
            data.update(
                {
                    "confidence_interval": self.confidence_interval,
                    "margin_of_error": self.margin_of_error,
                    "age": self.age,
                    "sex": self.sex,
                }
            )
        return data

    @abc.abstractmethod
    def sampling(self, recipients: QuerySet):
        pass


class RandomSampling(BaseSampling):
    def sampling(self, households: QuerySet[Household]):
        if self.sex is not None:
            households = households.filter(head_of_household__sex=self.sex)

        if self.age is not None:
            households = filter_age(
                "head_of_household__birth_date",
                households,
                self.age.get("min"),
                self.age.get("max"),
            )

        self.households = households.exclude(admin_area__id__in=self.excluded_admin_areas_decoded)
        self.sample_size = self.calc_sample_size(households.count())


class FullListSampling(BaseSampling):
    def sampling(self, households: QuerySet[Household]):
        self.households = households.exclude(admin_area__id__in=self.excluded_admin_areas_decoded)
        self.sample_size = self.calc_sample_size(households.count())


class Sampling:
    def __init__(self, input_data, households: QuerySet[Household]):
        self.input_data = input_data
        self.households = households

    def process_sampling(self, message: Message) -> QuerySet[Household]:
        print("1. Processing sampling", message.sampling_type)
        sampling = self._get_sampling(message.sampling_type)
        sampling.sampling(self.households)
        message.sample_size = sampling.sample_size
        sampling_data = sampling.data()
        print("2. Processing sampling", sampling_data)
        if message.sampling_type == Message.SamplingChoices.FULL_LIST:
            message.full_list_arguments = sampling_data
        else:
            message.random_sampling_arguments = sampling_data

        self.households = sampling.households

        if self.households and sampling.sampling_type == Message.SamplingChoices.RANDOM:
            self.households = self.households.order_by("?")[: sampling.sample_size]

        return self.households

    def generate_sampling(self, sampling_type) -> Tuple[int, int]:
        recipients_count = self.households.count()
        sampling = self._get_sampling(sampling_type)
        sampling.sampling(self.households)

        return recipients_count, sampling.sample_size

    def _get_sampling(self, sampling_type) -> BaseSampling:
        if sampling_type == Message.SamplingChoices.FULL_LIST:
            return FullListSampling(sampling_type, self.input_data)
        return RandomSampling(sampling_type, self.input_data)
