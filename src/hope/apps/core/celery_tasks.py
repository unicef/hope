import logging
from typing import Any

from django_celery_boost.models import AsyncJobModel

from hope.apps.core.celery import app
from hope.apps.utils.logs import log_start_and_end
from hope.apps.utils.sentry import sentry_tags
from hope.models import AsyncJob, XLSXKoboTemplate

logger = logging.getLogger(__name__)


def upload_new_kobo_template_and_update_flex_fields_task_with_retry_action(job: AsyncJob) -> None:
    from hope.apps.core.tasks.upload_new_template_and_update_flex_fields import (  # pragma: no cover
        KoboRetriableError,
        UploadNewKoboTemplateAndUpdateFlexFieldsTask,
    )

    xlsx_kobo_template_id = job.config["xlsx_kobo_template_id"]

    try:
        UploadNewKoboTemplateAndUpdateFlexFieldsTask().execute(xlsx_kobo_template_id=xlsx_kobo_template_id)
        if job.errors:
            job.errors = {}
            job.save(update_fields=["errors"])
    except KoboRetriableError as exc:
        from datetime import timedelta

        from django.utils import timezone

        one_day_earlier_time = timezone.now() - timedelta(days=1)
        if exc.xlsx_kobo_template_object.first_connection_failed_time > one_day_earlier_time:
            job.errors = {"error": str(exc)}
            job.save(update_fields=["errors"])
            logger.exception("Retrying Kobo template upload after retriable error")
            upload_new_kobo_template_and_update_flex_fields_task_with_retry.delay(xlsx_kobo_template_id)
            return
        exc.xlsx_kobo_template_object.status = XLSXKoboTemplate.UNSUCCESSFUL
        exc.xlsx_kobo_template_object.save(update_fields=["status"])
    except Exception as exc:
        job.errors = {"error": str(exc)}
        job.save(update_fields=["errors"])
        logger.exception("Failed to upload Kobo template and update flex fields with retry")
        raise


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def upload_new_kobo_template_and_update_flex_fields_task_with_retry(self: Any, xlsx_kobo_template_id: str) -> None:
    xlsx_kobo_template = XLSXKoboTemplate.objects.get(id=xlsx_kobo_template_id)
    job = AsyncJob.objects.create(
        owner=xlsx_kobo_template.uploaded_by,
        type=AsyncJobModel.JobType.JOB_TASK,
        action="hope.apps.core.celery_tasks.upload_new_kobo_template_and_update_flex_fields_task_with_retry_action",
        config={"xlsx_kobo_template_id": str(xlsx_kobo_template_id)},
        group_key=f"upload_new_kobo_template_and_update_flex_fields_task_with_retry:{xlsx_kobo_template_id}",
        description=f"Retry upload Kobo template {xlsx_kobo_template_id} and update flex fields",
    )
    job.queue()


def upload_new_kobo_template_and_update_flex_fields_task_action(job: AsyncJob) -> None:
    from hope.apps.core.tasks.upload_new_template_and_update_flex_fields import (  # pragma: no cover
        KoboRetriableError,
        UploadNewKoboTemplateAndUpdateFlexFieldsTask,
    )

    xlsx_kobo_template_id = job.config["xlsx_kobo_template_id"]

    try:
        UploadNewKoboTemplateAndUpdateFlexFieldsTask().execute(xlsx_kobo_template_id=xlsx_kobo_template_id)
        if job.errors:
            job.errors = {}
            job.save(update_fields=["errors"])
    except KoboRetriableError:
        upload_new_kobo_template_and_update_flex_fields_task_with_retry.delay(xlsx_kobo_template_id)
    except Exception as exc:
        job.errors = {"error": str(exc)}
        job.save(update_fields=["errors"])
        logger.exception("Failed to upload Kobo template and update flex fields")
        raise


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def upload_new_kobo_template_and_update_flex_fields_task(self: Any, xlsx_kobo_template_id: str) -> None:
    xlsx_kobo_template = XLSXKoboTemplate.objects.get(id=xlsx_kobo_template_id)
    job = AsyncJob.objects.create(
        owner=xlsx_kobo_template.uploaded_by,
        type=AsyncJobModel.JobType.JOB_TASK,
        action="hope.apps.core.celery_tasks.upload_new_kobo_template_and_update_flex_fields_task_action",
        config={"xlsx_kobo_template_id": str(xlsx_kobo_template_id)},
        group_key=f"upload_new_kobo_template_and_update_flex_fields_task:{xlsx_kobo_template_id}",
        description=f"Upload Kobo template {xlsx_kobo_template_id} and update flex fields",
    )
    job.queue()


@app.task(bind=True)
def async_job_task(self, pk: int, version: int | None = None, *args: Any, **kwargs: Any) -> Any:
    """Run the configured async job identified by the primary key.

    This task is invoked by ``AsyncJob.queue()`` with:

    - ``pk``: primary key of the AsyncJob row
    - ``version``: optimistic lock version (optional)
    """
    job = AsyncJob.objects.get(pk=pk)

    if version is not None and job.version != version:
        # job changed after it was queued → skip
        return None

    return job.execute()
