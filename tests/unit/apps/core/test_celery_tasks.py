from datetime import timedelta
from unittest.mock import MagicMock, PropertyMock, patch

from celery.exceptions import Retry
from django.utils import timezone
import pytest

from extras.test_utils.factories import PDUOnlineEditFactory
from hope.apps.core.celery import app
from hope.apps.core.celery_queues import CELERY_QUEUE_DEFAULT, CELERY_QUEUE_PERIODIC
from hope.apps.core.celery_tasks import (
    DEFAULT_RECOVER_MISSING_ASYNC_JOBS_MIN_AGE_SECONDS,
    async_job_task,
    async_retry_job_task,
    cleanup_old_periodic_async_jobs_async_task,
    cleanup_old_periodic_async_jobs_async_task_action,
    recover_missing_async_jobs_async_task,
    recover_missing_async_jobs_async_task_action,
)
from hope.apps.core.tasks_schedules import TASKS_SCHEDULES
from hope.config.fragments import celery as celery_fragment
from hope.models import AsyncJob, AsyncJobModel, AsyncRetryJob, PeriodicAsyncJob, PeriodicAsyncRetryJob


def fake_async_job_action(job: AsyncJob) -> None:
    return None


def fake_async_retry_job_success_action(job: AsyncRetryJob) -> None:
    return None


def fake_async_retry_job_failure_action(job: AsyncRetryJob) -> None:
    raise Exception("sync failed")


def test_async_job_task_skips_execution_when_version_mismatch():
    job = MagicMock(version=2)
    model = MagicMock()
    model.objects.get.return_value = job

    with patch("hope.apps.core.celery_tasks.apps.get_model", return_value=model) as mock_get_model:
        result = async_job_task.run(AsyncJob._meta.label_lower, 123, 1)

    mock_get_model.assert_called_once_with(AsyncJob._meta.label_lower)
    model.objects.get.assert_called_once_with(pk=123)
    job.execute.assert_not_called()
    assert result is None


def test_async_job_task_executes_when_version_matches():
    job = MagicMock(version=3)
    job.execute.return_value = "done"
    model = MagicMock()
    model.objects.get.return_value = job

    with patch("hope.apps.core.celery_tasks.apps.get_model", return_value=model) as mock_get_model:
        result = async_job_task.run(AsyncJob._meta.label_lower, 456, 3)

    mock_get_model.assert_called_once_with(AsyncJob._meta.label_lower)
    model.objects.get.assert_called_once_with(pk=456)
    job.execute.assert_called_once_with()
    assert result == "done"


@patch("hope.apps.core.celery_tasks.logger")
def test_async_job_task_logs_on_failure(mock_logger):
    job = MagicMock(version=3, pk=456, action="hope.apps.payment.celery_tasks.some_action")
    job.execute.side_effect = Exception("boom")
    model = MagicMock()
    model.objects.get.return_value = job

    with patch("hope.apps.core.celery_tasks.apps.get_model", return_value=model):
        with pytest.raises(Exception, match="boom"):
            async_job_task.run(AsyncJob._meta.label_lower, 456, 3)

    mock_logger.exception.assert_called_once_with(
        "Async retry job action failed for job 456 (hope.apps.payment.celery_tasks.some_action)"
    )


def create_async_job(
    *, repeatable: bool, job_model: type[AsyncJob] | type[PeriodicAsyncJob] = AsyncJob
) -> AsyncJob | PeriodicAsyncJob:
    job = job_model.objects.create(
        type="JOB_TASK",
        action="unit.apps.core.test_celery_tasks.fake_async_job_action",
        config={},
        repeatable=repeatable,
    )
    job_model.objects.filter(pk=job.pk).update(
        curr_async_result_id=f"async-result-{job.pk}",
        datetime_queued=timezone.now() - timedelta(seconds=DEFAULT_RECOVER_MISSING_ASYNC_JOBS_MIN_AGE_SECONDS + 60),
    )
    job.refresh_from_db()
    return job


@pytest.mark.django_db
def test_async_job_defaults_job_name_from_action() -> None:
    job = AsyncJob.objects.create(
        type="JOB_TASK",
        action="unit.apps.core.test_celery_tasks.fake_async_job_action",
        config={},
        repeatable=True,
    )

    assert job.job_name == "fake_async_job"


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("action", "expected"),
    [
        (None, ""),
        ("", ""),
        ("hope.apps.payment.celery_tasks.some_action", "some"),
        ("hope.apps.payment.celery_tasks.some_task", "some_task"),
    ],
)
def test_async_job_default_job_name(action: str | None, expected: str) -> None:
    assert AsyncJob.default_job_name(action) == expected


@pytest.mark.django_db
def test_async_job_create_for_instance_raises_for_unsaved_instance() -> None:
    pdu_online_edit = PDUOnlineEditFactory.build()

    with pytest.raises(ValueError, match="Cannot create an async job for an unsaved instance."):
        AsyncJob.create_for_instance(
            pdu_online_edit,
            action="unit.apps.core.test_celery_tasks.fake_async_job_action",
            type="JOB_TASK",
            config={},
            repeatable=True,
        )


@pytest.mark.django_db
def test_async_job_create_for_instance_uses_instance_program_and_default_job_name() -> None:
    pdu_online_edit = PDUOnlineEditFactory()

    job = AsyncJob.create_for_instance(
        pdu_online_edit,
        action="unit.apps.core.test_celery_tasks.fake_async_job_action",
        type="JOB_TASK",
        config={},
        repeatable=True,
    )

    assert job.content_object == pdu_online_edit
    assert job.program == pdu_online_edit.program
    assert job.job_name == "fake_async_job"


@pytest.mark.django_db
def test_periodic_async_job_create_for_instance_uses_periodic_queue() -> None:
    pdu_online_edit = PDUOnlineEditFactory()

    job = PeriodicAsyncJob.create_for_instance(
        pdu_online_edit,
        action="unit.apps.core.test_celery_tasks.fake_async_job_action",
        type="JOB_TASK",
        config={},
        repeatable=True,
    )

    assert job.celery_task_queue == CELERY_QUEUE_PERIODIC


@pytest.mark.django_db
def test_periodic_async_retry_job_queue_task_uses_periodic_queue() -> None:
    with patch.object(PeriodicAsyncJob, "queue", autospec=True) as mock_queue:
        PeriodicAsyncRetryJob.queue_task(
            action="unit.apps.core.test_celery_tasks.fake_async_retry_job_success_action",
            config={},
            group_key="periodic-job",
            description="Periodic retry job",
        )

    job = PeriodicAsyncRetryJob.objects.get()

    assert job.celery_task_queue == CELERY_QUEUE_PERIODIC
    assert job.group_key == "periodic-job"
    mock_queue.assert_called_once_with(job)


@pytest.mark.django_db
def test_async_job_set_queued_preserves_previous_async_result_id() -> None:
    job = AsyncJob.objects.create(
        type="JOB_TASK",
        action="unit.apps.core.test_celery_tasks.fake_async_job_action",
        config={},
        repeatable=True,
        curr_async_result_id="previous-task-id",
    )

    result = MagicMock()
    result.id = "new-task-id"

    job.set_queued(result)
    job.refresh_from_db()

    assert job.curr_async_result_id == "new-task-id"
    assert job.last_async_result_id == "previous-task-id"


@pytest.mark.django_db
def test_async_job_queue_uses_model_queue_and_flower_metadata() -> None:
    job = PeriodicAsyncJob.objects.create(
        type="JOB_TASK",
        action="unit.apps.core.test_celery_tasks.fake_async_job_action",
        config={},
        repeatable=True,
        job_name="logical_job_name",
    )

    with (
        patch("hope.apps.core.celery_tasks.async_job_task.apply_async") as mock_apply_async,
        patch.object(PeriodicAsyncJob, "set_queued", autospec=True) as mock_set_queued,
    ):
        result = MagicMock()
        result.id = "celery-task-id"
        mock_apply_async.return_value = result

        queue_result = job.queue()

    assert queue_result == "celery-task-id"
    mock_apply_async.assert_called_once_with(
        args=(job._meta.label_lower, job.pk, job.version),
        queue=CELERY_QUEUE_PERIODIC,
        shadow="logical_job_name",
        headers={
            "async_job_id": str(job.pk),
            "async_job_model": job._meta.label_lower,
            "job_name": "logical_job_name",
            "action": "unit.apps.core.test_celery_tasks.fake_async_job_action",
            "program_id": "",
            "object_id": "",
            "queue_name": CELERY_QUEUE_PERIODIC,
        },
        argsrepr=f"(async_job_model='{job._meta.label_lower}', async_job_id={job.pk}, job_name='logical_job_name')",
    )
    mock_set_queued.assert_called_once_with(job, result)


def test_async_job_queue_returns_none_for_active_jobs() -> None:
    job = AsyncJob(
        type="JOB_TASK",
        action="unit.apps.core.test_celery_tasks.fake_async_job_action",
        config={},
        repeatable=True,
    )

    with (
        patch.object(AsyncJob, "task_status", new_callable=PropertyMock, return_value=job.QUEUED),
        patch("hope.apps.core.celery_tasks.async_job_task.apply_async") as mock_apply_async,
        patch.object(AsyncJob, "set_queued", autospec=True) as mock_set_queued,
    ):
        queue_result = job.queue()

    assert queue_result is None
    mock_apply_async.assert_not_called()
    mock_set_queued.assert_not_called()


@pytest.mark.django_db
def test_celery_configuration_uses_shared_queue_constants() -> None:
    assert {queue.name for queue in app.conf["task_queues"]} == {
        CELERY_QUEUE_DEFAULT,
        CELERY_QUEUE_PERIODIC,
    }
    assert celery_fragment.CELERY_TASK_DEFAULT_QUEUE == CELERY_QUEUE_DEFAULT
    assert celery_fragment.CELERY_TASK_PERIODIC_QUEUE == CELERY_QUEUE_PERIODIC


@pytest.mark.django_db
def test_all_beat_schedules_use_periodic_queue() -> None:
    assert TASKS_SCHEDULES
    for schedule in TASKS_SCHEDULES.values():
        assert schedule["options"] == {"queue": CELERY_QUEUE_PERIODIC}


@pytest.mark.django_db
def test_cleanup_old_periodic_async_jobs_action_deletes_only_old_periodic_jobs() -> None:
    old_periodic_job = PeriodicAsyncJob.objects.create(
        type="JOB_TASK",
        action="unit.apps.core.test_celery_tasks.fake_async_job_action",
        config={},
        repeatable=True,
    )
    old_default_job = AsyncJob.objects.create(
        type="JOB_TASK",
        action="unit.apps.core.test_celery_tasks.fake_async_job_action",
        config={},
        repeatable=True,
    )
    fresh_periodic_job = PeriodicAsyncJob.objects.create(
        type="JOB_TASK",
        action="unit.apps.core.test_celery_tasks.fake_async_job_action",
        config={},
        repeatable=True,
    )

    stale_created_at = timezone.now() - timedelta(days=31)
    PeriodicAsyncJob.objects.filter(pk=old_periodic_job.pk).update(datetime_created=stale_created_at)
    AsyncJob.objects.filter(pk=old_default_job.pk).update(datetime_created=stale_created_at)

    deleted_count = cleanup_old_periodic_async_jobs_async_task_action()

    assert deleted_count == 1
    assert not PeriodicAsyncJob.objects.filter(pk=old_periodic_job.pk).exists()
    assert AsyncJob.objects.filter(pk=old_default_job.pk).exists()
    assert PeriodicAsyncJob.objects.filter(pk=fresh_periodic_job.pk).exists()


@pytest.mark.django_db
def test_cleanup_old_periodic_async_jobs_task_calls_action() -> None:
    with patch("hope.apps.core.celery_tasks.cleanup_old_periodic_async_jobs_async_task_action") as mock_action:
        mock_action.return_value = 7

        result = cleanup_old_periodic_async_jobs_async_task.run(retention_days=45)

    assert result == 7
    mock_action.assert_called_once_with(retention_days=45)


@pytest.mark.django_db
def test_recover_missing_async_jobs_requeues_repeatable_jobs_only() -> None:
    repeatable_job = create_async_job(repeatable=True)
    create_async_job(repeatable=False)

    with (
        patch("django_celery_boost.models.CeleryTaskModel.task_status", new_callable=PropertyMock) as mock_status,
        patch.object(AsyncJob, "queue", autospec=True, side_effect=["new-id-1"]) as mock_queue,
    ):
        mock_status.return_value = repeatable_job.MISSING

        result = recover_missing_async_jobs_async_task_action()

    assert result == {
        "checked": 2,
        "missing": 2,
        "recoverable": 1,
        "requeued": 1,
        "skipped_non_repeatable": 1,
    }
    mock_queue.assert_called_once_with(repeatable_job)


@pytest.mark.django_db
def test_recover_missing_async_jobs_ignores_non_missing_jobs() -> None:
    create_async_job(repeatable=True)

    with (
        patch("django_celery_boost.models.CeleryTaskModel.task_status", new_callable=PropertyMock) as mock_status,
        patch.object(AsyncJob, "queue", autospec=True) as mock_queue,
    ):
        mock_status.return_value = AsyncJob.SUCCESS

        result = recover_missing_async_jobs_async_task_action()

    assert result == {
        "checked": 1,
        "missing": 0,
        "recoverable": 0,
        "requeued": 0,
        "skipped_non_repeatable": 0,
    }
    mock_queue.assert_not_called()


@pytest.mark.django_db
def test_recover_missing_async_jobs_logs_requeue_when_new_async_result_id_is_returned() -> None:
    job = create_async_job(repeatable=True)

    with (
        patch("django_celery_boost.models.CeleryTaskModel.task_status", new_callable=PropertyMock) as mock_status,
        patch.object(AsyncJob, "queue", autospec=True, return_value="rerun-task-id") as mock_queue,
        patch("hope.apps.core.celery_tasks.logger.info") as mock_log_info,
    ):
        mock_status.return_value = AsyncJob.MISSING

        result = recover_missing_async_jobs_async_task_action()

    assert result["requeued"] == 1
    mock_queue.assert_called_once_with(job)
    mock_log_info.assert_called_once_with(
        "Requeued missing async job %s (%s): %s -> %s",
        job.pk,
        job.action,
        f"async-result-{job.pk}",
        "rerun-task-id",
    )


@pytest.mark.django_db
def test_recover_missing_async_jobs_does_not_count_or_log_when_requeue_returns_no_result_id() -> None:
    job = create_async_job(repeatable=True)

    with (
        patch("django_celery_boost.models.CeleryTaskModel.task_status", new_callable=PropertyMock) as mock_status,
        patch.object(AsyncJob, "queue", autospec=True, return_value=None) as mock_queue,
        patch("hope.apps.core.celery_tasks.logger.info") as mock_log_info,
    ):
        mock_status.return_value = AsyncJob.MISSING

        result = recover_missing_async_jobs_async_task_action()

    assert result == {
        "checked": 1,
        "missing": 1,
        "recoverable": 1,
        "requeued": 0,
        "skipped_non_repeatable": 0,
    }
    mock_queue.assert_called_once_with(job)
    mock_log_info.assert_not_called()


@pytest.mark.django_db
def test_recover_missing_async_jobs_task_reruns_missing_job() -> None:
    job = create_async_job(repeatable=True)

    with (
        patch("django_celery_boost.models.CeleryTaskModel.task_status", new_callable=PropertyMock) as mock_status,
        patch.object(AsyncJob, "queue", autospec=True, return_value="rerun-task-id") as mock_queue,
    ):
        mock_status.return_value = AsyncJob.MISSING

        result = recover_missing_async_jobs_async_task.run()

    assert result == {
        "checked": 1,
        "missing": 1,
        "recoverable": 1,
        "requeued": 1,
        "skipped_non_repeatable": 0,
    }
    mock_queue.assert_called_once_with(job)


@pytest.mark.django_db
def test_recover_missing_async_jobs_skips_jobs_older_than_max_age() -> None:
    job = AsyncJob.objects.create(
        type="JOB_TASK",
        action="unit.apps.core.test_celery_tasks.fake_async_job_action",
        config={},
        repeatable=True,
    )
    AsyncJob.objects.filter(pk=job.pk).update(
        curr_async_result_id=f"async-result-{job.pk}",
        datetime_queued=timezone.now() - timedelta(days=2),
    )

    with patch.object(AsyncJob, "queue", autospec=True) as mock_queue:
        result = recover_missing_async_jobs_async_task_action(max_age_seconds=24 * 60 * 60)

    assert result == {
        "checked": 0,
        "missing": 0,
        "recoverable": 0,
        "requeued": 0,
        "skipped_non_repeatable": 0,
    }
    mock_queue.assert_not_called()


@pytest.mark.django_db
def test_recover_missing_async_jobs_checks_periodic_jobs_on_periodic_model() -> None:
    periodic_job = create_async_job(repeatable=True, job_model=PeriodicAsyncJob)

    with (
        patch("django_celery_boost.models.CeleryTaskModel.task_status", new_callable=PropertyMock) as mock_status,
        patch.object(PeriodicAsyncJob, "queue", autospec=True, return_value="periodic-rerun-id") as mock_queue,
    ):
        mock_status.return_value = PeriodicAsyncJob.MISSING

        result = recover_missing_async_jobs_async_task_action()

    assert result == {
        "checked": 1,
        "missing": 1,
        "recoverable": 1,
        "requeued": 1,
        "skipped_non_repeatable": 0,
    }
    mock_queue.assert_called_once_with(periodic_job)


@pytest.mark.django_db
def test_async_retry_job_task_skips_execution_when_version_mismatch() -> None:
    job = MagicMock(version=2)
    model = MagicMock()
    model.objects.get.return_value = job

    with patch("hope.apps.core.celery_tasks.apps.get_model", return_value=model) as mock_get_model:
        result = async_retry_job_task.run(AsyncRetryJob._meta.label_lower, 123, 1)

    mock_get_model.assert_called_once_with(AsyncRetryJob._meta.label_lower)
    model.objects.get.assert_called_once_with(pk=123)
    job.execute.assert_not_called()
    assert result is None


@pytest.mark.django_db
def test_async_retry_job_task_clears_stale_job_errors_on_success() -> None:
    job = AsyncRetryJob.objects.create(
        type=AsyncJobModel.JobType.JOB_TASK,
        action="unit.apps.core.test_celery_tasks.fake_async_retry_job_success_action",
        config={},
        errors={"exception": "stale failure", "start_flow_error": "keep me"},
    )

    async_retry_job_task.run(job._meta.label_lower, job.pk, job.version)

    job.refresh_from_db()
    assert job.errors == {"start_flow_error": "keep me"}


@pytest.mark.django_db
@patch("hope.apps.core.celery_tasks.async_retry_job_task.retry")
def test_async_retry_job_task_sets_job_errors_before_retry(mock_retry) -> None:
    job = AsyncRetryJob.objects.create(
        type=AsyncJobModel.JobType.JOB_TASK,
        action="unit.apps.core.test_celery_tasks.fake_async_retry_job_failure_action",
        config={},
    )
    mock_retry.side_effect = Retry("retry")

    with pytest.raises(Retry):
        async_retry_job_task.run(job._meta.label_lower, job.pk, job.version)

    job.refresh_from_db()
    assert job.errors == {"exception": "sync failed"}
    mock_retry.assert_called_once()


@pytest.mark.django_db
@patch("hope.apps.core.celery_tasks.async_retry_job_task.retry")
def test_async_retry_job_task_preserves_partial_errors_on_failure(mock_retry) -> None:
    job = AsyncRetryJob.objects.create(
        type=AsyncJobModel.JobType.JOB_TASK,
        action="unit.apps.core.test_celery_tasks.fake_async_retry_job_failure_action",
        config={},
        errors={"start_flow_error": "keep me"},
    )
    mock_retry.side_effect = Retry("retry")

    with pytest.raises(Retry):
        async_retry_job_task.run(job._meta.label_lower, job.pk, job.version)

    job.refresh_from_db()
    assert job.errors == {"start_flow_error": "keep me", "exception": "sync failed"}
    mock_retry.assert_called_once()
