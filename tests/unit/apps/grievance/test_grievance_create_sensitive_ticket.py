from typing import Any, Callable

from django.urls import reverse
import pytest
from rest_framework import status

from extras.test_utils.factories import (
    AreaFactory,
    BusinessAreaFactory,
    HouseholdFactory,
    IndividualFactory,
    PaymentFactory,
    PaymentPlanFactory,
    ProgramCycleFactory,
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
    return AreaFactory(name="City Test", p_code="asfdsfg")


@pytest.fixture
def sensitive_context(business_area: BusinessArea, program: Program, user: User) -> dict[str, Any]:
    household1 = HouseholdFactory(
        business_area=business_area,
        program=program,
        create_role=False,
    )
    individual1 = IndividualFactory(
        household=household1,
        business_area=business_area,
        program=program,
        registration_data_import=household1.registration_data_import,
        given_name="John",
        family_name="Doe",
        middle_name="",
        full_name="John Doe",
    )
    household1.head_of_household = individual1
    household1.save(update_fields=["head_of_household"])

    household2 = HouseholdFactory(
        business_area=business_area,
        program=program,
        create_role=False,
    )
    individual2 = IndividualFactory(
        household=household2,
        business_area=business_area,
        program=program,
        registration_data_import=household2.registration_data_import,
        given_name="John",
        family_name="Doe",
        middle_name="",
        full_name="John Doe Second Individual",
    )
    household2.head_of_household = individual2
    household2.save(update_fields=["head_of_household"])

    program_cycle = ProgramCycleFactory(program=program)
    payment_plan = PaymentPlanFactory(program_cycle=program_cycle, business_area=business_area, created_by=user)
    payment = PaymentFactory(
        household=household1,
        collector=individual1,
        business_area=business_area,
        parent=payment_plan,
        currency="PLN",
    )
    second_payment = PaymentFactory(
        household=household2,
        collector=individual2,
        business_area=business_area,
        parent=payment_plan,
        currency="PLN",
    )

    return {
        "household1": household1,
        "individual1": individual1,
        "payment": payment,
        "second_payment": second_payment,
    }


@pytest.fixture
def list_url(business_area: BusinessArea) -> str:
    return reverse(
        "api:grievance-tickets:grievance-tickets-global-list",
        kwargs={"business_area_slug": business_area.slug},
    )


@pytest.fixture
def sensitive_input_builder(user: User, admin_area: Area) -> Callable[..., dict[str, Any]]:
    def _build(
        *,
        issue_type: int | None = GrievanceTicket.ISSUE_TYPE_MISCELLANEOUS,
        extras_key: str = "sensitive_grievance_ticket_extras",
        extras: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        input_data = {
            "description": "Test Feedback",
            "assigned_to": str(user.id),
            "category": GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
            "admin": str(admin_area.id),
            "language": "Polish, English",
            "consent": True,
        }
        if issue_type is not None:
            input_data["issue_type"] = issue_type
        if extras is not None:
            input_data["extras"] = {"category": {extras_key: extras}}
        return input_data

    return _build


def test_create_sensitive_ticket(
    authenticated_client: Any,
    create_user_role_with_permissions: Callable,
    user: User,
    business_area: BusinessArea,
    program: Program,
    sensitive_context: dict[str, Any],
    sensitive_input_builder: Callable[..., dict[str, Any]],
    list_url: str,
) -> None:
    create_user_role_with_permissions(user, [Permissions.GRIEVANCES_CREATE], business_area, program)
    input_data = sensitive_input_builder(
        extras={
            "household": str(sensitive_context["household1"].id),
            "individual": str(sensitive_context["individual1"].id),
        }
    )
    response = authenticated_client.post(list_url, input_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()[0]["payment_record"] is None


def test_create_sensitive_ticket_wrong_extras(
    authenticated_client: Any,
    create_user_role_with_permissions: Callable,
    user: User,
    business_area: BusinessArea,
    program: Program,
    sensitive_context: dict[str, Any],
    sensitive_input_builder: Callable[..., dict[str, Any]],
    list_url: str,
) -> None:
    create_user_role_with_permissions(user, [Permissions.GRIEVANCES_CREATE], business_area, program)
    input_data = sensitive_input_builder(
        extras_key="grievance_complaint_ticket_extras",
        extras={
            "household": str(sensitive_context["household1"].id),
            "individual": str(sensitive_context["individual1"].id),
        },
    )
    response = authenticated_client.post(list_url, input_data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "You can't provide extras.category.grievance_complaint_ticket_extras in 3" in str(response.json())


def test_create_sensitive_ticket_without_issue_type(
    authenticated_client: Any,
    create_user_role_with_permissions: Callable,
    user: User,
    business_area: BusinessArea,
    program: Program,
    sensitive_context: dict[str, Any],
    sensitive_input_builder: Callable[..., dict[str, Any]],
    list_url: str,
) -> None:
    create_user_role_with_permissions(user, [Permissions.GRIEVANCES_CREATE], business_area, program)
    input_data = sensitive_input_builder(
        issue_type=None,
        extras={
            "household": str(sensitive_context["household1"].id),
            "individual": str(sensitive_context["individual1"].id),
            "payment_record": [str(sensitive_context["payment"].id)],
        },
    )
    response = authenticated_client.post(list_url, input_data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "You have to provide issue_type in 3" in response.json()


def test_create_sensitive_ticket_with_two_payment_records(
    authenticated_client: Any,
    create_user_role_with_permissions: Callable,
    user: User,
    business_area: BusinessArea,
    program: Program,
    sensitive_context: dict[str, Any],
    sensitive_input_builder: Callable[..., dict[str, Any]],
    list_url: str,
) -> None:
    create_user_role_with_permissions(user, [Permissions.GRIEVANCES_CREATE], business_area, program)
    input_data = sensitive_input_builder(
        extras={
            "household": str(sensitive_context["household1"].id),
            "individual": str(sensitive_context["individual1"].id),
            "payment_record": [str(sensitive_context["payment"].id), str(sensitive_context["second_payment"].id)],
        }
    )

    response = authenticated_client.post(list_url, input_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()[0]["payment_record"] is not None


def test_create_sensitive_ticket_without_payment_record(
    authenticated_client: Any,
    create_user_role_with_permissions: Callable,
    user: User,
    business_area: BusinessArea,
    program: Program,
    sensitive_context: dict[str, Any],
    sensitive_input_builder: Callable[..., dict[str, Any]],
    list_url: str,
) -> None:
    create_user_role_with_permissions(user, [Permissions.GRIEVANCES_CREATE], business_area, program)
    input_data = sensitive_input_builder(
        extras={
            "household": str(sensitive_context["household1"].id),
            "individual": str(sensitive_context["individual1"].id),
        }
    )
    response = authenticated_client.post(list_url, input_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()[0]["payment_record"] is None


def test_create_sensitive_ticket_without_household(
    authenticated_client: Any,
    create_user_role_with_permissions: Callable,
    user: User,
    business_area: BusinessArea,
    program: Program,
    sensitive_context: dict[str, Any],
    sensitive_input_builder: Callable[..., dict[str, Any]],
    list_url: str,
) -> None:
    create_user_role_with_permissions(user, [Permissions.GRIEVANCES_CREATE], business_area, program)
    input_data = sensitive_input_builder(extras={"individual": str(sensitive_context["individual1"].id)})
    response = authenticated_client.post(list_url, input_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()[0]["payment_record"] is None
    assert response.json()[0]["household"] is None
    assert response.json()[0]["individual"] is not None


def test_create_sensitive_ticket_without_individual(
    authenticated_client: Any,
    create_user_role_with_permissions: Callable,
    user: User,
    business_area: BusinessArea,
    program: Program,
    sensitive_context: dict[str, Any],
    sensitive_input_builder: Callable[..., dict[str, Any]],
    list_url: str,
) -> None:
    create_user_role_with_permissions(user, [Permissions.GRIEVANCES_CREATE], business_area, program)
    input_data = sensitive_input_builder(extras={"household": str(sensitive_context["household1"].id)})
    response = authenticated_client.post(list_url, input_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()[0]["individual"] is None
    assert response.json()[0]["payment_record"] is None
    assert response.json()[0]["household"] is not None


def test_create_sensitive_ticket_without_extras(
    authenticated_client: Any,
    create_user_role_with_permissions: Callable,
    user: User,
    business_area: BusinessArea,
    program: Program,
    sensitive_input_builder: Callable[..., dict[str, Any]],
    list_url: str,
) -> None:
    create_user_role_with_permissions(user, [Permissions.GRIEVANCES_CREATE], business_area, program)
    input_data = sensitive_input_builder(extras=None)
    response = authenticated_client.post(list_url, input_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()[0]["individual"] is None
    assert response.json()[0]["payment_record"] is None
    assert response.json()[0]["household"] is None
