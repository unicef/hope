from datetime import timedelta
from unittest.mock import MagicMock, PropertyMock, patch

from django.utils import timezone
import pytest

from hope.apps.core.celery_tasks import (
    DEFAULT_RECOVER_MISSING_ASYNC_JOBS_MIN_AGE_SECONDS,
    async_job_task,
    recover_missing_async_jobs_async_task,
    recover_missing_async_jobs_async_task_action,
)
from hope.models import AsyncJob


def fake_async_job_action(job: AsyncJob) -> None:
    return None


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
