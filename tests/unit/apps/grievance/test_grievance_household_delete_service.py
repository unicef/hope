from unittest.mock import patch

import pytest
from rest_framework.exceptions import ValidationError

from extras.test_utils.factories import (
    BusinessAreaFactory,
    DocumentFactory,
    GrievanceTicketFactory,
    HouseholdFactory,
    IndividualFactory,
    IndividualRoleInHouseholdFactory,
    ProgramFactory,
    TicketComplaintDetailsFactory,
    TicketDeleteHouseholdDetailsFactory,
)
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.services.data_change.household_delete_service import HouseholdDeleteService
from hope.apps.household.const import ROLE_ALTERNATE
from hope.models import Document, Household, Individual

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area():
    return BusinessAreaFactory()


@pytest.fixture
def program(business_area):
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def household(program, business_area):
    return HouseholdFactory(program=program, business_area=business_area)


@pytest.fixture
def delete_ticket(household):
    ticket = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_HOUSEHOLD,
        status=GrievanceTicket.STATUS_IN_PROGRESS,
        business_area=household.business_area,
    )
    TicketDeleteHouseholdDetailsFactory(ticket=ticket, household=household, approve_status=True)
    return ticket


def test_close_does_nothing_when_approve_status_is_false(delete_ticket, household) -> None:
    details = delete_ticket.delete_household_ticket_details
    details.approve_status = False
    details.save()

    HouseholdDeleteService(delete_ticket, extras={}).close(user=None)

    household.refresh_from_db()
    assert household.withdrawn is False


def test_close_raises_when_external_collector_exists(delete_ticket, household, program, business_area) -> None:
    other_household = HouseholdFactory(program=program, business_area=business_area)
    member = IndividualFactory(household=household, program=program, business_area=business_area)
    IndividualRoleInHouseholdFactory(individual=member, household=other_household, role=ROLE_ALTERNATE)

    with pytest.raises(ValidationError):
        HouseholdDeleteService(delete_ticket, extras={}).close(user=None)

    household.refresh_from_db()
    assert household.withdrawn is False


def test_close_withdraws_household_and_individuals(delete_ticket, household) -> None:
    HouseholdDeleteService(delete_ticket, extras={}).close(user=None)

    household.refresh_from_db()
    assert household.withdrawn is True
    assert Individual.objects.filter(household=household, withdrawn=False, duplicate=False).count() == 0


def test_close_closes_all_related_tickets_except_the_processed_delete_ticket(
    delete_ticket, household, business_area
) -> None:
    complaint_ticket = GrievanceTicketFactory(
        status=GrievanceTicket.STATUS_IN_PROGRESS, business_area=business_area
    )
    TicketComplaintDetailsFactory(ticket=complaint_ticket, household=household)

    HouseholdDeleteService(delete_ticket, extras={}).close(user=None)

    complaint_ticket.refresh_from_db()
    delete_ticket.refresh_from_db()
    assert complaint_ticket.status == GrievanceTicket.STATUS_CLOSED
    assert delete_ticket.status == GrievanceTicket.STATUS_IN_PROGRESS


def test_close_does_not_close_already_closed_tickets(delete_ticket, household, business_area) -> None:
    closed_ticket = GrievanceTicketFactory(
        status=GrievanceTicket.STATUS_CLOSED, business_area=business_area
    )
    TicketComplaintDetailsFactory(ticket=closed_ticket, household=household)

    HouseholdDeleteService(delete_ticket, extras={}).close(user=None)

    closed_ticket.refresh_from_db()
    assert closed_ticket.extras.get("status_before_withdrawn") is None


def test_close_invalidates_documents(delete_ticket, household, program) -> None:
    individual = household.head_of_household
    document = DocumentFactory(individual=individual, program=program)

    HouseholdDeleteService(delete_ticket, extras={}).close(user=None)

    document.refresh_from_db()
    assert document.status == Document.STATUS_INVALID


def test_close_calls_adjust_program_size(delete_ticket, household) -> None:
    with patch("hope.apps.household.services.bulk_withdraw.adjust_program_size") as mock_adjust:
        HouseholdDeleteService(delete_ticket, extras={}).close(user=None)

    mock_adjust.assert_called_once_with(household.program)


def test_close_skips_household_already_withdrawn(delete_ticket, household) -> None:
    Household.objects.filter(pk=household.pk).update(withdrawn=True)

    HouseholdDeleteService(delete_ticket, extras={}).close(user=None)

    assert Household.objects.filter(pk=household.pk, withdrawn=True).count() == 1


def test_close_invalidates_grievance_ticket_cache(delete_ticket, household, business_area) -> None:
    complaint_ticket = GrievanceTicketFactory(
        status=GrievanceTicket.STATUS_IN_PROGRESS, business_area=business_area
    )
    TicketComplaintDetailsFactory(ticket=complaint_ticket, household=household)

    with patch(
        "hope.apps.household.services.bulk_withdraw.increment_grievance_ticket_version_cache_for_ticket_ids"
    ) as mock_cache:
        HouseholdDeleteService(delete_ticket, extras={}).close(user=None)

    mock_cache.assert_called_once()
