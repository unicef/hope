"""These pin the behaviour of `BusinessAreaVisibilityMixin.get_queryset`
(`src/hope/apps/core/api/mixins.py`) before it is rewritten to use `Exists()` over
the ticket -> program through model (ticket 331051).

The admin-area cases here are also covered by
`test_grievance_list_global.py::test_grievance_ticket_global_list_area_limits`.
"""

from typing import Any, Callable

from django.db import connection
from django.test.utils import CaptureQueriesContext
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory, CountryFactory
from extras.test_utils.factories.grievance import GrievanceTicketFactory
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.models import GrievanceTicket
from hope.models import Area, BusinessArea, Partner, Program, User

pytestmark = pytest.mark.django_db()

LIST_PERMISSIONS = [
    Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
    Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
]

GLOBAL_LIST_QUERY_COUNT = 46


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
def program_one(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(business_area=afghanistan, status=Program.ACTIVE, name="program one")


@pytest.fixture
def program_two(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(business_area=afghanistan, status=Program.ACTIVE, name="program two")


@pytest.fixture
def program_three(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(business_area=afghanistan, status=Program.ACTIVE, name="program three")


@pytest.fixture
def area_one() -> Area:
    return AreaFactory(parent=None, p_code="AF01", area_type=AreaTypeFactory(country=CountryFactory(), area_level=2))


@pytest.fixture
def area_two(area_one: Area) -> Area:
    return AreaFactory(parent=None, p_code="AF02", area_type=area_one.area_type)


@pytest.fixture
def ticket_in_three_programs(
    afghanistan: BusinessArea,
    program_one: Program,
    program_two: Program,
    program_three: Program,
) -> GrievanceTicket:
    ticket = GrievanceTicketFactory(business_area=afghanistan, admin2=None, description="in three programs")
    ticket.programs.set([program_one, program_two, program_three])
    return ticket


@pytest.fixture
def ticket_in_program_two_only(afghanistan: BusinessArea, program_two: Program) -> GrievanceTicket:
    ticket = GrievanceTicketFactory(business_area=afghanistan, admin2=None, description="in program two only")
    ticket.programs.set([program_two])
    return ticket


@pytest.fixture
def ticket_without_programs(afghanistan: BusinessArea) -> GrievanceTicket:
    return GrievanceTicketFactory(business_area=afghanistan, admin2=None, description="no programs")


@pytest.fixture
def ticket_in_program_one_area_one(afghanistan: BusinessArea, program_one: Program, area_one: Area) -> GrievanceTicket:
    ticket = GrievanceTicketFactory(business_area=afghanistan, admin2=area_one, description="program one, area one")
    ticket.programs.set([program_one])
    return ticket


@pytest.fixture
def ticket_in_program_one_area_two(afghanistan: BusinessArea, program_one: Program, area_two: Area) -> GrievanceTicket:
    ticket = GrievanceTicketFactory(business_area=afghanistan, admin2=area_two, description="program one, area two")
    ticket.programs.set([program_one])
    return ticket


@pytest.fixture
def ticket_in_program_one_without_area(afghanistan: BusinessArea, program_one: Program) -> GrievanceTicket:
    ticket = GrievanceTicketFactory(business_area=afghanistan, admin2=None, description="program one, no area")
    ticket.programs.set([program_one])
    return ticket


@pytest.fixture
def ticket_in_program_two_area_two(afghanistan: BusinessArea, program_two: Program, area_two: Area) -> GrievanceTicket:
    ticket = GrievanceTicketFactory(business_area=afghanistan, admin2=area_two, description="program two, area two")
    ticket.programs.set([program_two])
    return ticket


def list_url(business_area: BusinessArea) -> str:
    return reverse(
        "api:grievance:grievance-tickets-global-list",
        kwargs={"business_area_slug": business_area.slug},
    )


def count_url(business_area: BusinessArea) -> str:
    return reverse(
        "api:grievance:grievance-tickets-global-count",
        kwargs={"business_area_slug": business_area.slug},
    )


def test_list_returns_ticket_once_when_linked_to_multiple_programs(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    ticket_in_three_programs: GrievanceTicket,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, LIST_PERMISSIONS, afghanistan, whole_business_area_access=True)

    response = api_client(user).get(list_url(afghanistan))

    assert response.status_code == status.HTTP_200_OK
    assert [result["id"] for result in response.data["results"]] == [str(ticket_in_three_programs.id)]


@pytest.mark.xfail(
    strict=True,
    reason="get_count_queryset has the M2M join and no .distinct(), so it counts "
    "ticket x program rows. To be fixed by the Exists().",
)
def test_count_returns_one_when_ticket_linked_to_multiple_programs(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    ticket_in_three_programs: GrievanceTicket,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, LIST_PERMISSIONS, afghanistan, whole_business_area_access=True)

    response = api_client(user).get(count_url(afghanistan))

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["count"] == 1


def test_list_excludes_tickets_from_programs_without_access(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program_one: Program,
    ticket_in_program_two_only: GrievanceTicket,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, LIST_PERMISSIONS, afghanistan, program=program_one)

    response = api_client(user).get(list_url(afghanistan))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["results"] == []


def test_list_returns_tickets_without_programs(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program_one: Program,
    ticket_without_programs: GrievanceTicket,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, LIST_PERMISSIONS, afghanistan, program=program_one)

    response = api_client(user).get(list_url(afghanistan))

    assert response.status_code == status.HTTP_200_OK
    assert [result["id"] for result in response.data["results"]] == [str(ticket_without_programs.id)]


def test_area_limited_partner_sees_only_tickets_in_permitted_admin2(
    api_client: Any,
    user: User,
    partner: Partner,
    afghanistan: BusinessArea,
    program_one: Program,
    area_one: Area,
    ticket_in_program_one_area_one: GrievanceTicket,
    ticket_in_program_one_area_two: GrievanceTicket,
    create_user_role_with_permissions: Callable,
    set_admin_area_limits_in_program: Callable,
) -> None:
    create_user_role_with_permissions(user, LIST_PERMISSIONS, afghanistan, whole_business_area_access=True)
    set_admin_area_limits_in_program(partner, program_one, [area_one])

    response = api_client(user).get(list_url(afghanistan))

    assert response.status_code == status.HTTP_200_OK
    assert [result["id"] for result in response.data["results"]] == [str(ticket_in_program_one_area_one.id)]


def test_area_limited_partner_sees_tickets_with_null_admin2(
    api_client: Any,
    user: User,
    partner: Partner,
    afghanistan: BusinessArea,
    program_one: Program,
    area_one: Area,
    ticket_in_program_one_without_area: GrievanceTicket,
    create_user_role_with_permissions: Callable,
    set_admin_area_limits_in_program: Callable,
) -> None:
    create_user_role_with_permissions(user, LIST_PERMISSIONS, afghanistan, whole_business_area_access=True)
    set_admin_area_limits_in_program(partner, program_one, [area_one])

    response = api_client(user).get(list_url(afghanistan))

    assert response.status_code == status.HTTP_200_OK
    assert [result["id"] for result in response.data["results"]] == [str(ticket_in_program_one_without_area.id)]


def test_partner_with_limits_in_one_program_sees_all_areas_in_another(
    api_client: Any,
    user: User,
    partner: Partner,
    afghanistan: BusinessArea,
    program_one: Program,
    area_one: Area,
    ticket_in_program_two_area_two: GrievanceTicket,
    create_user_role_with_permissions: Callable,
    set_admin_area_limits_in_program: Callable,
) -> None:
    # program_one is area-limited to area_one; program_two has no AdminAreaLimitedTo rows at all
    create_user_role_with_permissions(user, LIST_PERMISSIONS, afghanistan, whole_business_area_access=True)
    set_admin_area_limits_in_program(partner, program_one, [area_one])

    response = api_client(user).get(list_url(afghanistan))

    assert response.status_code == status.HTTP_200_OK
    assert [result["id"] for result in response.data["results"]] == [str(ticket_in_program_two_area_two.id)]


def test_list_is_empty_when_business_area_has_no_programs(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    ticket_without_programs: GrievanceTicket,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, LIST_PERMISSIONS, afghanistan, whole_business_area_access=True)

    response = api_client(user).get(list_url(afghanistan))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["results"] == []


def test_list_query_count_is_stable(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    ticket_in_three_programs: GrievanceTicket,
    ticket_in_program_two_only: GrievanceTicket,
    ticket_without_programs: GrievanceTicket,
    create_user_role_with_permissions: Callable,
    django_assert_num_queries: Any,
) -> None:
    # The regression guard: the query count must not grow with the number of rows on the page
    create_user_role_with_permissions(user, LIST_PERMISSIONS, afghanistan, whole_business_area_access=True)
    client = api_client(user)

    with django_assert_num_queries(GLOBAL_LIST_QUERY_COUNT):
        response = client.get(list_url(afghanistan))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 3


@pytest.mark.xfail(
    strict=True,
    reason="The global list does not annotate existing_tickets_count, so "
    "GrievanceTicketListSerializer.get_related_tickets_count falls back to "
    "obj._related_tickets.count() - one COUNT per row.",
)
def test_list_query_count_does_not_grow_with_page_size(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    ticket_in_three_programs: GrievanceTicket,
    ticket_in_program_two_only: GrievanceTicket,
    ticket_without_programs: GrievanceTicket,
    ticket_in_program_one_area_one: GrievanceTicket,
    ticket_in_program_one_area_two: GrievanceTicket,
    ticket_in_program_two_area_two: GrievanceTicket,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, LIST_PERMISSIONS, afghanistan, whole_business_area_access=True)
    client = api_client(user)
    # Warm the per-request caches the first call populates (business area version, the
    # user's permissions) so the two measured calls differ only in page size.
    client.get(list_url(afghanistan), {"limit": 1})

    with CaptureQueriesContext(connection) as three_rows:
        client.get(list_url(afghanistan), {"limit": 3})
    with CaptureQueriesContext(connection) as six_rows:
        client.get(list_url(afghanistan), {"limit": 6})

    assert len(six_rows.captured_queries) == len(three_rows.captured_queries)
