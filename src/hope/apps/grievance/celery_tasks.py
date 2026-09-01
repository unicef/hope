from datetime import date, timedelta
import logging

from constance import config
from django.db import Error, transaction
from django.db.models import Q
from django.utils import timezone
from elasticsearch.exceptions import ConnectionError as ElasticsearchConnectionError, RequestError

from hope.apps.core.celery import app
from hope.apps.core.timezones import latest_local_schedule_time
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.notifications import GrievanceNotification
from hope.apps.grievance.services.daily_digest_service import DailyDigestService
from hope.apps.grievance.services.notification_schedule import (
    get_grievance_notification_hour,
    is_grievance_reminder_due,
)
from hope.apps.utils.sentry import set_sentry_business_area_tag
from hope.models import AsyncJob, AsyncRetryJob, BusinessArea, Individual, PeriodicAsyncJob

logger = logging.getLogger(__name__)


def _daily_digest_delivery_key(business_area_id: str, timezone_name: str, digest_date: date) -> str:
    return f"{business_area_id}:{timezone_name}:{digest_date.isoformat()}"


def _daily_digest_dispatch_exists(delivery_key: str) -> bool:
    return (
        PeriodicAsyncJob.objects.filter(
            job_name=daily_grievance_digest_async_task.__name__,
            config__delivery_key=delivery_key,
        )
        .filter(Q(config__completed=True) | Q(errors={}))
        .exists()
    )


def _sent_digest_user_ids(delivery_key: str) -> set[str]:
    sent_user_ids: set[str] = set()
    for job_config in PeriodicAsyncJob.objects.filter(
        job_name=daily_grievance_digest_async_task.__name__,
        config__delivery_key=delivery_key,
    ).values_list("config", flat=True):
        sent_user_ids.update(job_config.get("sent_user_ids", []))
    return sent_user_ids


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


def daily_grievance_digest_async_task_action(job: PeriodicAsyncJob) -> None:
    business_area_id = job.config["business_area_id"]
    digest_date = job.config["digest_date"]
    timezone_name = job.config["timezone_name"]
    delivery_key = job.config["delivery_key"]

    if job.config.get("completed") is True:
        return
    if (
        PeriodicAsyncJob.objects.filter(
            job_name=daily_grievance_digest_async_task.__name__,
            config__delivery_key=delivery_key,
            config__completed=True,
        )
        .exclude(pk=job.pk)
        .exists()
    ):
        return

    business_area = BusinessArea.objects.filter(id=business_area_id).first()
    if business_area is None:
        logger.warning(f"Skipping the {digest_date} grievance digest: business area {business_area_id} is gone")
        return

    set_sentry_business_area_tag(business_area.name)
    sent_user_ids = _sent_digest_user_ids(delivery_key)

    newly_sent_user_ids, failed = DailyDigestService(
        business_area,
        date.fromisoformat(digest_date),
        timezone_name,
    ).send(
        skip_user_ids=sent_user_ids,
    )
    sent_user_ids.update(newly_sent_user_ids)
    job.config["sent_user_ids"] = sorted(sent_user_ids)

    if failed:
        job.save(update_fields=["config"])
        raise RuntimeError(
            f"{failed} recipient(s) missed the {digest_date} grievance digest for "
            f"{business_area.slug} in {timezone_name}"
        )

    job.config["completed"] = True
    job.save(update_fields=["config"])


@app.task()
def daily_grievance_digest_async_task() -> None:
    if not config.SEND_GRIEVANCES_NOTIFICATION:
        return
    now = timezone.now()
    notification_hour = get_grievance_notification_hour()
    for business_area in BusinessArea.objects.filter(enable_email_notification=True).only("id", "name", "timezone"):
        for timezone_name in DailyDigestService.recipient_timezone_names(business_area):
            notification_date, _ = latest_local_schedule_time(timezone_name, now, notification_hour)
            digest_date = notification_date - timedelta(days=1)
            delivery_key = _daily_digest_delivery_key(str(business_area.id), timezone_name, digest_date)
            if _daily_digest_dispatch_exists(delivery_key):
                continue
            PeriodicAsyncJob.queue_task(
                job_name=daily_grievance_digest_async_task.__name__,
                action="hope.apps.grievance.celery_tasks.daily_grievance_digest_async_task_action",
                config={
                    "business_area_id": str(business_area.id),
                    "digest_date": digest_date.isoformat(),
                    "timezone_name": timezone_name,
                    "delivery_key": delivery_key,
                },
                group_key="grievance",
                description=f"Send the {digest_date} grievance digest for {business_area.name} in {timezone_name}",
            )


def periodic_grievances_notifications_async_task_action(job: AsyncJob) -> None:
    now = timezone.now()
    notification_hour = get_grievance_notification_hour()
    sensitive_tickets_one_day_date = now - timedelta(days=1)
    sensitive_tickets_to_notify = (
        GrievanceTicket.objects.select_related("business_area", "assigned_to")
        .exclude(status=GrievanceTicket.STATUS_CLOSED)
        .filter(
            Q(Q(last_notification_sent__isnull=True) & Q(created_at__lte=sensitive_tickets_one_day_date))
            | Q(last_notification_sent__lte=sensitive_tickets_one_day_date)
        )
        .filter(category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE)
    )

    other_tickets_30_days_date = now - timedelta(days=30)
    other_tickets_to_notify = (
        GrievanceTicket.objects.select_related("business_area", "assigned_to")
        .exclude(status=GrievanceTicket.STATUS_CLOSED)
        .filter(
            Q(Q(last_notification_sent__isnull=True) & Q(created_at__lte=other_tickets_30_days_date))
            | Q(last_notification_sent__lte=other_tickets_30_days_date)
        )
        .exclude(category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE)
    )
    for ticket in sensitive_tickets_to_notify:
        set_sentry_business_area_tag(ticket.business_area.name)
        if ticket.business_area.enable_email_notification and is_grievance_reminder_due(
            ticket,
            now,
            timedelta(days=1),
            notification_hour,
        ):
            notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_SENSITIVE_REMINDER)
            notification.send_email_notification()
            ticket.last_notification_sent = now
            ticket.save(update_fields=["last_notification_sent"])

    for ticket in other_tickets_to_notify:
        set_sentry_business_area_tag(ticket.business_area.name)
        if ticket.business_area.enable_email_notification and is_grievance_reminder_due(
            ticket,
            now,
            timedelta(days=30),
            notification_hour,
        ):
            notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_OVERDUE)
            notification.send_email_notification()
            ticket.last_notification_sent = now
            ticket.save(update_fields=["last_notification_sent"])


@app.task()
def periodic_grievances_notifications_async_task() -> None:
    PeriodicAsyncJob.queue_task(
        job_name=periodic_grievances_notifications_async_task.__name__,
        action="hope.apps.grievance.celery_tasks.periodic_grievances_notifications_async_task_action",
        config={},
        group_key="grievance",
        description="Send periodic grievance notifications",
    )
