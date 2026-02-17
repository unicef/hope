"""Tests for RdiMergeTask extracted helpers."""

from unittest.mock import MagicMock, patch
import uuid

import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    HouseholdFactory,
    PendingDocumentFactory,
    PendingHouseholdFactory,
    PendingIndividualFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
)
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.registration_data.tasks.rdi_merge import RdiMergeTask
from hope.models import (
    BusinessArea,
    Document,
    PendingHousehold,
    PendingIndividual,
    Program,
    RegistrationDataImport,
)
from hope.models.utils import MergeStatusModel

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan")


@pytest.fixture
def program(business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def rdi(program: Program) -> RegistrationDataImport:
    return RegistrationDataImportFactory(
        program=program,
        business_area=program.business_area,
        status=RegistrationDataImport.IN_REVIEW,
    )


@pytest.fixture
def pending_household(rdi: RegistrationDataImport) -> PendingHousehold:
    return PendingHouseholdFactory(
        registration_data_import=rdi,
        program=rdi.program,
        business_area=rdi.business_area,
    )


@pytest.fixture
def pending_individual(rdi: RegistrationDataImport, pending_household: PendingHousehold) -> PendingIndividual:
    return PendingIndividualFactory(
        registration_data_import=rdi,
        program=rdi.program,
        business_area=rdi.business_area,
        household=pending_household,
    )


@pytest.fixture
def pending_document(pending_individual, rdi):
    return PendingDocumentFactory(individual=pending_individual, program=rdi.program)


@pytest.fixture
def target_household(rdi):
    return HouseholdFactory(business_area=rdi.business_area, program=rdi.program)


def test_update_merge_statuses_sets_merged_on_all_models(
    rdi: RegistrationDataImport,
    pending_household: PendingHousehold,
    pending_individual: PendingIndividual,
    pending_document,
) -> None:
    task = RdiMergeTask()
    task._update_merge_statuses([pending_household.id], [pending_individual.id])

    pending_household.refresh_from_db()
    pending_individual.refresh_from_db()
    assert pending_household.rdi_merge_status == MergeStatusModel.MERGED
    assert pending_individual.rdi_merge_status == MergeStatusModel.MERGED
    assert Document.all_objects.filter(
        individual=pending_individual,
        rdi_merge_status=MergeStatusModel.MERGED,
    ).exists()


def test_clear_cache_deletes_matching_keys(business_area: BusinessArea) -> None:
    mock_cache = MagicMock()
    mock_cache.keys.return_value = [
        f"count_{business_area.slug}_HouseholdNodeConnection_abc",
        f"count_{business_area.slug}_IndividualNodeConnection_xyz",
        "unrelated_key",
    ]

    task = RdiMergeTask()
    with patch("hope.apps.registration_data.tasks.rdi_merge.cache", mock_cache):
        task._clear_cache(business_area.slug)

    assert mock_cache.delete.call_count == 2
    mock_cache.delete.assert_any_call(f"count_{business_area.slug}_HouseholdNodeConnection_abc")
    mock_cache.delete.assert_any_call(f"count_{business_area.slug}_IndividualNodeConnection_xyz")


def test_clear_cache_suppresses_connection_error(business_area: BusinessArea) -> None:
    mock_cache = MagicMock()
    mock_cache.keys.side_effect = ConnectionError("Redis down")

    task = RdiMergeTask()
    with patch("hope.apps.registration_data.tasks.rdi_merge.cache", mock_cache):
        # Should not raise
        task._clear_cache(business_area.slug)


# --- _process_collisions ---


def test_process_collisions_with_collision_detected(
    rdi: RegistrationDataImport,
    pending_household: PendingHousehold,
    target_household,
) -> None:
    mock_collision_detector = MagicMock()
    mock_collision_detector.detect_collision.return_value = target_household.id

    task = RdiMergeTask()
    with patch.object(
        type(rdi.program), "collision_detector", new_callable=lambda: property(lambda self: mock_collision_detector)
    ):
        households_to_merge_ids, household_ids_to_exclude = task._process_collisions(rdi, [pending_household.id])

    assert pending_household.id in household_ids_to_exclude
    assert pending_household.id not in households_to_merge_ids
    mock_collision_detector.update_household.assert_called_once_with(pending_household)
    target_household.refresh_from_db()
    assert rdi in target_household.extra_rdis.all()


# --- _run_biometric_deduplication ---


def test_run_biometric_deduplication_enabled_calls_all_service_methods(
    rdi: RegistrationDataImport,
) -> None:
    rdi.program.biometric_deduplication_enabled = True
    rdi.program.save(update_fields=["biometric_deduplication_enabled"])

    individual_ids = [uuid.uuid4(), uuid.uuid4()]

    task = RdiMergeTask()
    with patch("hope.apps.registration_data.tasks.rdi_merge.BiometricDeduplicationService") as mock_service_cls:
        mock_service_instance = mock_service_cls.return_value
        task._run_biometric_deduplication(rdi, individual_ids)

    mock_service_instance.create_grievance_tickets_for_duplicates.assert_called_once_with(rdi)
    mock_service_instance.update_rdis_deduplication_statistics.assert_called_once_with(rdi.program, exclude_rdi=rdi)
    mock_service_instance.report_individuals_status.assert_called_once_with(
        rdi.program,
        [str(_id) for _id in individual_ids],
        mock_service_cls.INDIVIDUALS_MERGED,
    )


# --- _run_deduplication ---


def test_run_deduplication_calls_dedup_and_creates_tickets(
    rdi: RegistrationDataImport,
) -> None:
    individuals_list = []
    registration_data_import_id = str(rdi.id)

    task = RdiMergeTask()
    with (
        patch("hope.apps.registration_data.tasks.rdi_merge.DeduplicateTask") as mock_dedup_cls,
        patch("hope.apps.registration_data.tasks.rdi_merge.create_needs_adjudication_tickets") as mock_create_tickets,
    ):
        mock_dedup_instance = mock_dedup_cls.return_value
        task._run_deduplication(rdi, individuals_list, registration_data_import_id)

    mock_dedup_cls.assert_called_once_with(rdi.business_area.slug, rdi.program.id)
    mock_dedup_instance.deduplicate_individuals_against_population.assert_called_once_with(individuals_list)

    assert mock_create_tickets.call_count == 2
    first_call = mock_create_tickets.call_args_list[0]
    second_call = mock_create_tickets.call_args_list[1]

    assert first_call[0][1] == "duplicates"
    assert first_call[0][2] == rdi.business_area
    assert first_call[1]["registration_data_import"] == rdi
    assert first_call[1]["issue_type"] == GrievanceTicket.ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY

    assert second_call[0][1] == "possible_duplicates"
    assert second_call[0][2] == rdi.business_area
    assert second_call[1]["registration_data_import"] == rdi
    assert second_call[1]["issue_type"] == GrievanceTicket.ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY


# --- _create_kobo_submissions ---


@pytest.fixture
def pending_household_with_kobo(rdi: RegistrationDataImport) -> PendingHousehold:
    import datetime

    return PendingHouseholdFactory(
        registration_data_import=rdi,
        program=rdi.program,
        business_area=rdi.business_area,
        kobo_submission_uuid=uuid.uuid4(),
        detail_id="asset123",
        kobo_submission_time=datetime.datetime(2024, 1, 1, tzinfo=datetime.timezone.utc),
    )


def test_create_kobo_submissions_with_valid_kobo_data(
    rdi: RegistrationDataImport, pending_household_with_kobo: PendingHousehold
):
    from hope.models import KoboImportedSubmission

    task = RdiMergeTask()
    households = PendingHousehold.objects.filter(id=pending_household_with_kobo.id)
    result = task._create_kobo_submissions(households, rdi)
    assert len(result) == 1
    assert KoboImportedSubmission.objects.filter(registration_data_import=rdi).exists()


def test_process_collisions_no_collision_detected(
    rdi: RegistrationDataImport,
    pending_household: PendingHousehold,
) -> None:
    """When detect_collision returns None, household is NOT excluded and stays in merge list."""
    mock_collision_detector = MagicMock()
    mock_collision_detector.detect_collision.return_value = None

    task = RdiMergeTask()
    with patch.object(
        type(rdi.program), "collision_detector", new_callable=lambda: property(lambda self: mock_collision_detector)
    ):
        households_to_merge_ids, household_ids_to_exclude = task._process_collisions(rdi, [pending_household.id])

    assert pending_household.id not in household_ids_to_exclude
    assert pending_household.id in households_to_merge_ids
    mock_collision_detector.update_household.assert_not_called()
