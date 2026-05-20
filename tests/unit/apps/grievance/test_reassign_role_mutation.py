from typing import Any

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
    IndividualRoleInHouseholdFactory,
    PartnerFactory,
    ProgramFactory,
    TicketDeleteIndividualDetailsFactory,
    TicketNeedsAdjudicationDetailsFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.household.const import ROLE_PRIMARY
from hope.models import Program

pytestmark = pytest.mark.django_db


@pytest.fixture
def common_context(api_client: Any) -> dict[str, Any]:
    country = CountryFactory(
        name="Afghanistan",
        short_name="Afghanistan",
        iso_code2="AF",
        iso_code3="AFG",
        iso_num="0004",
    )
    business_area = BusinessAreaFactory(slug="afghanistan")
    partner = PartnerFactory(name="TestPartner")
    user = UserFactory(partner=partner, first_name="TestUser")
    client = api_client(user)
    program = ProgramFactory(
        business_area=business_area,
        status=Program.ACTIVE,
        name="program afghanistan 1",
    )
    area_type = AreaTypeFactory(
        name="Admin type one",
        country=country,
        area_level=2,
    )
    admin_area = AreaFactory(name="City Test", area_type=area_type, p_code="asdfgfhghkjltr")
    return {
        "business_area": business_area,
        "user": user,
        "client": client,
        "program": program,
        "admin_area": admin_area,
    }


@pytest.fixture
def delete_individual_context(common_context: dict[str, Any]) -> dict[str, Any]:
    program = common_context["program"]
    business_area = common_context["business_area"]
    household = HouseholdFactory(
        program=program,
        business_area=business_area,
        create_role=False,
    )
    individual = household.head_of_household
    role = IndividualRoleInHouseholdFactory(
        household=household,
        individual=individual,
        role=ROLE_PRIMARY,
    )
    grievance_ticket = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL,
        admin2=common_context["admin_area"],
        business_area=business_area,
        status=GrievanceTicket.STATUS_FOR_APPROVAL,
    )
    grievance_ticket.programs.set([program])
    TicketDeleteIndividualDetailsFactory(
        ticket=grievance_ticket,
        individual=individual,
        approve_status=True,
    )
    return {
        **common_context,
        "household": household,
        "individual": individual,
        "role": role,
        "grievance_ticket": grievance_ticket,
    }


@pytest.fixture
def needs_adjudication_context(common_context: dict[str, Any]) -> dict[str, Any]:
    program = common_context["program"]
    business_area = common_context["business_area"]
    household = HouseholdFactory(
        program=program,
        business_area=business_area,
        create_role=False,
    )
    individual_1 = household.head_of_household
    individual_2 = IndividualFactory(
        household=household,
        program=program,
        business_area=business_area,
        registration_data_import=household.registration_data_import,
        full_name="Andrew Jackson",
        given_name="Andrew",
        family_name="Jackson",
        phone_no="(853)692-4696",
        birth_date="1963-09-12",
    )
    role = IndividualRoleInHouseholdFactory(
        household=household,
        individual=individual_1,
        role=ROLE_PRIMARY,
    )
    grievance_ticket = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        issue_type=GrievanceTicket.ISSUE_TYPE_UNIQUE_IDENTIFIERS_SIMILARITY,
        admin2=common_context["admin_area"],
        business_area=business_area,
        status=GrievanceTicket.STATUS_FOR_APPROVAL,
    )
    grievance_ticket.programs.set([program])
    TicketNeedsAdjudicationDetailsFactory(
        ticket=grievance_ticket,
        golden_records_individual=individual_1,
        possible_duplicate=individual_2,
        is_multiple_duplicates_version=True,
        selected_individual=None,
    )
    return {
        **common_context,
        "household": household,
        "individual_1": individual_1,
        "individual_2": individual_2,
        "role": role,
        "grievance_ticket": grievance_ticket,
    }


def test_role_reassignment(
    create_user_role_with_permissions: Any,
    delete_individual_context: dict[str, Any],
) -> None:
    create_user_role_with_permissions(
        delete_individual_context["user"],
        [Permissions.GRIEVANCES_UPDATE],
        delete_individual_context["business_area"],
        delete_individual_context["program"],
    )
    response = delete_individual_context["client"].post(
        reverse(
            "api:grievance-tickets:grievance-tickets-global-reassign-role",
            kwargs={
                "business_area_slug": delete_individual_context["business_area"].slug,
                "pk": str(delete_individual_context["grievance_ticket"].id),
            },
        ),
        {
            "household_id": str(delete_individual_context["household"].id),
            "individual_id": str(delete_individual_context["individual"].id),
            "role": ROLE_PRIMARY,
            "version": delete_individual_context["grievance_ticket"].version,
        },
        format="json",
    )
    response_data = response.json()
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert "id" in response_data

    delete_individual_context["grievance_ticket"].refresh_from_db()
    ticket_details = delete_individual_context["grievance_ticket"].delete_individual_ticket_details
    expected_data = {
        str(delete_individual_context["role"].id): {
            "role": "PRIMARY",
            "household": str(delete_individual_context["household"].id),
            "individual": str(delete_individual_context["individual"].id),
        }
    }
    assert ticket_details.role_reassign_data == expected_data


def test_role_reassignment_new_ticket(
    create_user_role_with_permissions: Any,
    needs_adjudication_context: dict[str, Any],
) -> None:
    create_user_role_with_permissions(
        needs_adjudication_context["user"],
        [Permissions.GRIEVANCES_UPDATE],
        needs_adjudication_context["business_area"],
        needs_adjudication_context["program"],
    )
    response = needs_adjudication_context["client"].post(
        reverse(
            "api:grievance-tickets:grievance-tickets-global-reassign-role",
            kwargs={
                "business_area_slug": needs_adjudication_context["business_area"].slug,
                "pk": str(needs_adjudication_context["grievance_ticket"].id),
            },
        ),
        {
            "household_id": str(needs_adjudication_context["household"].id),
            "individual_id": str(needs_adjudication_context["individual_1"].id),
            "new_individual_id": str(needs_adjudication_context["individual_2"].id),
            "role": ROLE_PRIMARY,
            "version": needs_adjudication_context["grievance_ticket"].version,
        },
        format="json",
    )
    response_data = response.json()
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert "id" in response_data

    needs_adjudication_context["grievance_ticket"].refresh_from_db()
    ticket_details = needs_adjudication_context["grievance_ticket"].ticket_details
    expected_data = {
        str(needs_adjudication_context["role"].id): {
            "role": "PRIMARY",
            "household": str(needs_adjudication_context["household"].id),
            "individual": str(needs_adjudication_context["individual_1"].id),
            "new_individual": str(needs_adjudication_context["individual_2"].id),
        }
    }
    assert ticket_details.role_reassign_data == expected_data
