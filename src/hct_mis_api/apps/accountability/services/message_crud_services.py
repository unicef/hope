import logging

from django.contrib.auth.models import AbstractUser
from django.db.models import Q, QuerySet
from django.shortcuts import get_object_or_404

from graphql import GraphQLError

from hct_mis_api.apps.accountability.models import Message
from hct_mis_api.apps.accountability.services.sampling import Sampling
from hct_mis_api.apps.accountability.services.verifiers import MessageArgumentVerifier
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.services.rapid_pro.api import RapidProAPI
from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.registration_data.models import RegistrationDataImport

logger = logging.getLogger(__name__)


class MessageCrudServices:
    @classmethod
    def create(cls, user: AbstractUser, business_area: BusinessArea, input_data: dict) -> Message:
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

        if payment_plan_id := input_data.get("payment_plan"):
            message.payment_plan = get_object_or_404(PaymentPlan, id=decode_id_string(payment_plan_id))

        if registration_data_import_id := input_data.get("registration_data_import"):
            message.registration_data_import = get_object_or_404(
                RegistrationDataImport, id=decode_id_string(registration_data_import_id)
            )

        if message.number_of_recipients == 0:
            err_msg = "No recipients found for the given criteria"
            logger.warning(err_msg)
            raise GraphQLError(err_msg)

        message.save()
        phone_numbers = message.households.filter(
            Q(head_of_household__phone_no__isnull=False) | ~Q(head_of_household__phone_no="")
        ).values_list("head_of_household__phone_no", flat=True)
        api = RapidProAPI(business_area.slug, RapidProAPI.MODE_MESSAGE)
        api.broadcast_message(phone_numbers, message.body)
        return message

    @classmethod
    def _get_households(cls, input_data: dict) -> QuerySet[Household]:
        if household_ids := [decode_id_string(household) for household in input_data.get("households", [])]:
            return Household.objects.filter(id__in=household_ids).exclude(
                head_of_household__phone_no_valid=False,
                head_of_household__phone_no_alternative_valid=False,
            )
        elif payment_plan_id := input_data.get("payment_plan"):
            payment_plan = PaymentPlan.objects.get(id=decode_id_string(payment_plan_id))
            if payment_plan.status == PaymentPlan.Status.TP_OPEN:
                return Household.objects.none()
            return Household.objects.filter(payment__parent=payment_plan).exclude(
                head_of_household__phone_no_valid=False,
                head_of_household__phone_no_alternative_valid=False,
            )
        elif registration_data_import_id := input_data.get("registration_data_import"):
            return Household.objects.filter(
                registration_data_import__status=RegistrationDataImport.MERGED,
                registration_data_import_id=decode_id_string(registration_data_import_id),
            ).exclude(
                head_of_household__phone_no_valid=False,
                head_of_household__phone_no_alternative_valid=False,
            )
        return Household.objects.none()
