"""Tests for grievance update referral ticket functionality."""

from typing import Any, Callable

from django.urls import reverse
import pytest
from rest_framework import status

from extras.test_utils.factories import (
    AreaFactory,
    AreaTypeFactory,
    BusinessAreaFactory,
    CountryFactory,
    HouseholdFactory,
    IndividualFactory,
    PartnerFactory,
    ProgramFactory,
    UserFactory,
)
from extras.test_utils.factories.grievance import TicketReferralDetailsFactory
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.models import GrievanceTicket
from hope.models import BusinessArea, Program


@pytest.fixture
def afghanistan() -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan")


@pytest.fixture
def partner() -> PartnerFactory:
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def user(partner: PartnerFactory) -> UserFactory:
    return UserFactory(partner=partner, first_name="TestUser")


@pytest.fixture
def program(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(
        business_area=afghanistan,
        status=Program.ACTIVE,
        name="program afghanistan 1",
    )


@pytest.fixture
def admin_area(afghanistan: BusinessArea) -> AreaFactory:
    country = CountryFactory(name="Afghanistan")
    area_type = AreaTypeFactory(
        name="Admin type one",
        country=country,
        area_level=2,
    )
    return AreaFactory(name="City Test", area_type=area_type, p_code="asdfgfhghkjltr")


@pytest.fixture
def household_and_individual(afghanistan: BusinessArea, program: Program) -> dict:
    individual = IndividualFactory(
        given_name="John",
        family_name="Doe",
        full_name="John Doe",
        business_area=afghanistan,
        program=program,
        household=None,
    )
    household = HouseholdFactory(
        size=1,
        business_area=afghanistan,
        program=program,
        head_of_household=individual,
    )
    individual.household = household
    individual.save()

    return {
        "household": household,
        "individuals": [individual],
    }


@pytest.fixture
def referral_ticket(afghanistan: BusinessArea, program: Program):
    ticket = TicketReferralDetailsFactory(
        ticket__business_area=afghanistan,
        ticket__status=GrievanceTicket.STATUS_NEW,
        ticket__language="",
    )
    ticket.ticket.programs.set([program])
    return ticket


@pytest.fixture
def detail_url(afghanistan: BusinessArea, referral_ticket) -> str:
    return reverse(
        "api:grievance-tickets:grievance-tickets-global-detail",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "pk": str(referral_ticket.ticket.pk),
        },
    )


def test_update_referral_ticket_without_extras(
    api_client: Any,
    user: UserFactory,
    admin_area: AreaFactory,
    afghanistan: BusinessArea,
    program: Program,
    referral_ticket,
    detail_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, [Permissions.GRIEVANCES_UPDATE], afghanistan, program)

    ticket = referral_ticket.ticket

    assert ticket.assigned_to is None
    assert ticket.language == ""
    assert ticket.admin2 is None

    input_data = {
        "assigned_to": str(user.id),
        "admin": str(admin_area.id),
        "language": "Polish, English, ESP",
    }

    client = api_client(user)
    response = client.patch(detail_url, input_data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["language"] == "Polish, English, ESP"
    assert response.json()["assigned_to"]["first_name"] == "TestUser"
    assert response.json()["admin"] == "City Test"

    ticket.refresh_from_db()
    assert ticket.language == "Polish, English, ESP"
    assert ticket.admin2 == admin_area
    assert ticket.assigned_to == user


def test_update_referral_ticket_with_household_extras(
    api_client: Any,
    user: UserFactory,
    admin_area: AreaFactory,
    afghanistan: BusinessArea,
    program: Program,
    household_and_individual: dict,
    referral_ticket,
    detail_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, [Permissions.GRIEVANCES_UPDATE], afghanistan, program)

    input_data = {
        "assigned_to": str(user.id),
        "admin": str(admin_area.id),
        "language": "Polish, English, ESP",
        "extras": {
            "category": {
                "referral_ticket_extras": {
                    "household": str(household_and_individual["household"].id),
                }
            }
        },
    }

    client = api_client(user)
    response = client.patch(detail_url, input_data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["household"]["id"] == str(household_and_individual["household"].id)


def test_update_referral_ticket_with_individual_extras(
    api_client: Any,
    user: UserFactory,
    admin_area: AreaFactory,
    afghanistan: BusinessArea,
    program: Program,
    household_and_individual: dict,
    referral_ticket,
    detail_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, [Permissions.GRIEVANCES_UPDATE], afghanistan, program)

    input_data = {
        "assigned_to": str(user.id),
        "admin": str(admin_area.id),
        "language": "Polish, English, ESP",
        "extras": {
            "category": {
                "referral_ticket_extras": {
                    "individual": str(household_and_individual["individuals"][0].id),
                }
            }
        },
    }

    client = api_client(user)
    response = client.patch(detail_url, input_data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["individual"]["id"] == str(household_and_individual["individuals"][0].id)


def test_update_referral_ticket_with_household_and_individual_extras(
    api_client: Any,
    user: UserFactory,
    admin_area: AreaFactory,
    afghanistan: BusinessArea,
    program: Program,
    household_and_individual: dict,
    referral_ticket,
    detail_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, [Permissions.GRIEVANCES_UPDATE], afghanistan, program)

    input_data = {
        "assigned_to": str(user.id),
        "admin": str(admin_area.id),
        "language": "Polish, English, ESP",
        "extras": {
            "category": {
                "referral_ticket_extras": {
                    "individual": str(household_and_individual["individuals"][0].id),
                    "household": str(household_and_individual["household"].id),
                }
            }
        },
    }

    client = api_client(user)
    response = client.patch(detail_url, input_data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["individual"]["id"] == str(household_and_individual["individuals"][0].id)
    assert response.json()["household"]["id"] == str(household_and_individual["household"].id)
