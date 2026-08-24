"""These pin the behaviour of `BusinessAreaVisibilityMixin.get_queryset`
(`src/hope/apps/core/api/mixins.py`), which uses `Exists()` over the ticket -> program
through model rather than joining it (ticket 331051).

The admin-area cases here are also covered by
`test_grievance_list_global.py::test_grievance_ticket_global_list_area_limits`.

A few tests here assert on the query's shape rather than on the response.
`extras.test_utils.sql` explains what those catch that a behavioural assertion does not.
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
from extras.test_utils.sql import joined_tables, list_queryset, main_list_statement
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.models import GrievanceTicket
from hope.models import Area, BusinessArea, Partner, Program, User

pytestmark = pytest.mark.django_db()

LIST_PERMISSIONS = [
    Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
    Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
]

GLOBAL_LIST_QUERY_COUNT = 41


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
def finished_program(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(business_area=afghanistan, status=Program.FINISHED, name="finished program")


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
def ticket_in_finished_program(afghanistan: BusinessArea, finished_program: Program) -> GrievanceTicket:
    ticket = GrievanceTicketFactory(business_area=afghanistan, admin2=None, description="in finished program")
    ticket.programs.set([finished_program])
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


def test_list_filtered_by_is_active_program_returns_active_and_program_less_tickets_once(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    ticket_in_three_programs: GrievanceTicket,
    ticket_in_finished_program: GrievanceTicket,
    ticket_without_programs: GrievanceTicket,
    create_user_role_with_permissions: Callable,
) -> None:
    # The filter used to join the through table, so a ticket in three active programs came back
    # three times - masked by the queryset-level .distinct() the Exists() rewrite removes.
    # `is_active_program=true` is `program_with_status_exists(ACTIVE) | without_program_q()`, so the
    # ticket with no programs at all belongs in the result and the finished-only one does not.
    create_user_role_with_permissions(user, LIST_PERMISSIONS, afghanistan, whole_business_area_access=True)

    response = api_client(user).get(list_url(afghanistan), {"is_active_program": "true"})

    assert response.status_code == status.HTTP_200_OK
    ids = [result["id"] for result in response.data["results"]]
    assert sorted(ids) == sorted([str(ticket_in_three_programs.id), str(ticket_without_programs.id)])


def test_list_filtered_by_active_programs_only_drops_tickets_without_programs(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    ticket_in_three_programs: GrievanceTicket,
    ticket_in_finished_program: GrievanceTicket,
    ticket_without_programs: GrievanceTicket,
    create_user_role_with_permissions: Callable,
) -> None:
    # `active_programs_only` is the stricter of the two: unlike `is_active_program=true` it is a bare
    # `program_with_status_exists(ACTIVE)`, so a ticket with no programs is not an active-programme
    # ticket. The parametrised version of this test hid that difference.
    create_user_role_with_permissions(user, LIST_PERMISSIONS, afghanistan, whole_business_area_access=True)

    response = api_client(user).get(list_url(afghanistan), {"active_programs_only": "true"})

    assert response.status_code == status.HTTP_200_OK
    assert [result["id"] for result in response.data["results"]] == [str(ticket_in_three_programs.id)]


def test_list_filtered_by_is_active_program_false_returns_only_finished_program_tickets(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    ticket_in_three_programs: GrievanceTicket,
    ticket_in_finished_program: GrievanceTicket,
    ticket_without_programs: GrievanceTicket,
    create_user_role_with_permissions: Callable,
) -> None:
    # The other branch of the same rewritten filter: a bare `program_with_status_exists(FINISHED)`,
    # which takes neither the active ticket nor the one without programs.
    create_user_role_with_permissions(user, LIST_PERMISSIONS, afghanistan, whole_business_area_access=True)

    response = api_client(user).get(list_url(afghanistan), {"is_active_program": "false"})

    assert response.status_code == status.HTTP_200_OK
    assert [result["id"] for result in response.data["results"]] == [str(ticket_in_finished_program.id)]


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


def test_list_queryset_does_not_join_the_program_through_table(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    ticket_in_three_programs: GrievanceTicket,
    ticket_in_program_one_area_one: GrievanceTicket,
    area_one: Area,
    program_one: Program,
    create_user_role_with_permissions: Callable,
) -> None:
    # The row explosion the Exists() rewrite removes: one join row per ticket x accessible program.
    # An area-limited program is included so the limited branch is exercised too, not just the plain one.
    create_user_role_with_permissions(
        user, LIST_PERMISSIONS, afghanistan, program=program_one, areas=[area_one], whole_business_area_access=False
    )
    create_user_role_with_permissions(user, LIST_PERMISSIONS, afghanistan, whole_business_area_access=True)

    response = api_client(user).get(list_url(afghanistan))

    assert response.status_code == status.HTTP_200_OK
    # The through table may still appear inside correlated subqueries - those return one row per
    # ticket, which is the point of the rewrite. Only the outer join list has to be clean, and
    # joined_tables reports just that.
    assert "grievance_grievanceticket_programs" not in joined_tables(list_queryset(response))


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


def test_list_returns_ticket_without_programs_when_other_tickets_have_programs(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program_one: Program,
    ticket_without_programs: GrievanceTicket,
    ticket_in_program_two_only: GrievanceTicket,
    create_user_role_with_permissions: Callable,
) -> None:
    # `NOT IN (subquery)` and `NOT EXISTS` only agree while the subquery has no NULLs, and they
    # agree trivially while it has no rows at all. This is the non-empty case: the through table
    # holds a link for another ticket, so the unlinked one has to survive a real anti-join.
    create_user_role_with_permissions(user, LIST_PERMISSIONS, afghanistan, program=program_one)

    response = api_client(user).get(list_url(afghanistan))

    assert response.status_code == status.HTTP_200_OK
    assert [result["id"] for result in response.data["results"]] == [str(ticket_without_programs.id)]


def test_list_main_statement_filters_permissions_without_id_in_subquery(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program_one: Program,
    ticket_in_program_one_area_one: GrievanceTicket,
    ticket_without_programs: GrievanceTicket,
    create_user_role_with_permissions: Callable,
) -> None:
    # `GrievancePermissionsMixin` used to express both permission predicates as
    # `id IN (<whole through table>)`. At prod scale that subplan does not fit in work_mem, so
    # the planner materialises a full scan of the through table and rescans it per candidate row.
    create_user_role_with_permissions(user, LIST_PERMISSIONS, afghanistan, program=program_one)

    with CaptureQueriesContext(connection) as captured:
        response = api_client(user).get(list_url(afghanistan))

    assert response.status_code == status.HTTP_200_OK
    # Only the absence of the bad construct is pinned. The EXISTS that replaced it is already
    # covered structurally by test_list_queryset_does_not_join_the_program_through_table, and
    # matching Django's rendering of it here would break on formatting changes alone.
    main_statement = main_list_statement(captured, "grievance_grievanceticket")
    assert '"grievance_grievanceticket"."id" IN (SELECT' not in main_statement
