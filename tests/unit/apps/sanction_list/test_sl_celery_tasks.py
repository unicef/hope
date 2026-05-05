from typing import TYPE_CHECKING
from unittest.mock import patch

import responses

from extras.test_utils.factories import CountryFactory
from hope.apps.core.celery_tasks import async_retry_job_task
from hope.apps.sanction_list.celery_tasks import check_against_sanction_list_async_task, sync_sanction_list_async_task
from hope.models import AsyncRetryJob, PeriodicAsyncRetryJob, SanctionList, SanctionListIndividual

if TYPE_CHECKING:
    from responses import RequestsMock


def queue_and_run_async_task(
    task: object,
    *args: object,
    job_model: type[AsyncRetryJob] | type[PeriodicAsyncRetryJob] = AsyncRetryJob,
    **kwargs: object,
) -> object:
    queue_path = (
        "hope.apps.sanction_list.celery_tasks.PeriodicAsyncRetryJob.queue"
        if job_model is PeriodicAsyncRetryJob
        else "hope.apps.sanction_list.celery_tasks.AsyncRetryJob.queue"
    )
    with patch(queue_path, autospec=True):
        task(*args, **kwargs)
    job = job_model.objects.latest("pk")
    return async_retry_job_task.run(job._meta.label_lower, job.pk, job.version)


def test_sync_sanction_list_task(mocked_responses: "RequestsMock", sanction_list: SanctionList, eu_file: bytes) -> None:
    SanctionList.objects.exclude(pk=sanction_list.pk).delete()
    CountryFactory(name="Afghanistan", short_name="Afghanistan", iso_code2="AF", iso_code3="AFG", iso_num="0004")
    mocked_responses.add(responses.GET, "http://example.com/sl.xml", body=eu_file, status=200)
    queue_and_run_async_task(sync_sanction_list_async_task, job_model=PeriodicAsyncRetryJob)
    assert SanctionListIndividual.objects.count() == 2


def test_check_against_sanction_list_task_queues_retry_job(django_capture_on_commit_callbacks) -> None:
    uploaded_file_id = "123e4567-e89b-12d3-a456-426614174000"
    original_file_name = "test.xlsx"

    with patch("hope.apps.sanction_list.celery_tasks.AsyncRetryJob.queue", autospec=True) as mock_queue:
        with django_capture_on_commit_callbacks(execute=True):
            check_against_sanction_list_async_task(uploaded_file_id, original_file_name)

    job = AsyncRetryJob.objects.latest("pk")
    assert job.action == "hope.apps.sanction_list.celery_tasks.check_against_sanction_list_async_task_action"
    assert job.config == {
        "uploaded_file_id": uploaded_file_id,
        "original_file_name": original_file_name,
    }
    mock_queue.assert_called_once()
