from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from hct_mis_api.apps.accountability.models import Survey
from hct_mis_api.apps.accountability.services.sampling import Sampling
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.program.models import Program


class SurveyCrudServices:
    @classmethod
    def create(cls, user: AbstractUser, business_area: BusinessArea, input_data: dict) -> Survey:
        survey = Survey(
            created_by=user,
            business_area=business_area,
            title=input_data.get("title"),
            category=input_data.get("category"),
            sampling_type=input_data.get("sampling_type"),
            body=input_data.get("body", ""),
        )

        if payment_plan := input_data.get("payment_plan"):
            obj = get_object_or_404(PaymentPlan, id=decode_id_string(payment_plan))
            households = Household.objects.filter(payment__parent=obj)
            survey.payment_plan = obj
            survey.program = obj.program_cycle.program
        elif program := input_data.get("program"):
            obj = get_object_or_404(Program, id=decode_id_string(program))
            households = obj.households_with_payments_in_program
            survey.program = obj
        else:
            raise ValidationError("Target population or program should be provided.")

        sampling = Sampling(input_data, households)
        result = sampling.process_sampling()
        survey.sample_size = result.sample_size
        survey.full_list_arguments = result.full_list_arguments if result.full_list_arguments else dict()
        survey.random_sampling_arguments = (
            result.random_sampling_arguments if result.random_sampling_arguments else dict()
        )
        survey.number_of_recipients = result.number_of_recipients
        survey.recipients.set(result.households)

        if "flow" in input_data:
            survey.flow_id = input_data["flow"]

        if not result.households:
            raise Exception("There are no selected recipients or no recipient meets criteria.")
        survey.save()
        return survey
