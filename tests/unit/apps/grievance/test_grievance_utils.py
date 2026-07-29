"""Tests for grievance utils — traverse_sibling_tickets intersection guard."""

from unittest.mock import patch
from uuid import uuid4

from django.core.files.uploadedfile import SimpleUploadedFile
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    GrievanceDocumentFactory,
    GrievanceTicketFactory,
    HouseholdFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    TicketHouseholdDataUpdateDetailsFactory,
    TicketNeedsAdjudicationDetailsFactory,
)
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.utils import clear_cache, traverse_sibling_tickets, update_grievance_documents
from hope.models import Individual

pytestmark = [
    pytest.mark.usefixtures("mock_elasticsearch"),
    pytest.mark.django_db,
]


@pytest.fixture
def business_area() -> object:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def program(business_area: object) -> object:
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def rdi(program: object, business_area: object) -> object:
    return RegistrationDataImportFactory(program=program, business_area=business_area)


@pytest.fixture
def household_golden(program: object, business_area: object, rdi: object) -> object:
    return HouseholdFactory(program=program, business_area=business_area, create_role=False)


@pytest.fixture
def household_dup(program: object, business_area: object, rdi: object) -> object:
    return HouseholdFactory(program=program, business_area=business_area, create_role=False)


@pytest.fixture
def individual_golden(household_golden: object) -> object:
    return household_golden.head_of_household


@pytest.fixture
def individual_dup(household_dup: object) -> object:
    return household_dup.head_of_household


@pytest.fixture
def grievance_ticket(business_area: object, rdi: object) -> object:
    return GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        issue_type=GrievanceTicket.ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY,
        business_area=business_area,
        status=GrievanceTicket.STATUS_FOR_APPROVAL,
        registration_data_import=rdi,
    )


@pytest.fixture
def sibling_ticket(business_area: object, rdi: object, individual_golden: object, individual_dup: object) -> object:
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


@pytest.fixture
def household_update_details(business_area: object, household_golden: object) -> object:
    ticket = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE,
        business_area=business_area,
    )
    return TicketHouseholdDataUpdateDetailsFactory(ticket=ticket, household=household_golden, household_data={})


@pytest.fixture
def grievance_document(business_area: object) -> object:
    ticket = GrievanceTicketFactory(business_area=business_area)
    return GrievanceDocumentFactory(
        grievance_ticket=ticket,
        file=SimpleUploadedFile("old.jpg", b"old-bytes", content_type="image/jpeg"),
        file_size=9,
    )


def test_traverse_sibling_tickets_no_rdi_returns_early(
    grievance_ticket: object,
    individual_golden: object,
) -> None:
    # When the ticket has no rdi the function returns immediately without error.
    grievance_ticket.registration_data_import = None
    selected = Individual.objects.filter(id=individual_golden.id)
    # Should not raise and should not modify anything.
    traverse_sibling_tickets(grievance_ticket, selected)


def test_traverse_sibling_tickets_empty_intersection_skips_add(
    grievance_ticket: object,
    sibling_ticket: object,
    individual_golden: object,
    individual_dup: object,
    program: object,
    business_area: object,
    rdi: object,
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


def test_traverse_sibling_tickets_empty_selected_returns_early(
    grievance_ticket: object,
    sibling_ticket: object,
) -> None:
    # Empty queryset → selected_individual_ids = [] → returns immediately, no DB writes.
    sibling_details = sibling_ticket.needs_adjudication_ticket_details
    initial_count = sibling_details.selected_individuals.count()

    traverse_sibling_tickets(grievance_ticket, Individual.objects.none())

    sibling_details.refresh_from_db()
    assert sibling_details.selected_individuals.count() == initial_count


def test_traverse_sibling_tickets_non_empty_intersection_adds_individuals(
    grievance_ticket: object,
    sibling_ticket: object,
    individual_dup: object,
) -> None:
    # Use individual_dup which IS in the sibling ticket's possible_duplicates.
    selected = Individual.objects.filter(id=individual_dup.id)
    sibling_details = sibling_ticket.needs_adjudication_ticket_details

    assert sibling_details.selected_individuals.count() == 0

    traverse_sibling_tickets(grievance_ticket, selected)

    assert sibling_details.selected_individuals.filter(id=individual_dup.id).exists()


def test_clear_cache_for_household_details_deletes_household_pattern(household_update_details: object) -> None:
    with patch("hope.apps.grievance.utils.cache") as mock_cache:
        clear_cache(household_update_details, "afghanistan")

    mock_cache.delete_pattern.assert_called_once_with("count_afghanistan_HouseholdNodeConnection_*")


def test_update_grievance_documents_replaces_file_and_metadata(grievance_document: object) -> None:
    assert grievance_document.file_size == 9
    assert "old" in grievance_document.file.name
    new_file = SimpleUploadedFile("new.jpg", b"new-bytes!", content_type="image/jpeg")

    update_grievance_documents([{"id": grievance_document.id, "name": "updated name", "file": new_file}])

    grievance_document.refresh_from_db()
    assert grievance_document.name == "updated name"
    assert grievance_document.file_size == 10
    assert grievance_document.content_type == "image/jpeg"
    assert "new" in grievance_document.file.name


def test_update_grievance_documents_skips_missing_document(grievance_document: object) -> None:
    new_file = SimpleUploadedFile("new.jpg", b"new-bytes!", content_type="image/jpeg")

    update_grievance_documents([{"id": uuid4(), "name": "updated name", "file": new_file}])

    grievance_document.refresh_from_db()
    assert grievance_document.name != "updated name"
