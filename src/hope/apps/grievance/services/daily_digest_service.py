"""Daily per-business-area grievance emails.

Replaces the per-event assignment and ticket-updated emails, and the per-ticket overdue reminders.
Reads the timestamp/actor fields on the ticket, so there is no event stream to keep. Every email
carries a count and a link to the matching My Tasks preset — never a list of tickets, which also
means a sensitive ticket's id never reaches an inbox.

One run covers one (business area, recipient timezone, day): the day boundaries are the recipient's
local midnights, and each run only mails the recipients sitting in that timezone bucket.
"""

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
import logging
from typing import TYPE_CHECKING, Any
from zoneinfo import ZoneInfo

from constance import config
from django.db.models import Count, Exists, F, OuterRef, Q
from django.template.loader import render_to_string

from hope.apps.account.permissions import Permissions
from hope.apps.core.timezones import resolve_timezone_name
from hope.apps.grievance.constants import PRESET_MINE, PRESET_MINE_SENSITIVE, PRESET_NEEDS_ASSIGNMENT
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.utils import my_tasks_url, overdue_q
from hope.apps.utils.mailjet import MailjetClient
from hope.apps.utils.recipients import users_with_permissions
from hope.models import User

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from hope.models import BusinessArea

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Section:
    """One count in an email and the list it links to, so the count always matches that page."""

    label: str
    preset: str
    overdue: bool = False


@dataclass(frozen=True)
class EmailSpec:
    """One notification type. An email carries one section per category the recipient has tickets in."""

    subject: str
    intro: str
    sections: tuple[Section, ...]


SENSITIVE_LABEL = "Sensitive"
OTHER_LABEL = "Other"

NEEDS_ASSIGNMENT = EmailSpec(
    subject="New Tickets Needing Assignment",
    intro="Grievance tickets are waiting to be assigned.",
    sections=(Section(label="", preset=PRESET_NEEDS_ASSIGNMENT),),
)
ASSIGNED_SENSITIVE = EmailSpec(
    subject="Pending Assigned Sensitive Tickets",
    intro="Sensitive grievance tickets were assigned to you.",
    sections=(Section(label="", preset=PRESET_MINE_SENSITIVE),),
)
ASSIGNED = EmailSpec(
    subject="Pending Assigned Tickets",
    intro="Grievance tickets were assigned to you.",
    sections=(Section(label="", preset=PRESET_MINE),),
)
OVERDUE = EmailSpec(
    subject="Overdue Tickets",
    intro="Grievance tickets assigned to you are past their due date.",
    sections=(
        Section(label=SENSITIVE_LABEL, preset=PRESET_MINE_SENSITIVE, overdue=True),
        Section(label=OTHER_LABEL, preset=PRESET_MINE, overdue=True),
    ),
)
UPDATED = EmailSpec(
    subject="Updated Tickets",
    intro="Grievance tickets you are responsible for were changed by someone else.",
    sections=(
        Section(label=SENSITIVE_LABEL, preset=PRESET_MINE_SENSITIVE),
        Section(label=OTHER_LABEL, preset=PRESET_MINE),
    ),
)


class DailyDigestService:
    """Builds and sends the grievance emails for one business area, timezone and day.

    One email per (recipient, notification type). A user is never notified about a change they made
    themselves, and a ticket assigned to someone today is not also reported to them as updated.
    """

    @staticmethod
    def recipient_timezone_names(business_area: "BusinessArea") -> set[str]:
        assigned_ticket_exists = GrievanceTicket.objects.filter(
            assigned_to_id=OuterRef("pk"),
            business_area_id=business_area.pk,
        )
        created_ticket_exists = GrievanceTicket.objects.filter(
            created_by_id=OuterRef("pk"),
            business_area_id=business_area.pk,
        )
        user_timezones = (
            User.objects.filter(is_active=True, timezone__isnull=False)
            .exclude(email="")
            .exclude(timezone="")
            .filter(Exists(assigned_ticket_exists) | Exists(created_ticket_exists))
            .order_by()
            .values_list("timezone", flat=True)
            .distinct()
        )
        return {
            resolve_timezone_name(business_area=business_area),
            *(str(timezone_name) for timezone_name in user_timezones),
        }

    def __init__(
        self,
        business_area: "BusinessArea",
        digest_date: date,
        timezone_name: str | None = None,
    ) -> None:
        self.business_area = business_area
        self.digest_date = digest_date
        self.timezone_name = timezone_name or resolve_timezone_name(business_area=business_area)
        recipient_timezone = ZoneInfo(self.timezone_name)
        self.start = datetime.combine(digest_date, time.min, tzinfo=recipient_timezone).astimezone(UTC)
        self.end = datetime.combine(
            digest_date + timedelta(days=1),
            time.min,
            tzinfo=recipient_timezone,
        ).astimezone(UTC)

    def send(self, *, skip_user_ids: set[str] | None = None) -> tuple[set[str], int]:
        """Send every email for the day and return successful user IDs and the failure count."""
        successful_user_ids: set[str] = set()
        failed = 0
        if skip_user_ids is None:
            skip_user_ids = set()

        if not config.SEND_GRIEVANCES_NOTIFICATION:
            return successful_user_ids, failed

        # A recipient is only recorded as done once every email of theirs has gone out, so a retry
        # re-sends the whole set rather than silently dropping the one that failed.
        for user, specs in self._emails_by_recipient().items():
            user_id = str(user.pk)
            if user_id in skip_user_ids:
                continue
            user_failed = 0
            for spec, sections in specs:
                try:
                    self._build_email(spec, user, sections).send_email()
                except Exception:
                    logger.exception(
                        f"Failed to send the {self.digest_date.isoformat()} {spec.subject} "
                        f"grievance email to user {user.pk}"
                    )
                    user_failed += 1
            if user_failed:
                failed += user_failed
            else:
                successful_user_ids.add(user_id)
        logger.info(
            f"Grievance emails for {self.business_area.slug} in {self.timezone_name} on "
            f"{self.digest_date.isoformat()}: {len(successful_user_ids)} recipients sent, {failed} failed"
        )
        return successful_user_ids, failed

    def build_emails(self) -> list[tuple[EmailSpec, dict[User, list[tuple[Section, int]]]]]:
        sensitive = {"category": GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE}
        assigned = self._assigned_tickets()
        overdue = self._overdue_tickets()
        updated_sensitive, updated_other = self._updated_counts()
        return [
            (NEEDS_ASSIGNMENT, self._sections(NEEDS_ASSIGNMENT, [self._needs_assignment_counts()])),
            (
                ASSIGNED_SENSITIVE,
                self._sections(ASSIGNED_SENSITIVE, [self._counts_by_assignee(assigned.filter(**sensitive))]),
            ),
            (ASSIGNED, self._sections(ASSIGNED, [self._counts_by_assignee(assigned.exclude(**sensitive))])),
            (
                OVERDUE,
                self._sections(
                    OVERDUE,
                    [
                        self._counts_by_assignee(overdue.filter(**sensitive)),
                        self._counts_by_assignee(overdue.exclude(**sensitive)),
                    ],
                ),
            ),
            (UPDATED, self._sections(UPDATED, [updated_sensitive, updated_other])),
        ]

    @staticmethod
    def _sections(spec: EmailSpec, counts_per_section: list[dict[User, int]]) -> dict[User, list[tuple[Section, int]]]:
        """Pair each section with its count, dropping the ones a recipient has no tickets in."""
        by_recipient: dict[User, list[tuple[Section, int]]] = defaultdict(list)
        for section, counts in zip(spec.sections, counts_per_section, strict=True):
            for user, total in counts.items():
                if total:
                    by_recipient[user].append((section, total))
        return dict(by_recipient)

    def _emails_by_recipient(self) -> dict[User, list[tuple[EmailSpec, list[tuple[Section, int]]]]]:
        by_recipient: dict[User, list[tuple[EmailSpec, list[tuple[Section, int]]]]] = {}
        for spec, per_recipient in self.build_emails():
            for user, sections in per_recipient.items():
                by_recipient.setdefault(user, []).append((spec, sections))
        return by_recipient

    @staticmethod
    def _counts_by_assignee(qs: "QuerySet[GrievanceTicket]") -> dict[User, int]:
        totals = {row["assigned_to"]: row["total"] for row in qs.values("assigned_to").annotate(total=Count("id"))}
        users = User.objects.in_bulk(totals)
        return {users[user_id]: total for user_id, total in totals.items()}

    def _updated_counts(self) -> tuple[dict[User, int], dict[User, int]]:
        """Count updated tickets per recipient, sensitive and other separately.

        Skips a recipient's own edits and tickets newly assigned to them the same day.
        """
        assigned_pairs = set(self._assigned_tickets().values_list("assigned_to_id", "id"))
        counted: set[tuple] = set()
        sensitive_totals: Counter = Counter()
        other_totals: Counter = Counter()

        rows = self._updated_tickets().values_list(
            "id",
            "category",
            "user_modified_by_id",
            "assigned_to_id",
            "assigned_to__is_active",
            "assigned_to__email",
            "assigned_to__timezone",
            "created_by_id",
            "created_by__is_active",
            "created_by__email",
            "created_by__timezone",
        )
        for ticket_id, category, modified_by_id, *candidate_fields in rows:
            totals = sensitive_totals if category == GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE else other_totals
            assignee = candidate_fields[:4]
            creator = candidate_fields[4:]
            for candidate_id, is_active, email, timezone_name in (assignee, creator):
                pair = (candidate_id, ticket_id)
                if candidate_id is None or candidate_id == modified_by_id:
                    continue
                # the queryset only guarantees that *one* of creator/assignee qualifies
                if not is_active or not email or not self._in_timezone_bucket(timezone_name):
                    continue
                if pair in assigned_pairs or pair in counted:
                    continue
                counted.add(pair)
                totals[candidate_id] += 1

        users = User.objects.in_bulk(set(sensitive_totals) | set(other_totals))
        return (
            {user: sensitive_totals[user_id] for user_id, user in users.items() if sensitive_totals[user_id]},
            {user: other_totals[user_id] for user_id, user in users.items() if other_totals[user_id]},
        )

    def _needs_assignment_counts(self) -> dict[User, int]:
        """Count unassigned tickets per user who can assign them, scoped to the programmes they hold.

        A ticket in several of a user's programmes still counts once, hence the id sets.
        """
        ticket_ids = set(self._unassigned_tickets().values_list("id", flat=True))
        if not ticket_ids:
            return {}

        through_model = GrievanceTicket.programs.through
        tickets_by_program: dict[Any, set[Any]] = defaultdict(set)
        for program_id, ticket_id in through_model.objects.filter(grievanceticket_id__in=ticket_ids).values_list(
            "program_id", "grievanceticket_id"
        ):
            tickets_by_program[program_id].add(ticket_id)

        visible: dict[User, set[Any]] = defaultdict(set)
        for program_id, program_ticket_ids in tickets_by_program.items():
            for user in users_with_permissions(
                self.business_area, [Permissions.GRIEVANCE_ASSIGN], programs=[program_id]
            ):
                visible[user].update(program_ticket_ids)

        # a ticket belonging to no programme is visible to anyone who can assign in the business area,
        # matching how the list endpoint scopes them (api/mixins.py:195-204)
        ticket_ids_without_program = ticket_ids.difference(*tickets_by_program.values())
        if ticket_ids_without_program:
            for user in users_with_permissions(self.business_area, [Permissions.GRIEVANCE_ASSIGN]):
                visible[user].update(ticket_ids_without_program)

        return {
            user: len(user_ticket_ids)
            for user, user_ticket_ids in visible.items()
            if self._in_timezone_bucket(user.timezone)
        }

    def _unassigned_tickets(self) -> "QuerySet[GrievanceTicket]":
        return self._for_business_area().filter(assigned_to__isnull=True).exclude(status=GrievanceTicket.STATUS_CLOSED)

    def _in_timezone_bucket(self, timezone_name: str | None) -> bool:
        if timezone_name:
            return str(timezone_name) == self.timezone_name
        return self.timezone_name == resolve_timezone_name(business_area=self.business_area)

    def _assigned_tickets(self) -> "QuerySet[GrievanceTicket]":
        return self._for_business_area().filter(
            self._recipient_timezone_filter("assigned_to"),
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
                self._recipient_timezone_filter("assigned_to"),
                overdue_q(),
                assigned_to__is_active=True,
                assigned_to__email__gt="",
            )
            .exclude(status=GrievanceTicket.STATUS_CLOSED)
        )

    def _updated_tickets(self) -> "QuerySet[GrievanceTicket]":
        return self._for_business_area().filter(
            self._recipient_timezone_filter("assigned_to") | self._recipient_timezone_filter("created_by"),
            Q(assigned_to__is_active=True, assigned_to__email__gt="")
            | Q(created_by__is_active=True, created_by__email__gt=""),
            user_modified__gte=self.start,
            user_modified__lt=self.end,
            # user_modified_by is not set during creation
            user_modified_by__isnull=False,
        )

    def _recipient_timezone_filter(self, field_name: str) -> Q:
        timezone_filter = Q(**{f"{field_name}__timezone": self.timezone_name})
        if self.timezone_name == resolve_timezone_name(business_area=self.business_area):
            timezone_filter |= Q(**{f"{field_name}__timezone__isnull": True}) | Q(**{f"{field_name}__timezone": ""})
        return timezone_filter

    def _for_business_area(self) -> "QuerySet[GrievanceTicket]":
        return GrievanceTicket.objects.filter(
            business_area=self.business_area,
            business_area__enable_email_notification=True,
        )

    def _build_email(self, spec: EmailSpec, user: User, sections: list[tuple[Section, int]]) -> MailjetClient:
        context = {
            "first_name": user.first_name or getattr(user, "username", ""),
            "last_name": user.last_name,
            "title": spec.subject,
            "intro": spec.intro,
            "digest_date": self.digest_date.isoformat(),
            "total_count": sum(total for _, total in sections),
            "sections": [
                {
                    "label": section.label,
                    "ticket_count": total,
                    "tickets_url": my_tasks_url(self.business_area, section.preset, overdue=section.overdue),
                }
                for section, total in sections
            ],
        }
        return MailjetClient(
            subject=f"HOPE {self.business_area.name}: {spec.subject}",
            recipients=[user.email],
            text_body=render_to_string("grievance_summary_notification_email.txt", context=context),
            html_body=render_to_string("grievance_summary_notification_email.html", context=context),
        )
