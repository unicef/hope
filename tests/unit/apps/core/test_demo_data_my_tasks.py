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


def test_every_tab_holds_an_unread_and_a_read_ticket(user: User, business_area: BusinessArea) -> None:
    generate_my_tasks_demo([user])

    tracking = MyTasksTracking.objects.get(user=user, business_area=business_area)
    tickets = annotate_unread(GrievanceTicket.objects.filter(business_area=business_area), user, tracking.created_at)
    for tab in MY_TASKS_TABS:
        in_tab = tickets.filter(TAB_SCOPES[tab](user, business_area))
        assert {bool(ticket.unread) for ticket in in_tab} == {True, False}, tab
    # each label says what the user should see, so a wrong backdate shows up as a mismatch here
    for ticket in tickets:
        assert bool(ticket.unread) == ticket.description.endswith("- unread"), ticket.description
    assert unread_tabs(user, business_area, tracking.created_at) == dict.fromkeys(MY_TASKS_TABS, True)


def test_running_twice_does_not_duplicate_the_tickets(user: User) -> None:
    generate_my_tasks_demo([user])
    count = GrievanceTicket.objects.count()

    generate_my_tasks_demo([user])

    assert GrievanceTicket.objects.count() == count
