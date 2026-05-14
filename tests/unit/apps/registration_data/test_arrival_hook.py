from decimal import Decimal
import os
from unittest import mock
from unittest.mock import Mock, patch
import uuid

from celery.exceptions import Retry
import pytest
from requests.exceptions import RequestException

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PendingIndividualFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
)
from hope.apps.core.celery_tasks import async_retry_job_task
from hope.apps.household.const import DUPLICATE, DUPLICATE_IN_BATCH, UNIQUE, UNIQUE_IN_BATCH
from hope.apps.registration_data.api.deduplication_engine import SimilarityPair
from hope.apps.registration_data.celery_tasks import (
    classify_findings_and_schedule_merge_async_task,
)
from hope.apps.registration_data.tasks.cw_arrival_hook import CwArrivalHookTask
from hope.models import (
    AsyncRetryJob,
    DeduplicationEngineSimilarityPair,
    Individual,
    RegistrationDataImport,
)
from hope.models.utils import MergeStatusModel

pytestmark = pytest.mark.django_db


def queue_and_run_retry_task(task: object, *args: object, **kwargs: object) -> object:
    with patch("hope.apps.registration_data.celery_tasks.AsyncRetryJob.queue", autospec=True):
        task(*args, **kwargs)
    job = AsyncRetryJob.objects.latest("pk")
    return async_retry_job_task.run(job._meta.label_lower, job.pk, job.version)


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
        status=RegistrationDataImport.MERGE_SCHEDULED,
        country_workspace_id=str(uuid.uuid4()),
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
) -> None:
    ind_a, ind_b = two_pending_individuals
    mock_get_findings.return_value = [_finding(first_pk="1001", second_pk="1002")]

    queue_and_run_retry_task(classify_findings_and_schedule_merge_async_task, registration_data_import=cw_rdi)

    pairs = list(DeduplicationEngineSimilarityPair.objects.filter(program=cw_rdi.program))
    assert len(pairs) == 1
    persisted_ids = {pairs[0].individual1_id, pairs[0].individual2_id}
    assert persisted_ids == {ind_a.id, ind_b.id}
    assert pairs[0].similarity_score == Decimal("95.00")

    cw_rdi.refresh_from_db()
    assert cw_rdi.status == RegistrationDataImport.MERGING

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
    mock_get_findings.return_value = findings

    queue_and_run_retry_task(classify_findings_and_schedule_merge_async_task, registration_data_import=cw_rdi)

    assert DeduplicationEngineSimilarityPair.objects.filter(program=cw_program).count() == len(findings)


@patch("hope.apps.registration_data.celery_tasks.merge_registration_data_import_async_task")
@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI.get_group_findings")
def test_arrival_hook_empty_findings_still_enqueues_merge(
    mock_get_findings: mock.Mock,
    mock_enqueue_merge: mock.Mock,
    cw_rdi: RegistrationDataImport,
    two_pending_individuals: tuple[Individual, Individual],
) -> None:
    mock_get_findings.return_value = []

    queue_and_run_retry_task(classify_findings_and_schedule_merge_async_task, registration_data_import=cw_rdi)

    assert DeduplicationEngineSimilarityPair.objects.filter(program=cw_rdi.program).count() == 0

    cw_rdi.refresh_from_db()
    assert cw_rdi.status == RegistrationDataImport.MERGING
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

    mock_get_findings.return_value = [_finding(first_pk="1001", second_pk="1002")]

    queue_and_run_retry_task(classify_findings_and_schedule_merge_async_task, registration_data_import=cw_rdi)

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

    mock_get_findings.return_value = [_finding(first_pk="1001", second_pk="1002")]

    queue_and_run_retry_task(classify_findings_and_schedule_merge_async_task, registration_data_import=cw_rdi)

    pending_ind.refresh_from_db()

    assert len(pending_ind.biometric_deduplication_golden_record_results) == 1
    assert pending_ind.biometric_deduplication_golden_record_results[0]["id"] == str(merged_ind.id)
    assert pending_ind.biometric_deduplication_batch_results == []


@patch("hope.apps.registration_data.celery_tasks.merge_registration_data_import_async_task")
@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI.get_group_findings")
@pytest.mark.parametrize(
    "post_publish_status",
    [
        RegistrationDataImport.MERGING,
        RegistrationDataImport.MERGED,
    ],
)
def test_arrival_hook_entry_guard_short_circuits_before_fetching_findings(
    mock_get_findings: mock.Mock,
    mock_enqueue_merge: mock.Mock,
    post_publish_status: str,
    cw_rdi: RegistrationDataImport,
    two_pending_individuals: tuple[Individual, Individual],
) -> None:
    cw_rdi.status = post_publish_status
    cw_rdi.save(update_fields=["status"])

    queue_and_run_retry_task(classify_findings_and_schedule_merge_async_task, registration_data_import=cw_rdi)

    cw_rdi.refresh_from_db()
    assert cw_rdi.status == post_publish_status
    mock_get_findings.assert_not_called()
    mock_enqueue_merge.assert_not_called()


@patch("hope.apps.registration_data.celery_tasks.merge_registration_data_import_async_task")
@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI.get_group_findings")
def test_arrival_hook_rerun_does_not_double_persist_pairs(
    mock_get_findings: mock.Mock,
    mock_enqueue_merge: mock.Mock,
    cw_rdi: RegistrationDataImport,
    two_pending_individuals: tuple[Individual, Individual],
) -> None:
    mock_get_findings.return_value = [_finding(first_pk="1001", second_pk="1002")]
    queue_and_run_retry_task(classify_findings_and_schedule_merge_async_task, registration_data_import=cw_rdi)
    rows_after_first = DeduplicationEngineSimilarityPair.objects.filter(program=cw_rdi.program).count()

    cw_rdi.refresh_from_db()
    cw_rdi.status = RegistrationDataImport.MERGE_SCHEDULED
    cw_rdi.save(update_fields=["status"])
    mock_get_findings.return_value = [_finding(first_pk="1001", second_pk="1002")]

    queue_and_run_retry_task(classify_findings_and_schedule_merge_async_task, registration_data_import=cw_rdi)

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
    mock_get_findings.return_value = [
        _finding(first_pk="1001", second_pk="1002"),
        _finding(first_pk="1001", second_pk="9999"),
    ]

    with caplog.at_level("WARNING"):
        queue_and_run_retry_task(classify_findings_and_schedule_merge_async_task, registration_data_import=cw_rdi)

    assert DeduplicationEngineSimilarityPair.objects.filter(program=cw_rdi.program).count() == 1
    assert any("9999" in rec.getMessage() for rec in caplog.records)
    cw_rdi.refresh_from_db()
    assert cw_rdi.status == RegistrationDataImport.MERGING
    mock_enqueue_merge.assert_called_once()


@patch("hope.apps.core.celery_tasks.async_retry_job_task.retry")
@patch("hope.apps.registration_data.celery_tasks.merge_registration_data_import_async_task")
@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI.get_group_findings")
def test_arrival_hook_marks_rdi_import_error_on_terminal_failure(
    mock_get_findings: mock.Mock,
    mock_enqueue_merge: mock.Mock,
    mock_retry: Mock,
    cw_rdi: RegistrationDataImport,
    two_pending_individuals: tuple[Individual, Individual],
) -> None:
    mock_get_findings.side_effect = RequestException("engine 503")
    mock_retry.side_effect = Retry("retry")

    with pytest.raises(Retry):
        queue_and_run_retry_task(classify_findings_and_schedule_merge_async_task, registration_data_import=cw_rdi)

    cw_rdi.refresh_from_db()
    assert cw_rdi.status == RegistrationDataImport.IMPORT_ERROR
    assert "engine 503" in cw_rdi.error_message
    mock_enqueue_merge.assert_not_called()
    assert DeduplicationEngineSimilarityPair.objects.filter(program=cw_rdi.program).count() == 0


@patch("hope.apps.registration_data.celery_tasks.merge_registration_data_import_async_task")
@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI.get_group_findings")
def test_arrival_hook_self_heals_import_error_to_merge_scheduled(
    mock_get_findings: mock.Mock,
    mock_enqueue_merge: mock.Mock,
    cw_rdi: RegistrationDataImport,
    two_pending_individuals: tuple[Individual, Individual],
) -> None:
    cw_rdi.status = RegistrationDataImport.IMPORT_ERROR
    cw_rdi.error_message = "engine 503"
    cw_rdi.sentry_id = "abc123"
    cw_rdi.save(update_fields=["status", "error_message", "sentry_id"])
    mock_get_findings.return_value = [_finding(first_pk="1001", second_pk="1002")]

    queue_and_run_retry_task(classify_findings_and_schedule_merge_async_task, registration_data_import=cw_rdi)

    cw_rdi.refresh_from_db()
    assert cw_rdi.status == RegistrationDataImport.MERGING
    assert cw_rdi.error_message == ""
    assert cw_rdi.sentry_id == ""
    mock_enqueue_merge.assert_called_once_with(cw_rdi)


@patch("hope.apps.registration_data.celery_tasks.merge_registration_data_import_async_task")
@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI.get_group_findings")
def test_arrival_hook_skips_self_pair_findings(
    mock_get_findings: mock.Mock,
    mock_enqueue_merge: mock.Mock,
    cw_rdi: RegistrationDataImport,
    two_pending_individuals: tuple[Individual, Individual],
    caplog: pytest.LogCaptureFixture,
) -> None:
    mock_get_findings.return_value = [_finding(first_pk="1001", second_pk="1001")]

    with caplog.at_level("WARNING"):
        queue_and_run_retry_task(classify_findings_and_schedule_merge_async_task, registration_data_import=cw_rdi)

    assert DeduplicationEngineSimilarityPair.objects.filter(program=cw_rdi.program).count() == 0
    assert any("duplicate pair" in rec.getMessage() for rec in caplog.records)
    cw_rdi.refresh_from_db()
    assert cw_rdi.status == RegistrationDataImport.MERGING
    mock_enqueue_merge.assert_called_once()


@patch("hope.apps.registration_data.celery_tasks.merge_registration_data_import_async_task")
@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI.get_group_findings")
def test_arrival_hook_orders_pair_by_individual_id(
    mock_get_findings: mock.Mock,
    mock_enqueue_merge: mock.Mock,
    cw_rdi: RegistrationDataImport,
    two_pending_individuals: tuple[Individual, Individual],
) -> None:
    ind_a, ind_b = two_pending_individuals
    lower, higher = sorted([ind_a, ind_b], key=lambda i: i.id)

    mock_get_findings.return_value = [
        _finding(first_pk=higher.country_workspace_id, second_pk=lower.country_workspace_id)
    ]

    queue_and_run_retry_task(classify_findings_and_schedule_merge_async_task, registration_data_import=cw_rdi)

    pair = DeduplicationEngineSimilarityPair.objects.get(program=cw_rdi.program)
    assert pair.individual1_id == lower.id
    assert pair.individual2_id == higher.id


@patch("hope.apps.registration_data.celery_tasks.merge_registration_data_import_async_task")
@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI.get_group_findings")
def test_arrival_hook_classifies_mixed_batch_and_population_for_same_individual(
    mock_get_findings: mock.Mock,
    mock_enqueue_merge: mock.Mock,
    cw_rdi: RegistrationDataImport,
    cw_program,
) -> None:
    pending_a = PendingIndividualFactory(
        program=cw_program,
        business_area=cw_program.business_area,
        registration_data_import=cw_rdi,
        country_workspace_id="1001",
    )
    pending_b = PendingIndividualFactory(
        program=cw_program,
        business_area=cw_program.business_area,
        registration_data_import=cw_rdi,
        country_workspace_id="1002",
    )
    merged_c = PendingIndividualFactory(
        program=cw_program,
        business_area=cw_program.business_area,
        country_workspace_id="1003",
        rdi_merge_status=MergeStatusModel.MERGED,
    )

    assert pending_a.rdi_merge_status == MergeStatusModel.PENDING
    assert pending_b.rdi_merge_status == MergeStatusModel.PENDING
    assert merged_c.rdi_merge_status == MergeStatusModel.MERGED

    mock_get_findings.return_value = [
        _finding(first_pk="1001", second_pk="1002"),
        _finding(first_pk="1001", second_pk="1003"),
    ]

    queue_and_run_retry_task(classify_findings_and_schedule_merge_async_task, registration_data_import=cw_rdi)

    pending_a.refresh_from_db()

    assert len(pending_a.biometric_deduplication_batch_results) == 1
    assert pending_a.biometric_deduplication_batch_results[0]["id"] == str(pending_b.id)

    assert len(pending_a.biometric_deduplication_golden_record_results) == 1
    assert pending_a.biometric_deduplication_golden_record_results[0]["id"] == str(merged_c.id)


@patch("hope.apps.registration_data.celery_tasks.merge_registration_data_import_async_task")
@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI.get_group_findings")
def test_arrival_hook_resolves_cw_id_within_correct_program(
    mock_get_findings: mock.Mock,
    mock_enqueue_merge: mock.Mock,
    cw_rdi: RegistrationDataImport,
    cw_program,
    two_pending_individuals: tuple[Individual, Individual],
) -> None:
    in_program_a, in_program_b = two_pending_individuals
    other_program = ProgramFactory(
        business_area=cw_program.business_area,
        biometric_deduplication_enabled=True,
    )
    other_program_collision = PendingIndividualFactory(
        program=other_program,
        business_area=other_program.business_area,
        country_workspace_id="1001",
    )

    mock_get_findings.return_value = [_finding(first_pk="1001", second_pk="1002")]

    queue_and_run_retry_task(classify_findings_and_schedule_merge_async_task, registration_data_import=cw_rdi)

    pair = DeduplicationEngineSimilarityPair.objects.get(program=cw_program)
    persisted_ids = {pair.individual1_id, pair.individual2_id}
    assert persisted_ids == {in_program_a.id, in_program_b.id}
    assert other_program_collision.id not in persisted_ids


@patch("hope.apps.registration_data.celery_tasks.merge_registration_data_import_async_task")
@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI.get_group_findings")
def test_arrival_hook_status_200_persists_with_scaled_score(
    mock_get_findings: mock.Mock,
    mock_enqueue_merge: mock.Mock,
    cw_rdi: RegistrationDataImport,
    two_pending_individuals: tuple[Individual, Individual],
) -> None:
    mock_get_findings.return_value = [_finding(first_pk="1001", second_pk="1002", score=0.87, status_code="200")]

    queue_and_run_retry_task(classify_findings_and_schedule_merge_async_task, registration_data_import=cw_rdi)

    pair = DeduplicationEngineSimilarityPair.objects.get(program=cw_rdi.program)
    assert pair.similarity_score == Decimal("87.00")
    assert pair.status_code == "200"


@patch("hope.apps.registration_data.celery_tasks.merge_registration_data_import_async_task")
@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI.get_group_findings")
@pytest.mark.parametrize("status_code", ["412", "416", "418", "429"])
def test_arrival_hook_invalid_pair_status_codes_persist_with_scaled_score(
    mock_get_findings: mock.Mock,
    mock_enqueue_merge: mock.Mock,
    status_code: str,
    cw_rdi: RegistrationDataImport,
    two_pending_individuals: tuple[Individual, Individual],
) -> None:
    mock_get_findings.return_value = [_finding(first_pk="1001", second_pk="1002", score=0.95, status_code=status_code)]

    queue_and_run_retry_task(classify_findings_and_schedule_merge_async_task, registration_data_import=cw_rdi)

    pair = DeduplicationEngineSimilarityPair.objects.get(program=cw_rdi.program)
    assert pair.similarity_score == Decimal("95.00")
    assert pair.status_code == status_code


@patch("hope.apps.registration_data.celery_tasks.merge_registration_data_import_async_task")
@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI.get_group_findings")
@pytest.mark.parametrize("status_code", ["404", "500"])
def test_arrival_hook_dropped_status_codes_skip_persist(
    mock_get_findings: mock.Mock,
    mock_enqueue_merge: mock.Mock,
    status_code: str,
    cw_rdi: RegistrationDataImport,
    two_pending_individuals: tuple[Individual, Individual],
) -> None:
    mock_get_findings.return_value = [_finding(first_pk="1001", second_pk="1002", status_code=status_code)]

    queue_and_run_retry_task(classify_findings_and_schedule_merge_async_task, registration_data_import=cw_rdi)

    assert DeduplicationEngineSimilarityPair.objects.filter(program=cw_rdi.program).count() == 0
    cw_rdi.refresh_from_db()
    assert cw_rdi.status == RegistrationDataImport.MERGING
    mock_enqueue_merge.assert_called_once()


@patch("hope.apps.registration_data.celery_tasks.merge_registration_data_import_async_task")
@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI.get_group_findings")
def test_arrival_hook_mixed_status_codes_persist_correct_subset(
    mock_get_findings: mock.Mock,
    mock_enqueue_merge: mock.Mock,
    cw_rdi: RegistrationDataImport,
    cw_program,
) -> None:
    codes = ["200", "404", "412", "416", "418", "429", "500"]
    for i, _code in enumerate(codes):
        PendingIndividualFactory(
            program=cw_program,
            business_area=cw_program.business_area,
            registration_data_import=cw_rdi,
            country_workspace_id=f"{i}A",
        )
        PendingIndividualFactory(
            program=cw_program,
            business_area=cw_program.business_area,
            registration_data_import=cw_rdi,
            country_workspace_id=f"{i}B",
        )
    findings = [_finding(first_pk=f"{i}A", second_pk=f"{i}B", status_code=code) for i, code in enumerate(codes)]
    mock_get_findings.return_value = findings

    queue_and_run_retry_task(classify_findings_and_schedule_merge_async_task, registration_data_import=cw_rdi)

    persisted_codes = sorted(
        DeduplicationEngineSimilarityPair.objects.filter(program=cw_rdi.program).values_list("status_code", flat=True)
    )
    assert persisted_codes == ["200", "412", "416", "418", "429"]


@patch("hope.apps.registration_data.celery_tasks.merge_registration_data_import_async_task")
@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI.get_group_findings")
def test_arrival_hook_dropped_finding_does_not_touch_individual_snapshots(
    mock_get_findings: mock.Mock,
    mock_enqueue_merge: mock.Mock,
    cw_rdi: RegistrationDataImport,
    two_pending_individuals: tuple[Individual, Individual],
) -> None:
    ind_a, ind_b = two_pending_individuals
    mock_get_findings.return_value = [_finding(first_pk="1001", second_pk="1002", status_code="404")]

    queue_and_run_retry_task(classify_findings_and_schedule_merge_async_task, registration_data_import=cw_rdi)

    ind_a.refresh_from_db()
    ind_b.refresh_from_db()
    assert ind_a.biometric_deduplication_batch_results == []
    assert ind_b.biometric_deduplication_batch_results == []


@patch("hope.apps.registration_data.celery_tasks.merge_registration_data_import_async_task")
@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI.get_group_findings")
def test_arrival_hook_invalid_pair_surfaces_zero_score_in_individual_snapshot(
    mock_get_findings: mock.Mock,
    mock_enqueue_merge: mock.Mock,
    cw_rdi: RegistrationDataImport,
    two_pending_individuals: tuple[Individual, Individual],
) -> None:
    ind_a, _ind_b = two_pending_individuals
    mock_get_findings.return_value = [_finding(first_pk="1001", second_pk="1002", score=0.95, status_code="412")]

    queue_and_run_retry_task(classify_findings_and_schedule_merge_async_task, registration_data_import=cw_rdi)

    ind_a.refresh_from_db()
    assert len(ind_a.biometric_deduplication_batch_results) == 1
    assert ind_a.biometric_deduplication_batch_results[0]["similarity_score"] == 95.0


def test_parse_findings_happy_path() -> None:
    findings = [
        {
            "first": {"reference_pk": "CW-001"},
            "second": {"reference_pk": "CW-002"},
            "score": 0.95,
            "status_code": "200",
        },
        {
            "first": {"reference_pk": "CW-003"},
            "second": {"reference_pk": "CW-004"},
            "score": 0.0,
            "status_code": "412",
        },
    ]

    pairs = CwArrivalHookTask()._parse_findings_to_similarity_pairs(findings)

    assert pairs == [
        SimilarityPair(score=0.95, status_code="200", first="CW-001", second="CW-002"),
        SimilarityPair(score=0.0, status_code="412", first="CW-003", second="CW-004"),
    ]


def test_parse_findings_drops_non_persisted_status_code() -> None:
    findings = [
        {
            "first": {"reference_pk": "CW-001"},
            "second": {"reference_pk": "CW-002"},
            "score": 0.0,
            "status_code": "404",
        },
        {
            "first": {"reference_pk": "CW-003"},
            "second": {"reference_pk": "CW-004"},
            "score": 0.0,
            "status_code": "500",
        },
    ]

    assert CwArrivalHookTask()._parse_findings_to_similarity_pairs(findings) == []


def test_parse_findings_drops_finding_with_both_reference_pks_empty() -> None:
    findings = [
        {
            "first": {"reference_pk": None},
            "second": {"reference_pk": ""},
            "score": 0.0,
            "status_code": "200",
        },
    ]

    assert CwArrivalHookTask()._parse_findings_to_similarity_pairs(findings) == []


def test_parse_findings_normalises_empty_string_to_none() -> None:
    findings = [
        {
            "first": {"reference_pk": "CW-001"},
            "second": {"reference_pk": ""},
            "score": 0.5,
            "status_code": "429",
        },
    ]

    pairs = CwArrivalHookTask()._parse_findings_to_similarity_pairs(findings)

    assert pairs == [SimilarityPair(score=0.5, status_code="429", first="CW-001", second=None)]


def test_parse_findings_empty_input() -> None:
    assert CwArrivalHookTask()._parse_findings_to_similarity_pairs([]) == []


@patch("hope.apps.registration_data.celery_tasks.merge_registration_data_import_async_task")
@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI.get_group_findings")
def test_arrival_hook_updates_rdi_counters_and_individual_dedup_statuses(
    mock_get_findings: mock.Mock,
    mock_enqueue_merge: mock.Mock,
    cw_rdi: RegistrationDataImport,
    cw_program,
) -> None:
    pending_a = PendingIndividualFactory(
        program=cw_program,
        business_area=cw_program.business_area,
        registration_data_import=cw_rdi,
        country_workspace_id="1001",
    )
    pending_b = PendingIndividualFactory(
        program=cw_program,
        business_area=cw_program.business_area,
        registration_data_import=cw_rdi,
        country_workspace_id="1002",
    )
    pending_c = PendingIndividualFactory(
        program=cw_program,
        business_area=cw_program.business_area,
        registration_data_import=cw_rdi,
        country_workspace_id="1003",
    )
    _merged_d = PendingIndividualFactory(
        program=cw_program,
        business_area=cw_program.business_area,
        country_workspace_id="2001",
        rdi_merge_status=MergeStatusModel.MERGED,
    )

    mock_get_findings.return_value = [
        _finding(first_pk="1001", second_pk="1002"),
        _finding(first_pk="1003", second_pk="2001"),
    ]

    queue_and_run_retry_task(classify_findings_and_schedule_merge_async_task, registration_data_import=cw_rdi)

    cw_rdi.refresh_from_db()
    assert cw_rdi.dedup_engine_batch_duplicates == 2
    assert cw_rdi.dedup_engine_golden_record_duplicates == 1

    pending_a.refresh_from_db()
    pending_b.refresh_from_db()
    pending_c.refresh_from_db()

    assert pending_a.biometric_deduplication_batch_status == DUPLICATE_IN_BATCH
    assert pending_a.biometric_deduplication_golden_record_status == UNIQUE

    assert pending_b.biometric_deduplication_batch_status == DUPLICATE_IN_BATCH
    assert pending_b.biometric_deduplication_golden_record_status == UNIQUE

    assert pending_c.biometric_deduplication_batch_status == UNIQUE_IN_BATCH
    assert pending_c.biometric_deduplication_golden_record_status == DUPLICATE


@patch("hope.apps.registration_data.celery_tasks.merge_registration_data_import_async_task")
@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI.get_group_findings")
def test_arrival_hook_delegates_statistics_to_biometric_dedup_service(
    mock_get_findings: mock.Mock,
    mock_enqueue_merge: mock.Mock,
    cw_rdi: RegistrationDataImport,
    two_pending_individuals: tuple[Individual, Individual],
) -> None:
    mock_get_findings.return_value = [_finding(first_pk="1001", second_pk="1002")]

    with patch(
        "hope.apps.registration_data.tasks.cw_arrival_hook.BiometricDeduplicationService.store_rdi_deduplication_statistics"
    ) as mock_store_stats:
        queue_and_run_retry_task(classify_findings_and_schedule_merge_async_task, registration_data_import=cw_rdi)

    assert mock_store_stats.call_count == 1
    (called_rdi,) = mock_store_stats.call_args.args
    assert called_rdi.id == cw_rdi.id


@patch("hope.apps.registration_data.celery_tasks.merge_registration_data_import_async_task")
@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI.get_group_findings")
def test_arrival_hook_skips_merge_when_status_changed_under_lock(
    mock_get_findings: mock.Mock,
    mock_enqueue_merge: mock.Mock,
    cw_rdi: RegistrationDataImport,
    two_pending_individuals: tuple[Individual, Individual],
) -> None:
    mock_get_findings.return_value = [_finding(first_pk="1001", second_pk="1002")]

    def flip_status_to_merging(rdi: RegistrationDataImport) -> None:
        RegistrationDataImport.objects.filter(pk=rdi.pk).update(status=RegistrationDataImport.MERGING)

    with patch(
        "hope.apps.registration_data.tasks.cw_arrival_hook.BiometricDeduplicationService.store_rdi_deduplication_statistics",
        side_effect=flip_status_to_merging,
    ):
        queue_and_run_retry_task(classify_findings_and_schedule_merge_async_task, registration_data_import=cw_rdi)

    cw_rdi.refresh_from_db()
    assert cw_rdi.status == RegistrationDataImport.MERGING
    mock_enqueue_merge.assert_not_called()


@patch("hope.apps.registration_data.tasks.cw_arrival_hook.CwArrivalHookTask.execute")
@patch("hope.apps.registration_data.celery_tasks.locked_cache")
def test_arrival_hook_returns_true_when_lock_not_acquired(
    mock_locked_cache: Mock,
    mock_execute: Mock,
    cw_rdi: RegistrationDataImport,
) -> None:
    mock_locked_cache.return_value.__enter__.return_value = False

    result = queue_and_run_retry_task(classify_findings_and_schedule_merge_async_task, registration_data_import=cw_rdi)

    assert result is True
    mock_execute.assert_not_called()
