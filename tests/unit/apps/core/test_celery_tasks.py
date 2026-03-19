from unittest.mock import MagicMock, patch

import pytest

from hope.apps.core.celery_tasks import async_job_task


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
