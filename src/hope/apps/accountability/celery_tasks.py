import logging

from hope.apps.accountability.services.export_survey_sample_service import (
    ExportSurveySampleService,
)
from hope.apps.core.services.rapid_pro.api import RapidProAPI
from hope.apps.core.utils import send_email_notification
from hope.apps.utils.sentry import set_sentry_business_area_tag
from hope.models import AsyncJob, Survey, User

logger = logging.getLogger(__name__)


def export_survey_sample_task_action(job: AsyncJob) -> None:
    from hope.models import User

    survey_id = job.config["survey_id"]
    user_id = job.config["user_id"]

    try:
        survey = Survey.objects.get(id=survey_id)
        user = User.objects.get(pk=user_id)
        set_sentry_business_area_tag(survey.business_area.name)

        service = ExportSurveySampleService(survey, user)
        service.export_sample()

        if survey.business_area.enable_email_notification:
            send_email_notification(service, user)

    except Exception as exc:
        job.errors = {
            "error": str(exc),
        }
        job.save(update_fields=["errors"])
        logger.exception("Failed to export survey sample")
        raise


def send_survey_to_users_action(job: AsyncJob) -> None:
    survey_id = job.config["survey_id"]
    try:
        survey = Survey.objects.get(id=survey_id)
        set_sentry_business_area_tag(survey.business_area.name)
        if survey.category == Survey.CATEGORY_MANUAL:
            return
        phone_numbers = survey.recipients.filter(head_of_household__phone_no_valid=True).values_list(
            "head_of_household__phone_no", flat=True
        )
        if survey.category == Survey.CATEGORY_SMS:
            api = RapidProAPI(survey.business_area.slug, RapidProAPI.MODE_MESSAGE)
            api.broadcast_message(phone_numbers, survey.body)
            return
        api = RapidProAPI(survey.business_area.slug, RapidProAPI.MODE_VERIFICATION)

        already_received = {
            phone_number
            for successful_call in survey.successful_rapid_pro_calls
            for phone_number in successful_call["urns"]
        }
        phone_numbers = [phone_number for phone_number in phone_numbers if phone_number not in already_received]

        successful_flows, error = api.start_flow(survey.flow_id, phone_numbers)
        if error:
            job.errors = {
                "start_flow_error": str(error),
            }
            job.save(update_fields=["errors"])

        for successful_flow in successful_flows:
            survey.successful_rapid_pro_calls.append(
                {
                    "flow_uuid": successful_flow.response["uuid"],
                    "urns": list(map(str, successful_flow.urns)),
                }
            )
        survey.save()
    except Exception as exc:
        job.errors = {
            "error": str(exc),
        }
        job.save(update_fields=["errors"])
        logger.exception("Failed to send survey to users")
        raise


def export_survey_sample_task(survey: Survey, user: User) -> None:
    survey_id = str(survey.id)
    user_id = str(user.id)
    AsyncJob.queue_task(
        job_name=export_survey_sample_task.__name__,
        owner_id=user.id,
        program=survey.program,
        action="hope.apps.accountability.celery_tasks.export_survey_sample_task_action",
        config={"survey_id": survey_id, "user_id": user_id},
        group_key=f"export_survey_sample_task:{survey_id}",
        description=f"Export survey sample for survey {survey_id}",
    )


def send_survey_to_users(survey: Survey) -> None:
    survey_id = str(survey.id)
    AsyncJob.queue_task(
        job_name=send_survey_to_users.__name__,
        program=survey.program,
        action="hope.apps.accountability.celery_tasks.send_survey_to_users_action",
        config={"survey_id": survey_id},
        group_key=f"send_survey_to_users:{survey_id}",
        description=f"Send survey to users for survey {survey_id}",
    )
