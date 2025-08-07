import logging
from datetime import timedelta
from typing import Any

from django.db.models import Q
from django.utils import timezone

from hope.apps.core.celery import app
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.notifications import GrievanceNotification
from hope.apps.utils.logs import log_start_and_end
from hope.apps.utils.sentry import sentry_tags, set_sentry_business_area_tag

logger = logging.getLogger(__name__)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def deduplicate_and_check_against_sanctions_list_task_single_individual(
    self: Any,
    should_populate_index: bool,
    individual_id: str,
) -> None:
    """
    This task is used in Grievance Tickets which changes/ adds an individual.
    """
    try:
        from hope.apps.grievance.tasks.deduplicate_and_check_sanctions import (
            deduplicate_and_check_against_sanctions_list_task_single_individual,
        )
        from hope.apps.household.models import Individual

        individual = Individual.objects.get(id=individual_id)
        if individual:
            business_area_name = individual.business_area.name
            set_sentry_business_area_tag(business_area_name)

        deduplicate_and_check_against_sanctions_list_task_single_individual(should_populate_index, individual)
    except Exception as e:
        logger.warning(e)
        raise self.retry(exc=e)


@app.task
@log_start_and_end
@sentry_tags
def periodic_grievances_notifications() -> None:
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
