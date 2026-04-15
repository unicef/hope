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

    with patch("hope.apps.core.celery_tasks.AsyncJob") as async_job_cls:
        async_job_cls.objects.get.return_value = job

        result = async_job_task.run(pk=123, version=1)

    async_job_cls.objects.get.assert_called_once_with(pk=123)
    job.execute.assert_not_called()
    assert result is None


def test_async_job_task_executes_when_version_matches():
    job = MagicMock(version=3)
    job.execute.return_value = "done"

    with patch("hope.apps.core.celery_tasks.AsyncJob") as async_job_cls:
        async_job_cls.objects.get.return_value = job

        result = async_job_task.run(pk=456, version=3)

    async_job_cls.objects.get.assert_called_once_with(pk=456)
    job.execute.assert_called_once_with()
    assert result == "done"


@patch("hope.apps.core.celery_tasks.logger")
def test_async_job_task_logs_on_failure(mock_logger):
    job = MagicMock(version=3, pk=456, action="hope.apps.payment.celery_tasks.some_action")
    job.execute.side_effect = Exception("boom")

    with patch("hope.apps.core.celery_tasks.AsyncJob") as async_job_cls:
        async_job_cls.objects.get.return_value = job

        with pytest.raises(Exception, match="boom"):
            async_job_task.run(pk=456, version=3)

    mock_logger.exception.assert_called_once_with(
        "Async retry job action failed for job 456 (hope.apps.payment.celery_tasks.some_action)"
    )


def create_async_job(*, repeatable: bool) -> AsyncJob:
    job = AsyncJob.objects.create(
        type="JOB_TASK",
        action="unit.apps.core.test_celery_tasks.fake_async_job_action",
        config={},
        repeatable=repeatable,
    )
    AsyncJob.objects.filter(pk=job.pk).update(
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

    assert job.queue_name == CELERY_QUEUE_PERIODIC


@pytest.mark.django_db
def test_periodic_async_retry_job_queue_task_uses_periodic_queue() -> None:
    with patch.object(AsyncJob, "queue", autospec=True) as mock_queue:
        PeriodicAsyncRetryJob.queue_task(
            action="unit.apps.core.test_celery_tasks.fake_async_retry_job_success_action",
            config={},
            group_key="periodic-job",
            description="Periodic retry job",
        )

    job = AsyncRetryJob.objects.get()

    assert job.queue_name == CELERY_QUEUE_PERIODIC
    assert job.group_key == "periodic-job"
    mock_queue.assert_called_once_with(job)


@pytest.mark.django_db
def test_async_job_save_sets_default_queue_name_when_blank() -> None:
    job = AsyncJob.objects.create(
        type="JOB_TASK",
        action="unit.apps.core.test_celery_tasks.fake_async_job_action",
        config={},
        repeatable=True,
        queue_name="",
    )

    assert job.queue_name == CELERY_QUEUE_DEFAULT


@pytest.mark.django_db
def test_async_job_queue_uses_queue_name_and_flower_metadata() -> None:
    job = AsyncJob.objects.create(
        type="JOB_TASK",
        action="unit.apps.core.test_celery_tasks.fake_async_job_action",
        config={},
        repeatable=True,
        job_name="logical_job_name",
        queue_name=CELERY_QUEUE_PERIODIC,
    )

    with (
        patch("hope.apps.core.celery_tasks.async_job_task.apply_async") as mock_apply_async,
        patch.object(AsyncJob, "set_queued", autospec=True) as mock_set_queued,
    ):
        result = MagicMock()
        result.id = "celery-task-id"
        mock_apply_async.return_value = result

        queue_result = job.queue()

    assert queue_result is None
    mock_apply_async.assert_called_once_with(
        args=(job.pk, job.version),
        queue=CELERY_QUEUE_PERIODIC,
        shadow="logical_job_name",
        headers={
            "async_job_id": str(job.pk),
            "job_name": "logical_job_name",
            "action": "unit.apps.core.test_celery_tasks.fake_async_job_action",
            "program_id": "",
            "object_id": "",
            "queue_name": CELERY_QUEUE_PERIODIC,
        },
        argsrepr=f"(async_job_id={job.pk}, job_name='logical_job_name')",
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
def test_recover_missing_async_jobs_schedule_uses_periodic_queue() -> None:
    assert TASKS_SCHEDULES["recover_missing_async_jobs_async_task"]["options"] == {"queue": CELERY_QUEUE_PERIODIC}


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
def test_recover_missing_async_jobs_can_requeue_non_repeatable_jobs_when_enabled() -> None:
    create_async_job(repeatable=True)
    create_async_job(repeatable=False)

    with (
        patch("django_celery_boost.models.CeleryTaskModel.task_status", new_callable=PropertyMock) as mock_status,
        patch.object(AsyncJob, "queue", autospec=True, side_effect=["new-id-1", "new-id-2"]) as mock_queue,
    ):
        mock_status.return_value = AsyncJob.MISSING

        result = recover_missing_async_jobs_async_task_action(recover_non_repeatable=True)

    assert result == {
        "checked": 2,
        "missing": 2,
        "recoverable": 2,
        "requeued": 2,
        "skipped_non_repeatable": 0,
    }
    assert mock_queue.call_count == 2


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
        "Recovered missing async job %s (%s): %s -> %s",
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
def test_recover_missing_async_jobs_honors_dry_run() -> None:
    create_async_job(repeatable=True)

    with (
        patch("django_celery_boost.models.CeleryTaskModel.task_status", new_callable=PropertyMock) as mock_status,
        patch.object(AsyncJob, "queue", autospec=True) as mock_queue,
    ):
        mock_status.return_value = AsyncJob.MISSING

        result = recover_missing_async_jobs_async_task_action(dry_run=True)

    assert result == {
        "checked": 1,
        "missing": 1,
        "recoverable": 1,
        "requeued": 0,
        "skipped_non_repeatable": 0,
    }
    mock_queue.assert_not_called()


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
def test_async_retry_job_task_skips_execution_when_version_mismatch() -> None:
    job = MagicMock(version=2)

    with patch("hope.apps.core.celery_tasks.AsyncRetryJob") as async_retry_job_cls:
        async_retry_job_cls.objects.get.return_value = job

        result = async_retry_job_task.run(pk=123, version=1)

    async_retry_job_cls.objects.get.assert_called_once_with(pk=123)
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

    async_retry_job_task.run(job.pk, job.version)

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
        async_retry_job_task.run(job.pk, job.version)

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
        async_retry_job_task.run(job.pk, job.version)

    job.refresh_from_db()
    assert job.errors == {"start_flow_error": "keep me", "exception": "sync failed"}
    mock_retry.assert_called_once()
