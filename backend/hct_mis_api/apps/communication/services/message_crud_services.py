from typing import Optional

from django.contrib.auth import get_user_model
from django.db.models import QuerySet

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.household.models import Household

from ..models import Message
from .sampling import Sampling
from .verifiers import MessageArgumentVerifier

User = get_user_model()


class MessageCrudServices:
    @classmethod
    def create(cls, user: User, business_area_slug: str, input_data: dict) -> Message:
        verifier = MessageArgumentVerifier(input_data)
        verifier.verify()

        message = Message()
        message.created_by = user
        message.business_area = BusinessArea.objects.filter(slug=business_area_slug).first()
        message.title = input_data.get("title")
        message.body = input_data.get("body")
        message.sampling_type = input_data.get("sampling_type")
        households = cls._get_households(input_data)
        message.households.set(households)
        message.number_of_recipients = households.count()

        sampling = Sampling(input_data, message.households)
        sampling.process_sampling(message)

        message.save()
        return message

    @classmethod
    def _get_households(cls, input_data: dict) -> Optional[QuerySet[Household]]:
        if (
            household_ids := [household for household in input_data.get("households")]
            if input_data.get("households")
            else []
        ):
            return Household.objects.filter(id__in=household_ids)
        elif trget_population_id := input_data.get("target_population"):
            return Household.objects.filter(selections__target_population__id=trget_population_id)
        elif registration_data_import_id := input_data.get("registration_data_import"):
            return Household.objects.filter(registration_data_import_id=registration_data_import_id)
