from typing import Any, Callable

from django.urls import reverse
import pytest
from rest_framework import status

from extras.test_utils.factories import (
    AreaFactory,
    BusinessAreaFactory,
    HouseholdFactory,
    IndividualFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.models import GrievanceTicket
from hope.models import Area, BusinessArea, Program, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan", code="0060")


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture
def authenticated_client(api_client: Callable, user: User) -> Any:
    return api_client(user)


@pytest.fixture
def program(business_area: BusinessArea) -> Program:
    return ProgramFactory(status=Program.ACTIVE, business_area=business_area)


@pytest.fixture
def admin_area() -> Area:
    return AreaFactory(name="City Test", p_code="asdfgfhghkjltr")


@pytest.fixture
def household_context(business_area: BusinessArea, program: Program) -> dict[str, Any]:
    household = HouseholdFactory(
        business_area=business_area,
        program=program,
        create_role=False,
    )
    individual = IndividualFactory(
        household=household,
        business_area=business_area,
        program=program,
        registration_data_import=household.registration_data_import,
        given_name="John",
        family_name="Doe",
        middle_name="",
        full_name="John Doe",
    )
    household.head_of_household = individual
    household.save(update_fields=["head_of_household"])
    return {"household": household, "individual": individual}


@pytest.fixture
def list_url(business_area: BusinessArea) -> str:
    return reverse(
        "api:grievance-tickets:grievance-tickets-global-list",
        kwargs={"business_area_slug": business_area.slug},
    )


@pytest.fixture
def referral_input_builder(user: User, admin_area: Area) -> Callable[..., dict[str, Any]]:
    def _build(extras: dict[str, Any] | None = None) -> dict[str, Any]:
        input_data = {
            "description": "Test Feedback",
            "assigned_to": str(user.id),
            "category": GrievanceTicket.CATEGORY_REFERRAL,
            "admin": str(admin_area.id),
            "language": "Polish, English",
            "consent": True,
            "business_area": "afghanistan",
        }
        if extras is not None:
            input_data["extras"] = {"category": {"referral_ticket_extras": extras}}
        return input_data

    return _build


def test_create_referral_ticket_without_extras(
    authenticated_client: Any,
    create_user_role_with_permissions: Callable,
    user: User,
    business_area: BusinessArea,
    program: Program,
    referral_input_builder: Callable[..., dict[str, Any]],
    list_url: str,
) -> None:
    create_user_role_with_permissions(user, [Permissions.GRIEVANCES_CREATE], business_area, program)
    input_data = referral_input_builder()

    response = authenticated_client.post(list_url, input_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED


def test_create_referral_ticket_with_household_extras(
    authenticated_client: Any,
    create_user_role_with_permissions: Callable,
    user: User,
    business_area: BusinessArea,
    program: Program,
    household_context: dict[str, Any],
    referral_input_builder: Callable[..., dict[str, Any]],
    list_url: str,
) -> None:
    create_user_role_with_permissions(user, [Permissions.GRIEVANCES_CREATE], business_area, program)
    household = household_context["household"]
    input_data = referral_input_builder(extras={"household": str(household.id)})

    response = authenticated_client.post(list_url, input_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()[0]["household"]["unicef_id"] == household.unicef_id
    assert response.json()[0]["individual"] is None


def test_create_referral_ticket_with_individual_extras(
    authenticated_client: Any,
    create_user_role_with_permissions: Callable,
    user: User,
    business_area: BusinessArea,
    program: Program,
    household_context: dict[str, Any],
    referral_input_builder: Callable[..., dict[str, Any]],
    list_url: str,
) -> None:
    create_user_role_with_permissions(user, [Permissions.GRIEVANCES_CREATE], business_area, program)
    individual = household_context["individual"]
    input_data = referral_input_builder(extras={"individual": str(individual.id)})

    response = authenticated_client.post(list_url, input_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()[0]["individual"]["unicef_id"] == individual.unicef_id
    assert response.json()[0]["household"] is None


def test_create_referral_ticket_with_household_and_individual_extras(
    authenticated_client: Any,
    create_user_role_with_permissions: Callable,
    user: User,
    business_area: BusinessArea,
    program: Program,
    household_context: dict[str, Any],
    referral_input_builder: Callable[..., dict[str, Any]],
    list_url: str,
) -> None:
    create_user_role_with_permissions(user, [Permissions.GRIEVANCES_CREATE], business_area, program)
    household = household_context["household"]
    individual = household_context["individual"]
    input_data = referral_input_builder(
        extras={
            "household": str(household.id),
            "individual": str(individual.id),
        }
    )

    response = authenticated_client.post(list_url, input_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()[0]["individual"]["unicef_id"] == individual.unicef_id
    assert response.json()[0]["household"]["unicef_id"] == household.unicef_id
