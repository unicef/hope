from datetime import UTC, datetime, timedelta
from typing import Callable
from unittest.mock import patch

from constance.test import override_config
from freezegun import freeze_time
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    GrievanceTicketFactory,
    MyTasksTrackingFactory,
    ProgramFactory,
    TicketNoteFactory,
    TicketSeenFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.celery_tasks import (
    my_tasks_notification_async_task,
    my_tasks_notification_async_task_action,
)
from hope.apps.grievance.constants import (
    PRESET_MINE,
    PRESET_NEEDS_ASSIGNMENT,
    PRESET_PENDING_APPROVAL,
)
from hope.apps.grievance.models import GrievanceTicket, MyTasksTracking, TicketSeen
from hope.apps.grievance.services import my_tasks_service
from hope.apps.grievance.services.my_tasks_service import (
    MyTasksNotificationService,
    mark_seen,
    mark_tab_seen,
    unread_tabs,
)
from hope.models import BusinessArea, PeriodicAsyncJob, Program, User

pytestmark = pytest.mark.django_db

TRACKING_START = datetime(2026, 10, 10, 9, 0, tzinfo=UTC)
BEFORE_START = datetime(2026, 10, 9, 15, 0, tzinfo=UTC)
AFTER_START = datetime(2026, 10, 10, 15, 0, tzinfo=UTC)
NEXT_MORNING = datetime(2026, 10, 11, 6, 0, tzinfo=UTC)


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan", enable_email_notification=True)


@pytest.fixture
def program(business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=business_area, status=Program.ACTIVE, name="program afghanistan")


@pytest.fixture
def hidden_program(business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=business_area, status=Program.ACTIVE, name="hidden programme")


@pytest.fixture
def colleague() -> User:
    return UserFactory(first_name="Col", last_name="League", email="colleague@example.com")


@pytest.fixture
def assignee(business_area: BusinessArea, program: Program, create_user_role_with_permissions: Callable) -> User:
    user = UserFactory(first_name="As", last_name="Signee", email="assignee@example.com")
    create_user_role_with_permissions(
        user, [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE], business_area, program=program
    )
    return user


@pytest.fixture
def assigner(business_area: BusinessArea, program: Program, create_user_role_with_permissions: Callable) -> User:
    user = UserFactory(first_name="As", last_name="Signer", email="assigner@example.com")
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCE_ASSIGN, Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        business_area,
        program=program,
    )
    return user


@pytest.fixture
def approver(business_area: BusinessArea, program: Program, create_user_role_with_permissions: Callable) -> User:
    user = UserFactory(first_name="Ap", last_name="Prover", email="approver@example.com")
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_APPROVE_DATA_CHANGE, Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        business_area,
        program=program,
    )
    return user


@pytest.fixture
def assigner_without_view_grant(
    business_area: BusinessArea, program: Program, create_user_role_with_permissions: Callable
) -> User:
    user = UserFactory(first_name="No", last_name="View", email="no-view@example.com")
    create_user_role_with_permissions(user, [Permissions.GRIEVANCE_ASSIGN], business_area, program=program)
    return user


@pytest.fixture
def assignee_tracking(assignee: User, business_area: BusinessArea) -> MyTasksTracking:
    with freeze_time(TRACKING_START):
        return MyTasksTrackingFactory(user=assignee, business_area=business_area)


@pytest.fixture
def assigner_tracking(assigner: User, business_area: BusinessArea) -> MyTasksTracking:
    with freeze_time(TRACKING_START):
        return MyTasksTrackingFactory(user=assigner, business_area=business_area)


@pytest.fixture
def ticket_assigned_after_start(
    business_area: BusinessArea, program: Program, assignee: User, colleague: User
) -> GrievanceTicket:
    with freeze_time(BEFORE_START):
        ticket = GrievanceTicketFactory(
            business_area=business_area,
            assigned_to=assignee,
            assigned_at=AFTER_START,
            assigned_by=colleague,
            status=GrievanceTicket.STATUS_ASSIGNED,
        )
    ticket.programs.set([program])
    return ticket


@pytest.fixture
def ticket_self_assigned_after_start(business_area: BusinessArea, program: Program, assignee: User) -> GrievanceTicket:
    with freeze_time(BEFORE_START):
        ticket = GrievanceTicketFactory(
            business_area=business_area,
            assigned_to=assignee,
            assigned_at=AFTER_START,
            assigned_by=assignee,
            status=GrievanceTicket.STATUS_ASSIGNED,
        )
    ticket.programs.set([program])
    return ticket


@pytest.fixture
def ticket_assigned_before_start(
    business_area: BusinessArea, program: Program, assignee: User, colleague: User
) -> GrievanceTicket:
    with freeze_time(BEFORE_START):
        ticket = GrievanceTicketFactory(
            business_area=business_area,
            assigned_to=assignee,
            assigned_at=BEFORE_START,
            assigned_by=colleague,
            status=GrievanceTicket.STATUS_ASSIGNED,
        )
    ticket.programs.set([program])
    return ticket


@pytest.fixture
def ticket_edited_after_start(
    business_area: BusinessArea, program: Program, assignee: User, colleague: User
) -> GrievanceTicket:
    with freeze_time(BEFORE_START):
        ticket = GrievanceTicketFactory(
            business_area=business_area,
            assigned_to=assignee,
            assigned_at=BEFORE_START,
            assigned_by=colleague,
            user_modified=AFTER_START,
            user_modified_by=colleague,
            status=GrievanceTicket.STATUS_IN_PROGRESS,
        )
    ticket.programs.set([program])
    return ticket


@pytest.fixture
def ticket_edited_by_assignee_after_start(
    business_area: BusinessArea, program: Program, assignee: User, colleague: User
) -> GrievanceTicket:
    with freeze_time(BEFORE_START):
        ticket = GrievanceTicketFactory(
            business_area=business_area,
            assigned_to=assignee,
            assigned_at=BEFORE_START,
            assigned_by=colleague,
            user_modified=AFTER_START,
            user_modified_by=assignee,
            status=GrievanceTicket.STATUS_IN_PROGRESS,
        )
    ticket.programs.set([program])
    return ticket


@pytest.fixture
def ticket_closed_after_start(
    business_area: BusinessArea, program: Program, assignee: User, colleague: User
) -> GrievanceTicket:
    with freeze_time(BEFORE_START):
        ticket = GrievanceTicketFactory(
            business_area=business_area,
            assigned_to=assignee,
            assigned_at=BEFORE_START,
            assigned_by=colleague,
            user_modified=AFTER_START,
            user_modified_by=colleague,
            status=GrievanceTicket.STATUS_CLOSED,
        )
    ticket.programs.set([program])
    return ticket


@pytest.fixture
def ticket_with_note_after_start(
    business_area: BusinessArea, program: Program, assignee: User, colleague: User
) -> GrievanceTicket:
    with freeze_time(BEFORE_START):
        ticket = GrievanceTicketFactory(
            business_area=business_area,
            assigned_to=assignee,
            assigned_at=BEFORE_START,
            assigned_by=colleague,
            status=GrievanceTicket.STATUS_IN_PROGRESS,
        )
    ticket.programs.set([program])
    with freeze_time(AFTER_START):
        TicketNoteFactory(ticket=ticket, created_by=colleague)
    return ticket


@pytest.fixture
def ticket_with_own_note_after_start(
    business_area: BusinessArea, program: Program, assignee: User, colleague: User
) -> GrievanceTicket:
    with freeze_time(BEFORE_START):
        ticket = GrievanceTicketFactory(
            business_area=business_area,
            assigned_to=assignee,
            assigned_at=BEFORE_START,
            assigned_by=colleague,
            status=GrievanceTicket.STATUS_IN_PROGRESS,
        )
    ticket.programs.set([program])
    with freeze_time(AFTER_START):
        TicketNoteFactory(ticket=ticket, created_by=assignee)
    return ticket


@pytest.fixture
def unassigned_ticket_created_after_start(
    business_area: BusinessArea, program: Program, colleague: User
) -> GrievanceTicket:
    with freeze_time(AFTER_START):
        ticket = GrievanceTicketFactory(business_area=business_area, assigned_to=None, created_by=colleague)
    ticket.programs.set([program])
    return ticket


@pytest.fixture
def unassigned_ticket_in_hidden_program(
    business_area: BusinessArea, hidden_program: Program, colleague: User
) -> GrievanceTicket:
    with freeze_time(AFTER_START):
        ticket = GrievanceTicketFactory(business_area=business_area, assigned_to=None, created_by=colleague)
    ticket.programs.set([hidden_program])
    return ticket


@pytest.fixture
def ticket_sent_for_approval_after_start(
    business_area: BusinessArea, program: Program, colleague: User
) -> GrievanceTicket:
    with freeze_time(BEFORE_START):
        ticket = GrievanceTicketFactory(
            business_area=business_area,
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
            assigned_to=colleague,
            user_modified=AFTER_START,
            user_modified_by=colleague,
        )
    ticket.programs.set([program])
    return ticket


@pytest.fixture
def assignee_opened_the_ticket_after_the_assignment(
    assignee: User, ticket_assigned_after_start: GrievanceTicket
) -> TicketSeen:
    return TicketSeenFactory(
        user=assignee, ticket=ticket_assigned_after_start, seen_at=datetime(2026, 10, 10, 16, 0, tzinfo=UTC)
    )


@pytest.fixture
def assignee_opened_the_ticket_before_the_assignment(
    assignee: User, ticket_assigned_after_start: GrievanceTicket
) -> TicketSeen:
    return TicketSeenFactory(
        user=assignee, ticket=ticket_assigned_after_start, seen_at=datetime(2026, 10, 10, 12, 0, tzinfo=UTC)
    )


# --- which tabs hold unread tickets ---


def test_ticket_assigned_by_someone_else_after_tracking_started_makes_the_mine_tab_unread(
    assignee: User, business_area: BusinessArea, ticket_assigned_after_start: GrievanceTicket
) -> None:
    tabs = unread_tabs(assignee, business_area, TRACKING_START)

    assert tabs == {PRESET_NEEDS_ASSIGNMENT: False, PRESET_MINE: True, PRESET_PENDING_APPROVAL: False}


def test_self_assignment_after_tracking_started_is_not_unread(
    assignee: User, business_area: BusinessArea, ticket_self_assigned_after_start: GrievanceTicket
) -> None:
    tabs = unread_tabs(assignee, business_area, TRACKING_START)

    assert tabs[PRESET_MINE] is False


def test_assignment_before_tracking_started_is_not_unread(
    assignee: User, business_area: BusinessArea, ticket_assigned_before_start: GrievanceTicket
) -> None:
    tabs = unread_tabs(assignee, business_area, TRACKING_START)

    assert tabs[PRESET_MINE] is False


def test_edit_by_someone_else_after_tracking_started_makes_the_mine_tab_unread(
    assignee: User, business_area: BusinessArea, ticket_edited_after_start: GrievanceTicket
) -> None:
    tabs = unread_tabs(assignee, business_area, TRACKING_START)

    assert tabs[PRESET_MINE] is True


def test_own_edit_after_tracking_started_is_not_unread(
    assignee: User, business_area: BusinessArea, ticket_edited_by_assignee_after_start: GrievanceTicket
) -> None:
    tabs = unread_tabs(assignee, business_area, TRACKING_START)

    assert tabs[PRESET_MINE] is False


def test_closed_ticket_is_not_unread(
    assignee: User, business_area: BusinessArea, ticket_closed_after_start: GrievanceTicket
) -> None:
    tabs = unread_tabs(assignee, business_area, TRACKING_START)

    assert tabs[PRESET_MINE] is False


def test_note_by_someone_else_after_tracking_started_makes_the_mine_tab_unread(
    assignee: User, business_area: BusinessArea, ticket_with_note_after_start: GrievanceTicket
) -> None:
    tabs = unread_tabs(assignee, business_area, TRACKING_START)

    assert tabs[PRESET_MINE] is True


def test_own_note_after_tracking_started_is_not_unread(
    assignee: User, business_area: BusinessArea, ticket_with_own_note_after_start: GrievanceTicket
) -> None:
    tabs = unread_tabs(assignee, business_area, TRACKING_START)

    assert tabs[PRESET_MINE] is False


def test_unassigned_ticket_created_after_tracking_started_makes_needs_assignment_unread_for_an_assigner(
    assigner: User, business_area: BusinessArea, unassigned_ticket_created_after_start: GrievanceTicket
) -> None:
    tabs = unread_tabs(assigner, business_area, TRACKING_START)

    assert tabs == {PRESET_NEEDS_ASSIGNMENT: True, PRESET_MINE: False, PRESET_PENDING_APPROVAL: False}


def test_unassigned_ticket_is_not_unread_for_a_user_who_cannot_assign(
    assignee: User, business_area: BusinessArea, unassigned_ticket_created_after_start: GrievanceTicket
) -> None:
    tabs = unread_tabs(assignee, business_area, TRACKING_START)

    assert tabs[PRESET_NEEDS_ASSIGNMENT] is False


def test_ticket_in_a_programme_the_user_cannot_view_is_not_unread(
    assigner: User, business_area: BusinessArea, unassigned_ticket_in_hidden_program: GrievanceTicket
) -> None:
    tabs = unread_tabs(assigner, business_area, TRACKING_START)

    assert tabs[PRESET_NEEDS_ASSIGNMENT] is False


def test_ticket_sent_for_approval_after_tracking_started_makes_pending_approval_unread_for_an_approver(
    approver: User, business_area: BusinessArea, ticket_sent_for_approval_after_start: GrievanceTicket
) -> None:
    tabs = unread_tabs(approver, business_area, TRACKING_START)

    assert tabs == {PRESET_NEEDS_ASSIGNMENT: False, PRESET_MINE: False, PRESET_PENDING_APPROVAL: True}


def test_ticket_sent_for_approval_is_not_unread_for_a_user_who_cannot_approve(
    assignee: User, business_area: BusinessArea, ticket_sent_for_approval_after_start: GrievanceTicket
) -> None:
    tabs = unread_tabs(assignee, business_area, TRACKING_START)

    assert tabs[PRESET_PENDING_APPROVAL] is False


def test_a_ticket_opened_after_the_change_is_read(
    assignee: User, business_area: BusinessArea, assignee_opened_the_ticket_after_the_assignment: TicketSeen
) -> None:
    tabs = unread_tabs(assignee, business_area, TRACKING_START)

    assert tabs[PRESET_MINE] is False


def test_a_ticket_opened_before_the_change_is_unread_again(
    assignee: User, business_area: BusinessArea, assignee_opened_the_ticket_before_the_assignment: TicketSeen
) -> None:
    tabs = unread_tabs(assignee, business_area, TRACKING_START)

    assert tabs[PRESET_MINE] is True


# --- opening a ticket ---


@freeze_time(NEXT_MORNING)
def test_opening_a_ticket_stamps_when_the_user_saw_it(
    assignee: User, ticket_assigned_after_start: GrievanceTicket
) -> None:
    mark_seen(assignee, ticket_assigned_after_start)

    assert TicketSeen.objects.get(user=assignee, ticket=ticket_assigned_after_start).seen_at == NEXT_MORNING


@freeze_time(NEXT_MORNING)
def test_opening_a_ticket_again_moves_the_stamp(
    assignee: User,
    ticket_assigned_after_start: GrievanceTicket,
    assignee_opened_the_ticket_before_the_assignment: TicketSeen,
) -> None:
    assert assignee_opened_the_ticket_before_the_assignment.seen_at == datetime(2026, 10, 10, 12, 0, tzinfo=UTC)
    assert TicketSeen.objects.filter(user=assignee).count() == 1

    mark_seen(assignee, ticket_assigned_after_start)

    assignee_opened_the_ticket_before_the_assignment.refresh_from_db()
    assert assignee_opened_the_ticket_before_the_assignment.seen_at == NEXT_MORNING
    assert TicketSeen.objects.filter(user=assignee).count() == 1


@freeze_time(NEXT_MORNING)
def test_opening_a_ticket_ends_the_email_cycle(
    assignee_tracking: MyTasksTracking, ticket_assigned_after_start: GrievanceTicket
) -> None:
    assignee_tracking.first_email_at = TRACKING_START
    assignee_tracking.last_reminder_at = AFTER_START
    assignee_tracking.save(update_fields=["first_email_at", "last_reminder_at"])

    mark_seen(assignee_tracking.user, ticket_assigned_after_start)

    assignee_tracking.refresh_from_db()
    assert (assignee_tracking.first_email_at, assignee_tracking.last_reminder_at) == (None, None)


@freeze_time(NEXT_MORNING)
@pytest.mark.usefixtures("ticket_assigned_after_start")
def test_opening_another_ticket_keeps_the_email_cycle_while_one_stays_unread(
    assignee_tracking: MyTasksTracking, ticket_assigned_before_start: GrievanceTicket
) -> None:
    assignee_tracking.first_email_at = TRACKING_START
    assignee_tracking.last_reminder_at = AFTER_START
    assignee_tracking.save(update_fields=["first_email_at", "last_reminder_at"])

    mark_seen(assignee_tracking.user, ticket_assigned_before_start)

    assignee_tracking.refresh_from_db()
    assert (assignee_tracking.first_email_at, assignee_tracking.last_reminder_at) == (TRACKING_START, AFTER_START)


# --- marking a tab as read ---


@freeze_time(NEXT_MORNING)
def test_marking_the_tab_as_read_stamps_its_unread_tickets(
    assignee_tracking: MyTasksTracking, ticket_assigned_after_start: GrievanceTicket
) -> None:
    assert unread_tabs(assignee_tracking.user, assignee_tracking.business_area, TRACKING_START)[PRESET_MINE] is True
    assert TicketSeen.objects.filter(user=assignee_tracking.user).exists() is False

    tabs = mark_tab_seen(assignee_tracking.user, assignee_tracking.business_area, PRESET_MINE)

    seen = TicketSeen.objects.get(user=assignee_tracking.user, ticket=ticket_assigned_after_start)
    assert tabs == {PRESET_NEEDS_ASSIGNMENT: False, PRESET_MINE: False, PRESET_PENDING_APPROVAL: False}
    assert seen.seen_at == NEXT_MORNING


@freeze_time(NEXT_MORNING)
def test_marking_the_tab_as_read_leaves_the_other_tabs_unread(
    assigner_tracking: MyTasksTracking, unassigned_ticket_created_after_start: GrievanceTicket
) -> None:
    tabs = mark_tab_seen(assigner_tracking.user, assigner_tracking.business_area, PRESET_MINE)

    assert tabs == {PRESET_NEEDS_ASSIGNMENT: True, PRESET_MINE: False, PRESET_PENDING_APPROVAL: False}
    assert TicketSeen.objects.filter(user=assigner_tracking.user).exists() is False


@freeze_time(NEXT_MORNING)
def test_marking_the_tab_as_read_ends_the_email_cycle(assignee_tracking: MyTasksTracking) -> None:
    assignee_tracking.first_email_at = TRACKING_START
    assignee_tracking.last_reminder_at = AFTER_START
    assignee_tracking.save(update_fields=["first_email_at", "last_reminder_at"])

    mark_tab_seen(assignee_tracking.user, assignee_tracking.business_area, PRESET_MINE)

    assignee_tracking.refresh_from_db()
    assert (assignee_tracking.first_email_at, assignee_tracking.last_reminder_at) == (None, None)


@freeze_time(NEXT_MORNING)
@pytest.mark.usefixtures("unassigned_ticket_created_after_start")
def test_marking_a_tab_as_read_keeps_the_email_cycle_while_another_tab_is_unread(
    assigner_tracking: MyTasksTracking,
) -> None:
    assigner_tracking.first_email_at = TRACKING_START
    assigner_tracking.last_reminder_at = AFTER_START
    assigner_tracking.save(update_fields=["first_email_at", "last_reminder_at"])

    mark_tab_seen(assigner_tracking.user, assigner_tracking.business_area, PRESET_MINE)

    assigner_tracking.refresh_from_db()
    assert (assigner_tracking.first_email_at, assigner_tracking.last_reminder_at) == (TRACKING_START, AFTER_START)


@freeze_time(NEXT_MORNING)
def test_marking_the_tab_as_read_starts_tracking_for_a_new_user(assignee: User, business_area: BusinessArea) -> None:
    tabs = mark_tab_seen(assignee, business_area, PRESET_MINE)

    assert tabs == {PRESET_NEEDS_ASSIGNMENT: False, PRESET_MINE: False, PRESET_PENDING_APPROVAL: False}
    assert MyTasksTracking.objects.get(user=assignee, business_area=business_area).created_at == NEXT_MORNING


# --- the daily email ---


@override_config(SEND_GRIEVANCES_NOTIFICATION=True)
@freeze_time(NEXT_MORNING)
def test_first_check_only_starts_tracking_the_user(
    business_area: BusinessArea, assignee: User, ticket_assigned_after_start: GrievanceTicket
) -> None:
    with patch.object(my_tasks_service.MailjetClient, "send_email"):
        sent, _ = MyTasksNotificationService(business_area, "UTC", NEXT_MORNING).send()

    assert sent == 0
    assert MyTasksTracking.objects.get(user=assignee, business_area=business_area).first_email_at is None


@override_config(SEND_GRIEVANCES_NOTIFICATION=True)
def test_an_unread_ticket_sends_the_new_tasks_email(
    business_area: BusinessArea, assignee_tracking: MyTasksTracking, ticket_assigned_after_start: GrievanceTicket
) -> None:
    with patch.object(my_tasks_service.MailjetClient, "send_email") as mock_send:
        sent, failed = MyTasksNotificationService(business_area, "UTC", NEXT_MORNING).send()

    assignee_tracking.refresh_from_db()
    assert (sent, failed) == (1, 0)
    assert mock_send.call_count == 1
    assert assignee_tracking.first_email_at == NEXT_MORNING


@override_config(SEND_GRIEVANCES_NOTIFICATION=True)
def test_the_email_names_the_business_area_and_links_the_unread_tab(
    business_area: BusinessArea, assignee_tracking: MyTasksTracking, ticket_assigned_after_start: GrievanceTicket
) -> None:
    with patch.object(my_tasks_service, "MailjetClient") as mock_client:
        MyTasksNotificationService(business_area, "UTC", NEXT_MORNING).send()

    kwargs = mock_client.call_args.kwargs
    assert kwargs["subject"] == "[Afghanistan] HOPE: you have new tasks"
    assert kwargs["recipients"] == ["assignee@example.com"]
    assert "Assigned to you - " in kwargs["text_body"]
    assert "afghanistan/programs/all/grievance/my-tasks?tab=mine" in kwargs["text_body"]
    assert "Needs assignment" not in kwargs["text_body"]


@override_config(SEND_GRIEVANCES_NOTIFICATION=True)
def test_nothing_unread_sends_nothing(
    business_area: BusinessArea, assignee_tracking: MyTasksTracking, ticket_assigned_before_start: GrievanceTicket
) -> None:
    with patch.object(my_tasks_service.MailjetClient, "send_email"):
        sent, _ = MyTasksNotificationService(business_area, "UTC", NEXT_MORNING).send()

    assert sent == 0


@override_config(SEND_GRIEVANCES_NOTIFICATION=True)
@pytest.mark.usefixtures("assigner_without_view_grant", "unassigned_ticket_created_after_start")
def test_a_user_without_a_view_list_grant_is_not_emailed(business_area: BusinessArea) -> None:
    with patch.object(my_tasks_service.MailjetClient, "send_email") as mock_send:
        sent, _ = MyTasksNotificationService(business_area, "UTC", NEXT_MORNING).send()

    assert sent == 0
    mock_send.assert_not_called()


@override_config(SEND_GRIEVANCES_NOTIFICATION=True)
def test_the_cycle_ends_when_the_unread_ticket_is_closed_by_someone_else(
    business_area: BusinessArea, assignee_tracking: MyTasksTracking, ticket_assigned_after_start: GrievanceTicket
) -> None:
    assignee_tracking.first_email_at = NEXT_MORNING
    assignee_tracking.last_reminder_at = NEXT_MORNING + timedelta(days=7)
    assignee_tracking.save(update_fields=["first_email_at", "last_reminder_at"])
    # closed by a colleague, so it left the Mine tab without the assignee ever opening it
    ticket_assigned_after_start.status = GrievanceTicket.STATUS_CLOSED
    ticket_assigned_after_start.save(update_fields=["status"])

    with patch.object(my_tasks_service.MailjetClient, "send_email") as mock_send:
        sent, _ = MyTasksNotificationService(business_area, "UTC", NEXT_MORNING + timedelta(days=9)).send()

    assignee_tracking.refresh_from_db()
    assert sent == 0
    mock_send.assert_not_called()
    assert (assignee_tracking.first_email_at, assignee_tracking.last_reminder_at) == (None, None)


@override_config(SEND_GRIEVANCES_NOTIFICATION=True, MY_TASKS_ALARM_WINDOW=7)
def test_a_reminder_is_not_sent_once_the_ticket_was_opened(
    business_area: BusinessArea,
    assignee_tracking: MyTasksTracking,
    ticket_assigned_after_start: GrievanceTicket,
    assignee_opened_the_ticket_after_the_assignment: TicketSeen,
) -> None:
    assignee_tracking.first_email_at = NEXT_MORNING
    assignee_tracking.save(update_fields=["first_email_at"])

    with patch.object(my_tasks_service.MailjetClient, "send_email"):
        sent, _ = MyTasksNotificationService(business_area, "UTC", NEXT_MORNING + timedelta(days=7)).send()

    assert sent == 0


@override_config(SEND_GRIEVANCES_NOTIFICATION=True, MY_TASKS_ALARM_WINDOW=7)
def test_nothing_more_is_sent_before_the_alarm_window(
    business_area: BusinessArea, assignee_tracking: MyTasksTracking, ticket_assigned_after_start: GrievanceTicket
) -> None:
    assignee_tracking.first_email_at = NEXT_MORNING
    assignee_tracking.save(update_fields=["first_email_at"])

    with patch.object(my_tasks_service.MailjetClient, "send_email"):
        sent, _ = MyTasksNotificationService(business_area, "UTC", NEXT_MORNING + timedelta(days=6)).send()

    assert sent == 0


@override_config(SEND_GRIEVANCES_NOTIFICATION=True, MY_TASKS_ALARM_WINDOW=7)
def test_the_alarm_window_sends_a_reminder(
    business_area: BusinessArea, assignee_tracking: MyTasksTracking, ticket_assigned_after_start: GrievanceTicket
) -> None:
    assignee_tracking.first_email_at = NEXT_MORNING
    assignee_tracking.save(update_fields=["first_email_at"])
    alarm_time = NEXT_MORNING + timedelta(days=7)

    with patch.object(my_tasks_service.MailjetClient, "send_email"):
        sent, _ = MyTasksNotificationService(business_area, "UTC", alarm_time).send()

    assignee_tracking.refresh_from_db()
    assert sent == 1
    assert assignee_tracking.last_reminder_at == alarm_time
    assert assignee_tracking.first_email_at == NEXT_MORNING


@override_config(SEND_GRIEVANCES_NOTIFICATION=True, MY_TASKS_ALARM_WINDOW=7)
@pytest.mark.usefixtures("ticket_assigned_after_start")
def test_the_reminder_has_its_own_subject(business_area: BusinessArea, assignee_tracking: MyTasksTracking) -> None:
    assignee_tracking.first_email_at = NEXT_MORNING
    assignee_tracking.save(update_fields=["first_email_at"])

    with patch.object(my_tasks_service, "MailjetClient") as mock_client:
        MyTasksNotificationService(business_area, "UTC", NEXT_MORNING + timedelta(days=7)).send()

    kwargs = mock_client.call_args.kwargs
    assert kwargs["subject"] == "[Afghanistan] HOPE reminder: you have new tasks"
    assert "Reminder: Tickets on your My Tasks page" in kwargs["text_body"]


@override_config(SEND_GRIEVANCES_NOTIFICATION=True, MY_TASKS_ALARM_WINDOW=7, MY_TASKS_REPEAT_EACH=2)
def test_nothing_more_is_sent_before_repeat_each(
    business_area: BusinessArea, assignee_tracking: MyTasksTracking, ticket_assigned_after_start: GrievanceTicket
) -> None:
    assignee_tracking.first_email_at = NEXT_MORNING
    assignee_tracking.last_reminder_at = NEXT_MORNING + timedelta(days=7)
    assignee_tracking.save(update_fields=["first_email_at", "last_reminder_at"])

    with patch.object(my_tasks_service.MailjetClient, "send_email"):
        sent, _ = MyTasksNotificationService(business_area, "UTC", NEXT_MORNING + timedelta(days=8)).send()

    assert sent == 0


@override_config(SEND_GRIEVANCES_NOTIFICATION=True, MY_TASKS_ALARM_WINDOW=7, MY_TASKS_REPEAT_EACH=2)
def test_repeat_each_sends_the_next_reminder(
    business_area: BusinessArea, assignee_tracking: MyTasksTracking, ticket_assigned_after_start: GrievanceTicket
) -> None:
    assignee_tracking.first_email_at = NEXT_MORNING
    assignee_tracking.last_reminder_at = NEXT_MORNING + timedelta(days=7)
    assignee_tracking.save(update_fields=["first_email_at", "last_reminder_at"])
    repeat_time = assignee_tracking.last_reminder_at + timedelta(days=2)

    with patch.object(my_tasks_service.MailjetClient, "send_email"):
        sent, _ = MyTasksNotificationService(business_area, "UTC", repeat_time).send()

    assignee_tracking.refresh_from_db()
    assert sent == 1
    assert assignee_tracking.last_reminder_at == repeat_time


@override_config(SEND_GRIEVANCES_NOTIFICATION=False)
def test_nothing_is_sent_when_the_global_flag_is_off(
    business_area: BusinessArea, assignee_tracking: MyTasksTracking, ticket_assigned_after_start: GrievanceTicket
) -> None:
    with patch.object(my_tasks_service.MailjetClient, "send_email") as mock_send:
        sent, _ = MyTasksNotificationService(business_area, "UTC", NEXT_MORNING).send()

    assert sent == 0
    mock_send.assert_not_called()


@override_config(SEND_GRIEVANCES_NOTIFICATION=True)
def test_nothing_is_sent_for_a_business_area_without_email_notification(
    business_area: BusinessArea, assignee_tracking: MyTasksTracking, ticket_assigned_after_start: GrievanceTicket
) -> None:
    business_area.enable_email_notification = False
    business_area.save(update_fields=["enable_email_notification"])

    with patch.object(my_tasks_service.MailjetClient, "send_email"):
        sent, _ = MyTasksNotificationService(business_area, "UTC", NEXT_MORNING).send()

    assert sent == 0


@override_config(SEND_GRIEVANCES_NOTIFICATION=True)
def test_a_recipient_in_another_timezone_waits_for_their_own_run(
    business_area: BusinessArea, assignee_tracking: MyTasksTracking, ticket_assigned_after_start: GrievanceTicket
) -> None:
    assignee_tracking.user.timezone = "Europe/Warsaw"
    assignee_tracking.user.save(update_fields=["timezone"])

    with patch.object(my_tasks_service.MailjetClient, "send_email"):
        utc_sent, _ = MyTasksNotificationService(business_area, "UTC", NEXT_MORNING).send()
    with patch.object(my_tasks_service.MailjetClient, "send_email"):
        warsaw_sent, _ = MyTasksNotificationService(business_area, "Europe/Warsaw", NEXT_MORNING).send()

    assert (utc_sent, warsaw_sent) == (0, 1)


def test_recipient_timezone_names_cover_the_business_area_and_every_recipient(
    business_area: BusinessArea, assignee: User, assigner: User
) -> None:
    assigner.timezone = "Europe/Warsaw"
    assigner.save(update_fields=["timezone"])

    assert MyTasksNotificationService.recipient_timezone_names(business_area) == {"UTC", "Europe/Warsaw"}


@override_config(SEND_GRIEVANCES_NOTIFICATION=True)
def test_a_failing_recipient_does_not_stop_the_others(
    business_area: BusinessArea,
    assignee_tracking: MyTasksTracking,
    ticket_assigned_after_start: GrievanceTicket,
    assigner_tracking: MyTasksTracking,
    unassigned_ticket_created_after_start: GrievanceTicket,
) -> None:
    with patch.object(my_tasks_service.MailjetClient, "send_email", side_effect=[Exception("boom"), None]):
        sent, failed = MyTasksNotificationService(business_area, "UTC", NEXT_MORNING).send()

    assert (sent, failed) == (1, 1)


# --- the celery task ---


@pytest.fixture
def job_config(business_area: BusinessArea) -> dict[str, str]:
    return {
        "business_area_id": str(business_area.id),
        "timezone_name": "UTC",
        "delivery_key": f"{business_area.id}:UTC:2026-10-11",
        "notification_time": NEXT_MORNING.isoformat(),
    }


@pytest.fixture
def job(job_config: dict[str, str]) -> PeriodicAsyncJob:
    return PeriodicAsyncJob.objects.create(
        type=PeriodicAsyncJob.JobType.JOB_TASK,
        job_name="my_tasks_notification_async_task",
        action="hope.apps.grievance.celery_tasks.my_tasks_notification_async_task_action",
        config=job_config,
    )


@override_config(SEND_GRIEVANCES_NOTIFICATION=True)
@freeze_time(NEXT_MORNING + timedelta(minutes=30))
def test_the_dispatcher_queues_one_job_per_business_area_and_timezone(
    business_area: BusinessArea, assignee: User
) -> None:
    with patch.object(PeriodicAsyncJob, "queue_task") as mock_queue:
        my_tasks_notification_async_task()

    assert mock_queue.call_count == 1
    config = mock_queue.call_args.kwargs["config"]
    assert config["timezone_name"] == "UTC"
    assert config["notification_time"] == NEXT_MORNING.isoformat()
    assert config["delivery_key"] == f"{business_area.id}:UTC:2026-10-11"


@override_config(SEND_GRIEVANCES_NOTIFICATION=True)
@freeze_time(NEXT_MORNING + timedelta(hours=3))
def test_the_dispatcher_does_not_queue_the_same_morning_twice(job: PeriodicAsyncJob, assignee: User) -> None:
    with patch.object(PeriodicAsyncJob, "queue_task") as mock_queue:
        my_tasks_notification_async_task()

    mock_queue.assert_not_called()


@override_config(SEND_GRIEVANCES_NOTIFICATION=True, MY_TASKS_MONITOR_WINDOW=2)
@freeze_time(NEXT_MORNING + timedelta(days=1, minutes=30))
def test_the_dispatcher_waits_out_the_monitor_window(job: PeriodicAsyncJob, assignee: User) -> None:
    with patch.object(PeriodicAsyncJob, "queue_task") as mock_queue:
        my_tasks_notification_async_task()

    mock_queue.assert_not_called()


@override_config(SEND_GRIEVANCES_NOTIFICATION=True, MY_TASKS_MONITOR_WINDOW=2)
@freeze_time(NEXT_MORNING + timedelta(days=2, minutes=30))
def test_the_dispatcher_queues_again_once_the_monitor_window_passed(
    job: PeriodicAsyncJob, business_area: BusinessArea, assignee: User
) -> None:
    with patch.object(PeriodicAsyncJob, "queue_task") as mock_queue:
        my_tasks_notification_async_task()

    assert mock_queue.call_count == 1
    assert mock_queue.call_args.kwargs["config"]["delivery_key"] == f"{business_area.id}:UTC:2026-10-13"


@override_config(SEND_GRIEVANCES_NOTIFICATION=False)
def test_the_dispatcher_queues_nothing_when_the_flag_is_off(business_area: BusinessArea, assignee: User) -> None:
    with patch.object(PeriodicAsyncJob, "queue_task") as mock_queue:
        my_tasks_notification_async_task()

    mock_queue.assert_not_called()


@override_config(SEND_GRIEVANCES_NOTIFICATION=True)
def test_the_job_sends_the_emails_and_completes(
    job: PeriodicAsyncJob, assignee_tracking: MyTasksTracking, ticket_assigned_after_start: GrievanceTicket
) -> None:
    with patch.object(my_tasks_service.MailjetClient, "send_email") as mock_send:
        my_tasks_notification_async_task_action(job)

    job.refresh_from_db()
    assert mock_send.call_count == 1
    assert job.config["completed"] is True


@override_config(SEND_GRIEVANCES_NOTIFICATION=True)
def test_a_completed_job_does_nothing_when_run_again(
    job: PeriodicAsyncJob, assignee_tracking: MyTasksTracking, ticket_assigned_after_start: GrievanceTicket
) -> None:
    job.config["completed"] = True
    job.save(update_fields=["config"])

    with patch.object(my_tasks_service.MailjetClient, "send_email") as mock_send:
        my_tasks_notification_async_task_action(job)

    mock_send.assert_not_called()


@override_config(SEND_GRIEVANCES_NOTIFICATION=True)
def test_a_failed_recipient_fails_the_job_so_it_is_retried(
    job: PeriodicAsyncJob, assignee_tracking: MyTasksTracking, ticket_assigned_after_start: GrievanceTicket
) -> None:
    with (
        patch.object(my_tasks_service.MailjetClient, "send_email", side_effect=Exception("boom")),
        pytest.raises(RuntimeError, match="1 My Tasks email"),
    ):
        my_tasks_notification_async_task_action(job)

    job.refresh_from_db()
    assert "completed" not in job.config


def test_the_job_skips_a_business_area_that_is_gone(job: PeriodicAsyncJob) -> None:
    job.config["business_area_id"] = "11111111-1111-1111-1111-111111111111"
    job.save(update_fields=["config"])

    with patch.object(my_tasks_service.MailjetClient, "send_email") as mock_send:
        my_tasks_notification_async_task_action(job)

    mock_send.assert_not_called()
