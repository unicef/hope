"""These pin the behaviour of `BusinessAreaMixin.get_queryset`
(`src/hope/apps/core/api/mixins.py`), which filters the business area by primary key
rather than by joining `core_businessarea` on its slug (ticket 331051).

That the filter still *excludes* other business areas is covered by
`tests/unit/apps/grievance/test_grievance_list_global.py` (grievance) and
`tests/unit/apps/program/test_views_program_list.py` (programs); what is new here is the
statement shape and the unknown-slug path.
"""

from typing import Callable

from django.db import connection
from django.test.utils import CaptureQueriesContext
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.grievance import GrievanceTicketFactory
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.sql import joined_tables, list_queryset, main_list_statement
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.models import GrievanceTicket
from hope.models import BusinessArea, Partner, Program, User

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
def program_afghanistan(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(business_area=afghanistan, status=Program.ACTIVE, name="program afghanistan")


@pytest.fixture
def ticket_afghanistan(afghanistan: BusinessArea, program_afghanistan: Program) -> GrievanceTicket:
    ticket = GrievanceTicketFactory(business_area=afghanistan, admin2=None, description="afghanistan ticket")
    ticket.programs.set([program_afghanistan])
    return ticket


def grievance_list_url(business_area_slug: str) -> str:
    return reverse(
        "api:grievance:grievance-tickets-global-list",
        kwargs={"business_area_slug": business_area_slug},
    )


def test_list_main_statement_filters_business_area_without_joining_it(
    api_client: Callable,
    user: User,
    afghanistan: BusinessArea,
    ticket_afghanistan: GrievanceTicket,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, LIST_PERMISSIONS, afghanistan, whole_business_area_access=True)

    with CaptureQueriesContext(connection) as captured:
        response = api_client(user).get(grievance_list_url(afghanistan.slug))

    assert response.status_code == status.HTTP_200_OK
    statement = main_list_statement(captured, "grievance_grievanceticket")
    assert '"grievance_grievanceticket"."business_area_id" = ' in statement
    # The mixin still resolves the slug to a BusinessArea, so the table stays in the queryset's
    # alias map - joined_tables reports what the compiler actually emits, which is nothing.
    assert "core_businessarea" not in joined_tables(list_queryset(response))


@pytest.mark.parametrize(
    ("url_name", "permissions"),
    [
        ("api:grievance:grievance-tickets-global-list", LIST_PERMISSIONS),
        ("api:programs:programs-list", [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS]),
    ],
    ids=["grievance-global-list", "program-list"],
)
def test_list_of_unknown_business_area_is_rejected_by_the_permission_check(
    api_client: Callable,
    user: User,
    afghanistan: BusinessArea,
    create_user_role_with_permissions: Callable,
    url_name: str,
    permissions: list,
) -> None:
    create_user_role_with_permissions(user, permissions, afghanistan, whole_business_area_access=True)

    response = api_client(user).get(reverse(url_name, kwargs={"business_area_slug": "no-such-business-area"}))

    assert response.status_code == status.HTTP_403_FORBIDDEN
