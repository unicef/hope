import logging
from typing import Any
from uuid import UUID

from django_celery_boost.models import AsyncJobModel

from hope.apps.core.celery import app
from hope.apps.utils.logs import log_start_and_end
from hope.apps.utils.sentry import sentry_tags
from hope.models import AsyncJob, AsyncRetryJob, SanctionList

logger = logging.getLogger(__name__)


def sync_sanction_list_task_action(job: AsyncJob) -> None:
    for sl in SanctionList.objects.all():
        sl.refresh()


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@sentry_tags
def sync_sanction_list_task(self: Any) -> None:
    config: dict[str, str] = {}
    job = AsyncJob.objects.create(
        type=AsyncJobModel.JobType.JOB_TASK,
        repeatable=True,
        action="hope.apps.sanction_list.celery_tasks.sync_sanction_list_task_action",
        config=config,
        group_key="sync_sanction_list_task",
        description="Sync sanction lists",
    )
    job.queue()


def check_against_sanction_list_task_action(job: AsyncRetryJob) -> None:
    from hope.apps.sanction_list.tasks.check_against_sanction_list import (
        CheckAgainstSanctionListTask,
    )

    CheckAgainstSanctionListTask().execute(
        uploaded_file_id=UUID(job.config["uploaded_file_id"]),
        original_file_name=job.config["original_file_name"],
    )


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def check_against_sanction_list_task(self: Any, uploaded_file_id: UUID, original_file_name: str) -> None:
    config = {
        "uploaded_file_id": str(uploaded_file_id),
        "original_file_name": original_file_name,
    }
    job = AsyncRetryJob.objects.create(
        type=AsyncJobModel.JobType.JOB_TASK,
        repeatable=True,
        action="hope.apps.sanction_list.celery_tasks.check_against_sanction_list_task_action",
        config=config,
        group_key=f"check_against_sanction_list_task:{uploaded_file_id}",
        description=f"Check file {uploaded_file_id} against sanction lists",
    )
    job.queue()
