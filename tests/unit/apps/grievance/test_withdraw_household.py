from typing import Any

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    AreaFactory,
    AreaTypeFactory,
    BusinessAreaFactory,
    CountryFactory,
    GrievanceTicketFactory,
    HouseholdFactory,
    PartnerFactory,
    ProgramFactory,
    TicketDeleteIndividualDetailsFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.models import GrievanceTicket
from hope.models import Household, Individual, Program

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> Any:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def program(business_area: Any) -> Program:
    return ProgramFactory(
        business_area=business_area,
        status=Program.ACTIVE,
        name="program afghanistan 1",
    )


@pytest.fixture
def area_1() -> Any:
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
    return AreaFactory(name="City Test", area_type=area_type, p_code="dffgh565556")


@pytest.fixture
def user_and_client(api_client: Any) -> dict[str, Any]:
    partner = PartnerFactory(name="TestPartner")
    user = UserFactory(partner=partner)
    return {"user": user, "client": api_client(user)}


def test_withdraw_household_when_withdraw_last_individual_empty(
    create_user_role_with_permissions: Any,
    business_area: Any,
    program: Program,
    area_1: Any,
    user_and_client: dict[str, Any],
) -> None:
    user = user_and_client["user"]
    client = user_and_client["client"]

    create_user_role_with_permissions(
        user,
        [
            Permissions.GRIEVANCES_UPDATE,
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
        ],
        business_area,
        program,
    )

    household = HouseholdFactory(program=program, business_area=business_area, create_role=False)
    individual = household.head_of_household

    ticket = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL,
        admin2=area_1,
        business_area=business_area,
        status=GrievanceTicket.STATUS_FOR_APPROVAL,
    )
    ticket.programs.set([program])
    TicketDeleteIndividualDetailsFactory(
        ticket=ticket,
        individual=individual,
        role_reassign_data={},
        approve_status=True,
    )

    url = reverse(
        "api:grievance-tickets:grievance-tickets-global-status-change",
        kwargs={
            "business_area_slug": business_area.slug,
            "pk": str(ticket.id),
        },
    )
    response = client.post(url, {"status": GrievanceTicket.STATUS_CLOSED}, format="json")
    assert response.status_code == status.HTTP_202_ACCEPTED

    withdrawn_individual = Individual.objects.get(id=individual.id)
    withdrawn_household = Household.objects.get(id=household.id)

    assert withdrawn_individual.withdrawn is True
    assert withdrawn_household.withdrawn is True
