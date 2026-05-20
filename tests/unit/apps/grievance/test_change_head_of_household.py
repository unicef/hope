from typing import Any, Callable

from django.urls import reverse
import pytest
from rest_framework import status

from extras.test_utils.factories import (
    AreaFactory,
    AreaTypeFactory,
    BusinessAreaFactory,
    CountryFactory,
    GrievanceTicketFactory,
    HouseholdFactory,
    IndividualFactory,
    ProgramFactory,
    TicketIndividualDataUpdateDetailsFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.household.const import AUNT_UNCLE, BROTHER_SISTER, HEAD
from hope.models import Area, BusinessArea, Program, User

pytestmark = [
    pytest.mark.usefixtures("mock_elasticsearch"),
    pytest.mark.django_db,
]


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
    return AreaFactory(name="City Test", area_type=area_type, p_code="asdeeed")


@pytest.fixture
def grievance_context(
    afghanistan: BusinessArea,
    program: Program,
    admin_area: Area,
    user: User,
) -> dict[str, Any]:
    household = HouseholdFactory(
        business_area=afghanistan,
        program=program,
        create_role=False,
    )
    individual1 = IndividualFactory(
        household=household,
        business_area=afghanistan,
        program=program,
        registration_data_import=household.registration_data_import,
        relationship=HEAD,
    )
    individual2 = IndividualFactory(
        household=household,
        business_area=afghanistan,
        program=program,
        registration_data_import=household.registration_data_import,
        relationship=BROTHER_SISTER,
    )
    household.head_of_household = individual1
    household.save(update_fields=["head_of_household"])

    grievance_ticket = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
        admin2=admin_area,
        business_area=afghanistan,
        status=GrievanceTicket.STATUS_FOR_APPROVAL,
        created_by=user,
    )
    grievance_ticket.programs.set([program])
    TicketIndividualDataUpdateDetailsFactory(
        ticket=grievance_ticket,
        individual=individual2,
        individual_data={
            "relationship": {
                "value": "HEAD",
                "approve_status": True,
                "previous_value": "BROTHER_SISTER",
            }
        },
    )
    return {
        "household": household,
        "individual1": individual1,
        "individual2": individual2,
        "grievance_ticket": grievance_ticket,
    }


@pytest.fixture
def close_ticket_url(afghanistan: BusinessArea, grievance_context: dict[str, Any]) -> str:
    grievance_ticket = grievance_context["grievance_ticket"]
    return reverse(
        "api:grievance-tickets:grievance-tickets-global-status-change",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "pk": str(grievance_ticket.pk),
        },
    )


def test_close_update_individual_should_throw_error_when_there_is_one_head_of_household(
    authenticated_client: Any,
    create_user_role_with_permissions: Callable,
    afghanistan: BusinessArea,
    program: Program,
    user: User,
    grievance_context: dict[str, Any],
    close_ticket_url: str,
) -> None:
    create_user_role_with_permissions(
        user,
        [
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
            Permissions.GRIEVANCES_UPDATE,
        ],
        afghanistan,
        program,
    )
    household = grievance_context["household"]
    individual1 = grievance_context["individual1"]
    individual2 = grievance_context["individual2"]
    individual1.relationship = HEAD
    individual1.save(update_fields=["relationship"])
    household.head_of_household = individual1
    household.save(update_fields=["head_of_household"])

    individual1.refresh_from_db()
    individual2.refresh_from_db()
    assert individual1.relationship == HEAD
    assert individual2.relationship == BROTHER_SISTER

    response = authenticated_client.post(
        close_ticket_url,
        {"status": GrievanceTicket.STATUS_CLOSED},
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "There is one head of household. First, you need to change its role." in response.json()

    individual1.refresh_from_db()
    individual2.refresh_from_db()
    assert individual1.relationship == HEAD
    assert individual2.relationship == BROTHER_SISTER


def test_close_update_individual_should_change_head_of_household_if_there_was_no_one(
    authenticated_client: Any,
    create_user_role_with_permissions: Callable,
    afghanistan: BusinessArea,
    program: Program,
    user: User,
    grievance_context: dict[str, Any],
    close_ticket_url: str,
) -> None:
    create_user_role_with_permissions(
        user,
        [
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
            Permissions.GRIEVANCES_UPDATE,
        ],
        afghanistan,
        program,
    )
    household = grievance_context["household"]
    individual1 = grievance_context["individual1"]
    individual2 = grievance_context["individual2"]
    individual1.relationship = AUNT_UNCLE
    individual1.save(update_fields=["relationship"])
    household.head_of_household = individual1
    household.save(update_fields=["head_of_household"])

    response = authenticated_client.post(
        close_ticket_url,
        {"status": GrievanceTicket.STATUS_CLOSED},
        format="json",
    )
    assert response.status_code == status.HTTP_202_ACCEPTED

    individual1.refresh_from_db()
    individual2.refresh_from_db()
    assert individual1.relationship == AUNT_UNCLE
    assert individual2.relationship == HEAD
