import logging
from datetime import timedelta
from typing import Any, List

from django.db.models import Q
from django.utils import timezone

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.grievance.notifications import GrievanceNotification
from hct_mis_api.apps.utils.logs import log_start_and_end
from hct_mis_api.apps.utils.sentry import sentry_tags, set_sentry_business_area_tag

logger = logging.getLogger(__name__)


@app.task(bind=True, queue="priority", default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def deduplicate_and_check_against_sanctions_list_task(
    self: Any, should_populate_index: bool, individuals_ids: List[str]
) -> None:
    try:
        from hct_mis_api.apps.grievance.tasks.deduplicate_and_check_sanctions import (
            DeduplicateAndCheckAgainstSanctionsListTask,
        )
        from hct_mis_api.apps.household.models import Individual

        individual = Individual.objects.filter(id__in=individuals_ids[:1]).first()
        if individual:
            business_area_name = individual.business_area.name
            set_sentry_business_area_tag(business_area_name)

        DeduplicateAndCheckAgainstSanctionsListTask().execute(should_populate_index, individuals_ids)
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
