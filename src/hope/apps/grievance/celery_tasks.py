from datetime import timedelta
import logging

from django.db import Error, transaction
from django.db.models import Q
from django.utils import timezone
from elasticsearch.exceptions import ConnectionError as ElasticsearchConnectionError, RequestError

from hope.apps.core.celery import app
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.notifications import GrievanceNotification
from hope.apps.utils.sentry import set_sentry_business_area_tag
from hope.models import AsyncJob, AsyncRetryJob, Individual, PeriodicAsyncJob, User

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


def bulk_assign_notifications_async_task_action(job: AsyncJob) -> None:
    ticket_ids = job.config["ticket_ids"]
    action_user_id = job.config.get("action_user_id")
    action_user = User.objects.filter(id=action_user_id).first() if action_user_id else None
    GrievanceNotification.send_all_notifications(
        [
            GrievanceNotification(ticket, GrievanceNotification.ACTION_ASSIGNMENT_CHANGED, editor=action_user)
            for ticket in GrievanceTicket.objects.filter(id__in=ticket_ids)
        ]
    )


def bulk_assign_notifications_async_task(ticket_ids: list[str], action_user_id: str | None) -> None:
    action_user_id = str(action_user_id) if action_user_id else None
    AsyncJob.queue_task(
        job_name=bulk_assign_notifications_async_task.__name__,
        owner_id=action_user_id,
        action="hope.apps.grievance.celery_tasks.bulk_assign_notifications_async_task_action",
        config={
            "ticket_ids": [str(ticket_id) for ticket_id in ticket_ids],
            "action_user_id": action_user_id,
        },
        group_key="grievance",
        description=f"Send assignment-change notifications for {len(ticket_ids)} grievance ticket(s)",
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
