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
def afghanistan() -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan", code="0060")


@pytest.fixture
def user() -> User:
    return UserFactory(first_name="TestUser")


@pytest.fixture
def authenticated_client(api_client: Callable, user: User) -> Any:
    return api_client(user)


@pytest.fixture
def program(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(
        business_area=afghanistan,
        status=Program.ACTIVE,
        name="program afghanistan 1",
    )


@pytest.fixture
def admin_area() -> Area:
    return AreaFactory(name="City Test", p_code="asdfgfhghkjltr")


@pytest.fixture
def complaint_context(afghanistan: BusinessArea, program: Program, user: User) -> dict[str, Any]:
    household = HouseholdFactory(
        business_area=afghanistan,
        program=program,
        create_role=False,
    )
    individual = IndividualFactory(
        household=household,
        business_area=afghanistan,
        program=program,
        registration_data_import=household.registration_data_import,
        given_name="John",
        family_name="Doe",
        middle_name="",
        full_name="John Doe",
    )
    household.head_of_household = individual
    household.save(update_fields=["head_of_household"])

    household2 = HouseholdFactory(
        business_area=afghanistan,
        program=program,
        create_role=False,
    )
    individual2 = IndividualFactory(
        household=household2,
        business_area=afghanistan,
        program=program,
        registration_data_import=household2.registration_data_import,
        given_name="John222",
        family_name="Doe222",
        middle_name="",
        full_name="John Doe222",
    )
    household2.head_of_household = individual2
    household2.save(update_fields=["head_of_household"])

    program_cycle = ProgramCycleFactory(program=program)
    payment_plan = PaymentPlanFactory(program_cycle=program_cycle, business_area=afghanistan, created_by=user)
    payment = PaymentFactory(
        household=household,
        collector=individual,
        business_area=afghanistan,
        parent=payment_plan,
        currency="PLN",
    )
    second_payment = PaymentFactory(
        household=household2,
        collector=individual2,
        business_area=afghanistan,
        parent=payment_plan,
        currency="PLN",
    )
    return {
        "household": household,
        "individual": individual,
        "payment": payment,
        "second_payment": second_payment,
    }


@pytest.fixture
def list_url(afghanistan: BusinessArea) -> str:
    return reverse(
        "api:grievance-tickets:grievance-tickets-global-list",
        kwargs={"business_area_slug": afghanistan.slug},
    )


@pytest.fixture
def complaint_input_builder(user: User, admin_area: Area) -> Callable[..., dict[str, Any]]:
    def _build(
        household: str | None = None,
        individual: str | None = None,
        payment_records: list[str] | None = None,
    ) -> dict[str, Any]:
        return {
            "description": "Test Feedback",
            "assigned_to": str(user.id),
            "category": GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
            "issue_type": GrievanceTicket.ISSUE_TYPE_FSP_COMPLAINT,
            "admin": str(admin_area.id),
            "language": "Polish, English",
            "consent": True,
            "extras": {
                "category": {
                    "grievance_complaint_ticket_extras": {
                        "household": household,
                        "individual": individual,
                        "payment_record": payment_records,
                    }
                }
            },
        }

    return _build


@pytest.mark.parametrize(
    (
        "household_key",
        "individual_key",
        "payment_keys",
    ),
    [
        ("household", "individual", ["payment"]),
        ("household", "individual", []),
        ("household", "individual", ["payment", "second_payment"]),
        (None, "individual", ["payment"]),
        ("household", None, ["payment"]),
        (None, None, []),
    ],
)
def test_create_complaint_ticket_variants(
    authenticated_client: Any,
    create_user_role_with_permissions: Callable,
    afghanistan: BusinessArea,
    program: Program,
    user: User,
    complaint_context: dict[str, Any],
    complaint_input_builder: Callable[..., dict[str, Any]],
    list_url: str,
    household_key: str | None,
    individual_key: str | None,
    payment_keys: list[str],
) -> None:
    create_user_role_with_permissions(user, [Permissions.GRIEVANCES_CREATE], afghanistan, program)
    household_id = str(complaint_context[household_key].id) if household_key else None
    individual_id = str(complaint_context[individual_key].id) if individual_key else None
    payment_ids = [str(complaint_context[key].id) for key in payment_keys]
    input_data = complaint_input_builder(
        household=household_id,
        individual=individual_id,
        payment_records=payment_ids,
    )

    response = authenticated_client.post(list_url, input_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert "id" in response.json()[0]
