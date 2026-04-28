import logging
from uuid import UUID

from hope.apps.core.celery import app
from hope.models import AsyncRetryJob, PeriodicAsyncRetryJob, SanctionList

logger = logging.getLogger(__name__)


def sync_sanction_list_async_task_action(job: AsyncRetryJob | None = None) -> None:
    for sl in SanctionList.objects.all():
        sl.refresh()


@app.task()
def sync_sanction_list_async_task() -> None:
    PeriodicAsyncRetryJob.queue_task(
        job_name=sync_sanction_list_async_task.__name__,
        action="hope.apps.sanction_list.celery_tasks.sync_sanction_list_async_task_action",
        config={},
        group_key="sync_sanction_list_async_task",
        description="Sync sanction lists",
    )


def check_against_sanction_list_async_task_action(job: AsyncRetryJob) -> None:
    from hope.apps.sanction_list.tasks.check_against_sanction_list import (
        CheckAgainstSanctionListTask,
    )

    CheckAgainstSanctionListTask().execute(
        uploaded_file_id=UUID(job.config["uploaded_file_id"]),
        original_file_name=job.config["original_file_name"],
    )


def check_against_sanction_list_async_task(uploaded_file_id: str, original_file_name: str) -> None:
    config = {
        "uploaded_file_id": uploaded_file_id,
        "original_file_name": original_file_name,
    }
    AsyncRetryJob.queue_task(
        job_name=check_against_sanction_list_async_task.__name__,
        action="hope.apps.sanction_list.celery_tasks.check_against_sanction_list_async_task_action",
        config=config,
        group_key=f"check_against_sanction_list_async_task:{uploaded_file_id}",
        description=f"Check file {uploaded_file_id} against sanction lists",
    )
