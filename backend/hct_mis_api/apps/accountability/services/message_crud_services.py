import logging
from typing import Optional

from django.contrib.auth import get_user_model
from django.db.models import QuerySet

from graphql import GraphQLError

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.models import Household

from ..models import Message
from .sampling import Sampling
from .verifiers import MessageArgumentVerifier

User = get_user_model()
logger = logging.getLogger(__name__)


class MessageCrudServices:
    @classmethod
    def create(cls, user: User, business_area_slug: str, input_data: dict) -> Message:
        verifier = MessageArgumentVerifier(input_data)
        verifier.verify()

        households = cls._get_households(input_data)
        message = Message(
            created_by=user,
            business_area=BusinessArea.objects.get(slug=business_area_slug),
            title=input_data["title"],
            body=input_data["body"],
            sampling_type=input_data["sampling_type"],
        )
        message.households.set(households)

        sampling = Sampling(input_data, households)
        sampling.process_sampling(message)

        if message.number_of_recipients == 0:
            err_msg = "No recipients found for the given criteria"
            logger.error(err_msg)
            raise GraphQLError(err_msg)

        message.save()
        return message

    @classmethod
    def _get_households(cls, input_data: dict) -> Optional[QuerySet[Household]]:
        if household_ids := [household for household in input_data.get("households", [])]:
            return Household.objects.filter(id__in=household_ids)
        elif target_population_id := input_data.get("target_population"):
            return Household.objects.filter(selections__target_population__id=target_population_id)
        elif registration_data_import_id := input_data.get("registration_data_import"):
            return Household.objects.filter(registration_data_import_id=registration_data_import_id)
