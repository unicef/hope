import logging

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from django.db.models import Q, QuerySet

from hct_mis_api.apps.accountability.models import Message
from hct_mis_api.apps.accountability.services.sampling import Sampling
from hct_mis_api.apps.accountability.services.verifiers import MessageArgumentVerifier
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.services.rapid_pro.api import RapidProAPI
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.registration_data.models import RegistrationDataImport

logger = logging.getLogger(__name__)


class MessageCrudServices:
    @classmethod
    def create(cls, user: AbstractBaseUser | AnonymousUser, business_area: BusinessArea, input_data: dict) -> Message:
        verifier = MessageArgumentVerifier(input_data)
        verifier.verify()

        households = cls._get_households(input_data)
        message = Message(
            created_by=user,
            business_area=business_area,
            title=input_data["title"],
            body=input_data["body"],
            sampling_type=input_data["sampling_type"],
        )

        sampling = Sampling(input_data, households)
        result = sampling.process_sampling()
        message.sample_size = result.sample_size
        message.full_list_arguments = result.full_list_arguments
        message.random_sampling_arguments = result.random_sampling_arguments
        message.number_of_recipients = result.number_of_recipients
        message.households.set(result.households)

        if payment_plan := input_data.get("payment_plan"):
            message.payment_plan = payment_plan

        if registration_data_import := input_data.get("registration_data_import"):
            message.registration_data_import = registration_data_import

        if message.number_of_recipients == 0:
            raise ValidationError("No recipients found for the given criteria")

        message.save()
        phone_numbers = message.households.filter(
            Q(head_of_household__phone_no__isnull=False) | ~Q(head_of_household__phone_no="")
        ).values_list("head_of_household__phone_no", flat=True)
        api = RapidProAPI(business_area.slug, RapidProAPI.MODE_MESSAGE)
        api.broadcast_message(phone_numbers, message.body)
        return message

    @classmethod
    def _get_households(cls, input_data: dict) -> QuerySet[Household]:
        if household_ids := input_data.get("households", []):
            return Household.objects.filter(id__in=household_ids).exclude(
                head_of_household__phone_no_valid=False,
                head_of_household__phone_no_alternative_valid=False,
            )
        if payment_plan := input_data.get("payment_plan"):
            if payment_plan.status == PaymentPlan.Status.TP_OPEN:
                return Household.objects.none()
            return Household.objects.filter(payment__parent=payment_plan).exclude(
                head_of_household__phone_no_valid=False,
                head_of_household__phone_no_alternative_valid=False,
            )
        if registration_data_import := input_data.get("registration_data_import"):
            return Household.objects.filter(
                registration_data_import__status=RegistrationDataImport.MERGED,
                registration_data_import=registration_data_import,
            ).exclude(
                head_of_household__phone_no_valid=False,
                head_of_household__phone_no_alternative_valid=False,
            )
        return Household.objects.none()
