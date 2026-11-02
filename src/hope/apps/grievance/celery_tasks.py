from datetime import date, datetime, timedelta
import logging

from constance import config
from django.db import Error, transaction
from django.db.models import Q
from django.utils import timezone
from elasticsearch.exceptions import ConnectionError as ElasticsearchConnectionError, RequestError

from hope.apps.core.celery import app
from hope.apps.core.timezones import latest_local_schedule_time
from hope.apps.grievance.services.my_tasks_service import MyTasksNotificationService
from hope.apps.grievance.services.notification_schedule import get_grievance_notification_hour
from hope.apps.utils.sentry import set_sentry_business_area_tag
from hope.models import AsyncRetryJob, BusinessArea, Individual, PeriodicAsyncJob

logger = logging.getLogger(__name__)


def deduplicate_and_check_against_sanctions_list_task_single_individual_async_task_action(job: AsyncRetryJob) -> None:
    """Deduplicate and check against the sanction List.

    This task is used in Grievance Tickets which changes or adds an individual.
    """
    should_populate_index = job.config["should_populate_index"]
    individual_id = job.config["individual_id"]

    try:
        from hope.apps.grievance.tasks.deduplicate_and_check_sanctions import (
            deduplicate_and_check_against_sanctions_list_task_single_individual,
        )
        from hope.models import Individual

        try:
            individual = (
                Individual.objects.select_related("business_area", "program")
                .prefetch_related("program__sanction_lists")
                .get(id=individual_id)
            )
        except Individual.DoesNotExist as e:
            logger.warning(e)
            return

        if individual:
            set_sentry_business_area_tag(individual.business_area.name)
        with transaction.atomic():
            deduplicate_and_check_against_sanctions_list_task_single_individual(should_populate_index, individual)
    except (Individual.DoesNotExist, Error, ElasticsearchConnectionError, RequestError):
        logger.exception("Failed to deduplicate and check individual against sanctions list")
        raise


def deduplicate_and_check_against_sanctions_list_task_single_individual_async_task(
    should_populate_index: bool,
    individual: Individual,
) -> None:
    individual_id = str(individual.id)
    AsyncRetryJob.queue_task(
        job_name=deduplicate_and_check_against_sanctions_list_task_single_individual_async_task.__name__,
        program=individual.program,
        action="hope.apps.grievance.celery_tasks.deduplicate_and_check_against_sanctions_list_task_single_individual_async_task_action",
        config={
            "should_populate_index": should_populate_index,
            "individual_id": individual_id,
        },
        group_key="grievance",
        description=f"Deduplicate and sanctions-check grievance individual {individual_id}",
    )


def _my_tasks_delivery_key(business_area_id: str, timezone_name: str, notification_date: date) -> str:
    return f"{business_area_id}:{timezone_name}:{notification_date.isoformat()}"


def _my_tasks_dispatched_within_monitor_window(
    business_area_id: str, timezone_name: str, notification_date: date
) -> bool:
    """Whether a job ran, or is still queued, for one of the last MY_TASKS_MONITOR_WINDOW days."""
    delivery_keys = [
        _my_tasks_delivery_key(business_area_id, timezone_name, notification_date - timedelta(days=days_ago))
        for days_ago in range(int(config.MY_TASKS_MONITOR_WINDOW))
    ]
    return (
        PeriodicAsyncJob.objects.filter(
            job_name=my_tasks_notification_async_task.__name__,
            config__delivery_key__in=delivery_keys,
        )
        .filter(Q(config__completed=True) | Q(errors={}))
        .exists()
    )


def my_tasks_notification_async_task_action(job: PeriodicAsyncJob) -> None:
    """One (business area, timezone, day): the cycle stamps make a re-run of a failed job safe."""
    if job.config.get("completed") is True:
        return
    business_area = BusinessArea.objects.filter(id=job.config["business_area_id"]).first()
    if business_area is None:
        logger.warning(f"Skipping the My Tasks emails: business area {job.config['business_area_id']} is gone")
        return

    set_sentry_business_area_tag(business_area.name)
    _, failed = MyTasksNotificationService(
        business_area,
        job.config["timezone_name"],
        datetime.fromisoformat(job.config["notification_time"]),
    ).send()
    if failed:
        raise RuntimeError(
            f"{failed} My Tasks email(s) failed for {business_area.slug} in {job.config['timezone_name']} "
            f"at {job.config['notification_time']}"
        )
    job.config["completed"] = True
    job.save(update_fields=["config"])


@app.task()
def my_tasks_notification_async_task() -> None:
    if not config.SEND_GRIEVANCES_NOTIFICATION:
        return
    now = timezone.now()
    notification_hour = get_grievance_notification_hour()
    for business_area in BusinessArea.objects.filter(enable_email_notification=True).only("id", "name", "timezone"):
        for timezone_name in MyTasksNotificationService.recipient_timezone_names(business_area):
            notification_date, notification_time = latest_local_schedule_time(timezone_name, now, notification_hour)
            if _my_tasks_dispatched_within_monitor_window(str(business_area.id), timezone_name, notification_date):
                continue
            delivery_key = _my_tasks_delivery_key(str(business_area.id), timezone_name, notification_date)
            PeriodicAsyncJob.queue_task(
                job_name=my_tasks_notification_async_task.__name__,
                action="hope.apps.grievance.celery_tasks.my_tasks_notification_async_task_action",
                config={
                    "business_area_id": str(business_area.id),
                    "timezone_name": timezone_name,
                    "delivery_key": delivery_key,
                    "notification_time": notification_time.isoformat(),
                },
                group_key="grievance",
                description=f"Send the {notification_date} My Tasks emails for {business_area.name} in {timezone_name}",
            )
