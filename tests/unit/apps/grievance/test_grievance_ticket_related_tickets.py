"""Tests for grievance ticket related tickets functionality."""

from typing import Any, Callable
from unittest.mock import MagicMock

import hope.apps.household.api.serializers.household  # noqa: F401, isort: skip - resolve circular import; must load before grievance views

from django.db import connection
from django.test.utils import CaptureQueriesContext
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.grievance import GrievanceTicketFactory
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.models import GrievanceTicket
from hope.models import BusinessArea, Program, User

LIST_PERMISSIONS = [
    Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
    Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
]
HOUSEHOLD_UNICEF_ID = "HH-0000-0000.0001"
OTHER_HOUSEHOLD_UNICEF_ID = "HH-0000-0000.0002"


@pytest.fixture
def grievance_tickets() -> list:
    return GrievanceTicketFactory.create_batch(5)


def test_should_return_distinct_related_tickets(
    grievance_tickets: list,
) -> None:
    ticket1 = GrievanceTicketFactory()
    ticket2 = GrievanceTicketFactory()

    # ticket1 links to 5 grievance_tickets
    ticket1.linked_tickets.set(grievance_tickets)

    # ticket2 links to the same 5 tickets PLUS ticket1
    ticket2.linked_tickets.set(list(grievance_tickets) + [ticket1])

    # ticket1 should have: 5 original + ticket2 (added via ticket2 linking to ticket1) = 6
    # ticket2 should have: 5 original + ticket1 = 6
    assert ticket1.linked_tickets.count() == 6
    assert ticket2.linked_tickets.count() == 6


def test_get_related_tickets_count_deduplicates_linked_ticket_with_same_household() -> None:
    """A linked ticket that shares household_unicef_id with obj is counted only once."""
    from hope.apps.grievance.api.serializers.grievance_ticket import GrievanceTicketListSerializer

    # GrievanceListBatchMixin builds existing_tickets_counts once per page and passes it
    # through the serializer context; without it the serializer falls back to a per-row count.
    serializer = GrievanceTicketListSerializer(context={"existing_tickets_counts": {"HH-001": 3}})

    same_hh_ticket = MagicMock()
    same_hh_ticket.household_unicef_id = "HH-001"

    other_hh_ticket = MagicMock()
    other_hh_ticket.household_unicef_id = "HH-002"

    obj = MagicMock()
    obj.household_unicef_id = "HH-001"
    obj.linked_tickets.all.return_value = [same_hh_ticket, other_hh_ticket]

    # overlap = 1 (same_hh_ticket matches obj.household_unicef_id)
    # result = len([same, other]) + 3 - 1 = 4
    assert serializer.get_related_tickets_count(obj) == 4


@pytest.fixture
def afghanistan() -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan", code="AFG")


@pytest.fixture
def user() -> User:
    return UserFactory(partner=PartnerFactory(name="TestPartner"))


@pytest.fixture
def program(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(business_area=afghanistan, status=Program.ACTIVE, name="program")


@pytest.fixture
def three_tickets_for_one_household(afghanistan: BusinessArea, program: Program) -> list[GrievanceTicket]:
    first = GrievanceTicketFactory(
        business_area=afghanistan, admin2=None, household_unicef_id=HOUSEHOLD_UNICEF_ID, description="household one"
    )
    second = GrievanceTicketFactory(
        business_area=afghanistan, admin2=None, household_unicef_id=HOUSEHOLD_UNICEF_ID, description="household two"
    )
    third = GrievanceTicketFactory(
        business_area=afghanistan, admin2=None, household_unicef_id=HOUSEHOLD_UNICEF_ID, description="household three"
    )
    first.programs.set([program])
    second.programs.set([program])
    third.programs.set([program])
    return [first, second, third]


@pytest.fixture
def ticket_for_another_household(afghanistan: BusinessArea, program: Program) -> GrievanceTicket:
    ticket = GrievanceTicketFactory(
        business_area=afghanistan,
        admin2=None,
        household_unicef_id=OTHER_HOUSEHOLD_UNICEF_ID,
        description="other household",
    )
    ticket.programs.set([program])
    return ticket


def global_list_url(business_area: BusinessArea) -> str:
    return reverse(
        "api:grievance:grievance-tickets-global-list",
        kwargs={"business_area_slug": business_area.slug},
    )


@pytest.mark.django_db
def test_global_list_related_tickets_count_is_the_number_of_other_tickets_for_the_same_household(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    three_tickets_for_one_household: list[GrievanceTicket],
    ticket_for_another_household: GrievanceTicket,
    create_user_role_with_permissions: Callable,
) -> None:
    # GrievanceListBatchMixin counts every ticket of the household in one statement and
    # subtracts the row itself, so the arithmetic is only right if that subtraction lands.
    create_user_role_with_permissions(user, LIST_PERMISSIONS, afghanistan, whole_business_area_access=True)

    response = api_client(user).get(global_list_url(afghanistan))

    assert response.status_code == status.HTTP_200_OK
    counts_by_id = {result["id"]: result["related_tickets_count"] for result in response.data["results"]}
    assert counts_by_id[str(three_tickets_for_one_household[0].id)] == 2
    assert counts_by_id[str(three_tickets_for_one_household[1].id)] == 2
    assert counts_by_id[str(three_tickets_for_one_household[2].id)] == 2
    assert counts_by_id[str(ticket_for_another_household.id)] == 0


@pytest.mark.django_db
def test_global_list_counts_related_tickets_in_one_statement_per_page(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    three_tickets_for_one_household: list[GrievanceTicket],
    ticket_for_another_household: GrievanceTicket,
    create_user_role_with_permissions: Callable,
) -> None:
    # The page-size pin in test_grievance_list_global_visibility.py uses tickets without a
    # household, where the batched lookup short-circuits without querying at all. This one
    # keeps the batched statement itself at one per page instead of one per row.
    create_user_role_with_permissions(user, LIST_PERMISSIONS, afghanistan, whole_business_area_access=True)
    client = api_client(user)
    # Warm the business area version and permission caches the first call populates.
    client.get(global_list_url(afghanistan), {"limit": 1})

    with CaptureQueriesContext(connection) as two_rows:
        client.get(global_list_url(afghanistan), {"limit": 2})
    with CaptureQueriesContext(connection) as four_rows:
        client.get(global_list_url(afghanistan), {"limit": 4})

    batched_statements = [
        query["sql"]
        for query in four_rows.captured_queries
        if "COUNT" in query["sql"] and "household_unicef_id" in query["sql"] and "GROUP BY" in query["sql"]
    ]
    assert len(batched_statements) == 1
    assert len(four_rows.captured_queries) == len(two_rows.captured_queries)


@pytest.mark.django_db
def test_get_related_tickets_count_falls_back_to_a_per_row_count_without_the_batch_context(
    three_tickets_for_one_household: list[GrievanceTicket],
    ticket_for_another_household: GrievanceTicket,
) -> None:
    """Without `existing_tickets_counts` in the context the serializer counts per row."""
    from hope.apps.grievance.api.serializers.grievance_ticket import GrievanceTicketListSerializer

    serializer = GrievanceTicketListSerializer()

    count = serializer.get_related_tickets_count(three_tickets_for_one_household[0])

    assert count == 2
