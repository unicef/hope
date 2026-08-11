from datetime import date, timedelta
import logging

from django.db import Error, transaction
from django.db.models import Q
from django.utils import timezone
from elasticsearch.exceptions import ConnectionError as ElasticsearchConnectionError, RequestError

from hope.apps.core.celery import app
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.notifications import GrievanceNotification
from hope.apps.grievance.services.daily_digest_service import DailyDigestService
from hope.apps.utils.sentry import set_sentry_business_area_tag
from hope.models import AsyncJob, AsyncRetryJob, BusinessArea, Individual, PeriodicAsyncJob

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


def daily_grievance_digest_async_task_action(job: PeriodicAsyncJob) -> None:
    business_area_id = job.config["business_area_id"]
    digest_date = job.config["digest_date"]

    # Jobs can run more than once (redelivery, recovery re-queue, a duplicate beat firing), and
    # rerunning would mail everyone again. Skip a business area/day that already went out.
    completed_key = f"{business_area_id}:{digest_date}"
    if job.config.get("completed_for") == completed_key:
        return
    if (
        PeriodicAsyncJob.objects.filter(
            job_name=daily_grievance_digest_async_task.__name__,
            config__completed_for=completed_key,
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
    _, failed = DailyDigestService(business_area, date.fromisoformat(digest_date)).send()

    if failed:
        raise RuntimeError(f"{failed} recipient(s) missed the {digest_date} grievance digest for {business_area.slug}")

    job.config["completed_for"] = completed_key
    job.save(update_fields=["config"])


@app.task()
def daily_grievance_digest_async_task() -> None:
    digest_date = (timezone.now() - timedelta(days=1)).date().isoformat()
    for business_area_id, name in BusinessArea.objects.filter(enable_email_notification=True).values_list("id", "name"):
        PeriodicAsyncJob.queue_task(
            job_name=daily_grievance_digest_async_task.__name__,
            action="hope.apps.grievance.celery_tasks.daily_grievance_digest_async_task_action",
            config={"business_area_id": str(business_area_id), "digest_date": digest_date},
            group_key="grievance",
            description=f"Send the {digest_date} grievance digest for {name}",
        )


def periodic_grievances_notifications_async_task_action(job: AsyncJob) -> None:
    now = timezone.now()
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
        if ticket.business_area.enable_email_notification:
            notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_SENSITIVE_REMINDER)
            notification.send_email_notification()
            ticket.last_notification_sent = now
            ticket.save(update_fields=["last_notification_sent"])

    for ticket in other_tickets_to_notify:
        set_sentry_business_area_tag(ticket.business_area.name)
        if ticket.business_area.enable_email_notification:
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
