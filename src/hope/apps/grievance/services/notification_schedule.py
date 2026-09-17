from datetime import datetime, timedelta

from constance import config

from hope.apps.core.timezones import latest_local_schedule_time, resolve_timezone_name
from hope.apps.grievance.models import GrievanceTicket


def get_grievance_notification_hour() -> int:
    return int(config.GRIEVANCE_NOTIFICATION_HOUR)


def is_grievance_reminder_due(
    ticket: GrievanceTicket,
    at: datetime,
    reminder_interval: timedelta,
    notification_hour: int,
) -> bool:
    if ticket.assigned_to is None:
        return False
    timezone_name = resolve_timezone_name(user=ticket.assigned_to, business_area=ticket.business_area)
    _, notification_time = latest_local_schedule_time(timezone_name, at, notification_hour)
    if ticket.last_notification_sent is None:
        return ticket.created_at <= notification_time - reminder_interval
    return ticket.last_notification_sent < notification_time and ticket.last_notification_sent <= at - reminder_interval
