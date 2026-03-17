from datetime import timedelta
import logging
from typing import Any

from django.db import Error, transaction
from django.db.models import Q
from django.utils import timezone
from django_celery_boost.models import AsyncJobModel
from elasticsearch.exceptions import ConnectionError as ElasticsearchConnectionError, RequestError

from hope.apps.core.celery import app
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.notifications import GrievanceNotification
from hope.apps.utils.logs import log_start_and_end
from hope.apps.utils.sentry import sentry_tags, set_sentry_business_area_tag
from hope.models import AsyncJob

logger = logging.getLogger(__name__)


def deduplicate_and_check_against_sanctions_list_task_single_individual_action(job: AsyncJob) -> None:
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
        if job.errors:
            job.errors = {}
            job.save(update_fields=["errors"])
    except (Individual.DoesNotExist, Error, ElasticsearchConnectionError, RequestError) as exc:
        job.errors = {"error": str(exc)}
        job.save(update_fields=["errors"])
        logger.exception("Failed to deduplicate and check individual against sanctions list")
        raise


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def deduplicate_and_check_against_sanctions_list_task_single_individual(
    self: Any,
    should_populate_index: bool,
    individual_id: str,
) -> None:
    job = AsyncJob.objects.create(
        owner=None,
        type=AsyncJobModel.JobType.JOB_TASK,
        action="hope.apps.grievance.celery_tasks.deduplicate_and_check_against_sanctions_list_task_single_individual_action",
        config={
            "should_populate_index": should_populate_index,
            "individual_id": str(individual_id),
        },
        group_key=f"grievance_single_individual_deduplication:{individual_id}",
        description=f"Deduplicate and sanctions-check grievance individual {individual_id}",
    )
    job.queue()


def periodic_grievances_notifications_action(job: AsyncJob) -> None:
    sensitive_tickets_one_day_date = timezone.now() - timedelta(days=1)
    sensitive_tickets_to_notify = (
        GrievanceTicket.objects.exclude(status=GrievanceTicket.STATUS_CLOSED)
        .filter(
            Q(Q(last_notification_sent__isnull=True) & Q(created_at__lte=sensitive_tickets_one_day_date))
            | Q(last_notification_sent__lte=sensitive_tickets_one_day_date)
        )
        .filter(category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE)
    )

    other_tickets_30_days_date = timezone.now() - timedelta(days=30)
    other_tickets_to_notify = (
        GrievanceTicket.objects.exclude(status=GrievanceTicket.STATUS_CLOSED)
        .filter(
            Q(Q(last_notification_sent__isnull=True) & Q(created_at__lte=other_tickets_30_days_date))
            | Q(last_notification_sent__lte=other_tickets_30_days_date)
        )
        .exclude(category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE)
    )
    try:
        for ticket in sensitive_tickets_to_notify:
            set_sentry_business_area_tag(ticket.business_area.name)
            if ticket.business_area.enable_email_notification:
                notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_SENSITIVE_REMINDER)
                notification.send_email_notification()
                ticket.last_notification_sent = timezone.now()
                ticket.save()

        for ticket in other_tickets_to_notify:
            set_sentry_business_area_tag(ticket.business_area.name)
            if ticket.business_area.enable_email_notification:
                notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_OVERDUE)
                notification.send_email_notification()
                ticket.last_notification_sent = timezone.now()
                ticket.save()
    except Exception as exc:
        job.errors = {"error": str(exc)}
        job.save(update_fields=["errors"])
        logger.exception("Failed to send periodic grievance notifications")
        raise


@app.task
@log_start_and_end
@sentry_tags
def periodic_grievances_notifications() -> None:
    job = AsyncJob.objects.create(
        owner=None,
        type=AsyncJobModel.JobType.JOB_TASK,
        action="hope.apps.grievance.celery_tasks.periodic_grievances_notifications_action",
        config={},
        group_key="periodic_grievances_notifications",
        description="Send periodic grievance notifications",
    )
    job.queue()
