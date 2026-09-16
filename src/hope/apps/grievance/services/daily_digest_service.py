"""Daily per-business-area grievance emails.

Replaces the per-event assignment and ticket-updated emails, and the per-ticket overdue reminders.
Reads the timestamp/actor fields on the ticket, so there is no event stream to keep. Every email
carries a count and a link to the matching My Tasks preset — never a list of tickets, which also
means a sensitive ticket's id never reaches an inbox.

One run covers one (business area, recipient timezone, day), and mails only the recipients in that
timezone.
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
from django.utils import timezone

from hope.apps.account.permissions import Permissions
from hope.apps.core.timezones import latest_local_schedule_time, resolve_timezone_name
from hope.apps.grievance.constants import PRESET_MINE, PRESET_NEEDS_ASSIGNMENT
from hope.apps.grievance.filters import program_with_status_exists, without_program_q
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.services.notification_schedule import get_grievance_notification_hour
from hope.apps.grievance.utils import my_tasks_url, overdue_q
from hope.apps.utils.mailjet import MailjetClient
from hope.apps.utils.recipients import users_with_permissions, users_with_permissions_by_program
from hope.models import Program, User

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from hope.models import BusinessArea

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Section:
    """One count in an email and the list it links to.

    The count matches the list for NEEDS_ASSIGNMENT and OVERDUE. ASSIGNED and UPDATED count only
    today's tickets but link to the whole list, so their count is smaller than what the page shows.
    """

    label: str
    preset: str
    sensitive: bool
    overdue: bool = False


@dataclass(frozen=True)
class EmailSpec:
    """One notification type. An email carries one section per category the recipient has tickets in."""

    # which notification this is, e.g. "overdue"; once sent it is stored as "<user id>:<key>"
    key: str
    subject: str
    intro: str
    sections: tuple[Section, ...]
    # repeat-limited by GrievanceTicket.last_notification_sent, so a stale backlog does not mail daily
    throttled: bool = False


SENSITIVE_LABEL = "Sensitive"
OTHER_LABEL = "Other"

SENSITIVE_VIEW_PERMISSIONS = [Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE]
OTHER_VIEW_PERMISSIONS = [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE]

NEEDS_ASSIGNMENT = EmailSpec(
    key="needs-assignment",
    # counts every open unassigned ticket, not just today's, so it is sent daily until they are assigned
    subject="Tickets Needing Assignment",
    intro="Grievance tickets are waiting to be assigned.",
    sections=(
        Section(label=SENSITIVE_LABEL, preset=PRESET_NEEDS_ASSIGNMENT, sensitive=True),
        Section(label=OTHER_LABEL, preset=PRESET_NEEDS_ASSIGNMENT, sensitive=False),
    ),
)
ASSIGNED = EmailSpec(
    key="assigned",
    # any assignment made that day, a reassignment of an old ticket included
    subject="Tickets Assigned to You",
    intro="Grievance tickets were assigned to you.",
    sections=(
        Section(label=SENSITIVE_LABEL, preset=PRESET_MINE, sensitive=True),
        Section(label=OTHER_LABEL, preset=PRESET_MINE, sensitive=False),
    ),
)
OVERDUE = EmailSpec(
    key="overdue",
    subject="Overdue Tickets",
    intro="Grievance tickets assigned to you are past their due date.",
    sections=(
        Section(label=SENSITIVE_LABEL, preset=PRESET_MINE, overdue=True, sensitive=True),
        Section(label=OTHER_LABEL, preset=PRESET_MINE, overdue=True, sensitive=False),
    ),
    throttled=True,
)
UPDATED = EmailSpec(
    key="updated",
    subject="Updated Tickets",
    intro="Grievance tickets you are responsible for were changed by someone else.",
    sections=(
        Section(label=SENSITIVE_LABEL, preset=PRESET_MINE, sensitive=True),
        Section(label=OTHER_LABEL, preset=PRESET_MINE, sensitive=False),
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
        # needs-assignment recipients hold a permission rather than a ticket
        assigner_timezones = (
            users_with_permissions(business_area, [Permissions.GRIEVANCE_ASSIGN])
            .exclude(timezone__isnull=True)
            .exclude(timezone="")
            .order_by()
            .values_list("timezone", flat=True)
            .distinct()
        )
        return {
            resolve_timezone_name(business_area=business_area),
            *(str(timezone_name) for timezone_name in user_timezones),
            *(str(timezone_name) for timezone_name in assigner_timezones),
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

    @staticmethod
    def delivery_key(user_id: Any, spec: EmailSpec) -> str:
        return f"{user_id}:{spec.key}"

    def send(self, *, skip_email_keys: set[str] | None = None) -> tuple[set[str], int]:
        """Send every email for the day and return the delivered keys and the failure count.

        Delivery is tracked per (recipient, email), not per recipient: when one of a recipient's four
        emails fails the caller re-runs the day, and only the failed one is sent again.
        """
        sent_email_keys: set[str] = set()
        failed = 0
        if skip_email_keys is None:
            skip_email_keys = set()

        if not config.SEND_GRIEVANCES_NOTIFICATION:
            return sent_email_keys, failed

        for user, specs in self._emails_by_recipient().items():
            for spec, sections in specs:
                email_key = self.delivery_key(user.pk, spec)
                if email_key in skip_email_keys:
                    continue
                try:
                    self._build_email(spec, user, sections).send_email()
                except Exception:
                    logger.exception(
                        f"Failed to send the {self.digest_date.isoformat()} {spec.subject} "
                        f"grievance email to user {user.pk}"
                    )
                    failed += 1
                else:
                    sent_email_keys.add(email_key)
                    if spec.throttled:
                        try:
                            self._stamp_reminder(user, sections)
                        except Exception:
                            logger.exception(
                                f"Failed to stamp the overdue reminder clock for user {user.pk} "
                                f"after the {self.digest_date.isoformat()} email went out"
                            )
        logger.info(
            f"Grievance emails for {self.business_area.slug} in {self.timezone_name} on "
            f"{self.digest_date.isoformat()}: {len(sent_email_keys)} sent, {failed} failed"
        )
        return sent_email_keys, failed

    def _stamp_reminder(self, user: User, sections: list[tuple[Section, int]]) -> None:
        now = timezone.now()
        for section, _ in sections:
            self._overdue_tickets(sensitive=section.sensitive).filter(assigned_to=user).update(
                last_notification_sent=now
            )

    def build_emails(self) -> list[tuple[EmailSpec, dict[User, list[tuple[Section, int]]]]]:
        sensitive = {"category": GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE}
        assigned = self._assigned_tickets()
        updated_sensitive, updated_other = self._updated_counts()
        return [
            (NEEDS_ASSIGNMENT, self._sections(NEEDS_ASSIGNMENT, list(self._needs_assignment_counts()))),
            (
                ASSIGNED,
                self._sections(
                    ASSIGNED,
                    [
                        self._counts_by_assignee(assigned.filter(**sensitive)),
                        self._counts_by_assignee(assigned.exclude(**sensitive)),
                    ],
                ),
            ),
            (
                OVERDUE,
                self._sections(
                    OVERDUE,
                    [self._overdue_counts(sensitive=True), self._overdue_counts(sensitive=False)],
                ),
            ),
            (UPDATED, self._sections(UPDATED, [updated_sensitive, updated_other])),
        ]

    @staticmethod
    def _sections(spec: EmailSpec, counts_per_section: list[dict[User, int]]) -> dict[User, list[tuple[Section, int]]]:
        """Pair each section with its count.

        Every count here is above zero already: they come from `Count()` aggregates, which produce
        no row for an empty group, or from dicts that dropped their zeros when they were built.
        """
        by_recipient: dict[User, list[tuple[Section, int]]] = defaultdict(list)
        for section, counts in zip(spec.sections, counts_per_section, strict=True):
            for user, total in counts.items():
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

    def _needs_assignment_counts(self) -> tuple[dict[User, int], dict[User, int]]:
        """Count unassigned tickets per user who can assign them, sensitive and other separately."""
        category_by_ticket_id = dict(self._unassigned_tickets().values_list("id", "category"))
        if not category_by_ticket_id:
            return {}, {}
        sensitive_ids = {
            ticket_id
            for ticket_id, category in category_by_ticket_id.items()
            if category == GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE
        }
        visible, visible_sensitive = self._unassigned_visibility(set(category_by_ticket_id), sensitive_ids)

        sensitive_counts: dict[User, int] = {}
        other_counts: dict[User, int] = {}
        for user in set(visible) | set(visible_sensitive):
            sensitive_total = len(visible_sensitive.get(user, ()))
            if sensitive_total:
                sensitive_counts[user] = sensitive_total
            other_total = len(visible.get(user, ()))
            if other_total:
                other_counts[user] = other_total
        return sensitive_counts, other_counts

    def _unassigned_visibility(
        self, ticket_ids: set[Any], sensitive_ids: set[Any]
    ) -> tuple[dict[User, set[Any]], dict[User, set[Any]]]:
        """Which of `ticket_ids` each recipient may see, as two sets: other tickets and sensitive.

        A user is given the tickets of each category only in the programmes where they hold that category's grant.
        """
        through_model = GrievanceTicket.programs.through
        tickets_by_program: dict[Any, set[Any]] = defaultdict(set)
        for program_id, ticket_id in through_model.objects.filter(grievanceticket_id__in=ticket_ids).values_list(
            "program_id", "grievanceticket_id"
        ):
            tickets_by_program[program_id].add(ticket_id)

        program_ids = list(tickets_by_program)
        sensitive_viewer_programs = users_with_permissions_by_program(
            self.business_area, SENSITIVE_VIEW_PERMISSIONS, program_ids
        )
        other_viewer_programs = users_with_permissions_by_program(
            self.business_area, OTHER_VIEW_PERMISSIONS, program_ids
        )
        visible: dict[User, set[Any]] = defaultdict(set)
        visible_sensitive: dict[User, set[Any]] = defaultdict(set)
        for user, assigned_program_ids in users_with_permissions_by_program(
            self.business_area, [Permissions.GRIEVANCE_ASSIGN], program_ids
        ).items():
            # a run builds id sets for its own timezone bucket only
            if not self._in_timezone_bucket(user.timezone):
                continue
            may_view_sensitive_in = sensitive_viewer_programs.get(user, set())
            may_view_other_in = other_viewer_programs.get(user, set())
            for program_id in assigned_program_ids:
                program_ticket_ids = tickets_by_program[program_id]
                if program_id in may_view_other_in:
                    visible[user].update(program_ticket_ids - sensitive_ids)
                if program_id in may_view_sensitive_in:
                    visible_sensitive[user].update(program_ticket_ids & sensitive_ids)

        self._add_tickets_without_programme(
            ticket_ids.difference(*tickets_by_program.values()), sensitive_ids, visible, visible_sensitive
        )
        return visible, visible_sensitive

    def _add_tickets_without_programme(
        self,
        ticket_ids: set[Any],
        sensitive_ids: set[Any],
        visible: dict[User, set[Any]],
        visible_sensitive: dict[User, set[Any]],
    ) -> None:
        """Add the tickets that belong to no programme, visible to any assigner in the business area."""
        if not ticket_ids:
            return
        sensitive_viewers = set(users_with_permissions(self.business_area, SENSITIVE_VIEW_PERMISSIONS))
        other_viewers = set(users_with_permissions(self.business_area, OTHER_VIEW_PERMISSIONS))
        for user in users_with_permissions(self.business_area, [Permissions.GRIEVANCE_ASSIGN]):
            if not self._in_timezone_bucket(user.timezone):
                continue
            if user in other_viewers:
                visible[user].update(ticket_ids - sensitive_ids)
            if user in sensitive_viewers:
                visible_sensitive[user].update(ticket_ids & sensitive_ids)

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

    def _overdue_counts(self, *, sensitive: bool) -> dict[User, int]:
        """Count a recipient's overdue tickets, but only mail them when one is due a reminder.

        Counting the whole set keeps the number honest against the page the email links to; gating on
        `last_notification_sent` keeps the existing repeat spacing, so a stale backlog does not mail
        every morning.
        """
        tickets = self._overdue_tickets(sensitive=sensitive)
        due_assignee_ids = set(
            tickets.filter(self._reminder_due_q(sensitive=sensitive)).values_list("assigned_to_id", flat=True)
        )
        return {user: total for user, total in self._counts_by_assignee(tickets).items() if user.pk in due_assignee_ids}

    def _reminder_due_q(self, *, sensitive: bool) -> Q:
        """Tickets whose reminder is due at the recipient's local notification hour."""
        now = timezone.now()
        interval = timedelta(days=self._overdue_threshold(sensitive=sensitive))
        _, notification_time = latest_local_schedule_time(self.timezone_name, now, get_grievance_notification_hour())
        return Q(last_notification_sent__isnull=True, created_at__lte=notification_time - interval) | Q(
            last_notification_sent__lt=notification_time, last_notification_sent__lte=now - interval
        )

    @staticmethod
    def _overdue_threshold(*, sensitive: bool) -> int:
        return int(
            config.GRIEVANCE_OVERDUE_THRESHOLD_SENSITIVE
            if sensitive
            else config.GRIEVANCE_OVERDUE_THRESHOLD_NON_SENSITIVE
        )

    def _overdue_tickets(self, *, sensitive: bool) -> "QuerySet[GrievanceTicket]":
        tickets = (
            self._for_business_area()
            .filter(
                self._recipient_timezone_filter("assigned_to"),
                overdue_q(),
                assigned_to__is_active=True,
                assigned_to__email__gt="",
            )
            .exclude(status=GrievanceTicket.STATUS_CLOSED)
        )
        category = {"category": GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE}
        return tickets.filter(**category) if sensitive else tickets.exclude(**category)

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
        """Tickets the My Tasks list can show - it hides finished programmes, so the counts do too."""
        return GrievanceTicket.objects.filter(
            program_with_status_exists(Program.ACTIVE) | without_program_q(),
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
                    "tickets_url": my_tasks_url(
                        self.business_area,
                        section.preset,
                        overdue=section.overdue,
                        sensitive=section.sensitive,
                    ),
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
