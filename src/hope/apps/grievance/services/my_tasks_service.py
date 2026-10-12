"""Unread tickets on My Tasks and the "you have new tasks" email.

A ticket is unread for a user when somebody else changed it after the user last opened it. A user with
unread tickets is told once by email, reminded after MY_TASKS_ALARM_WINDOW days and then every
MY_TASKS_REPEAT_EACH days, for as long as something stays unread. Opening a ticket ends the cycle, and
so does a check that finds nothing unread. Nothing a user did themselves counts as a change.

One run covers one (business area, recipient timezone, day) and evaluates only the recipients in
that timezone, so every email goes out at the local notification hour.
"""

from datetime import datetime, timedelta
import logging
from typing import TYPE_CHECKING

from constance import config
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone

from hope.apps.core.timezones import resolve_timezone_name
from hope.apps.grievance.constants import PRESET_MINE, PRESET_NEEDS_ASSIGNMENT, PRESET_PENDING_APPROVAL
from hope.apps.grievance.models import GrievanceTicket, MyTasksTracking, TicketSeen
from hope.apps.grievance.my_tasks import (
    MY_TASKS_PERMISSIONS,
    TAB_SCOPES,
    annotate_unread,
    in_active_program_q,
)
from hope.apps.grievance.utils import my_tasks_url
from hope.apps.grievance.visibility import VIEW_LIST_PERMISSIONS, visible_tickets_q
from hope.apps.utils.mailjet import MailjetClient
from hope.apps.utils.recipients import users_with_permissions

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from hope.models import BusinessArea, User

logger = logging.getLogger(__name__)

TAB_LABELS = {
    PRESET_NEEDS_ASSIGNMENT: "Needs assignment",
    PRESET_MINE: "Assigned to you",
    PRESET_PENDING_APPROVAL: "Pending approval",
}

NEW_TASKS_INTRO = "Tickets on your My Tasks page were created or changed and you have not opened them yet."
REMINDER_INTRO = "Tickets on your My Tasks page are still waiting for you."


def start_tracking(user: "User", business_area: "BusinessArea") -> MyTasksTracking:
    """Return the user's tracking row for the business area, creating it on their first visit or check."""
    tracking, _ = MyTasksTracking.objects.get_or_create(user=user, business_area=business_area)
    return tracking


def mark_seen(user: "User", ticket: GrievanceTicket, now: datetime | None = None) -> None:
    """Stamp that the user opened the ticket and end their email cycle in its business area."""
    TicketSeen.objects.bulk_create(
        [TicketSeen(user=user, ticket=ticket, seen_at=now or timezone.now())],
        update_conflicts=True,
        unique_fields=["user", "ticket"],
        update_fields=["seen_at", "updated_at"],
    )
    MyTasksTracking.objects.filter(user=user, business_area=ticket.business_area).update(
        first_email_at=None, last_reminder_at=None
    )


def unread_tabs(user: "User", business_area: "BusinessArea", tracking_start: datetime) -> dict[str, bool]:
    """Per My Tasks tab, whether it holds a ticket the user has not opened since somebody else changed it."""
    # closed tickets are what the tabs hide by default, so a closure never lights a tab or mails
    tickets = GrievanceTicket.objects.filter(
        in_active_program_q(),
        visible_tickets_q(user, business_area, VIEW_LIST_PERMISSIONS),
        business_area=business_area,
    ).exclude(status=GrievanceTicket.STATUS_CLOSED)
    unread = annotate_unread(tickets, user, tracking_start)
    return {
        preset: unread.filter(scope(user, business_area), unread=True).exists() for preset, scope in TAB_SCOPES.items()
    }


class MyTasksNotificationService:
    """Evaluates every recipient of one business area and timezone and mails the ones due an email."""

    def __init__(self, business_area: "BusinessArea", timezone_name: str, notification_time: datetime) -> None:
        self.business_area = business_area
        self.timezone_name = timezone_name
        # the instant the run was scheduled for, so a late or retried run stamps the same cycle dates
        self.notification_time = notification_time

    def send(self) -> tuple[int, int]:
        """Return how many emails were handed to the mail queue and how many failed before that."""
        sent = 0
        failed = 0
        if not config.SEND_GRIEVANCES_NOTIFICATION or not self.business_area.enable_email_notification:
            return sent, failed
        for user in self._recipients():
            try:
                sent += self._evaluate(user)
            except Exception:
                logger.exception(
                    f"Failed to evaluate the My Tasks email for user {user.pk} in {self.business_area.slug}"
                )
                failed += 1
        logger.info(
            f"My Tasks emails for {self.business_area.slug} in {self.timezone_name} at "
            f"{self.notification_time.isoformat()}: {sent} sent, {failed} failed"
        )
        return sent, failed

    def _recipients(self) -> "QuerySet[User]":
        users = users_with_permissions(self.business_area, MY_TASKS_PERMISSIONS)
        timezone_filter = Q(timezone=self.timezone_name)
        if self.timezone_name == resolve_timezone_name(business_area=self.business_area):
            timezone_filter |= Q(timezone__isnull=True) | Q(timezone="")
        return users.filter(timezone_filter)

    @staticmethod
    def recipient_timezone_names(business_area: "BusinessArea") -> set[str]:
        timezone_names = (
            users_with_permissions(business_area, MY_TASKS_PERMISSIONS)
            .exclude(timezone__isnull=True)
            .exclude(timezone="")
            .order_by()
            .values_list("timezone", flat=True)
            .distinct()
        )
        return {
            resolve_timezone_name(business_area=business_area),
            *(str(timezone_name) for timezone_name in timezone_names),
        }

    def _evaluate(self, user: "User") -> int:
        """Send the email the user is due, if any, and return 1 when one went out."""
        tracking = start_tracking(user, self.business_area)
        tabs = unread_tabs(user, self.business_area, tracking.created_at)
        if not any(tabs.values()):
            # everything was opened: the next unread ticket starts a new cycle with a "new tasks" email
            tracking.first_email_at = None
            tracking.last_reminder_at = None
            tracking.save(update_fields=["first_email_at", "last_reminder_at"])
            return 0

        if tracking.first_email_at is None:
            self._send(user, NEW_TASKS_INTRO, tabs)
            tracking.first_email_at = self.notification_time
            tracking.save(update_fields=["first_email_at"])
            return 1

        alarm_window = timedelta(days=int(config.MY_TASKS_ALARM_WINDOW))
        repeat_each = timedelta(days=int(config.MY_TASKS_REPEAT_EACH))
        # stamps are schedule instants, 24h +- 1h apart across a DST change; the half-day slack keeps
        # "N days later" true on those days and still rejects a same-day re-run
        slack = timedelta(hours=12)
        if self.notification_time < tracking.first_email_at + alarm_window - slack:
            return 0
        if (
            tracking.last_reminder_at is not None
            and self.notification_time < tracking.last_reminder_at + repeat_each - slack
        ):
            return 0
        self._send(user, REMINDER_INTRO, tabs)
        tracking.last_reminder_at = self.notification_time
        tracking.save(update_fields=["last_reminder_at"])
        return 1

    def _send(self, user: "User", intro: str, tabs: dict[str, bool]) -> None:
        context = {
            "first_name": user.first_name or getattr(user, "username", ""),
            "last_name": user.last_name,
            "business_area_name": self.business_area.name,
            "intro": intro,
            "tabs": [
                {"label": TAB_LABELS[preset], "url": my_tasks_url(self.business_area, preset)}
                for preset, changed in tabs.items()
                if changed
            ],
        }
        MailjetClient(
            subject=f"[{self.business_area.name}] HOPE: you have new tasks",
            recipients=[user.email],
            text_body=render_to_string("my_tasks_notification_email.txt", context=context),
            html_body=render_to_string("my_tasks_notification_email.html", context=context),
        ).send_email()
