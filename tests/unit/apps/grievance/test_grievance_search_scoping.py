"""`GrievanceTicketFilter.search_filter` and `.document_number_filter`
(`src/hope/apps/grievance/filters.py`) match tickets through the denormalised
`household_unicef_id` column. The subquery that produces those ids used to scan
`household_individual` globally, so at prod scale one search read the whole table to
filter down to a single business area.
"""

import re
from typing import Any, Callable

from django.db import connection
from django.test.utils import CaptureQueriesContext
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.grievance import GrievanceTicketFactory
from extras.test_utils.factories.household import (
    DocumentFactory,
    DocumentTypeFactory,
    HouseholdFactory,
    IndividualFactory,
)
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.sql import main_list_statement
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.household.const import HEAD
from hope.models import BusinessArea, Document, Individual, Partner, Program, User

pytestmark = pytest.mark.django_db()

LIST_PERMISSIONS = [
    Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
    Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
]

# The one household unicef id the ticket points at. Both business areas below reuse it, so
# the only thing separating the local head of household from the foreign one is the
# business area predicate under test.
SHARED_HOUSEHOLD_UNICEF_ID = "HH-SCOPE-0001"


def assert_individual_subquery_is_business_area_scoped(main_statement: str) -> None:
    """Fail unless the `household_individual` subquery carries a business-area predicate.

    The alias Django gives the table (`U0`, `U1`, ...) depends on how many other subqueries
    the compiled statement holds, so it is read off the statement rather than hard-coded.
    """
    alias_match = re.search(r'FROM "household_individual" (\w+)', main_statement)
    assert alias_match, f"no household_individual subquery in:\n{main_statement}"
    alias = alias_match.group(1)
    assert f'{alias}."business_area_id" = ' in main_statement, main_statement


def count_business_area_slug_lookups(captured: CaptureQueriesContext) -> int:
    """How many times the request looked a business area up by slug."""
    return len(
        [
            query["sql"]
            for query in captured.captured_queries
            if 'FROM "core_businessarea"' in query["sql"] and '"slug" = ' in query["sql"]
        ]
    )


@pytest.fixture
def afghanistan() -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan", code="AFG")


@pytest.fixture
def ukraine() -> BusinessArea:
    return BusinessAreaFactory(slug="ukraine", name="Ukraine", code="UKR")


@pytest.fixture
def partner() -> Partner:
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def program_afghanistan(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(business_area=afghanistan, status=Program.ACTIVE, name="afghanistan program")


@pytest.fixture
def program_ukraine(ukraine: BusinessArea) -> Program:
    return ProgramFactory(business_area=ukraine, status=Program.ACTIVE, name="ukraine program")


@pytest.fixture
def user(partner: Partner) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def local_head_of_household(afghanistan: BusinessArea, program_afghanistan: Program) -> Individual:
    individual = IndividualFactory(
        business_area=afghanistan,
        program=program_afghanistan,
        household=None,
        full_name="Local Resident",
        relationship=HEAD,
    )
    household = HouseholdFactory(
        business_area=afghanistan,
        program=program_afghanistan,
        head_of_household=individual,
    )
    household.unicef_id = SHARED_HOUSEHOLD_UNICEF_ID
    household.save(update_fields=["unicef_id"])
    individual.unicef_id = "IND-SCOPE-0001"
    individual.save(update_fields=["unicef_id"])
    return individual


@pytest.fixture
def foreign_head_of_household(ukraine: BusinessArea, program_ukraine: Program) -> Individual:
    individual = IndividualFactory(
        business_area=ukraine,
        program=program_ukraine,
        household=None,
        full_name="Foreign Namesake",
        relationship=HEAD,
    )
    household = HouseholdFactory(
        business_area=ukraine,
        program=program_ukraine,
        head_of_household=individual,
    )
    household.unicef_id = SHARED_HOUSEHOLD_UNICEF_ID
    household.save(update_fields=["unicef_id"])
    individual.unicef_id = "IND-SCOPE-0002"
    individual.save(update_fields=["unicef_id"])
    return individual


@pytest.fixture
def local_document(local_head_of_household: Individual) -> Document:
    return DocumentFactory(
        individual=local_head_of_household,
        type=DocumentTypeFactory(key="national_id"),
        document_number="SCOPE-DOC-LOCAL",
    )


@pytest.fixture
def foreign_document(foreign_head_of_household: Individual) -> Document:
    return DocumentFactory(
        individual=foreign_head_of_household,
        type=DocumentTypeFactory(key="national_id"),
        document_number="SCOPE-DOC-FOREIGN",
    )


@pytest.fixture
def ticket(afghanistan: BusinessArea, program_afghanistan: Program) -> GrievanceTicket:
    ticket = GrievanceTicketFactory(
        business_area=afghanistan,
        household_unicef_id=SHARED_HOUSEHOLD_UNICEF_ID,
    )
    ticket.programs.add(program_afghanistan)
    return ticket


@pytest.fixture
def list_url(afghanistan: BusinessArea) -> str:
    return reverse(
        "api:grievance:grievance-tickets-global-list",
        kwargs={"business_area_slug": afghanistan.slug},
    )


@pytest.fixture
def program_list_url(afghanistan: BusinessArea, program_afghanistan: Program) -> str:
    return reverse(
        "api:grievance:grievance-tickets-list",
        kwargs={"business_area_slug": afghanistan.slug, "program_code": program_afghanistan.code},
    )


def test_search_by_name_matches_head_of_household_in_the_request_business_area(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program_afghanistan: Program,
    local_head_of_household: Individual,
    ticket: GrievanceTicket,
    list_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, LIST_PERMISSIONS, afghanistan, whole_business_area_access=True)

    response = api_client(user).get(list_url, {"search": "Local Resident"})

    assert response.status_code == status.HTTP_200_OK
    assert [result["id"] for result in response.data["results"]] == [str(ticket.id)]


def test_search_by_name_ignores_head_of_household_in_another_business_area(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program_afghanistan: Program,
    local_head_of_household: Individual,
    foreign_head_of_household: Individual,
    ticket: GrievanceTicket,
    list_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    # The Ukrainian household carries the same unicef id as the Afghan one, so before the
    # subquery was scoped its head of household could pull an Afghan ticket into the result.
    create_user_role_with_permissions(user, LIST_PERMISSIONS, afghanistan, whole_business_area_access=True)

    response = api_client(user).get(list_url, {"search": "Foreign Namesake"})

    assert response.status_code == status.HTTP_200_OK
    assert response.data["results"] == []


def test_search_by_individual_unicef_id_matches_within_the_request_business_area(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program_afghanistan: Program,
    local_head_of_household: Individual,
    ticket: GrievanceTicket,
    list_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, LIST_PERMISSIONS, afghanistan, whole_business_area_access=True)

    response = api_client(user).get(list_url, {"search": "IND-SCOPE-0001"})

    assert response.status_code == status.HTTP_200_OK
    assert [result["id"] for result in response.data["results"]] == [str(ticket.id)]


def test_search_by_individual_unicef_id_ignores_individuals_in_another_business_area(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program_afghanistan: Program,
    local_head_of_household: Individual,
    foreign_head_of_household: Individual,
    ticket: GrievanceTicket,
    list_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    # The `IND-` branch has its own shape - `istartswith` inside a correlated `EXISTS` - so
    # it needs its own case rather than riding on the free-text one.
    create_user_role_with_permissions(user, LIST_PERMISSIONS, afghanistan, whole_business_area_access=True)

    response = api_client(user).get(list_url, {"search": "IND-SCOPE-0002"})

    assert response.status_code == status.HTTP_200_OK
    assert response.data["results"] == []


def test_document_number_matches_document_in_the_request_business_area(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program_afghanistan: Program,
    local_document: Document,
    ticket: GrievanceTicket,
    list_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, LIST_PERMISSIONS, afghanistan, whole_business_area_access=True)

    response = api_client(user).get(list_url, {"document_type": "national_id", "document_number": "SCOPE-DOC-LOCAL"})

    assert response.status_code == status.HTTP_200_OK
    assert [result["id"] for result in response.data["results"]] == [str(ticket.id)]


def test_document_number_ignores_document_of_an_individual_in_another_business_area(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program_afghanistan: Program,
    local_document: Document,
    foreign_document: Document,
    ticket: GrievanceTicket,
    list_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, LIST_PERMISSIONS, afghanistan, whole_business_area_access=True)

    response = api_client(user).get(list_url, {"document_type": "national_id", "document_number": "SCOPE-DOC-FOREIGN"})

    assert response.status_code == status.HTTP_200_OK
    assert response.data["results"] == []


@pytest.mark.parametrize(
    ("query", "expected_id"),
    [
        pytest.param({"search": "Local Resident"}, "IND-SCOPE-0001", id="free-text"),
        pytest.param({"search": "IND-SCOPE-0001"}, "IND-SCOPE-0001", id="ind-prefix"),
        pytest.param(
            {"document_type": "national_id", "document_number": "SCOPE-DOC-LOCAL"},
            "SCOPE-DOC-LOCAL",
            id="document-number",
        ),
    ],
)
def test_search_subquery_carries_a_business_area_predicate(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program_afghanistan: Program,
    local_document: Document,
    ticket: GrievanceTicket,
    list_url: str,
    create_user_role_with_permissions: Callable,
    query: dict,
    expected_id: str,
) -> None:
    # Without this the regression "someone dropped the business-area predicate from the
    # subquery" stays green everywhere, because household unicef ids are globally unique
    # and the response therefore does not change.
    create_user_role_with_permissions(user, LIST_PERMISSIONS, afghanistan, whole_business_area_access=True)
    client = api_client(user)
    client.get(list_url)  # warm the business-area version and permission caches

    with CaptureQueriesContext(connection) as captured:
        response = client.get(list_url, query)

    assert response.status_code == status.HTTP_200_OK
    assert [result["id"] for result in response.data["results"]] == [str(ticket.id)]
    assert_individual_subquery_is_business_area_scoped(main_list_statement(captured, "grievance_grievanceticket"))


def test_program_nested_search_subquery_carries_a_business_area_predicate(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program_afghanistan: Program,
    local_head_of_household: Individual,
    ticket: GrievanceTicket,
    program_list_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    # `GrievanceTicketOfficeSearchFilter` inherits `search_filter`, so the program-nested
    # list has to be scoped too.
    create_user_role_with_permissions(
        user, LIST_PERMISSIONS, afghanistan, program=program_afghanistan, whole_business_area_access=True
    )
    client = api_client(user)
    client.get(program_list_url)  # warm the business-area version and permission caches

    with CaptureQueriesContext(connection) as captured:
        response = client.get(program_list_url, {"search": "Local Resident"})

    assert response.status_code == status.HTTP_200_OK
    assert [result["id"] for result in response.data["results"]] == [str(ticket.id)]
    assert_individual_subquery_is_business_area_scoped(main_list_statement(captured, "grievance_grievanceticket"))


def test_business_area_is_resolved_once_however_many_filters_need_it(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program_afghanistan: Program,
    local_document: Document,
    ticket: GrievanceTicket,
    list_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    # `search`, `document_number` and `is_cross_area` all need the business area. The
    # cached property is what keeps that at one lookup rather than one per filter method,
    # so the two requests below must issue the same number of them.
    create_user_role_with_permissions(user, LIST_PERMISSIONS, afghanistan, whole_business_area_access=True)
    client = api_client(user)
    one_filter = {"is_cross_area": "false"}
    three_filters = {
        "search": "Local Resident",
        "document_type": "national_id",
        "document_number": "SCOPE-DOC-LOCAL",
        "is_cross_area": "false",
    }
    client.get(list_url, three_filters)  # warm the business-area version and permission caches

    with CaptureQueriesContext(connection) as captured_one:
        response_one = client.get(list_url, one_filter)
    with CaptureQueriesContext(connection) as captured_three:
        response_three = client.get(list_url, three_filters)

    assert response_one.status_code == status.HTTP_200_OK
    assert response_three.status_code == status.HTTP_200_OK
    assert count_business_area_slug_lookups(captured_three) == count_business_area_slug_lookups(captured_one)


@pytest.fixture
def second_local_individual_in_the_same_household(
    afghanistan: BusinessArea, program_afghanistan: Program, local_head_of_household: Individual
) -> Individual:
    """A second individual under the household the ticket points at, matching the same prefix.

    The `IND-` branch used to dedupe with `DISTINCT ON (household__unicef_id)` before feeding
    an `IN` list; the `EXISTS` rewrite has no such step, so this is what proves it does not
    need one.
    """
    individual = IndividualFactory(
        business_area=afghanistan,
        program=program_afghanistan,
        household=local_head_of_household.household,
        full_name="Local Dependant",
    )
    individual.unicef_id = "IND-SCOPE-0001-B"
    individual.save(update_fields=["unicef_id"])
    return individual


def test_search_by_individual_unicef_id_returns_a_ticket_once_per_matching_household(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program_afghanistan: Program,
    local_head_of_household: Individual,
    second_local_individual_in_the_same_household: Individual,
    ticket: GrievanceTicket,
    list_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, LIST_PERMISSIONS, afghanistan, whole_business_area_access=True)

    response = api_client(user).get(list_url, {"search": "IND-SCOPE-0001"})

    assert response.status_code == status.HTTP_200_OK
    assert [result["id"] for result in response.data["results"]] == [str(ticket.id)]


def test_search_by_individual_unicef_id_correlates_on_household_unicef_id(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program_afghanistan: Program,
    local_head_of_household: Individual,
    ticket: GrievanceTicket,
    list_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, LIST_PERMISSIONS, afghanistan, whole_business_area_access=True)

    with CaptureQueriesContext(connection) as captured:
        response = api_client(user).get(list_url, {"search": "IND-SCOPE-0001"})

    assert response.status_code == status.HTTP_200_OK
    main_statement = main_list_statement(captured, "grievance_grievanceticket")
    assert '"household_unicef_id" IN (SELECT' not in main_statement, main_statement
    assert "DISTINCT ON" not in main_statement, main_statement
    assert re.search(
        r'"unicef_id" = \("grievance_grievanceticket"\."household_unicef_id"\)', main_statement
    ), main_statement
