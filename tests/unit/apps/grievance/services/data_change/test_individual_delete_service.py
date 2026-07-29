import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    HouseholdFactory,
    IndividualFactory,
    IndividualRoleInHouseholdFactory,
    ProgramFactory,
    TicketDeleteIndividualDetailsFactory,
    UserFactory,
)
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.services.data_change.individual_delete_service import IndividualDeleteService
from hope.apps.household.const import ROLE_PRIMARY

pytestmark = [
    pytest.mark.usefixtures("mock_elasticsearch"),
    pytest.mark.django_db,
]


@pytest.fixture
def delete_context() -> dict[str, object]:
    business_area = BusinessAreaFactory()
    program = ProgramFactory(business_area=business_area)
    user = UserFactory()
    household = HouseholdFactory(program=program, business_area=business_area, create_role=False)
    individual = household.head_of_household
    IndividualRoleInHouseholdFactory(household=household, individual=individual, role=ROLE_PRIMARY)
    ticket_details = TicketDeleteIndividualDetailsFactory(
        ticket__business_area=business_area,
        ticket__category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        ticket__issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL,
        ticket__status=GrievanceTicket.STATUS_FOR_APPROVAL,
        individual=individual,
        approve_status=True,
        role_reassign_data={},
    )
    ticket = ticket_details.ticket
    ticket.programs.set([program])
    return {
        "business_area": business_area,
        "program": program,
        "user": user,
        "household": household,
        "individual": individual,
        "ticket": ticket,
    }


def test_close_delete_individual_locks_household_and_withdraws(delete_context: dict[str, object]) -> None:
    service = IndividualDeleteService(delete_context["ticket"], {})

    service.close(delete_context["user"])

    delete_context["individual"].refresh_from_db()
    delete_context["household"].refresh_from_db()
    assert delete_context["individual"].withdrawn is True
    assert delete_context["household"].withdrawn is True


def test_close_delete_individual_without_household(delete_context: dict[str, object]) -> None:
    individual_without_household = IndividualFactory(
        business_area=delete_context["business_area"],
        program=delete_context["program"],
    )
    ticket_details = TicketDeleteIndividualDetailsFactory(
        ticket__business_area=delete_context["business_area"],
        ticket__category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        ticket__issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL,
        ticket__status=GrievanceTicket.STATUS_FOR_APPROVAL,
        individual=individual_without_household,
        approve_status=True,
        role_reassign_data={},
    )
    ticket = ticket_details.ticket
    ticket.programs.set([delete_context["program"]])
    service = IndividualDeleteService(ticket, {})

    service.close(delete_context["user"])

    individual_without_household.refresh_from_db()
    assert individual_without_household.household_id is None
    assert individual_without_household.withdrawn is True


def test_close_delete_individual_not_approved_is_noop(delete_context: dict[str, object]) -> None:
    ticket_details = delete_context["ticket"].delete_individual_ticket_details
    ticket_details.approve_status = False
    ticket_details.save()
    service = IndividualDeleteService(delete_context["ticket"], {})

    service.close(delete_context["user"])

    delete_context["individual"].refresh_from_db()
    assert delete_context["individual"].withdrawn is False
