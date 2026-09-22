from typing import Any, Callable

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    GrievanceTicketFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.filters import GrievanceTicketFilter
from hope.apps.grievance.models import GrievanceTicket
from hope.models import BusinessArea, Program, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def sensitive_ticket() -> GrievanceTicket:
    return GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_BREACH,
    )


@pytest.fixture
def complaint_ticket() -> GrievanceTicket:
    return GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
        issue_type=GrievanceTicket.ISSUE_TYPE_FSP_COMPLAINT,
    )


@pytest.fixture
def assignee() -> User:
    return UserFactory()


@pytest.fixture
def assigned_ticket(assignee: User) -> GrievanceTicket:
    return GrievanceTicketFactory(assigned_to=assignee)


@pytest.fixture
def unassigned_ticket() -> GrievanceTicket:
    return GrievanceTicketFactory(assigned_to=None)


def test_sensitive_filter_set_to_true_returns_only_sensitive_tickets(
    sensitive_ticket: GrievanceTicket, complaint_ticket: GrievanceTicket
) -> None:
    result = GrievanceTicketFilter(data={"sensitive": "true"}, queryset=GrievanceTicket.objects.all()).qs

    assert sensitive_ticket in result
    assert complaint_ticket not in result


def test_sensitive_filter_set_to_false_excludes_sensitive_tickets(
    sensitive_ticket: GrievanceTicket, complaint_ticket: GrievanceTicket
) -> None:
    result = GrievanceTicketFilter(data={"sensitive": "false"}, queryset=GrievanceTicket.objects.all()).qs

    assert complaint_ticket in result
    assert sensitive_ticket not in result


def test_omitting_the_sensitive_filter_returns_every_ticket(
    sensitive_ticket: GrievanceTicket, complaint_ticket: GrievanceTicket
) -> None:
    result = GrievanceTicketFilter(data={}, queryset=GrievanceTicket.objects.all()).qs

    assert sensitive_ticket in result
    assert complaint_ticket in result


def test_unassigned_filter_set_to_false_returns_only_assigned_tickets(
    unassigned_ticket: GrievanceTicket, assigned_ticket: GrievanceTicket
) -> None:
    result = GrievanceTicketFilter(data={"unassigned": "false"}, queryset=GrievanceTicket.objects.all()).qs

    assert assigned_ticket in result
    assert unassigned_ticket not in result


def test_sensitive_and_assigned_to_compose_into_the_mine_sensitive_preset(
    assignee: User, sensitive_ticket: GrievanceTicket
) -> None:
    sensitive_ticket.assigned_to = assignee
    sensitive_ticket.save(update_fields=["assigned_to"])
    someone_elses_sensitive = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_BREACH,
    )

    result = GrievanceTicketFilter(
        data={"sensitive": "true", "assigned_to": str(assignee.pk)},
        queryset=GrievanceTicket.objects.all(),
    ).qs

    assert sensitive_ticket in result
    assert someone_elses_sensitive not in result


@pytest.fixture
def my_tasks_business_area() -> BusinessArea:
    return BusinessAreaFactory(slug="my-tasks-area", name="My Tasks Area")


@pytest.fixture
def assignable_program(my_tasks_business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=my_tasks_business_area, status=Program.ACTIVE, name="assignable")


@pytest.fixture
def view_only_program(my_tasks_business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=my_tasks_business_area, status=Program.ACTIVE, name="view only")


@pytest.fixture
def my_tasks_list_url(my_tasks_business_area: BusinessArea) -> str:
    return reverse(
        "api:grievance:grievance-tickets-global-list",
        kwargs={"business_area_slug": my_tasks_business_area.slug},
    )


def test_unassigned_filter_returns_tickets_only_from_programmes_the_user_may_assign_in(
    api_client: Any,
    my_tasks_business_area: BusinessArea,
    assignable_program: Program,
    view_only_program: Program,
    my_tasks_list_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    user = UserFactory()
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCE_ASSIGN, Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        my_tasks_business_area,
        program=assignable_program,
    )
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        my_tasks_business_area,
        program=view_only_program,
    )
    assignable_ticket = GrievanceTicketFactory(business_area=my_tasks_business_area, assigned_to=None)
    assignable_ticket.programs.set([assignable_program])
    view_only_ticket = GrievanceTicketFactory(business_area=my_tasks_business_area, assigned_to=None)
    view_only_ticket.programs.set([view_only_program])

    response = api_client(user).get(my_tasks_list_url, {"unassigned": "true"})

    assert response.status_code == status.HTTP_200_OK
    assert [result["id"] for result in response.data["results"]] == [str(assignable_ticket.id)]


def test_unassigned_filter_returns_nothing_for_a_user_who_may_view_but_not_assign(
    api_client: Any,
    my_tasks_business_area: BusinessArea,
    view_only_program: Program,
    my_tasks_list_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    user = UserFactory()
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        my_tasks_business_area,
        program=view_only_program,
    )
    view_only_ticket = GrievanceTicketFactory(business_area=my_tasks_business_area, assigned_to=None)
    view_only_ticket.programs.set([view_only_program])

    response = api_client(user).get(my_tasks_list_url, {"unassigned": "true"})

    assert response.status_code == status.HTTP_200_OK
    assert response.data["results"] == []


def test_unassigned_filter_excludes_tickets_that_already_have_an_assignee(
    api_client: Any,
    my_tasks_business_area: BusinessArea,
    assignable_program: Program,
    my_tasks_list_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    user = UserFactory()
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCE_ASSIGN, Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        my_tasks_business_area,
        program=assignable_program,
    )
    assigned_ticket = GrievanceTicketFactory(business_area=my_tasks_business_area, assigned_to=user)
    assigned_ticket.programs.set([assignable_program])

    response = api_client(user).get(my_tasks_list_url, {"unassigned": "true"})

    assert response.status_code == status.HTTP_200_OK
    assert response.data["results"] == []
