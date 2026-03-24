from typing import Any, Callable

from django.urls import reverse
import pytest
from rest_framework import status

from extras.test_utils.factories import (
    AreaFactory,
    AreaTypeFactory,
    BusinessAreaFactory,
    CountryFactory,
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
    country = CountryFactory(
        name="Afghanistan",
        short_name="Afghanistan",
        iso_code2="AF",
        iso_code3="AFG",
        iso_num="0004",
    )
    area_type = AreaTypeFactory(
        name="Admin type one",
        country=country,
        area_level=2,
    )
    return AreaFactory(name="City Test", area_type=area_type, p_code="asdfgfhghkjltr")


@pytest.fixture
def list_url(afghanistan: BusinessArea) -> str:
    return reverse(
        "api:grievance-tickets:grievance-tickets-global-list",
        kwargs={"business_area_slug": afghanistan.slug},
    )


@pytest.mark.parametrize(
    "category",
    [
        GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK,
        GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
    ],
)
def test_create_feedback_ticket_not_supported(
    authenticated_client: Any,
    create_user_role_with_permissions: Callable,
    afghanistan: BusinessArea,
    program: Program,
    user: User,
    admin_area: Area,
    list_url: str,
    category: int,
) -> None:
    create_user_role_with_permissions(user, [Permissions.GRIEVANCES_CREATE], afghanistan, program)
    input_data = {
        "description": "Test Feedback AaaaQwooL",
        "assigned_to": str(user.id),
        "category": category,
        "admin": str(admin_area.id),
        "language": "Polish, English",
        "consent": True,
    }

    response = authenticated_client.post(list_url, input_data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Feedback tickets are not allowed to be created through this mutation." in response.json()
