"""Tests for routing biometric photo-error findings to Data Change photo-fix tickets."""

from typing import Any

from django.core.files.base import ContentFile
import pytest
from rest_framework.exceptions import ValidationError

from extras.test_utils.factories import (
    BusinessAreaFactory,
    DeduplicationEngineSimilarityPairFactory,
    HouseholdFactory,
    IndividualFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.grievance.constants import SUBMISSION_CHANNEL_HOPE
from hope.apps.grievance.models import (
    GrievanceTicket,
    TicketIndividualDataUpdateDetails,
    TicketNeedsAdjudicationDetails,
)
from hope.apps.grievance.services.biometric_photo_ticket import (
    create_biometrics_photo_data_change_tickets,
)
from hope.apps.grievance.services.ticket_status_changer_service import (
    TicketStatusChangerService,
)
from hope.models import BusinessArea, DeduplicationEngineSimilarityPair, User

pytestmark = [
    pytest.mark.usefixtures("mock_elasticsearch"),
    pytest.mark.django_db,
]


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan", code="0060")


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture
def one_bad_photo_context(business_area: BusinessArea, user: User) -> dict[str, Any]:
    program = ProgramFactory(name="One Bad Photo HOPE", business_area=business_area)
    household = HouseholdFactory(business_area=business_area, program=program, create_role=False)
    rdi = household.registration_data_import
    individual = IndividualFactory(
        household=household,
        business_area=business_area,
        program=program,
        registration_data_import=rdi,
        deduplication_golden_record_results={"duplicates": [], "possible_duplicates": []},
        photo=ContentFile(b"aaa", name="bad.png"),
    )
    DeduplicationEngineSimilarityPairFactory(
        program=program,
        individual1=individual,
        individual2=None,
        similarity_score=0.0,
        status_code=DeduplicationEngineSimilarityPair.StatusCode.STATUS_412,
    )
    return {"user": user, "rdi": rdi, "individual": individual}


@pytest.fixture
def two_bad_photos_context(business_area: BusinessArea) -> dict[str, Any]:
    program = ProgramFactory(name="Two Bad Photos HOPE", business_area=business_area)
    household_a = HouseholdFactory(business_area=business_area, program=program, create_role=False)
    household_b = HouseholdFactory(business_area=business_area, program=program, create_role=False)
    rdi = household_a.registration_data_import
    ind_a = IndividualFactory(
        household=household_a,
        business_area=business_area,
        program=program,
        registration_data_import=rdi,
        deduplication_golden_record_results={"duplicates": [], "possible_duplicates": []},
        photo=ContentFile(b"aaa", name="a.png"),
    )
    ind_b = IndividualFactory(
        household=household_b,
        business_area=business_area,
        program=program,
        registration_data_import=rdi,
        deduplication_golden_record_results={"duplicates": [], "possible_duplicates": []},
        photo=ContentFile(b"bbb", name="b.png"),
    )
    DeduplicationEngineSimilarityPairFactory(
        program=program,
        individual1=ind_a,
        individual2=None,
        similarity_score=0.0,
        status_code=DeduplicationEngineSimilarityPair.StatusCode.STATUS_412,
    )
    DeduplicationEngineSimilarityPairFactory(
        program=program,
        individual1=ind_b,
        individual2=None,
        similarity_score=0.0,
        status_code=DeduplicationEngineSimilarityPair.StatusCode.STATUS_429,
    )
    return {"rdi": rdi, "ind_a": ind_a, "ind_b": ind_b}


@pytest.fixture
def two_sided_error_context(business_area: BusinessArea) -> dict[str, Any]:
    program = ProgramFactory(name="Two Sided HOPE", business_area=business_area)
    household_a = HouseholdFactory(business_area=business_area, program=program, create_role=False)
    household_b = HouseholdFactory(business_area=business_area, program=program, create_role=False)
    rdi = household_a.registration_data_import
    ind_a = IndividualFactory(
        household=household_a,
        business_area=business_area,
        program=program,
        registration_data_import=rdi,
        deduplication_golden_record_results={"duplicates": [], "possible_duplicates": []},
        photo=ContentFile(b"aaa", name="a.png"),
    )
    ind_b = IndividualFactory(
        household=household_b,
        business_area=business_area,
        program=program,
        registration_data_import=rdi,
        deduplication_golden_record_results={"duplicates": [], "possible_duplicates": []},
        photo=ContentFile(b"bbb", name="b.png"),
    )
    # Deliberately malformed input to exercise the defensive guard - a photo error (score 0) only names 1 individual
    DeduplicationEngineSimilarityPairFactory(
        program=program,
        individual1=ind_a,
        individual2=ind_b,
        similarity_score=0.0,
        status_code=DeduplicationEngineSimilarityPair.StatusCode.STATUS_412,
    )
    return {"rdi": rdi}


def test_single_sided_error_finding_creates_photo_data_change_ticket(
    one_bad_photo_context: dict[str, Any],
) -> None:
    rdi = one_bad_photo_context["rdi"]
    individual = one_bad_photo_context["individual"]

    create_biometrics_photo_data_change_tickets(DeduplicationEngineSimilarityPair.objects.all(), rdi)

    assert TicketNeedsAdjudicationDetails.objects.count() == 0
    assert GrievanceTicket.objects.count() == 1
    ticket = GrievanceTicket.objects.get()
    assert ticket.category == GrievanceTicket.CATEGORY_DATA_CHANGE
    assert ticket.issue_type == GrievanceTicket.ISSUE_TYPE_BIOMETRICS_PHOTO
    assert ticket.submission_channel == SUBMISSION_CHANNEL_HOPE
    details = TicketIndividualDataUpdateDetails.objects.get()
    assert str(details.individual_id) == str(individual.id)
    assert details.individual_data == {
        "photo": {"value": None, "approve_status": False, "previous_value": individual.photo.name}
    }


def test_ticket_description_reports_the_engine_status_code(one_bad_photo_context: dict[str, Any]) -> None:
    rdi = one_bad_photo_context["rdi"]

    create_biometrics_photo_data_change_tickets(DeduplicationEngineSimilarityPair.objects.all(), rdi)

    assert GrievanceTicket.objects.get().description == (
        "Biometric deduplication could not read this individual's photo "
        "(412 - No face detected). Upload a valid photo to resolve."
    )


def test_each_bad_photo_individual_gets_its_own_ticket(two_bad_photos_context: dict[str, Any]) -> None:
    rdi = two_bad_photos_context["rdi"]
    ind_a = two_bad_photos_context["ind_a"]
    ind_b = two_bad_photos_context["ind_b"]

    create_biometrics_photo_data_change_tickets(DeduplicationEngineSimilarityPair.objects.all(), rdi)

    assert GrievanceTicket.objects.count() == 2
    assert {str(d.individual_id) for d in TicketIndividualDataUpdateDetails.objects.all()} == {
        str(ind_a.id),
        str(ind_b.id),
    }


def test_two_sided_finding_creates_no_photo_ticket(two_sided_error_context: dict[str, Any]) -> None:
    # Guards the "exactly one individual" rule: a photo error that names two individuals cannot
    # occur, but if it did we skip it rather than guess whose photo is bad.
    rdi = two_sided_error_context["rdi"]

    create_biometrics_photo_data_change_tickets(DeduplicationEngineSimilarityPair.objects.all(), rdi)

    assert GrievanceTicket.objects.count() == 0


def test_photo_error_ticket_not_duplicated_on_rerun(one_bad_photo_context: dict[str, Any]) -> None:
    rdi = one_bad_photo_context["rdi"]

    create_biometrics_photo_data_change_tickets(DeduplicationEngineSimilarityPair.objects.all(), rdi)
    assert GrievanceTicket.objects.count() == 1

    create_biometrics_photo_data_change_tickets(DeduplicationEngineSimilarityPair.objects.all(), rdi)
    assert GrievanceTicket.objects.count() == 1


def test_empty_queryset_creates_nothing(one_bad_photo_context: dict[str, Any]) -> None:
    rdi = one_bad_photo_context["rdi"]

    create_biometrics_photo_data_change_tickets(DeduplicationEngineSimilarityPair.objects.none(), rdi)

    assert GrievanceTicket.objects.count() == 0


def test_photo_ticket_cannot_be_sent_for_approval_without_photo(one_bad_photo_context: dict[str, Any]) -> None:
    rdi = one_bad_photo_context["rdi"]
    user = one_bad_photo_context["user"]
    create_biometrics_photo_data_change_tickets(DeduplicationEngineSimilarityPair.objects.all(), rdi)
    ticket = GrievanceTicket.objects.get(issue_type=GrievanceTicket.ISSUE_TYPE_BIOMETRICS_PHOTO)
    ticket.status = GrievanceTicket.STATUS_IN_PROGRESS
    ticket.save()

    with pytest.raises(ValidationError):
        TicketStatusChangerService(ticket, user).change_status(GrievanceTicket.STATUS_FOR_APPROVAL)

    ticket.refresh_from_db()
    assert ticket.status == GrievanceTicket.STATUS_IN_PROGRESS


def test_photo_ticket_sent_for_approval_after_photo_assigned(one_bad_photo_context: dict[str, Any]) -> None:
    rdi = one_bad_photo_context["rdi"]
    user = one_bad_photo_context["user"]
    create_biometrics_photo_data_change_tickets(DeduplicationEngineSimilarityPair.objects.all(), rdi)
    ticket = GrievanceTicket.objects.get(issue_type=GrievanceTicket.ISSUE_TYPE_BIOMETRICS_PHOTO)
    ticket.status = GrievanceTicket.STATUS_IN_PROGRESS
    ticket.save()
    details = ticket.individual_data_update_ticket_details
    details.individual_data["photo"]["value"] = "new_valid_photo.png"
    details.save(update_fields=["individual_data"])

    TicketStatusChangerService(ticket, user).change_status(GrievanceTicket.STATUS_FOR_APPROVAL)

    ticket.refresh_from_db()
    assert ticket.status == GrievanceTicket.STATUS_FOR_APPROVAL
