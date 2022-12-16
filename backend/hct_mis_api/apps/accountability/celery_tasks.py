import logging

from django.contrib.auth import get_user_model

from sentry_sdk import configure_scope

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.accountability.models import Survey
from hct_mis_api.apps.accountability.services.export_survey_sample_service import (
    ExportSurveySampleService,
)
from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.utils.logs import log_start_and_end
from hct_mis_api.apps.utils.sentry import sentry_tags
from hct_mis_api.apps.payment.services.rapid_pro.api import RapidProAPI

logger = logging.getLogger(__name__)


@app.task
@log_start_and_end
@sentry_tags
def export_survey_sample_task(survey_id: str, user_id: str) -> None:
    try:
        survey = Survey.objects.get(id=survey_id)
        user = get_user_model().objects.get(pk=user_id)

        with configure_scope() as scope:
            scope.set_tag("business_area", survey.business_area)

            service = ExportSurveySampleService(survey, user)
            service.export_sample()
            service.send_email()
    except Exception as e:
        logger.exception(e)
        raise


@app.task
@log_start_and_end
@sentry_tags
def send_survey_to_users(survey_id: str, flow_uuid: str, business_area_id: str) -> None:
    survey = Survey.objects.get(id=survey_id)
    business_area = BusinessArea.objects.get(id=business_area_id)
    api = RapidProAPI(business_area.slug)
    print(survey.title)
    print(survey.target_population.households.all())

    # phone_numbers = survey.target_population.households.all().values_list("phone_no", flat=True)
    # get all individuals from households and get their phone numbers
    phone_numbers = survey.target_population.households.all().values_list("individuals__phone_no", flat=True)
    print(phone_numbers)

    successful_flows, error = api.start_flows(flow_uuid, phone_numbers)
    print("Successful flows: ", successful_flows)
    print("Error: ", error)

    # save successful ones to target population under successful_rapid_pro_flows list with phone numbers
