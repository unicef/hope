"""Tests for grievance utils — traverse_sibling_tickets intersection guard."""

from typing import Any

import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    GrievanceTicketFactory,
    HouseholdFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    TicketNeedsAdjudicationDetailsFactory,
)
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.utils import traverse_sibling_tickets
from hope.models import Individual

pytestmark = [
    pytest.mark.usefixtures("mock_elasticsearch"),
    pytest.mark.django_db,
]


@pytest.fixture
def business_area() -> Any:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def program(business_area: Any) -> Any:
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def rdi(program: Any, business_area: Any) -> Any:
    return RegistrationDataImportFactory(program=program, business_area=business_area)


@pytest.fixture
def household_golden(program: Any, business_area: Any, rdi: Any) -> Any:
    return HouseholdFactory(program=program, business_area=business_area, create_role=False)


@pytest.fixture
def household_dup(program: Any, business_area: Any, rdi: Any) -> Any:
    return HouseholdFactory(program=program, business_area=business_area, create_role=False)


@pytest.fixture
def individual_golden(household_golden: Any) -> Any:
    return household_golden.head_of_household


@pytest.fixture
def individual_dup(household_dup: Any) -> Any:
    return household_dup.head_of_household


@pytest.fixture
def grievance_ticket(business_area: Any, rdi: Any) -> Any:
    return GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        issue_type=GrievanceTicket.ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY,
        business_area=business_area,
        status=GrievanceTicket.STATUS_FOR_APPROVAL,
        registration_data_import=rdi,
    )


@pytest.fixture
def sibling_ticket(business_area: Any, rdi: Any, individual_golden: Any, individual_dup: Any) -> Any:
    ticket = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        issue_type=GrievanceTicket.ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY,
        business_area=business_area,
        status=GrievanceTicket.STATUS_NEW,
        registration_data_import=rdi,
    )
    details = TicketNeedsAdjudicationDetailsFactory(
        ticket=ticket,
        golden_records_individual=individual_golden,
        possible_duplicate=individual_dup,
        is_multiple_duplicates_version=True,
        selected_individual=None,
    )
    details.possible_duplicates.add(individual_dup)
    return ticket


def test_traverse_sibling_tickets_no_rdi_returns_early(
    grievance_ticket: Any,
    individual_golden: Any,
) -> None:
    # When the ticket has no rdi the function returns immediately without error.
    grievance_ticket.registration_data_import = None
    selected = Individual.objects.filter(id=individual_golden.id)
    # Should not raise and should not modify anything.
    traverse_sibling_tickets(grievance_ticket, selected)


def test_traverse_sibling_tickets_empty_intersection_skips_add(
    grievance_ticket: Any,
    sibling_ticket: Any,
    individual_golden: Any,
    individual_dup: Any,
    program: Any,
    business_area: Any,
    rdi: Any,
) -> None:
    # Use an individual that is NOT in the sibling ticket — intersection will be empty.
    unrelated_household = HouseholdFactory(program=program, business_area=business_area, create_role=False)
    unrelated_individual = unrelated_household.head_of_household

    selected = Individual.objects.filter(id=unrelated_individual.id)
    sibling_details = sibling_ticket.needs_adjudication_ticket_details
    initial_selected_count = sibling_details.selected_individuals.count()

    traverse_sibling_tickets(grievance_ticket, selected)

    sibling_details.refresh_from_db()
    assert sibling_details.selected_individuals.count() == initial_selected_count


def test_traverse_sibling_tickets_non_empty_intersection_adds_individuals(
    grievance_ticket: Any,
    sibling_ticket: Any,
    individual_dup: Any,
) -> None:
    # Use individual_dup which IS in the sibling ticket's possible_duplicates.
    selected = Individual.objects.filter(id=individual_dup.id)
    sibling_details = sibling_ticket.needs_adjudication_ticket_details

    assert sibling_details.selected_individuals.count() == 0

    traverse_sibling_tickets(grievance_ticket, selected)

    assert sibling_details.selected_individuals.filter(id=individual_dup.id).exists()
