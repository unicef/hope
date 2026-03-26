from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    GrievanceTicketFactory,
    HouseholdFactory,
    IndividualFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    TicketNeedsAdjudicationDetailsFactory,
)
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.utils import delete_grievance_documents, traverse_sibling_tickets
from hope.models import Individual

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area():
    return BusinessAreaFactory()


@pytest.fixture
def program(business_area):
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def household(business_area, program):
    return HouseholdFactory(business_area=business_area, program=program)


def test_traverse_sibling_tickets_no_intersection(business_area, program, household):
    """When selected_individuals don't overlap with sibling ticket's individuals, no individuals are added."""
    rdi = RegistrationDataImportFactory(business_area=business_area, program=program)
    ind1 = IndividualFactory(
        business_area=business_area, program=program, household=household, registration_data_import=rdi
    )
    ind2 = IndividualFactory(
        business_area=business_area, program=program, household=household, registration_data_import=rdi
    )
    ind3 = IndividualFactory(
        business_area=business_area, program=program, household=household, registration_data_import=rdi
    )

    ticket = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        issue_type=GrievanceTicket.ISSUE_TYPE_UNIQUE_IDENTIFIERS_SIMILARITY,
        business_area=business_area,
        registration_data_import=rdi,
    )
    details = TicketNeedsAdjudicationDetailsFactory(
        ticket=ticket,
        golden_records_individual=ind1,
        possible_duplicate=ind2,
    )
    details.possible_duplicates.add(ind2)

    # Sibling ticket with ind3 only — no overlap with ind1
    sibling_ticket = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        issue_type=GrievanceTicket.ISSUE_TYPE_UNIQUE_IDENTIFIERS_SIMILARITY,
        business_area=business_area,
        registration_data_import=rdi,
    )
    sibling_details = TicketNeedsAdjudicationDetailsFactory(
        ticket=sibling_ticket,
        golden_records_individual=ind3,
        possible_duplicate=ind3,
    )
    sibling_details.possible_duplicates.add(ind3)

    # Select ind1 — no intersection with sibling (which only has ind3)
    traverse_sibling_tickets(ticket, Individual.objects.filter(id=ind1.id))

    assert sibling_details.selected_individuals.count() == 0


def test_traverse_sibling_tickets_with_intersection(business_area, program, household):
    """When selected_individuals overlap with sibling ticket, individuals are added to selected_individuals."""
    rdi = RegistrationDataImportFactory(business_area=business_area, program=program)
    ind1 = IndividualFactory(
        business_area=business_area, program=program, household=household, registration_data_import=rdi
    )
    ind2 = IndividualFactory(
        business_area=business_area, program=program, household=household, registration_data_import=rdi
    )

    ticket = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        issue_type=GrievanceTicket.ISSUE_TYPE_UNIQUE_IDENTIFIERS_SIMILARITY,
        business_area=business_area,
        registration_data_import=rdi,
    )
    TicketNeedsAdjudicationDetailsFactory(
        ticket=ticket,
        golden_records_individual=ind1,
        possible_duplicate=ind2,
    )

    # Sibling ticket that ALSO involves ind1 — creates intersection
    sibling_ticket = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        issue_type=GrievanceTicket.ISSUE_TYPE_UNIQUE_IDENTIFIERS_SIMILARITY,
        business_area=business_area,
        registration_data_import=rdi,
    )
    sibling_details = TicketNeedsAdjudicationDetailsFactory(
        ticket=sibling_ticket,
        golden_records_individual=ind1,
        possible_duplicate=ind2,
    )
    sibling_details.possible_duplicates.add(ind2)

    # Select ind1 — overlaps with sibling (golden_records_individual=ind1)
    traverse_sibling_tickets(ticket, Individual.objects.filter(id=ind1.id))

    assert sibling_details.selected_individuals.count() == 1
    assert sibling_details.selected_individuals.first() == ind1


def test_delete_grievance_documents_removes_files_and_deletes():
    """Exercise delete_grievance_documents including os.remove loop body."""
    ticket_id = str(uuid4())
    doc_id = str(uuid4())

    mock_doc = MagicMock()
    mock_doc.file.path = "/tmp/fake_file.pdf"

    with patch("hope.apps.grievance.utils.GrievanceDocument") as mock_doc_cls, patch(
        "hope.apps.grievance.utils.os.remove"
    ) as mock_remove:
        mock_qs = MagicMock()
        mock_qs.__iter__ = MagicMock(return_value=iter([mock_doc]))
        mock_doc_cls.objects.filter.return_value = mock_qs

        delete_grievance_documents(ticket_id, [doc_id])

        mock_remove.assert_called_once_with("/tmp/fake_file.pdf")
        mock_qs.delete.assert_called_once()
