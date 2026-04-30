import os
from unittest import mock
from unittest.mock import patch
import uuid

import pytest
from requests.exceptions import RequestException

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PendingIndividualFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
)
from hope.apps.registration_data.celery_tasks import classify_findings_and_schedule_merge_task
from hope.models import (
    DeduplicationEngineSimilarityPair,
    Individual,
    RegistrationDataImport,
)
from hope.models.utils import MergeStatusModel

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def mock_deduplication_engine_env_vars() -> None:
    with mock.patch.dict(
        os.environ,
        {
            "DEDUPLICATION_ENGINE_API_KEY": "TEST",
            "DEDUPLICATION_ENGINE_API_URL": "TEST/",
        },
    ):
        yield


@pytest.fixture
def cw_program():
    business_area = BusinessAreaFactory(slug="syria", name="Syria")
    return ProgramFactory(business_area=business_area, biometric_deduplication_enabled=True)


@pytest.fixture
def cw_rdi(cw_program):
    return RegistrationDataImportFactory(
        program=cw_program,
        business_area=cw_program.business_area,
        status=RegistrationDataImport.IN_REVIEW,
        correlation_id=str(uuid.uuid4()),
    )


@pytest.fixture
def two_pending_individuals(cw_rdi, cw_program):
    ind_a = PendingIndividualFactory(
        program=cw_program,
        business_area=cw_program.business_area,
        registration_data_import=cw_rdi,
        country_workspace_id="1001",
    )
    ind_b = PendingIndividualFactory(
        program=cw_program,
        business_area=cw_program.business_area,
        registration_data_import=cw_rdi,
        country_workspace_id="1002",
    )
    return ind_a, ind_b


def _finding(first_pk: str, second_pk: str, *, score: float = 0.95, status_code: str = "200") -> dict:
    return {
        "first": {"reference_pk": first_pk},
        "second": {"reference_pk": second_pk},
        "score": score,
        "status_code": status_code,
        "config": "default",
        "updated_at": "2026-04-29T00:00:00Z",
    }


@patch("hope.apps.registration_data.celery_tasks.merge_registration_data_import_async_task")
@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI.get_group_findings")
def test_arrival_hook_persists_pairs_and_enqueues_merge(
    mock_get_findings: mock.Mock,
    mock_enqueue_merge: mock.Mock,
    cw_rdi: RegistrationDataImport,
    two_pending_individuals: tuple[Individual, Individual],
    django_assert_num_queries,
) -> None:
    ind_a, ind_b = two_pending_individuals
    mock_get_findings.return_value = iter([_finding(first_pk="1001", second_pk="1002")])

    with django_assert_num_queries(18):
        classify_findings_and_schedule_merge_task(str(cw_rdi.id))

    pairs = list(DeduplicationEngineSimilarityPair.objects.filter(program=cw_rdi.program))
    assert len(pairs) == 1
    persisted_ids = {pairs[0].individual1_id, pairs[0].individual2_id}
    assert persisted_ids == {ind_a.id, ind_b.id}

    cw_rdi.refresh_from_db()
    assert cw_rdi.status == RegistrationDataImport.MERGE_SCHEDULED

    mock_enqueue_merge.assert_called_once_with(cw_rdi)


@patch("hope.apps.registration_data.celery_tasks.merge_registration_data_import_async_task")
@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI.get_group_findings")
def test_arrival_hook_consumes_full_findings_iterator(
    mock_get_findings: mock.Mock,
    mock_enqueue_merge: mock.Mock,
    cw_rdi: RegistrationDataImport,
    cw_program,
) -> None:
    for i in range(6):
        PendingIndividualFactory(
            program=cw_program,
            business_area=cw_program.business_area,
            registration_data_import=cw_rdi,
            country_workspace_id=str(2000 + i),
        )
    findings = [
        _finding(first_pk="2000", second_pk="2001"),
        _finding(first_pk="2002", second_pk="2003"),
        _finding(first_pk="2004", second_pk="2005"),
    ]
    mock_get_findings.return_value = iter(findings)

    classify_findings_and_schedule_merge_task(str(cw_rdi.id))

    assert DeduplicationEngineSimilarityPair.objects.filter(program=cw_program).count() == len(findings)


@patch("hope.apps.registration_data.celery_tasks.merge_registration_data_import_async_task")
@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI.get_group_findings")
def test_arrival_hook_empty_findings_still_enqueues_merge(
    mock_get_findings: mock.Mock,
    mock_enqueue_merge: mock.Mock,
    cw_rdi: RegistrationDataImport,
    two_pending_individuals: tuple[Individual, Individual],
) -> None:
    mock_get_findings.return_value = iter([])

    classify_findings_and_schedule_merge_task(str(cw_rdi.id))

    assert DeduplicationEngineSimilarityPair.objects.filter(program=cw_rdi.program).count() == 0

    cw_rdi.refresh_from_db()
    assert cw_rdi.status == RegistrationDataImport.MERGE_SCHEDULED
    mock_enqueue_merge.assert_called_once()


@patch("hope.apps.registration_data.celery_tasks.merge_registration_data_import_async_task")
@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI.get_group_findings")
def test_arrival_hook_classifies_batch_when_both_sides_pending(
    mock_get_findings: mock.Mock,
    mock_enqueue_merge: mock.Mock,
    cw_rdi: RegistrationDataImport,
    two_pending_individuals: tuple[Individual, Individual],
) -> None:
    ind_a, ind_b = two_pending_individuals
    assert ind_a.rdi_merge_status == MergeStatusModel.PENDING
    assert ind_b.rdi_merge_status == MergeStatusModel.PENDING

    mock_get_findings.return_value = iter([_finding(first_pk="1001", second_pk="1002")])

    classify_findings_and_schedule_merge_task(str(cw_rdi.id))

    ind_a.refresh_from_db()
    ind_b.refresh_from_db()

    assert len(ind_a.biometric_deduplication_batch_results) == 1
    assert ind_a.biometric_deduplication_batch_results[0]["id"] == str(ind_b.id)
    assert ind_a.biometric_deduplication_golden_record_results == []

    assert len(ind_b.biometric_deduplication_batch_results) == 1
    assert ind_b.biometric_deduplication_batch_results[0]["id"] == str(ind_a.id)
    assert ind_b.biometric_deduplication_golden_record_results == []


@patch("hope.apps.registration_data.celery_tasks.merge_registration_data_import_async_task")
@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI.get_group_findings")
def test_arrival_hook_classifies_population_when_one_side_merged(
    mock_get_findings: mock.Mock,
    mock_enqueue_merge: mock.Mock,
    cw_rdi: RegistrationDataImport,
    cw_program,
) -> None:
    pending_ind = PendingIndividualFactory(
        program=cw_program,
        business_area=cw_program.business_area,
        registration_data_import=cw_rdi,
        country_workspace_id="1001",
    )
    merged_ind = PendingIndividualFactory(
        program=cw_program,
        business_area=cw_program.business_area,
        country_workspace_id="1002",
        rdi_merge_status=MergeStatusModel.MERGED,
    )

    mock_get_findings.return_value = iter([_finding(first_pk="1001", second_pk="1002")])

    classify_findings_and_schedule_merge_task(str(cw_rdi.id))

    pending_ind.refresh_from_db()

    assert len(pending_ind.biometric_deduplication_golden_record_results) == 1
    assert pending_ind.biometric_deduplication_golden_record_results[0]["id"] == str(merged_ind.id)
    assert pending_ind.biometric_deduplication_batch_results == []


@patch("hope.apps.registration_data.celery_tasks.merge_registration_data_import_async_task")
@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI.get_group_findings")
@pytest.mark.parametrize(
    "non_in_review_status",
    [
        RegistrationDataImport.MERGE_SCHEDULED,
        RegistrationDataImport.MERGING,
        RegistrationDataImport.MERGED,
    ],
)
def test_arrival_hook_noop_when_status_not_in_review(
    mock_get_findings: mock.Mock,
    mock_enqueue_merge: mock.Mock,
    non_in_review_status: str,
    cw_rdi: RegistrationDataImport,
    two_pending_individuals: tuple[Individual, Individual],
) -> None:
    cw_rdi.status = non_in_review_status
    cw_rdi.save(update_fields=["status"])
    mock_get_findings.return_value = iter([_finding(first_pk="1001", second_pk="1002")])

    classify_findings_and_schedule_merge_task(str(cw_rdi.id))

    cw_rdi.refresh_from_db()
    assert cw_rdi.status == non_in_review_status
    mock_enqueue_merge.assert_not_called()


@patch("hope.apps.registration_data.celery_tasks.merge_registration_data_import_async_task")
@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI.get_group_findings")
def test_arrival_hook_rerun_does_not_double_persist_pairs(
    mock_get_findings: mock.Mock,
    mock_enqueue_merge: mock.Mock,
    cw_rdi: RegistrationDataImport,
    two_pending_individuals: tuple[Individual, Individual],
) -> None:
    mock_get_findings.return_value = iter([_finding(first_pk="1001", second_pk="1002")])
    classify_findings_and_schedule_merge_task(str(cw_rdi.id))
    rows_after_first = DeduplicationEngineSimilarityPair.objects.filter(program=cw_rdi.program).count()

    cw_rdi.refresh_from_db()
    cw_rdi.status = RegistrationDataImport.IN_REVIEW
    cw_rdi.save(update_fields=["status"])
    mock_get_findings.return_value = iter([_finding(first_pk="1001", second_pk="1002")])

    classify_findings_and_schedule_merge_task(str(cw_rdi.id))

    rows_after_second = DeduplicationEngineSimilarityPair.objects.filter(program=cw_rdi.program).count()
    assert rows_after_first == rows_after_second == 1


@patch("hope.apps.registration_data.celery_tasks.merge_registration_data_import_async_task")
@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI.get_group_findings")
def test_arrival_hook_skips_findings_with_unknown_country_workspace_id(
    mock_get_findings: mock.Mock,
    mock_enqueue_merge: mock.Mock,
    cw_rdi: RegistrationDataImport,
    two_pending_individuals: tuple[Individual, Individual],
    caplog: pytest.LogCaptureFixture,
) -> None:
    mock_get_findings.return_value = iter(
        [
            _finding(first_pk="1001", second_pk="1002"),
            _finding(first_pk="1001", second_pk="9999"),
        ]
    )

    with caplog.at_level("WARNING"):
        classify_findings_and_schedule_merge_task(str(cw_rdi.id))

    assert DeduplicationEngineSimilarityPair.objects.filter(program=cw_rdi.program).count() == 1
    assert any("9999" in rec.getMessage() for rec in caplog.records)
    cw_rdi.refresh_from_db()
    assert cw_rdi.status == RegistrationDataImport.MERGE_SCHEDULED
    mock_enqueue_merge.assert_called_once()


@patch("hope.apps.registration_data.celery_tasks.merge_registration_data_import_async_task")
@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI.get_group_findings")
def test_arrival_hook_terminal_failure_keeps_rdi_in_review(
    mock_get_findings: mock.Mock,
    mock_enqueue_merge: mock.Mock,
    cw_rdi: RegistrationDataImport,
    two_pending_individuals: tuple[Individual, Individual],
) -> None:
    mock_get_findings.side_effect = RequestException("engine 503")

    with pytest.raises(RequestException):
        classify_findings_and_schedule_merge_task(str(cw_rdi.id))

    cw_rdi.refresh_from_db()
    assert cw_rdi.status == RegistrationDataImport.IN_REVIEW
    mock_enqueue_merge.assert_not_called()
    assert DeduplicationEngineSimilarityPair.objects.filter(program=cw_rdi.program).count() == 0


@pytest.mark.skip(reason="Pending BE-08")
def test_arrival_hook_status_code_handling() -> None:
    pass
