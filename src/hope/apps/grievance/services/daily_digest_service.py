"""Daily per-business-area digest of grievance tickets assigned to or edited by a user.

Replaces the per-event assignment and ticket-updated emails. Reads the timestamp/actor fields on
the ticket, so there is no event stream to keep.
"""

from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time, timedelta
import logging
from typing import TYPE_CHECKING, Any

from constance import config
from django.db.models import F, Q
from django.template.loader import render_to_string

from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.utils import grievance_ticket_url
from hope.apps.utils.mailjet import MailjetClient
from hope.apps.utils.recipients import is_mailable

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from hope.models import BusinessArea, User

logger = logging.getLogger(__name__)


@dataclass
class RecipientDigest:
    user: "User"
    assigned: list[GrievanceTicket] = field(default_factory=list)
    edited: list[GrievanceTicket] = field(default_factory=list)
    assigned_total: int = 0
    edited_total: int = 0


class DailyDigestService:
    """Builds and sends the grievance summary for one business area and one day.

    Each recipient gets a single email with two sections: tickets assigned to them that day, and
    tickets they created or are assigned to that someone else edited that day.

    A user is never notified about a change they made themselves, and a ticket appears at most once per
    recipient, under "assigned" when it qualifies for both sections.
    """

    # limit number of tickets that can be send in one email, and how many are ever held in memory
    ROW_LIMIT = 50

    def __init__(self, business_area: "BusinessArea", digest_date: date) -> None:
        self.business_area = business_area
        self.digest_date = digest_date
        self.start = datetime.combine(digest_date, time.min, tzinfo=UTC)
        self.end = self.start + timedelta(days=1)

    def send(self) -> tuple[int, int]:
        """Send one digest per recipient. Returns number of (sent, failed)."""
        sent = 0
        failed = 0

        if not config.SEND_GRIEVANCES_NOTIFICATION:
            return sent, failed

        for digest in self.build_digests():
            try:
                self._build_email(digest).send_email()
                sent += 1
            except Exception:
                logger.exception(
                    f"Failed to send the {self.digest_date.isoformat()} grievance digest to user {digest.user.pk}"
                )
                failed += 1
        logger.info(
            f"Grievance digest for {self.business_area.slug} on {self.digest_date.isoformat()}: "
            f"{sent} sent, {failed} failed"
        )
        return sent, failed

    def build_digests(self) -> list[RecipientDigest]:
        def digest_for(user: "User") -> RecipientDigest:
            return digests.setdefault(user.pk, RecipientDigest(user=user))

        digests: dict[Any, RecipientDigest] = {}
        # A ticket already listed under "assigned" is not repeated under "edited" for that user.
        assigned_pairs: set[tuple[Any, Any]] = set()

        for ticket in self._assigned_tickets().iterator():
            if not is_mailable(ticket.assigned_to):
                continue
            digest = digest_for(ticket.assigned_to)
            digest.assigned_total += 1
            if digest.assigned_total <= self.ROW_LIMIT:
                digest.assigned.append(ticket)
            assigned_pairs.add((ticket.assigned_to_id, ticket.pk))

        for ticket in self._edited_tickets().iterator():
            candidates = {c.pk: c for c in (ticket.created_by, ticket.assigned_to) if is_mailable(c)}
            for pk, candidate in candidates.items():
                if pk == ticket.user_modified_by_id or (pk, ticket.pk) in assigned_pairs:
                    continue
                digest = digest_for(candidate)
                digest.edited_total += 1
                if digest.edited_total <= self.ROW_LIMIT:
                    digest.edited.append(ticket)

        return list(digests.values())

    def _assigned_tickets(self) -> "QuerySet[GrievanceTicket]":
        return (
            GrievanceTicket.objects.filter(
                Q(assigned_by__isnull=True) | ~Q(assigned_by=F("assigned_to")),
                Q(assigned_to__is_active=True, assigned_to__email__gt=""),
                business_area=self.business_area,
                business_area__enable_email_notification=True,
                assigned_at__gte=self.start,
                assigned_at__lt=self.end,
                assigned_to__isnull=False,
            )
            .select_related("business_area", "assigned_to")
            .order_by("unicef_id")
        )

    def _edited_tickets(self) -> "QuerySet[GrievanceTicket]":
        return (
            GrievanceTicket.objects.filter(
                Q(assigned_to__is_active=True, assigned_to__email__gt="")
                | Q(created_by__is_active=True, created_by__email__gt=""),
                business_area=self.business_area,
                business_area__enable_email_notification=True,
                user_modified__gte=self.start,
                user_modified__lt=self.end,
                # user_modified_by is not set during creation
                user_modified_by__isnull=False,
            )
            .select_related("business_area", "assigned_to", "created_by", "user_modified_by")
            .order_by("unicef_id")
        )

    @staticmethod
    def _rows(tickets: list[GrievanceTicket], total: int) -> tuple[list[dict[str, Any]], int]:
        rows = [
            {
                "ticket_id": ticket.unicef_id,
                "ticket_category": ticket.get_category_display(),
                "ticket_status": ticket.get_status_display(),
                "ticket_url": grievance_ticket_url(ticket),
            }
            for ticket in tickets
        ]
        return rows, max(total - len(rows), 0)

    def _build_email(self, digest: RecipientDigest) -> MailjetClient:
        assigned_rows, assigned_remaining = self._rows(digest.assigned, digest.assigned_total)
        edited_rows, edited_remaining = self._rows(digest.edited, digest.edited_total)
        context = {
            "first_name": digest.user.first_name or getattr(digest.user, "username", ""),
            "last_name": digest.user.last_name,
            "title": "Grievance and feedback daily summary",
            "digest_date": self.digest_date.isoformat(),
            "assigned_rows": assigned_rows,
            "assigned_remaining": assigned_remaining,
            "edited_rows": edited_rows,
            "edited_remaining": edited_remaining,
        }
        return MailjetClient(
            subject=f"Your Grievance & Feedback summary for {self.digest_date.isoformat()}",
            recipients=[digest.user.email],
            text_body=render_to_string("daily_digest_notification_email.txt", context=context),
            html_body=render_to_string("daily_digest_notification_email.html", context=context),
        )
