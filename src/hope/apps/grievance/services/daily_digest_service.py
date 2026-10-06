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
from functools import cached_property
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

    NEEDS_ASSIGNMENT and OVERDUE count what the list behind the link shows: the needs-assignment
    list is scoped to the programmes the recipient may assign in, exactly as this count is.
    ASSIGNED and UPDATED count only today's tickets but link to the whole list, so their count is
    smaller than what the page shows.
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
        notification_time: datetime | None = None,
    ) -> None:
        self.business_area = business_area
        self.digest_date = digest_date
        self.timezone_name = timezone_name or resolve_timezone_name(business_area=business_area)
        # the instant the run was scheduled for, so a job that starts late reports the same tickets
        # it would have reported on time, and a retry repeats rather than moves the cut-off
        self.notification_time = notification_time or self._scheduled_notification_time(self.timezone_name)
        recipient_timezone = ZoneInfo(self.timezone_name)
        self.start = datetime.combine(digest_date, time.min, tzinfo=recipient_timezone).astimezone(UTC)
        self.end = datetime.combine(
            digest_date + timedelta(days=1),
            time.min,
            tzinfo=recipient_timezone,
        ).astimezone(UTC)

    @staticmethod
    def _scheduled_notification_time(timezone_name: str) -> datetime:
        _, notification_time = latest_local_schedule_time(
            timezone_name, timezone.now(), get_grievance_notification_hour()
        )
        return notification_time

    @staticmethod
    def delivery_key(user_id: Any, spec: EmailSpec) -> str:
        return f"{user_id}:{spec.key}"

    def send(self, *, skip_email_keys: set[str] | None = None) -> tuple[set[str], int]:
        """Send every email for the day and return the delivered keys and the failure count.

        Delivery is tracked per (recipient, email), not per recipient: when one of a recipient's four
        emails fails the caller re-runs the day, and only the failed one is sent again. Only failures
        up to handing the email to the mail queue are visible here - MailjetClient.send_email() queues
        a Celery task, which retries a temporary Mailjet failure on its own and drops a rejected
        message without it ever being counted as failed.
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
        # the schedule instant, not "now", so the next run's "one interval later" test is exact
        for section, _ in sections:
            self._overdue_tickets(sensitive=section.sensitive).filter(assigned_to=user).update(
                last_notification_sent=self.notification_time
            )

    def build_emails(self) -> list[tuple[EmailSpec, dict[User, list[tuple[Section, int]]]]]:
        return [
            (NEEDS_ASSIGNMENT, self._sections(NEEDS_ASSIGNMENT, list(self._needs_assignment_counts()))),
            (ASSIGNED, self._sections(ASSIGNED, list(self._assigned_counts()))),
            (OVERDUE, self._sections(OVERDUE, list(self._overdue_counts()))),
            (UPDATED, self._sections(UPDATED, list(self._updated_counts()))),
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

    @cached_property
    def _assigned_rows(self) -> list[tuple[Any, Any, int]]:
        """The day's assignments, read once for both the assigned counts and the updated dedup."""
        return list(self._assigned_tickets().values_list("assigned_to_id", "id", "category").distinct())

    def _assigned_counts(self) -> tuple[dict[User, int], dict[User, int]]:
        sensitive_totals: Counter = Counter()
        other_totals: Counter = Counter()
        for assignee_id, _, category in self._assigned_rows:
            totals = sensitive_totals if category == GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE else other_totals
            totals[assignee_id] += 1
        users = User.objects.in_bulk(set(sensitive_totals) | set(other_totals))
        return (
            {users[user_id]: total for user_id, total in sensitive_totals.items()},
            {users[user_id]: total for user_id, total in other_totals.items()},
        )

    def _updated_counts(self) -> tuple[dict[User, int], dict[User, int]]:
        """Count updated tickets per recipient, sensitive and other separately.

        Skips a recipient's own edits and tickets newly assigned to them the same day.
        """
        assigned_pairs = {(assignee_id, ticket_id) for assignee_id, ticket_id, _ in self._assigned_rows}
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
        """Count unassigned tickets per user who can assign them, sensitive and other separately.

        Counted in the database per distinct scope rather than per user, so a backlog of any size
        costs a handful of aggregates and no ticket ids in memory.
        """
        scopes = self._assigner_scopes()
        counts: dict[tuple[bool, frozenset, bool], int] = {}

        sensitive_counts: dict[User, int] = {}
        other_counts: dict[User, int] = {}
        for user, (sensitive_scope, other_scope) in scopes.items():
            if sensitive_scope and (total := self._unassigned_count(counts, sensitive=True, scope=sensitive_scope)):
                sensitive_counts[user] = total
            if other_scope and (total := self._unassigned_count(counts, sensitive=False, scope=other_scope)):
                other_counts[user] = total
        return sensitive_counts, other_counts

    def _unassigned_count(
        self,
        counts: dict[tuple[bool, frozenset, bool], int],
        *,
        sensitive: bool,
        scope: tuple[frozenset, bool],
    ) -> int:
        """One `COUNT(DISTINCT id)` per distinct scope, reused by every recipient who shares it."""
        program_ids, without_programme = scope
        key = (sensitive, program_ids, without_programme)
        if key not in counts:
            category = Q(category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE)
            counts[key] = self._unassigned_tickets(
                self._scope_q(program_ids, without_programme=without_programme),
                category if sensitive else ~category,
            ).aggregate(total=Count("id", distinct=True))["total"]
        return counts[key]

    @staticmethod
    def _scope_q(program_ids: frozenset, *, without_programme: bool) -> Q:
        """Tickets in one of `program_ids`, plus the ones in no programme when the user may see those."""
        scope = Q(programs__in=program_ids)
        return scope | Q(programs__isnull=True) if without_programme else scope

    def _assigner_scopes(self) -> dict[User, tuple[tuple[frozenset, bool] | None, tuple[frozenset, bool] | None]]:
        """Per assigner in this timezone bucket: (programmes, may see no-programme tickets) per category.

        A user is given a category only where they hold both the assign grant and that category's
        view grant, which is what makes the count match the list the email links to.
        """
        assigners = [user for user in self._assigners() if self._in_timezone_bucket(user.timezone)]
        if not assigners:
            return {}

        program_ids = set(
            Program.objects.filter(business_area=self.business_area, status=Program.ACTIVE).values_list("id", flat=True)
        )
        assignable_by_user = users_with_permissions_by_program(
            self.business_area, [Permissions.GRIEVANCE_ASSIGN], program_ids
        )
        sensitive_by_user = users_with_permissions_by_program(
            self.business_area, SENSITIVE_VIEW_PERMISSIONS, program_ids
        )
        other_by_user = users_with_permissions_by_program(self.business_area, OTHER_VIEW_PERMISSIONS, program_ids)
        # a ticket in no programme is visible to anyone holding the view grant anywhere in the business
        # area, programme-scoped roles included, which is what the list endpoint does too
        sensitive_viewers = set(users_with_permissions(self.business_area, SENSITIVE_VIEW_PERMISSIONS))
        other_viewers = set(users_with_permissions(self.business_area, OTHER_VIEW_PERMISSIONS))

        scopes = {}
        for user in assigners:
            assignable = assignable_by_user.get(user, set())
            sensitive_scope = (frozenset(assignable & sensitive_by_user.get(user, set())), user in sensitive_viewers)
            other_scope = (frozenset(assignable & other_by_user.get(user, set())), user in other_viewers)
            scopes[user] = (
                sensitive_scope if any(sensitive_scope) else None,
                other_scope if any(other_scope) else None,
            )
        return scopes

    def _assigners(self) -> "QuerySet[User]":
        return users_with_permissions(self.business_area, [Permissions.GRIEVANCE_ASSIGN])

    def _unassigned_tickets(self, *extra: Q) -> "QuerySet[GrievanceTicket]":
        return (
            self._for_business_area(*extra)
            .filter(assigned_to__isnull=True)
            .exclude(status=GrievanceTicket.STATUS_CLOSED)
        )

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

    def _overdue_counts(self) -> tuple[dict[User, int], dict[User, int]]:
        """Count a recipient's overdue tickets, but only mail them when one is due a reminder.

        Counting the whole set keeps the number honest against the page the email links to; gating on
        `last_notification_sent` keeps the existing repeat spacing, so a stale backlog does not mail
        every morning. Both categories come from one grouped scan.
        """
        is_sensitive = Q(category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE)
        rows = list(
            self._overdue_tickets()
            .values("assigned_to")
            .annotate(
                sensitive_total=Count("id", filter=is_sensitive, distinct=True),
                sensitive_due=Count("id", filter=is_sensitive & self._reminder_due_q(sensitive=True), distinct=True),
                other_total=Count("id", filter=~is_sensitive, distinct=True),
                other_due=Count("id", filter=~is_sensitive & self._reminder_due_q(sensitive=False), distinct=True),
            )
        )
        users = User.objects.in_bulk([row["assigned_to"] for row in rows])
        return (
            {users[row["assigned_to"]]: row["sensitive_total"] for row in rows if row["sensitive_due"]},
            {users[row["assigned_to"]]: row["other_total"] for row in rows if row["other_due"]},
        )

    def _reminder_due_q(self, *, sensitive: bool) -> Q:
        """Tickets whose reminder is due at the recipient's local notification hour."""
        interval = timedelta(days=self._overdue_threshold(sensitive=sensitive))
        # stamps are schedule instants, 24h ± 1h apart across a DST change; the half-day slack keeps
        # "interval days later" true on those days and still rejects a same-day re-run
        return Q(last_notification_sent__isnull=True, created_at__lte=self.notification_time - interval) | Q(
            last_notification_sent__lt=self.notification_time,
            last_notification_sent__lte=self.notification_time - interval + timedelta(hours=12),
        )

    @staticmethod
    def _overdue_threshold(*, sensitive: bool) -> int:
        return int(
            config.GRIEVANCE_OVERDUE_THRESHOLD_SENSITIVE
            if sensitive
            else config.GRIEVANCE_OVERDUE_THRESHOLD_NON_SENSITIVE
        )

    def _overdue_tickets(self, *, sensitive: bool | None = None) -> "QuerySet[GrievanceTicket]":
        tickets = (
            self._for_business_area()
            .filter(
                self._recipient_timezone_filter("assigned_to"),
                overdue_q(now=self.notification_time),
                assigned_to__is_active=True,
                assigned_to__email__gt="",
            )
            .exclude(status=GrievanceTicket.STATUS_CLOSED)
        )
        if sensitive is None:
            return tickets
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

    def _for_business_area(self, *extra: Q) -> "QuerySet[GrievanceTicket]":
        """Tickets the My Tasks list can show - it hides finished programmes, so the counts do too."""
        return GrievanceTicket.objects.filter(
            Q(programs__status=Program.ACTIVE) | Q(programs__isnull=True),
            *extra,
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
