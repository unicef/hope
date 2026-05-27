"""Tests for the grievance-tickets-global ``related-tickets`` action."""

from datetime import datetime
from typing import Any, Callable

from django.utils import timezone
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    HouseholdFactory,
    IndividualFactory,
    PartnerFactory,
    ProgramFactory,
    UserFactory,
)
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory, CountryFactory
from extras.test_utils.factories.grievance import GrievanceTicketFactory
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.models import GrievanceTicket
from hope.models import Area, BusinessArea, Country, Household, Partner, Program, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def afghanistan() -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan", code="AFG")


@pytest.fixture
def partner() -> Partner:
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def user(partner: Partner) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def authenticated_client(api_client: Callable, user: User) -> Any:
    return api_client(user)


@pytest.fixture
def country() -> Country:
    return CountryFactory()


@pytest.fixture
def admin_type(country: Country) -> Any:
    return AreaTypeFactory(country=country, area_level=1)


@pytest.fixture
def area1(admin_type: Any) -> Area:
    return AreaFactory(parent=None, p_code="AF01", area_type=admin_type)


@pytest.fixture
def program(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(
        business_area=afghanistan,
        status=Program.ACTIVE,
        name="program afghanistan 1",
    )


@pytest.fixture
def household(area1: Area, country: Country, program: Program, afghanistan: BusinessArea) -> Household:
    individual = IndividualFactory(business_area=afghanistan, program=program, household=None)
    hh = HouseholdFactory(
        admin1=area1,
        admin2=area1,
        country=country,
        country_origin=country,
        program=program,
        business_area=afghanistan,
        head_of_household=individual,
        start=timezone.now(),
    )
    individual.household = hh
    individual.save()
    return hh


@pytest.fixture
def main_ticket(afghanistan: BusinessArea, area1: Area, user: User, household: Household) -> GrievanceTicket:
    return GrievanceTicketFactory(
        business_area=afghanistan,
        admin2=area1,
        language="Polish",
        consent=True,
        description="Main",
        category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
        issue_type=GrievanceTicket.ISSUE_TYPE_OTHER_COMPLAINT,
        status=GrievanceTicket.STATUS_NEW,
        created_by=user,
        assigned_to=user,
        household_unicef_id=household.unicef_id,
    )


@pytest.fixture
def linked_ticket_a(afghanistan: BusinessArea, area1: Area, user: User) -> GrievanceTicket:
    t = GrievanceTicketFactory(
        business_area=afghanistan,
        admin2=area1,
        language="Polish",
        consent=True,
        description="Linked A",
        category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
        issue_type=GrievanceTicket.ISSUE_TYPE_OTHER_COMPLAINT,
        status=GrievanceTicket.STATUS_NEW,
        created_by=user,
        assigned_to=user,
    )
    t.created_at = timezone.make_aware(datetime(year=2024, month=1, day=10))
    t.save()
    return t


@pytest.fixture
def existing_ticket_b(afghanistan: BusinessArea, area1: Area, user: User, household: Household) -> GrievanceTicket:
    t = GrievanceTicketFactory(
        business_area=afghanistan,
        admin2=area1,
        language="Polish",
        consent=True,
        description="Existing B",
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE,
        status=GrievanceTicket.STATUS_ASSIGNED,
        created_by=user,
        assigned_to=user,
        household_unicef_id=household.unicef_id,
    )
    t.created_at = timezone.make_aware(datetime(year=2024, month=3, day=1))
    t.save()
    return t


@pytest.fixture
def related_tickets_url_name() -> str:
    return "api:grievance:grievance-tickets-global-related-tickets"


def _url(name: str, afghanistan: BusinessArea, ticket: GrievanceTicket) -> str:
    return reverse(
        name,
        kwargs={"business_area_slug": afghanistan.slug, "pk": str(ticket.id)},
    )


def test_related_tickets_returns_rich_fields(
    authenticated_client: Any,
    afghanistan: BusinessArea,
    user: User,
    main_ticket: GrievanceTicket,
    linked_ticket_a: GrievanceTicket,
    existing_ticket_b: GrievanceTicket,
    related_tickets_url_name: str,
    create_user_role_with_permissions: Callable,
) -> None:
    main_ticket.linked_tickets.add(linked_ticket_a)
    create_user_role_with_permissions(
        user=user,
        permissions=[
            Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE,
            Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE,
        ],
        business_area=afghanistan,
        whole_business_area_access=True,
    )

    response = authenticated_client.get(_url(related_tickets_url_name, afghanistan, main_ticket))

    assert response.status_code == status.HTTP_200_OK
    payload = response.data
    returned_ids = {row["id"] for row in payload}
    assert returned_ids == {str(linked_ticket_a.id), str(existing_ticket_b.id)}
    row_a = next(r for r in payload if r["id"] == str(linked_ticket_a.id))
    assert row_a["unicef_id"] == linked_ticket_a.unicef_id
    assert row_a["category"] == linked_ticket_a.category
    assert row_a["issue_type"] == linked_ticket_a.issue_type
    assert row_a["status"] == linked_ticket_a.status


def test_related_tickets_ordered_by_created_at_desc(
    authenticated_client: Any,
    afghanistan: BusinessArea,
    user: User,
    main_ticket: GrievanceTicket,
    linked_ticket_a: GrievanceTicket,
    existing_ticket_b: GrievanceTicket,
    related_tickets_url_name: str,
    create_user_role_with_permissions: Callable,
) -> None:
    main_ticket.linked_tickets.add(linked_ticket_a)
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE],
        business_area=afghanistan,
        whole_business_area_access=True,
    )

    response = authenticated_client.get(_url(related_tickets_url_name, afghanistan, main_ticket))

    assert response.status_code == status.HTTP_200_OK
    created_ats = [GrievanceTicket.objects.get(id=row["id"]).created_at for row in response.data]
    assert created_ats == sorted(created_ats, reverse=True)


def test_related_tickets_requires_detail_permission(
    authenticated_client: Any,
    afghanistan: BusinessArea,
    user: User,
    main_ticket: GrievanceTicket,
    related_tickets_url_name: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[],
        business_area=afghanistan,
        whole_business_area_access=True,
    )

    response = authenticated_client.get(_url(related_tickets_url_name, afghanistan, main_ticket))

    assert response.status_code == status.HTTP_403_FORBIDDEN
