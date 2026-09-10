"""Daily per-business-area grievance emails.

Replaces the per-event assignment and ticket-updated emails, and the per-ticket overdue reminders.
Reads the timestamp/actor fields on the ticket, so there is no event stream to keep. Every email
carries a count and a link to the matching My Tasks preset — never a list of tickets, which also
means a sensitive ticket's id never reaches an inbox.
"""

from collections import Counter
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
import logging
from typing import TYPE_CHECKING

from constance import config
from django.db.models import Count, F, Q
from django.template.loader import render_to_string

from hope.apps.grievance.constants import (
    PRESET_MINE,
    PRESET_MINE_SENSITIVE,
)
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.utils import my_tasks_url, overdue_q
from hope.apps.utils.mailjet import MailjetClient
from hope.models import User

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from hope.models import BusinessArea

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EmailSpec:
    """One notification type: its subject, its copy, and the list it links to."""

    subject: str
    intro: str
    preset: str
    overdue: bool = False


ASSIGNED_SENSITIVE = EmailSpec(
    subject="Pending Assigned Sensitive Tickets",
    intro="Sensitive grievance tickets were assigned to you.",
    preset=PRESET_MINE_SENSITIVE,
)
ASSIGNED = EmailSpec(
    subject="Pending Assigned Tickets",
    intro="Grievance tickets were assigned to you.",
    preset=PRESET_MINE,
)
OVERDUE = EmailSpec(
    subject="Overdue Tickets",
    intro="Grievance tickets assigned to you are past their due date.",
    preset=PRESET_MINE,
    overdue=True,
)
UPDATED = EmailSpec(
    subject="Updated Tickets",
    intro="Grievance tickets you are responsible for were changed by someone else.",
    preset=PRESET_MINE,
)


class DailyDigestService:
    """Builds and sends the grievance emails for one business area and one day.

    One email per (recipient, notification type). A user is never notified about a change they made
    themselves, and a ticket assigned to someone today is not also reported to them as updated.
    """

    def __init__(self, business_area: "BusinessArea", digest_date: date) -> None:
        self.business_area = business_area
        self.digest_date = digest_date
        self.start = datetime.combine(digest_date, time.min, tzinfo=UTC)
        self.end = self.start + timedelta(days=1)

    def send(self) -> tuple[int, int]:
        """Send every email for the day. Returns number of (sent, failed)."""
        sent = 0
        failed = 0

        if not config.SEND_GRIEVANCES_NOTIFICATION:
            return sent, failed

        for spec, counts in self.build_emails():
            for user, ticket_count in counts.items():
                try:
                    self._build_email(spec, user, ticket_count).send_email()
                    sent += 1
                except Exception:
                    logger.exception(
                        f"Failed to send the {self.digest_date.isoformat()} {spec.subject} "
                        f"grievance email to user {user.pk}"
                    )
                    failed += 1
        logger.info(
            f"Grievance emails for {self.business_area.slug} on {self.digest_date.isoformat()}: "
            f"{sent} sent, {failed} failed"
        )
        return sent, failed

    def build_emails(self) -> list[tuple[EmailSpec, dict[User, int]]]:
        assigned = self._assigned_tickets()
        sensitive = {"category": GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE}
        return [
            (ASSIGNED_SENSITIVE, self._counts_by_assignee(assigned.filter(**sensitive))),
            (ASSIGNED, self._counts_by_assignee(assigned.exclude(**sensitive))),
            (OVERDUE, self._counts_by_assignee(self._overdue_tickets())),
            (UPDATED, self._updated_counts()),
        ]

    @staticmethod
    def _counts_by_assignee(qs: "QuerySet[GrievanceTicket]") -> dict[User, int]:
        totals = {row["assigned_to"]: row["total"] for row in qs.values("assigned_to").annotate(total=Count("id"))}
        users = User.objects.in_bulk(totals)
        return {users[user_id]: total for user_id, total in totals.items()}

    def _updated_counts(self) -> dict[User, int]:
        """Count updated tickets per recipient, skipping their own edits and their own new assignments."""
        assigned_pairs = set(self._assigned_tickets().values_list("assigned_to_id", "id"))
        counted: set[tuple] = set()
        totals: Counter = Counter()

        for ticket_id, assigned_to_id, created_by_id, modified_by_id in self._updated_tickets().values_list(
            "id", "assigned_to_id", "created_by_id", "user_modified_by_id"
        ):
            for candidate_id in (assigned_to_id, created_by_id):
                pair = (candidate_id, ticket_id)
                if candidate_id is None or candidate_id == modified_by_id:
                    continue
                if pair in assigned_pairs or pair in counted:
                    continue
                counted.add(pair)
                totals[candidate_id] += 1

        # the querysets only guarantee that *one* of creator/assignee is mailable, so re-check here
        users = User.objects.filter(pk__in=totals, is_active=True).exclude(email="")
        return {user: totals[user.pk] for user in users}

    def _assigned_tickets(self) -> "QuerySet[GrievanceTicket]":
        return self._for_business_area().filter(
            Q(assigned_by__isnull=True) | ~Q(assigned_by=F("assigned_to")),
            Q(assigned_to__is_active=True, assigned_to__email__gt=""),
            assigned_at__gte=self.start,
            assigned_at__lt=self.end,
            assigned_to__isnull=False,
        )

    def _overdue_tickets(self) -> "QuerySet[GrievanceTicket]":
        return (
            self._for_business_area()
            .filter(
                overdue_q(),
                assigned_to__is_active=True,
                assigned_to__email__gt="",
            )
            .exclude(status=GrievanceTicket.STATUS_CLOSED)
        )

    def _updated_tickets(self) -> "QuerySet[GrievanceTicket]":
        return self._for_business_area().filter(
            Q(assigned_to__is_active=True, assigned_to__email__gt="")
            | Q(created_by__is_active=True, created_by__email__gt=""),
            user_modified__gte=self.start,
            user_modified__lt=self.end,
            # user_modified_by is not set during creation
            user_modified_by__isnull=False,
        )

    def _for_business_area(self) -> "QuerySet[GrievanceTicket]":
        return GrievanceTicket.objects.filter(
            business_area=self.business_area,
            business_area__enable_email_notification=True,
        )

    def _build_email(self, spec: EmailSpec, user: User, ticket_count: int) -> MailjetClient:
        context = {
            "first_name": user.first_name or getattr(user, "username", ""),
            "last_name": user.last_name,
            "title": spec.subject,
            "intro": spec.intro,
            "digest_date": self.digest_date.isoformat(),
            "ticket_count": ticket_count,
            "tickets_url": my_tasks_url(self.business_area, spec.preset, overdue=spec.overdue),
        }
        return MailjetClient(
            subject=f"HOPE {self.business_area.name}: {spec.subject}",
            recipients=[user.email],
            text_body=render_to_string("grievance_summary_notification_email.txt", context=context),
            html_body=render_to_string("grievance_summary_notification_email.html", context=context),
        )
