from datetime import UTC, datetime
from typing import Any, Callable

from freezegun import freeze_time
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    GrievanceTicketFactory,
    MyTasksTrackingFactory,
    ProgramFactory,
    TicketSeenFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.constants import PRESET_MINE, PRESET_PENDING_APPROVAL
from hope.apps.grievance.models import GrievanceTicket, MyTasksTracking, TicketSeen
from hope.models import BusinessArea, Program, User

pytestmark = pytest.mark.django_db

TRACKING_START = datetime(2026, 10, 9, 15, 0, tzinfo=UTC)
ASSIGNED_AT = datetime(2026, 10, 10, 15, 0, tzinfo=UTC)
NEXT_DAY = datetime(2026, 10, 11, 9, 0, tzinfo=UTC)


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan")


@pytest.fixture
def program(business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=business_area, status=Program.ACTIVE, name="program afghanistan")


@pytest.fixture
def colleague() -> User:
    return UserFactory(email="colleague@example.com")


@pytest.fixture
def user(business_area: BusinessArea, program: Program, create_user_role_with_permissions: Callable) -> User:
    user = UserFactory(email="user@example.com")
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE, Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE],
        business_area,
        program=program,
    )
    return user


@pytest.fixture
def approver(business_area: BusinessArea, program: Program, create_user_role_with_permissions: Callable) -> User:
    user = UserFactory(email="approver@example.com")
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_APPROVE_DATA_CHANGE, Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        business_area,
        program=program,
    )
    return user


@pytest.fixture
def user_without_permissions() -> User:
    return UserFactory(email="nobody@example.com")


@pytest.fixture
def visit_url(business_area: BusinessArea) -> str:
    return reverse(
        "api:grievance:grievance-tickets-global-my-tasks-visit",
        kwargs={"business_area_slug": business_area.slug},
    )


@pytest.fixture
def mark_read_url(business_area: BusinessArea) -> str:
    return reverse(
        "api:grievance:grievance-tickets-global-my-tasks-mark-read",
        kwargs={"business_area_slug": business_area.slug},
    )


@pytest.fixture
def list_url(business_area: BusinessArea) -> str:
    return reverse(
        "api:grievance:grievance-tickets-global-list",
        kwargs={"business_area_slug": business_area.slug},
    )


@pytest.fixture
def count_url(business_area: BusinessArea) -> str:
    return reverse(
        "api:grievance:grievance-tickets-global-count",
        kwargs={"business_area_slug": business_area.slug},
    )


@pytest.fixture
def program_list_url(business_area: BusinessArea, program: Program) -> str:
    return reverse(
        "api:grievance:grievance-tickets-list",
        kwargs={"business_area_slug": business_area.slug, "program_code": program.code},
    )


@pytest.fixture
def tracking(user: User, business_area: BusinessArea) -> MyTasksTracking:
    with freeze_time(TRACKING_START):
        return MyTasksTrackingFactory(user=user, business_area=business_area)


@pytest.fixture
def ticket_assigned_after_start(
    business_area: BusinessArea, program: Program, user: User, colleague: User
) -> GrievanceTicket:
    with freeze_time(TRACKING_START):
        ticket = GrievanceTicketFactory(
            business_area=business_area,
            assigned_to=user,
            assigned_at=ASSIGNED_AT,
            assigned_by=colleague,
            status=GrievanceTicket.STATUS_ASSIGNED,
        )
    ticket.programs.set([program])
    return ticket


@pytest.fixture
def ticket_assigned_before_start(
    business_area: BusinessArea, program: Program, user: User, colleague: User
) -> GrievanceTicket:
    with freeze_time(TRACKING_START):
        ticket = GrievanceTicketFactory(
            business_area=business_area,
            assigned_to=user,
            assigned_at=datetime(2026, 10, 8, 15, 0, tzinfo=UTC),
            assigned_by=colleague,
            status=GrievanceTicket.STATUS_ASSIGNED,
        )
    ticket.programs.set([program])
    return ticket


@pytest.fixture
def ticket_assigned_without_a_timestamp(
    business_area: BusinessArea, program: Program, user: User, colleague: User
) -> GrievanceTicket:
    with freeze_time(TRACKING_START):
        ticket = GrievanceTicketFactory(
            business_area=business_area,
            assigned_to=user,
            assigned_at=None,
            assigned_by=colleague,
            status=GrievanceTicket.STATUS_ASSIGNED,
        )
    ticket.programs.set([program])
    return ticket


@pytest.fixture
def detail_url(business_area: BusinessArea, ticket_assigned_after_start: GrievanceTicket) -> str:
    return reverse(
        "api:grievance:grievance-tickets-global-detail",
        kwargs={"business_area_slug": business_area.slug, "pk": str(ticket_assigned_after_start.id)},
    )


@pytest.fixture
def ticket_opened_after_the_assignment(user: User, ticket_assigned_after_start: GrievanceTicket) -> TicketSeen:
    return TicketSeenFactory(
        user=user, ticket=ticket_assigned_after_start, seen_at=datetime(2026, 10, 10, 16, 0, tzinfo=UTC)
    )


@pytest.fixture
def ticket_opened_before_the_assignment(user: User, ticket_assigned_after_start: GrievanceTicket) -> TicketSeen:
    return TicketSeenFactory(
        user=user, ticket=ticket_assigned_after_start, seen_at=datetime(2026, 10, 10, 12, 0, tzinfo=UTC)
    )


@pytest.fixture
def ticket_for_approval(business_area: BusinessArea, program: Program, colleague: User) -> GrievanceTicket:
    with freeze_time(TRACKING_START):
        ticket = GrievanceTicketFactory(
            business_area=business_area,
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
            assigned_to=colleague,
        )
    ticket.programs.set([program])
    return ticket


@pytest.fixture
def ticket_in_progress(business_area: BusinessArea, program: Program, colleague: User) -> GrievanceTicket:
    with freeze_time(TRACKING_START):
        ticket = GrievanceTicketFactory(
            business_area=business_area,
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            status=GrievanceTicket.STATUS_IN_PROGRESS,
            assigned_to=colleague,
        )
    ticket.programs.set([program])
    return ticket


# --- the visit: start tracking and report the unread tabs ---


@freeze_time(NEXT_DAY)
def test_the_first_visit_starts_tracking_and_reports_nothing_unread(
    api_client: Any,
    user: User,
    business_area: BusinessArea,
    visit_url: str,
    ticket_assigned_after_start: GrievanceTicket,
) -> None:
    response = api_client(user).post(visit_url)

    tracking = MyTasksTracking.objects.get(user=user, business_area=business_area)
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"unread_tabs": []}
    assert tracking.created_at == NEXT_DAY


def test_a_visit_reports_the_tabs_holding_unread_tickets(
    api_client: Any, user: User, visit_url: str, tracking: MyTasksTracking, ticket_assigned_after_start: GrievanceTicket
) -> None:
    response = api_client(user).post(visit_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"unread_tabs": [PRESET_MINE]}


def test_a_visit_after_the_ticket_was_opened_reports_nothing_unread(
    api_client: Any,
    user: User,
    visit_url: str,
    tracking: MyTasksTracking,
    ticket_assigned_after_start: GrievanceTicket,
    ticket_opened_after_the_assignment: TicketSeen,
) -> None:
    response = api_client(user).post(visit_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"unread_tabs": []}


def test_a_visit_does_not_restart_tracking(
    api_client: Any, user: User, visit_url: str, tracking: MyTasksTracking
) -> None:
    api_client(user).post(visit_url)

    tracking.refresh_from_db()
    assert tracking.created_at == TRACKING_START


def test_a_user_without_a_grievance_grant_cannot_visit(
    api_client: Any, user_without_permissions: User, visit_url: str
) -> None:
    response = api_client(user_without_permissions).post(visit_url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


# --- mark all as read ---


@freeze_time(NEXT_DAY)
def test_mark_read_stamps_the_unread_tickets_of_the_tab(
    api_client: Any,
    user: User,
    mark_read_url: str,
    tracking: MyTasksTracking,
    ticket_assigned_after_start: GrievanceTicket,
    ticket_assigned_before_start: GrievanceTicket,
) -> None:
    response = api_client(user).post(mark_read_url, {"tab": PRESET_MINE})

    stamped = list(TicketSeen.objects.filter(user=user).values_list("ticket_id", "seen_at"))
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"unread_tabs": []}
    assert stamped == [(ticket_assigned_after_start.id, NEXT_DAY)]


def test_mark_read_on_another_tab_leaves_the_unread_tab_flagged(
    api_client: Any,
    user: User,
    mark_read_url: str,
    tracking: MyTasksTracking,
    ticket_assigned_after_start: GrievanceTicket,
) -> None:
    response = api_client(user).post(mark_read_url, {"tab": PRESET_PENDING_APPROVAL})

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"unread_tabs": [PRESET_MINE]}


def test_mark_read_without_a_tab_is_rejected(api_client: Any, user: User, mark_read_url: str) -> None:
    response = api_client(user).post(mark_read_url, {})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "tab" in response.data


def test_a_user_without_a_grievance_grant_cannot_mark_read(
    api_client: Any, user_without_permissions: User, mark_read_url: str
) -> None:
    response = api_client(user_without_permissions).post(mark_read_url, {"tab": PRESET_MINE})

    assert response.status_code == status.HTTP_403_FORBIDDEN


# --- opening a ticket marks it seen ---


@freeze_time(NEXT_DAY)
def test_opening_the_ticket_detail_marks_it_seen(
    api_client: Any, user: User, detail_url: str, ticket_assigned_after_start: GrievanceTicket
) -> None:
    response = api_client(user).get(detail_url)

    seen = TicketSeen.objects.get(user=user, ticket=ticket_assigned_after_start)
    assert response.status_code == status.HTTP_200_OK
    assert seen.seen_at == NEXT_DAY


@freeze_time(NEXT_DAY)
def test_opening_the_ticket_detail_again_moves_the_seen_stamp(
    api_client: Any, user: User, detail_url: str, ticket_opened_before_the_assignment: TicketSeen
) -> None:
    api_client(user).get(detail_url)

    ticket_opened_before_the_assignment.refresh_from_db()
    assert ticket_opened_before_the_assignment.seen_at == NEXT_DAY


@freeze_time(NEXT_DAY)
def test_opening_the_ticket_detail_ends_the_email_cycle(
    api_client: Any, user: User, detail_url: str, tracking: MyTasksTracking
) -> None:
    tracking.first_email_at = TRACKING_START
    tracking.last_reminder_at = ASSIGNED_AT
    tracking.save(update_fields=["first_email_at", "last_reminder_at"])

    api_client(user).get(detail_url)

    tracking.refresh_from_db()
    assert (tracking.first_email_at, tracking.last_reminder_at) == (None, None)


# --- the list: unread rows and the unread filter ---


def test_the_tab_list_flags_the_unread_rows(
    api_client: Any,
    user: User,
    list_url: str,
    tracking: MyTasksTracking,
    ticket_assigned_after_start: GrievanceTicket,
    ticket_assigned_before_start: GrievanceTicket,
) -> None:
    response = api_client(user).get(list_url, {"my_tasks_tab": PRESET_MINE})

    flags = {result["id"]: result["unread"] for result in response.data["results"]}
    assert response.status_code == status.HTTP_200_OK
    assert flags == {str(ticket_assigned_after_start.id): True, str(ticket_assigned_before_start.id): False}


def test_the_program_list_flags_the_unread_rows(
    api_client: Any,
    user: User,
    program_list_url: str,
    tracking: MyTasksTracking,
    ticket_assigned_after_start: GrievanceTicket,
    ticket_assigned_before_start: GrievanceTicket,
) -> None:
    response = api_client(user).get(program_list_url, {"my_tasks_tab": PRESET_MINE})

    flags = {result["id"]: result["unread"] for result in response.data["results"]}
    assert response.status_code == status.HTTP_200_OK
    assert flags == {str(ticket_assigned_after_start.id): True, str(ticket_assigned_before_start.id): False}


def test_an_opened_ticket_is_no_longer_flagged(
    api_client: Any,
    user: User,
    list_url: str,
    tracking: MyTasksTracking,
    ticket_assigned_after_start: GrievanceTicket,
    ticket_opened_after_the_assignment: TicketSeen,
) -> None:
    response = api_client(user).get(list_url, {"my_tasks_tab": PRESET_MINE})

    assert response.status_code == status.HTTP_200_OK
    assert [result["unread"] for result in response.data["results"]] == [False]


def test_a_ticket_changed_after_it_was_opened_is_flagged_again(
    api_client: Any,
    user: User,
    list_url: str,
    tracking: MyTasksTracking,
    ticket_assigned_after_start: GrievanceTicket,
    ticket_opened_before_the_assignment: TicketSeen,
) -> None:
    response = api_client(user).get(list_url, {"my_tasks_tab": PRESET_MINE})

    assert response.status_code == status.HTTP_200_OK
    assert [result["unread"] for result in response.data["results"]] == [True]


def test_the_list_flags_nothing_before_the_first_visit(
    api_client: Any, user: User, list_url: str, ticket_assigned_after_start: GrievanceTicket
) -> None:
    response = api_client(user).get(list_url, {"my_tasks_tab": PRESET_MINE})

    assert response.status_code == status.HTTP_200_OK
    assert [result["unread"] for result in response.data["results"]] == [False]


def test_the_list_flags_nothing_without_a_tab(
    api_client: Any, user: User, list_url: str, tracking: MyTasksTracking, ticket_assigned_after_start: GrievanceTicket
) -> None:
    response = api_client(user).get(list_url, {"assigned_to": str(user.id)})

    assert response.status_code == status.HTTP_200_OK
    assert [result["unread"] for result in response.data["results"]] == [False]


def test_the_unread_filter_keeps_only_the_flagged_rows(
    api_client: Any,
    user: User,
    list_url: str,
    tracking: MyTasksTracking,
    ticket_assigned_after_start: GrievanceTicket,
    ticket_assigned_before_start: GrievanceTicket,
) -> None:
    response = api_client(user).get(list_url, {"my_tasks_tab": PRESET_MINE, "unread": "true"})

    assert response.status_code == status.HTTP_200_OK
    assert [result["id"] for result in response.data["results"]] == [str(ticket_assigned_after_start.id)]


def test_the_unread_filter_set_to_false_drops_the_flagged_rows(
    api_client: Any,
    user: User,
    list_url: str,
    tracking: MyTasksTracking,
    ticket_assigned_after_start: GrievanceTicket,
    ticket_assigned_before_start: GrievanceTicket,
) -> None:
    response = api_client(user).get(list_url, {"my_tasks_tab": PRESET_MINE, "unread": "false"})

    assert response.status_code == status.HTTP_200_OK
    assert [result["id"] for result in response.data["results"]] == [str(ticket_assigned_before_start.id)]


def test_the_unread_filter_set_to_false_keeps_a_ticket_assigned_without_a_timestamp(
    api_client: Any,
    user: User,
    list_url: str,
    tracking: MyTasksTracking,
    ticket_assigned_without_a_timestamp: GrievanceTicket,
) -> None:
    response = api_client(user).get(list_url, {"my_tasks_tab": PRESET_MINE, "unread": "false"})

    assert response.status_code == status.HTTP_200_OK
    assert [(result["id"], result["unread"]) for result in response.data["results"]] == [
        (str(ticket_assigned_without_a_timestamp.id), False)
    ]


def test_the_unread_filter_returns_nothing_before_the_first_visit(
    api_client: Any, user: User, list_url: str, ticket_assigned_after_start: GrievanceTicket
) -> None:
    response = api_client(user).get(list_url, {"my_tasks_tab": PRESET_MINE, "unread": "true"})

    assert response.status_code == status.HTTP_200_OK
    assert response.data["results"] == []


def test_the_count_follows_the_unread_filter(
    api_client: Any,
    user: User,
    count_url: str,
    tracking: MyTasksTracking,
    ticket_assigned_after_start: GrievanceTicket,
    ticket_assigned_before_start: GrievanceTicket,
) -> None:
    response = api_client(user).get(count_url, {"my_tasks_tab": PRESET_MINE, "unread": "true"})

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"count": 1}


# --- the tab scopes ---


def test_the_pending_approval_tab_lists_tickets_the_user_may_approve(
    api_client: Any,
    approver: User,
    list_url: str,
    ticket_for_approval: GrievanceTicket,
    ticket_in_progress: GrievanceTicket,
) -> None:
    response = api_client(approver).get(list_url, {"my_tasks_tab": PRESET_PENDING_APPROVAL})

    assert response.status_code == status.HTTP_200_OK
    assert [result["id"] for result in response.data["results"]] == [str(ticket_for_approval.id)]


def test_the_pending_approval_tab_is_empty_for_a_user_who_cannot_approve(
    api_client: Any, user: User, list_url: str, ticket_for_approval: GrievanceTicket
) -> None:
    response = api_client(user).get(list_url, {"my_tasks_tab": PRESET_PENDING_APPROVAL})

    assert response.status_code == status.HTTP_200_OK
    assert response.data["results"] == []


def test_the_mine_tab_lists_only_the_tickets_assigned_to_the_user(
    api_client: Any,
    user: User,
    list_url: str,
    ticket_assigned_before_start: GrievanceTicket,
    ticket_in_progress: GrievanceTicket,
) -> None:
    response = api_client(user).get(list_url, {"my_tasks_tab": PRESET_MINE})

    assert response.status_code == status.HTTP_200_OK
    assert [result["id"] for result in response.data["results"]] == [str(ticket_assigned_before_start.id)]


def test_an_unknown_tab_is_rejected(api_client: Any, user: User, list_url: str) -> None:
    response = api_client(user).get(list_url, {"my_tasks_tab": "everything"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
