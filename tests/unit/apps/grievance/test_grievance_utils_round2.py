"""Additional tests for traverse_sibling_tickets covering the non-empty intersection branch."""

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
    return BusinessAreaFactory(slug="test-ba-round2")


@pytest.fixture
def program(business_area: Any) -> Any:
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def rdi(program: Any, business_area: Any) -> Any:
    return RegistrationDataImportFactory(program=program, business_area=business_area)


@pytest.fixture
def household_golden(program: Any, business_area: Any) -> Any:
    return HouseholdFactory(program=program, business_area=business_area, create_role=False)


@pytest.fixture
def household_dup(program: Any, business_area: Any) -> Any:
    return HouseholdFactory(program=program, business_area=business_area, create_role=False)


@pytest.fixture
def individual_golden(household_golden: Any) -> Any:
    return household_golden.head_of_household


@pytest.fixture
def individual_dup(household_dup: Any) -> Any:
    return household_dup.head_of_household


@pytest.fixture
def main_ticket(business_area: Any, rdi: Any) -> Any:
    return GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        issue_type=GrievanceTicket.ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY,
        business_area=business_area,
        status=GrievanceTicket.STATUS_FOR_APPROVAL,
        registration_data_import=rdi,
    )


@pytest.fixture
def sibling_ticket_with_details(
    business_area: Any,
    rdi: Any,
    individual_golden: Any,
    individual_dup: Any,
) -> Any:
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


def test_traverse_sibling_tickets_early_return_when_no_rdi(
    main_ticket: Any,
    individual_golden: Any,
) -> None:
    """When grievance ticket has no rdi, the function returns immediately."""
    main_ticket.registration_data_import = None
    selected = Individual.objects.filter(id=individual_golden.id)
    # Should complete without error and without any DB side-effects.
    traverse_sibling_tickets(main_ticket, selected)


def test_traverse_sibling_tickets_adds_individual_when_intersection_is_non_empty(
    main_ticket: Any,
    sibling_ticket_with_details: Any,
    individual_dup: Any,
) -> None:
    """When a selected individual overlaps with a sibling ticket, it is added to selected_individuals."""
    selected = Individual.objects.filter(id=individual_dup.id)
    sibling_details = sibling_ticket_with_details.needs_adjudication_ticket_details

    assert sibling_details.selected_individuals.count() == 0

    traverse_sibling_tickets(main_ticket, selected)

    assert sibling_details.selected_individuals.filter(id=individual_dup.id).exists()


def test_traverse_sibling_tickets_golden_record_individual_in_intersection(
    main_ticket: Any,
    sibling_ticket_with_details: Any,
    individual_golden: Any,
) -> None:
    """When the golden_records_individual is in the selected set, it is added to selected_individuals."""
    selected = Individual.objects.filter(id=individual_golden.id)
    sibling_details = sibling_ticket_with_details.needs_adjudication_ticket_details

    assert sibling_details.selected_individuals.count() == 0

    traverse_sibling_tickets(main_ticket, selected)

    assert sibling_details.selected_individuals.filter(id=individual_golden.id).exists()
