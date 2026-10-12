"""My Tasks visits and the "you have new tasks" email.

A user is told once, by email, that a tab of their My Tasks page changed since they last opened that
tab. Opening any tab of the page ends the cycle. A user who does not open it is reminded after
MY_TASKS_ALARM_WINDOW days and then every MY_TASKS_REPEAT_EACH days, for as long as the changes are
still waiting. Nothing a user did themselves counts as a change, and nothing is ever emailed about
a ticket the user already saw.

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
from hope.apps.grievance.models import GrievanceTicket, MyTasksTabVisit, MyTasksVisit
from hope.apps.grievance.my_tasks import (
    MY_TASKS_PERMISSIONS,
    TAB_SCOPES,
    changed_since_q,
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

NEW_TASKS_INTRO = "Tickets on your My Tasks page were created or changed since you last opened it."
REMINDER_INTRO = "Tickets on your My Tasks page are still waiting for you."


def record_visit(user: "User", business_area: "BusinessArea", tab: str, now: datetime | None = None) -> dict[str, bool]:
    """Stamp the visit of one tab, end the user's email cycle and return which tabs changed.

    The visited tab is compared with its previous visit, every other tab with its own last visit, so
    a tab the user never opened keeps reporting its changes.
    """
    now = now or timezone.now()
    visit, _ = MyTasksVisit.objects.get_or_create(user=user, business_area=business_area)
    tab_visit, created = MyTasksTabVisit.objects.get_or_create(
        visit=visit, tab=tab, defaults={"last_visit_at": now, "seen_until": visit.created_at}
    )
    if not created:
        tab_visit.seen_until = tab_visit.last_visit_at
        tab_visit.last_visit_at = now
        tab_visit.save(update_fields=["seen_until", "last_visit_at"])
    visit.first_email_at = None
    visit.last_reminder_at = None
    visit.save(update_fields=["first_email_at", "last_reminder_at"])
    return changed_tabs(user, business_area, {**visit.tab_baselines(), tab: tab_visit.seen_until})


def seen_until(user: "User", business_area: "BusinessArea", tab: str) -> datetime | None:
    """Return the visit before the user's latest one to the tab; the rows changed after it are highlighted."""
    return (
        MyTasksTabVisit.objects.filter(visit__user=user, visit__business_area=business_area, tab=tab)
        .values_list("seen_until", flat=True)
        .first()
    )


def changed_tabs(user: "User", business_area: "BusinessArea", since: dict[str, datetime]) -> dict[str, bool]:
    """Per My Tasks tab, whether it holds a ticket somebody else changed after that tab's `since`."""
    # closed tickets are what the tabs hide by default, so a closure never lights a tab or mails
    tickets = GrievanceTicket.objects.filter(
        in_active_program_q(),
        visible_tickets_q(user, business_area, VIEW_LIST_PERMISSIONS),
        business_area=business_area,
    ).exclude(status=GrievanceTicket.STATUS_CLOSED)
    return {
        preset: tickets.filter(changed_since_q(user, since[preset]), scope(user, business_area)).exists()
        for preset, scope in TAB_SCOPES.items()
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
        visit, _ = MyTasksVisit.objects.get_or_create(user=user, business_area=self.business_area)
        tabs = changed_tabs(user, self.business_area, visit.tab_baselines())
        if not any(tabs.values()):
            return 0

        if visit.first_email_at is None:
            self._send(user, NEW_TASKS_INTRO, tabs)
            visit.first_email_at = self.notification_time
            visit.save(update_fields=["first_email_at"])
            return 1

        alarm_window = timedelta(days=int(config.MY_TASKS_ALARM_WINDOW))
        repeat_each = timedelta(days=int(config.MY_TASKS_REPEAT_EACH))
        # stamps are schedule instants, 24h +- 1h apart across a DST change; the half-day slack keeps
        # "N days later" true on those days and still rejects a same-day re-run
        slack = timedelta(hours=12)
        if self.notification_time < visit.first_email_at + alarm_window - slack:
            return 0
        if visit.last_reminder_at is not None and self.notification_time < visit.last_reminder_at + repeat_each - slack:
            return 0
        self._send(user, REMINDER_INTRO, tabs)
        visit.last_reminder_at = self.notification_time
        visit.save(update_fields=["last_reminder_at"])
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
