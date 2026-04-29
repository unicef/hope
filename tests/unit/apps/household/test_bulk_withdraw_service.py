from unittest.mock import patch

import pytest

from extras.test_utils.factories import (
    DocumentFactory,
    GrievanceTicketFactory,
    HouseholdFactory,
    IndividualFactory,
    TicketComplaintDetailsFactory,
    TicketDeleteHouseholdDetailsFactory,
)
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.household.services.bulk_withdraw import HouseholdBulkWithdrawService
from hope.models import Document, Household, Individual
from hope.models.utils import MergeStatusModel

pytestmark = pytest.mark.django_db


@pytest.fixture
def household_with_documents():
    household = HouseholdFactory(size=5)
    individuals = [household.head_of_household] + IndividualFactory.create_batch(
        4,
        household=household,
        business_area=household.business_area,
        program=household.program,
        registration_data_import=household.registration_data_import,
        rdi_merge_status=household.rdi_merge_status,
    )
    for individual in individuals:
        DocumentFactory.create_batch(
            2,
            individual=individual,
            status=Document.STATUS_VALID,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        DocumentFactory.create_batch(
            3,
            individual=individual,
            status=Document.STATUS_NEED_INVESTIGATION,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
    return household


def test_withdraw_marks_household_individuals_and_documents(household_with_documents) -> None:
    household = household_with_documents
    bystander = HouseholdFactory()

    assert Household.objects.filter(withdrawn=True).count() == 0
    assert Individual.objects.filter(withdrawn=True).count() == 0
    assert Document.objects.filter(status=Document.STATUS_VALID).count() == 10
    assert Document.objects.filter(status=Document.STATUS_NEED_INVESTIGATION).count() == 15
    assert Document.objects.filter(status=Document.STATUS_INVALID).count() == 0

    HouseholdBulkWithdrawService(household.program).withdraw(
        Household.objects.filter(pk=household.pk),
        tag="test",
    )

    assert Household.objects.filter(withdrawn=True).count() == 1
    assert Individual.objects.filter(withdrawn=True).count() == 5
    assert Document.objects.filter(status=Document.STATUS_VALID).count() == 0
    assert Document.objects.filter(status=Document.STATUS_NEED_INVESTIGATION).count() == 0
    assert Document.objects.filter(status=Document.STATUS_INVALID).count() == 25
    bystander.refresh_from_db()
    assert bystander.withdrawn is False


def test_withdraw_skips_already_withdrawn_households() -> None:
    household = HouseholdFactory(withdrawn=True)

    count = HouseholdBulkWithdrawService(household.program).withdraw(
        Household.objects.filter(pk=household.pk),
        tag="test",
    )

    assert count == 0


def test_withdraw_returns_count_of_newly_withdrawn() -> None:
    household = HouseholdFactory()

    count = HouseholdBulkWithdrawService(household.program).withdraw(
        Household.objects.filter(pk=household.pk),
        tag="test",
    )

    assert count == 1


def test_withdraw_stores_withdrawn_tag_in_internal_data() -> None:
    household = HouseholdFactory()

    HouseholdBulkWithdrawService(household.program).withdraw(
        Household.objects.filter(pk=household.pk),
        tag="my_tag",
    )

    household.refresh_from_db()
    assert household.internal_data.get("withdrawn_tag") == "my_tag"


def test_withdraw_skips_duplicate_individuals() -> None:
    household = HouseholdFactory()
    duplicate = IndividualFactory(
        household=household,
        business_area=household.business_area,
        program=household.program,
        duplicate=True,
    )

    HouseholdBulkWithdrawService(household.program).withdraw(
        Household.objects.filter(pk=household.pk),
        tag="test",
    )

    duplicate.refresh_from_db()
    assert duplicate.withdrawn is False


def test_withdraw_closes_related_grievance_tickets() -> None:
    household = HouseholdFactory()
    ticket = GrievanceTicketFactory(
        status=GrievanceTicket.STATUS_IN_PROGRESS,
        business_area=household.business_area,
    )
    TicketComplaintDetailsFactory(ticket=ticket, household=household)

    HouseholdBulkWithdrawService(household.program).withdraw(
        Household.objects.filter(pk=household.pk),
        tag="test",
    )

    ticket.refresh_from_db()
    assert ticket.status == GrievanceTicket.STATUS_CLOSED
    assert ticket.extras.get("status_before_withdrawn") == str(GrievanceTicket.STATUS_IN_PROGRESS)


def test_withdraw_does_not_update_already_closed_tickets() -> None:
    household = HouseholdFactory()
    ticket = GrievanceTicketFactory(
        status=GrievanceTicket.STATUS_CLOSED,
        business_area=household.business_area,
    )
    TicketComplaintDetailsFactory(ticket=ticket, household=household)

    HouseholdBulkWithdrawService(household.program).withdraw(
        Household.objects.filter(pk=household.pk),
        tag="test",
    )

    ticket.refresh_from_db()
    assert ticket.extras.get("status_before_withdrawn") is None


def test_withdraw_excludes_processed_ticket_from_closing() -> None:
    household = HouseholdFactory()
    delete_ticket = GrievanceTicketFactory(
        status=GrievanceTicket.STATUS_IN_PROGRESS,
        business_area=household.business_area,
    )
    TicketDeleteHouseholdDetailsFactory(ticket=delete_ticket, household=household)

    HouseholdBulkWithdrawService(household.program).withdraw(
        Household.objects.filter(pk=household.pk),
        tag="test",
        processed_ticket_id=delete_ticket.id,
    )

    delete_ticket.refresh_from_db()
    assert delete_ticket.status == GrievanceTicket.STATUS_IN_PROGRESS


def test_unwithdraw_marks_household_individuals_and_documents() -> None:
    household = HouseholdFactory(withdrawn=True)
    individual = IndividualFactory(
        household=household,
        business_area=household.business_area,
        program=household.program,
        withdrawn=True,
    )
    document = DocumentFactory(individual=individual, status=Document.STATUS_INVALID)

    HouseholdBulkWithdrawService(household.program).unwithdraw(
        Household.objects.filter(pk=household.pk),
    )

    household.refresh_from_db()
    individual.refresh_from_db()
    document.refresh_from_db()
    assert household.withdrawn is False
    assert individual.withdrawn is False
    assert document.status == Document.STATUS_NEED_INVESTIGATION


def test_unwithdraw_skips_already_unwithdrawn_households() -> None:
    household = HouseholdFactory(withdrawn=False)

    count = HouseholdBulkWithdrawService(household.program).unwithdraw(
        Household.objects.filter(pk=household.pk),
    )

    assert count == 0


def test_unwithdraw_returns_count() -> None:
    household = HouseholdFactory(withdrawn=True)

    count = HouseholdBulkWithdrawService(household.program).unwithdraw(
        Household.objects.filter(pk=household.pk),
    )

    assert count == 1


def test_unwithdraw_reopens_tickets_with_prior_status() -> None:
    household = HouseholdFactory(withdrawn=True)
    ticket = GrievanceTicketFactory(
        status=GrievanceTicket.STATUS_CLOSED,
        business_area=household.business_area,
        extras={"status_before_withdrawn": str(GrievanceTicket.STATUS_IN_PROGRESS)},
    )
    TicketComplaintDetailsFactory(ticket=ticket, household=household)

    HouseholdBulkWithdrawService(household.program).unwithdraw(
        Household.objects.filter(pk=household.pk),
    )

    ticket.refresh_from_db()
    assert ticket.status == GrievanceTicket.STATUS_IN_PROGRESS


def test_unwithdraw_skips_ticket_reopen_when_flag_is_false() -> None:
    household = HouseholdFactory(withdrawn=True)
    ticket = GrievanceTicketFactory(
        status=GrievanceTicket.STATUS_CLOSED,
        business_area=household.business_area,
        extras={"status_before_withdrawn": str(GrievanceTicket.STATUS_IN_PROGRESS)},
    )
    TicketComplaintDetailsFactory(ticket=ticket, household=household)

    HouseholdBulkWithdrawService(household.program).unwithdraw(
        Household.objects.filter(pk=household.pk),
        reopen_tickets=False,
    )

    ticket.refresh_from_db()
    assert ticket.status == GrievanceTicket.STATUS_CLOSED


def test_unwithdraw_does_not_reopen_tickets_without_prior_status() -> None:
    household = HouseholdFactory(withdrawn=True)
    ticket = GrievanceTicketFactory(
        status=GrievanceTicket.STATUS_CLOSED,
        business_area=household.business_area,
        extras={},
    )
    TicketComplaintDetailsFactory(ticket=ticket, household=household)

    HouseholdBulkWithdrawService(household.program).unwithdraw(
        Household.objects.filter(pk=household.pk),
    )

    ticket.refresh_from_db()
    assert ticket.status == GrievanceTicket.STATUS_CLOSED


def test_withdraw_invalidates_grievance_ticket_cache() -> None:
    household = HouseholdFactory()
    ticket = GrievanceTicketFactory(
        status=GrievanceTicket.STATUS_IN_PROGRESS,
        business_area=household.business_area,
    )
    TicketComplaintDetailsFactory(ticket=ticket, household=household)

    with patch(
        "hope.apps.household.services.bulk_withdraw.increment_grievance_ticket_version_cache_for_ticket_ids"
    ) as mock_cache:
        HouseholdBulkWithdrawService(household.program).withdraw(
            Household.objects.filter(pk=household.pk),
            tag="test",
        )

    mock_cache.assert_called_once()


def test_unwithdraw_invalidates_grievance_ticket_cache() -> None:
    household = HouseholdFactory(withdrawn=True)
    ticket = GrievanceTicketFactory(
        status=GrievanceTicket.STATUS_CLOSED,
        business_area=household.business_area,
        extras={"status_before_withdrawn": str(GrievanceTicket.STATUS_IN_PROGRESS)},
    )
    TicketComplaintDetailsFactory(ticket=ticket, household=household)

    with patch(
        "hope.apps.household.services.bulk_withdraw.increment_grievance_ticket_version_cache_for_ticket_ids"
    ) as mock_cache:
        HouseholdBulkWithdrawService(household.program).unwithdraw(
            Household.objects.filter(pk=household.pk),
        )

    mock_cache.assert_called_once()


def test_withdraw_calls_adjust_program_size() -> None:
    household = HouseholdFactory()

    with patch("hope.apps.household.services.bulk_withdraw.adjust_program_size") as mock_adjust:
        HouseholdBulkWithdrawService(household.program).withdraw(
            Household.objects.filter(pk=household.pk),
            tag="test",
        )

    mock_adjust.assert_called_once_with(household.program)


def test_unwithdraw_calls_adjust_program_size() -> None:
    household = HouseholdFactory(withdrawn=True)

    with patch("hope.apps.household.services.bulk_withdraw.adjust_program_size") as mock_adjust:
        HouseholdBulkWithdrawService(household.program).unwithdraw(
            Household.objects.filter(pk=household.pk),
        )

    mock_adjust.assert_called_once_with(household.program)
