from datetime import timedelta
import logging
from typing import Any

from django.apps import apps
from django.utils import timezone

from hope.apps.core.celery import app
from hope.apps.utils.logs import log_start_and_end
from hope.apps.utils.sentry import sentry_tags
from hope.models import AsyncJob, AsyncRetryJob, PeriodicAsyncJob, XLSXKoboTemplate

logger = logging.getLogger(__name__)
ASYNC_EXCEPTION_KEY = "exception"
DEFAULT_PERIODIC_ASYNC_JOBS_RETENTION_DAYS = 30
DEFAULT_RECOVER_MISSING_ASYNC_JOBS_LIMIT = 1000
DEFAULT_RECOVER_MISSING_ASYNC_JOBS_MIN_AGE_SECONDS = 4 * 60 * 60 + 5 * 60
DEFAULT_RECOVER_MISSING_ASYNC_JOBS_MAX_AGE_SECONDS = 12 * 60 * 60


def requeue_async_job(job: AsyncJob | PeriodicAsyncJob) -> bool:
    previous_async_result_id = job.curr_async_result_id
    new_async_result_id = job.queue()
    if new_async_result_id:
        logger.info(
            "Requeued missing async job %s (%s): %s -> %s",
            job.pk,
            job.action,
            previous_async_result_id,
            new_async_result_id,
        )
        return True
    return False


def upload_new_kobo_template_and_update_flex_fields_task_with_retry_async_task_action(job: AsyncRetryJob) -> None:
    from hope.apps.core.tasks.upload_new_template_and_update_flex_fields import (  # pragma: no cover
        KoboRetriableError,
        UploadNewKoboTemplateAndUpdateFlexFieldsTask,
    )

    xlsx_kobo_template_id = job.config["xlsx_kobo_template_id"]

    try:
        UploadNewKoboTemplateAndUpdateFlexFieldsTask().execute(xlsx_kobo_template_id=xlsx_kobo_template_id)
    except KoboRetriableError as exc:
        from datetime import timedelta

        from django.utils import timezone

        one_day_earlier_time = timezone.now() - timedelta(days=1)
        if exc.xlsx_kobo_template_object.first_connection_failed_time > one_day_earlier_time:  # type: ignore[operator]
            job.errors = {
                **job.errors,
                ASYNC_EXCEPTION_KEY: str(exc),
            }
            job.save(update_fields=["errors"])
            logger.exception("Retrying Kobo template upload after retriable error")
            upload_new_kobo_template_and_update_flex_fields_task_with_retry_async_task(xlsx_kobo_template_id)
            return
        exc.xlsx_kobo_template_object.status = XLSXKoboTemplate.UNSUCCESSFUL
        exc.xlsx_kobo_template_object.save(update_fields=["status"])
    except Exception:
        logger.exception("Failed to upload Kobo template and update flex fields with retry")
        raise


def upload_new_kobo_template_and_update_flex_fields_task_with_retry_async_task(xlsx_kobo_template_id: str) -> None:
    AsyncRetryJob.queue_task(
        job_name=upload_new_kobo_template_and_update_flex_fields_task_with_retry_async_task.__name__,
        action="hope.apps.core.celery_tasks.upload_new_kobo_template_and_update_flex_fields_task_with_retry_async_task_action",
        config={"xlsx_kobo_template_id": xlsx_kobo_template_id},
        group_key=f"upload_new_kobo_template_and_update_flex_fields_task_with_retry_async_task:{xlsx_kobo_template_id}",
        description=f"Retry upload Kobo template {xlsx_kobo_template_id} and update flex fields",
    )


def upload_new_kobo_template_and_update_flex_fields_async_task_action(job: AsyncRetryJob) -> None:
    from hope.apps.core.tasks.upload_new_template_and_update_flex_fields import (  # pragma: no cover
        KoboRetriableError,
        UploadNewKoboTemplateAndUpdateFlexFieldsTask,
    )

    xlsx_kobo_template_id = job.config["xlsx_kobo_template_id"]

    try:
        UploadNewKoboTemplateAndUpdateFlexFieldsTask().execute(xlsx_kobo_template_id=xlsx_kobo_template_id)
    except KoboRetriableError:
        upload_new_kobo_template_and_update_flex_fields_task_with_retry_async_task(xlsx_kobo_template_id)


def upload_new_kobo_template_and_update_flex_fields_async_task(xlsx_kobo_template_id: str) -> None:
    AsyncRetryJob.queue_task(
        job_name=upload_new_kobo_template_and_update_flex_fields_async_task.__name__,
        action="hope.apps.core.celery_tasks.upload_new_kobo_template_and_update_flex_fields_async_task_action",
        config={"xlsx_kobo_template_id": xlsx_kobo_template_id},
        group_key=f"upload_new_kobo_template_and_update_flex_fields_async_task:{xlsx_kobo_template_id}",
        description=f"Upload Kobo template {xlsx_kobo_template_id} and update flex fields",
    )


@app.task(bind=True, acks_late=True, reject_on_worker_lost=True)
@log_start_and_end
@sentry_tags
def async_job_task(
    self: Any,
    model_label: str,
    pk: int,
    version: int | None = None,
    *args: Any,
    **kwargs: Any,
) -> Any:
    job = apps.get_model(model_label).objects.get(pk=pk)

    if version is not None and job.version != version:
        return None

    try:
        return job.execute()
    except Exception as exc:
        job.errors = {
            **job.errors,
            ASYNC_EXCEPTION_KEY: str(exc),
        }
        job.save(update_fields=["errors"])
        logger.exception(f"Async retry job action failed for job {job.pk} ({job.action})")
        raise


@app.task(bind=True, default_retry_delay=60, max_retries=3, acks_late=True, reject_on_worker_lost=True)
@log_start_and_end
@sentry_tags
def async_retry_job_task(
    self: Any,
    model_label: str,
    pk: int,
    version: int | None = None,
    *args: Any,
    **kwargs: Any,
) -> Any:
    job = apps.get_model(model_label).objects.get(pk=pk)

    if version is not None and job.version != version:
        return None

    try:
        result = job.execute()
        if ASYNC_EXCEPTION_KEY in job.errors:
            job.errors.pop(ASYNC_EXCEPTION_KEY, None)
            job.save(update_fields=["errors"])
        return result
    except Exception as exc:
        job.errors = {
            **job.errors,
            ASYNC_EXCEPTION_KEY: str(exc),
        }
        job.save(update_fields=["errors"])
        logger.exception(f"Async retry job action failed for job {job.pk} ({job.action})")
        raise self.retry(exc=exc)


def recover_missing_async_jobs_async_task_action(
    *,
    limit: int = DEFAULT_RECOVER_MISSING_ASYNC_JOBS_LIMIT,
    min_age_seconds: int = DEFAULT_RECOVER_MISSING_ASYNC_JOBS_MIN_AGE_SECONDS,
    max_age_seconds: int = DEFAULT_RECOVER_MISSING_ASYNC_JOBS_MAX_AGE_SECONDS,
) -> dict[str, int]:
    newest_allowed = timezone.now() - timedelta(seconds=min_age_seconds)
    oldest_allowed = timezone.now() - timedelta(seconds=max_age_seconds)
    stats = {
        "checked": 0,
        "missing": 0,
        "recoverable": 0,
        "requeued": 0,
        "skipped_non_repeatable": 0,
    }
    candidates: list[AsyncJob | PeriodicAsyncJob] = []
    for job_model in (AsyncJob, PeriodicAsyncJob):
        candidates.extend(
            list(
                job_model.objects.filter(
                    curr_async_result_id__isnull=False,
                    datetime_queued__isnull=False,
                    datetime_queued__gte=oldest_allowed,
                    datetime_queued__lte=newest_allowed,
                ).order_by("datetime_queued")[:limit]
            )
        )

    for job in sorted(candidates, key=lambda candidate: candidate.datetime_queued or timezone.now())[:limit]:
        stats["checked"] += 1
        if job.task_status != job.MISSING:
            continue

        stats["missing"] += 1
        if not job.repeatable:
            stats["skipped_non_repeatable"] += 1
            continue

        stats["recoverable"] += 1
        if requeue_async_job(job):
            stats["requeued"] += 1

    return stats


@app.task()
def recover_missing_async_jobs_async_task(
    limit: int = DEFAULT_RECOVER_MISSING_ASYNC_JOBS_LIMIT,
    min_age_seconds: int = DEFAULT_RECOVER_MISSING_ASYNC_JOBS_MIN_AGE_SECONDS,
    max_age_seconds: int = DEFAULT_RECOVER_MISSING_ASYNC_JOBS_MAX_AGE_SECONDS,
) -> dict[str, int]:
    return recover_missing_async_jobs_async_task_action(
        limit=limit,
        min_age_seconds=min_age_seconds,
        max_age_seconds=max_age_seconds,
    )


def cleanup_old_periodic_async_jobs_async_task_action(
    retention_days: int = DEFAULT_PERIODIC_ASYNC_JOBS_RETENTION_DAYS,
) -> int:
    cutoff = timezone.now() - timedelta(days=retention_days)
    deleted_count, _ = PeriodicAsyncJob.objects.filter(
        datetime_created__lt=cutoff,
    ).delete()
    return deleted_count


@app.task()
def cleanup_old_periodic_async_jobs_async_task(
    retention_days: int = DEFAULT_PERIODIC_ASYNC_JOBS_RETENTION_DAYS,
) -> int:
    return cleanup_old_periodic_async_jobs_async_task_action(retention_days=retention_days)
