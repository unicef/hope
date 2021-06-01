import logging
from datetime import datetime, timedelta

from django.db.models import Q

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.grievance.notifications import GrievanceNotification

logger = logging.getLogger(__name__)


@app.task
def deduplicate_and_check_against_sanctions_list_task(
    should_populate_index, registration_data_import_id, individuals_ids
):
    logger.info("deduplicate_and_check_against_sanctions_list_task start")

    try:
        from hct_mis_api.apps.grievance.tasks.deduplicate_and_check_sanctions import (
            DeduplicateAndCheckAgainstSanctionsListTask,
        )

        DeduplicateAndCheckAgainstSanctionsListTask().execute(
            should_populate_index, registration_data_import_id, individuals_ids
        )
    except Exception as e:
        logger.exception(e)
        raise

    logger.info("deduplicate_and_check_against_sanctions_list_task end")


@app.task
def periodic_grievances_notifications():
    sensitive_tickets_one_day_date = datetime.now() - timedelta(days=1)
    sensitive_tickets_to_notify = (
        GrievanceTicket.objects.exclude(status=GrievanceTicket.STATUS_CLOSED)
        .filter(
            Q(Q(last_notification_sent__isnull=True) & Q(created_at__lte=sensitive_tickets_one_day_date))
            | Q(last_notification_sent__lte=sensitive_tickets_one_day_date)
        )
        .filter(category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE)
    )

    other_tickets_30_days_date = datetime.now() - timedelta(days=30)
    other_tickets_to_notify = (
        GrievanceTicket.objects.exclude(status=GrievanceTicket.STATUS_CLOSED)
        .filter(
            Q(Q(last_notification_sent__isnull=True) & Q(created_at__lte=other_tickets_30_days_date))
            | Q(last_notification_sent__lte=other_tickets_30_days_date)
        )
        .exclude(category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE)
    )
    for ticket in sensitive_tickets_to_notify:
        notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_SENSITIVE_REMINDER)
        notification.send_email_notification()
        ticket.last_notification_sent = datetime.now()
        ticket.save()
    for ticket in other_tickets_to_notify:
        notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_OVERDUE)
        notification.send_email_notification()
        ticket.last_notification_sent = datetime.now()
        ticket.save()
