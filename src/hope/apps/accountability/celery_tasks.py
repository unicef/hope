import logging

from django_celery_boost.models import AsyncJobModel

from hope.apps.accountability.services.export_survey_sample_service import (
    ExportSurveySampleService,
)
from hope.apps.core.celery import app
from hope.apps.core.services.rapid_pro.api import RapidProAPI
from hope.apps.core.utils import send_email_notification
from hope.apps.utils.logs import log_start_and_end
from hope.apps.utils.sentry import sentry_tags, set_sentry_business_area_tag
from hope.models import AsyncJob, BusinessArea, Survey

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
        if job.errors:
            job.errors = {}
            job.save(update_fields=["errors"])

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
            if job.errors:
                job.errors = {}
                job.save(update_fields=["errors"])
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
        if "start_flow_error" not in job.errors and job.errors:
            job.errors = {}
            job.save(update_fields=["errors"])
    except Exception as exc:
        job.errors = {
            "error": str(exc),
        }
        job.save(update_fields=["errors"])
        logger.exception("Failed to send survey to users")
        raise


@app.task
@log_start_and_end
@sentry_tags
def export_survey_sample_task(survey_id: str, user_id: str) -> None:
    survey = Survey.objects.get(id=survey_id)
    job = AsyncJob.objects.create(
        owner_id=user_id,
        program=survey.program,
        type=AsyncJobModel.JobType.JOB_TASK,
        action="hope.apps.accountability.celery_tasks.export_survey_sample_task_action",
        config={"survey_id": str(survey_id), "user_id": str(user_id)},
        group_key=f"export_survey_sample_task:{survey_id}",
        description=f"Export survey sample for survey {survey_id}",
    )
    job.queue()


@app.task
@log_start_and_end
@sentry_tags
def send_survey_to_users(survey_id: str) -> None:
    survey = Survey.objects.get(id=survey_id)
    job = AsyncJob.objects.create(
        owner=survey.created_by,
        program=survey.program,
        type=AsyncJobModel.JobType.JOB_TASK,
        action="hope.apps.accountability.celery_tasks.send_survey_to_users_action",
        config={"survey_id": str(survey_id)},
        group_key=f"send_survey_to_users:{survey_id}",
        description=f"Send survey to users for survey {survey_id}",
    )
    job.queue()
