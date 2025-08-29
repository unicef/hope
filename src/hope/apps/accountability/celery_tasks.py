import logging

from django.db.models import Q

from hope.apps.accountability.services.export_survey_sample_service import (
    ExportSurveySampleService,
)
from hope.apps.core.celery import app
from hope.apps.core.services.rapid_pro.api import RapidProAPI
from hope.apps.core.utils import send_email_notification
from hope.apps.utils.logs import log_start_and_end
from hope.apps.utils.sentry import sentry_tags, set_sentry_business_area_tag
from hope.models.business_area import BusinessArea
from hope.models.survey import Survey

logger = logging.getLogger(__name__)


@app.task
@log_start_and_end
@sentry_tags
def export_survey_sample_task(survey_id: str, user_id: str) -> None:
    from hope.models.user import User

    try:
        survey = Survey.objects.get(id=survey_id)
        user = User.objects.get(pk=user_id)
        set_sentry_business_area_tag(survey.business_area.name)

        service = ExportSurveySampleService(survey, user)
        service.export_sample()

        if survey.business_area.enable_email_notification:
            send_email_notification(service, user)

    except Exception as e:
        logger.warning(e)
        raise


@app.task
@log_start_and_end
@sentry_tags
def send_survey_to_users(survey_id: str) -> None:
    survey = Survey.objects.get(id=survey_id)
    set_sentry_business_area_tag(survey.business_area.name)
    if survey.category == Survey.CATEGORY_MANUAL:
        return
    phone_numbers = survey.recipients.filter(
        Q(head_of_household__phone_no__isnull=False) | ~Q(head_of_household__phone_no="")
    ).values_list("head_of_household__phone_no", flat=True)
    if survey.category == Survey.CATEGORY_SMS:
        api = RapidProAPI(survey.business_area.slug, RapidProAPI.MODE_MESSAGE)
        api.broadcast_message(phone_numbers, survey.body)
        return
    business_area = BusinessArea.objects.get(id=survey.business_area_id)
    api = RapidProAPI(business_area.slug, RapidProAPI.MODE_VERIFICATION)

    already_received = [
        phone_number
        for successful_call in survey.successful_rapid_pro_calls
        for phone_number in successful_call["urns"]
    ]
    phone_numbers = [phone_number for phone_number in phone_numbers if phone_number not in already_received]

    successful_flows, error = api.start_flow(survey.flow_id, phone_numbers)

    for successful_flow in successful_flows:
        survey.successful_rapid_pro_calls.append(
            {
                "flow_uuid": successful_flow.response["uuid"],
                "urns": list(map(str, successful_flow.urns)),
            }
        )
    survey.save()
