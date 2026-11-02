"""My Tasks demo: tickets on every tab, some unread and some not, for each user who can see them.

Unread means somebody else changed the ticket after the user last opened it, counted from the day
tracking started. The timestamps are backdated around that day, so every rule has one ticket that
trips it and one that does not.
"""

from datetime import timedelta
from typing import TYPE_CHECKING, Any

from django.utils import timezone

from extras.test_utils.factories import (
    GrievanceTicketFactory,
    TicketComplaintDetailsFactory,
    TicketNoteFactory,
    TicketSeenFactory,
    TicketSensitiveDetailsFactory,
    UserFactory,
)
from hope.apps.grievance.models import GrievanceTicket, MyTasksTracking, TicketNote
from hope.models import Area, BusinessArea, Program

if TYPE_CHECKING:
    from collections.abc import Iterable

    from hope.models import User

_TAG = "[My Tasks demo]"


def _ticket(ctx: dict[str, Any], label: str, sensitive: bool = False, **fields: Any) -> GrievanceTicket:
    category, issue_type, details_factory = (
        (
            GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
            GrievanceTicket.ISSUE_TYPE_DATA_BREACH,
            TicketSensitiveDetailsFactory,
        )
        if sensitive
        else (
            GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
            GrievanceTicket.ISSUE_TYPE_PAYMENT_COMPLAINT,
            TicketComplaintDetailsFactory,
        )
    )
    # auto_now_add would stamp now, so the dates that decide unread are written after the insert
    dates = {key: fields.pop(key) for key in ("created_at", "assigned_at", "user_modified") if key in fields}
    ticket = GrievanceTicketFactory(
        business_area=ctx["ba"],
        admin2=ctx["admin2"],
        category=category,
        issue_type=issue_type,
        consent=True,
        description=f"{_TAG} {label}",
        created_by=ctx["colleague"],
        **fields,
    )
    ticket.programs.set([ctx["program"]])
    details_factory(ticket=ticket)
    GrievanceTicket.objects.filter(pk=ticket.pk).update(created_at=dates.pop("created_at", ctx["old"]), **dates)
    return ticket


def _generate_for_user(ctx: dict[str, Any], user: "User") -> None:
    now, old, recent = ctx["now"], ctx["old"], ctx["recent"]
    colleague = ctx["colleague"]
    tracking, _ = MyTasksTracking.objects.get_or_create(user=user, business_area=ctx["ba"])
    MyTasksTracking.objects.filter(pk=tracking.pk).update(created_at=ctx["tracking_start"])

    # NEEDS ASSIGNMENT
    _ticket(ctx, "unassigned, created after tracking started - unread", created_at=recent)
    _ticket(ctx, "unassigned, created before tracking started - read")

    # ASSIGNED TO ME
    common = {"status": GrievanceTicket.STATUS_ASSIGNED, "assigned_to": user, "assigned_by": colleague}
    _ticket(ctx, "assigned to you by a colleague yesterday - unread", assigned_at=recent, **common)
    _ticket(ctx, "assigned to you before tracking started - read", assigned_at=old, **common)
    _ticket(ctx, "sensitive, assigned to you yesterday - unread", sensitive=True, assigned_at=recent, **common)
    common = {**common, "status": GrievanceTicket.STATUS_IN_PROGRESS, "assigned_at": old}
    noted = _ticket(ctx, "colleague added a note yesterday - unread", **common)
    note = TicketNoteFactory(ticket=noted, created_by=colleague, description="Can you take another look?")
    TicketNote.objects.filter(pk=note.pk).update(created_at=recent)
    _ticket(ctx, "colleague edited it yesterday - unread", user_modified=recent, user_modified_by=colleague, **common)
    opened = _ticket(
        ctx,
        "colleague edited it, you opened it since - read",
        user_modified=recent,
        user_modified_by=colleague,
        **common,
    )
    TicketSeenFactory(user=user, ticket=opened, seen_at=now - timedelta(hours=1))
    _ticket(ctx, "you edited it yourself yesterday - read", user_modified=recent, user_modified_by=user, **common)

    # PENDING APPROVAL
    common = {"status": GrievanceTicket.STATUS_FOR_APPROVAL, "assigned_to": colleague, "assigned_at": old}
    _ticket(ctx, "sent for approval yesterday - unread", user_modified=recent, user_modified_by=colleague, **common)
    _ticket(
        ctx, "sent for approval before tracking started - read", user_modified=old, user_modified_by=colleague, **common
    )


def generate_my_tasks_demo(users: "Iterable[User]") -> None:
    program = Program.objects.get(name="Test Program")
    now = timezone.now()
    ctx = {
        "program": program,
        "ba": BusinessArea.objects.get(slug="afghanistan"),
        "admin2": Area.objects.filter(area_type__area_level=2).first(),
        # the author of every change, since nothing a user does themselves makes a ticket unread
        "colleague": UserFactory(
            username="demo_colleague",
            email="demo.colleague@example.com",
            first_name="Demo",
            last_name="Colleague",
        ),
        "now": now,
        "tracking_start": now - timedelta(days=7),
        "old": now - timedelta(days=14),
        "recent": now - timedelta(days=1),
    }
    for user in users:
        if not GrievanceTicket.objects.filter(description__startswith=_TAG, assigned_to=user).exists():
            _generate_for_user(ctx, user)
