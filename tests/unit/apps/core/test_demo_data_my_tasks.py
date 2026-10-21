from typing import Callable

import pytest

from extras.test_utils.factories import BusinessAreaFactory, ProgramFactory, UserFactory
from hope.apps.account.permissions import Permissions
from hope.apps.core.management.commands.demo_data.my_tasks import generate_my_tasks_demo
from hope.apps.grievance.constants import MY_TASKS_TABS
from hope.apps.grievance.models import GrievanceTicket, MyTasksTracking
from hope.apps.grievance.my_tasks import TAB_SCOPES, annotate_unread
from hope.apps.grievance.services.my_tasks_service import unread_tabs
from hope.models import BusinessArea, Program, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan")


@pytest.fixture
def program(business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=business_area, name="Test Program", status=Program.ACTIVE)


@pytest.fixture
def user(business_area: BusinessArea, program: Program, create_user_role_with_permissions: Callable) -> User:
    user = UserFactory()
    create_user_role_with_permissions(user, list(Permissions), business_area, whole_business_area_access=True)
    return user


@pytest.mark.parametrize("tab", MY_TASKS_TABS)
def test_every_tab_holds_an_unread_and_a_read_ticket(user: User, business_area: BusinessArea, tab: str) -> None:
    generate_my_tasks_demo([user])

    tracking = MyTasksTracking.objects.get(user=user, business_area=business_area)
    tickets = annotate_unread(GrievanceTicket.objects.filter(business_area=business_area), user, tracking.created_at)
    in_tab = tickets.filter(TAB_SCOPES[tab](user, business_area))
    assert set(in_tab.values_list("unread", flat=True)) == {True, False}
    assert unread_tabs(user, business_area, tracking.created_at)[tab] is True


def test_every_label_says_whether_its_ticket_is_unread(user: User, business_area: BusinessArea) -> None:
    generate_my_tasks_demo([user])

    tracking = MyTasksTracking.objects.get(user=user, business_area=business_area)
    tickets = annotate_unread(GrievanceTicket.objects.filter(business_area=business_area), user, tracking.created_at)
    # each label says what the user should see, so a wrong backdate shows up as a mismatch here
    assert set(tickets.filter(unread=True).values_list("description", flat=True)) == {
        "[My Tasks demo] unassigned, created after tracking started - unread",
        "[My Tasks demo] assigned to you by a colleague yesterday - unread",
        "[My Tasks demo] sensitive, assigned to you yesterday - unread",
        "[My Tasks demo] colleague added a note yesterday - unread",
        "[My Tasks demo] colleague edited it yesterday - unread",
        "[My Tasks demo] sent for approval yesterday - unread",
    }
    assert set(tickets.filter(unread=False).values_list("description", flat=True)) == {
        "[My Tasks demo] unassigned, created before tracking started - read",
        "[My Tasks demo] assigned to you before tracking started - read",
        "[My Tasks demo] colleague edited it, you opened it since - read",
        "[My Tasks demo] you edited it yourself yesterday - read",
        "[My Tasks demo] sent for approval before tracking started - read",
    }


def test_running_twice_does_not_duplicate_the_tickets(user: User) -> None:
    generate_my_tasks_demo([user])
    count = GrievanceTicket.objects.count()

    generate_my_tasks_demo([user])

    assert GrievanceTicket.objects.count() == count
