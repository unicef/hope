"""`GrievanceTicketGlobalViewSet.get_count_queryset` (`src/hope/apps/grievance/api/views.py`)
no longer ends in `.distinct()`. Dropping it is only safe while nothing upstream of the
count can multiply a ticket into several rows, and the two things that historically did
were the `programs` m2m and the office-search joins.

These cases pin that: every one of them puts a ticket on **two** programs — the shape that
inflated `/count` before A2/A3 — and asserts the endpoint still reports it once.
"""

from typing import Any, Callable

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.grievance import (
    GrievanceTicketFactory,
    TicketNeedsAdjudicationDetailsFactory,
)
from extras.test_utils.factories.household import HouseholdFactory, IndividualFactory
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.models import GrievanceTicket
from hope.models import BusinessArea, Individual, Partner, Program, User

pytestmark = pytest.mark.django_db()

LIST_PERMISSIONS = [
    Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
    Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
]


@pytest.fixture
def afghanistan() -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan", code="AFG")


@pytest.fixture
def partner() -> Partner:
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def user(partner: Partner) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def first_program(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(business_area=afghanistan, status=Program.ACTIVE, name="first program")


@pytest.fixture
def second_program(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(business_area=afghanistan, status=Program.ACTIVE, name="second program")


@pytest.fixture
def two_program_ticket(afghanistan: BusinessArea, first_program: Program, second_program: Program) -> GrievanceTicket:
    ticket = GrievanceTicketFactory(business_area=afghanistan)
    ticket.programs.set([first_program, second_program])
    return ticket


@pytest.fixture
def two_duplicates_on_the_ticket(
    afghanistan: BusinessArea, first_program: Program, two_program_ticket: GrievanceTicket
) -> list[Individual]:
    """A needs-adjudication ticket whose office-search join fans out to two individuals.

    `filter_by_individual_for_office_search` walks `possible_duplicates`, a many-to-many, so
    a term matching both duplicates yields two rows per ticket before deduplication.
    """
    household = HouseholdFactory(business_area=afghanistan, program=first_program)
    duplicates = [
        IndividualFactory(household=household, full_name=f"Adjudication Namesake {index}") for index in range(2)
    ]
    details = TicketNeedsAdjudicationDetailsFactory(ticket=two_program_ticket)
    details.possible_duplicates.set(duplicates)
    return duplicates


@pytest.fixture
def count_url(afghanistan: BusinessArea) -> str:
    return reverse(
        "api:grievance:grievance-tickets-global-count",
        kwargs={"business_area_slug": afghanistan.slug},
    )


@pytest.fixture
def list_url(afghanistan: BusinessArea) -> str:
    return reverse(
        "api:grievance:grievance-tickets-global-list",
        kwargs={"business_area_slug": afghanistan.slug},
    )


def test_count_reports_a_ticket_on_two_programs_once(
    afghanistan: BusinessArea,
    user: User,
    api_client: Any,
    create_user_role_with_permissions: Callable,
    two_program_ticket: GrievanceTicket,
    count_url: str,
) -> None:
    create_user_role_with_permissions(user, LIST_PERMISSIONS, afghanistan, whole_business_area_access=True)

    response = api_client(user).get(count_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["count"] == 1


def test_count_matches_the_number_of_listed_tickets_for_a_ticket_on_two_programs(
    afghanistan: BusinessArea,
    user: User,
    api_client: Any,
    create_user_role_with_permissions: Callable,
    two_program_ticket: GrievanceTicket,
    count_url: str,
    list_url: str,
) -> None:
    create_user_role_with_permissions(user, LIST_PERMISSIONS, afghanistan, whole_business_area_access=True)
    client = api_client(user)

    count_response = client.get(count_url)
    list_response = client.get(list_url)

    assert count_response.status_code == status.HTTP_200_OK
    assert list_response.status_code == status.HTTP_200_OK
    assert count_response.json()["count"] == len(list_response.data["results"]) == 1


def test_count_reports_a_ticket_on_two_programs_once_when_filtered_by_program(
    afghanistan: BusinessArea,
    user: User,
    api_client: Any,
    create_user_role_with_permissions: Callable,
    first_program: Program,
    two_program_ticket: GrievanceTicket,
    count_url: str,
) -> None:
    create_user_role_with_permissions(user, LIST_PERMISSIONS, afghanistan, whole_business_area_access=True)

    response = api_client(user).get(count_url, {"program": first_program.code})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["count"] == 1


def test_count_reports_a_ticket_on_two_active_programs_once_when_filtered_to_active_programs(
    afghanistan: BusinessArea,
    user: User,
    api_client: Any,
    create_user_role_with_permissions: Callable,
    two_program_ticket: GrievanceTicket,
    count_url: str,
) -> None:
    create_user_role_with_permissions(user, LIST_PERMISSIONS, afghanistan, whole_business_area_access=True)

    response = api_client(user).get(count_url, {"active_programs_only": "true"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["count"] == 1


def test_count_reports_a_ticket_with_two_matching_duplicates_once_for_an_office_search(
    afghanistan: BusinessArea,
    user: User,
    api_client: Any,
    create_user_role_with_permissions: Callable,
    two_duplicates_on_the_ticket: list[Individual],
    count_url: str,
) -> None:
    create_user_role_with_permissions(user, LIST_PERMISSIONS, afghanistan, whole_business_area_access=True)

    response = api_client(user).get(count_url, {"office_search": "Adjudication Namesake"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["count"] == 1
