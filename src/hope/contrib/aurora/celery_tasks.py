import logging
from typing import Any

from constance import config
from django.utils import timezone

from hope.apps.core.celery import app
from hope.apps.core.celery_tasks import NonRetriableTaskError
from hope.apps.registration_data.celery_tasks import (
    check_and_set_taxid,
    locked_cache,
    merge_registration_data_import_async_task,
)
from hope.apps.utils.logs import log_start_and_end
from hope.apps.utils.sentry import sentry_tags
from hope.contrib.aurora.models import Record, Registration
from hope.contrib.aurora.services.extract_record import extract
from hope.models import AsyncJob, AsyncRetryJob, RegistrationDataImport

logger = logging.getLogger(__name__)


def process_flex_records_async_task_action(job: AsyncRetryJob) -> None:
    registration = Registration.objects.get(id=job.config["registration_id"])
    try:
        if service := registration.rdi_parser:
            service.process_records(job.config["rdi_id"], job.config["records_ids"])
        else:
            logger.warning("Not Implemented Service for Registration")
            raise NotImplementedError
    except NotImplementedError as exc:
        logger.warning("Process Flex Records Task error")
        raise exc


def process_flex_records_async_task(
    registration: Registration,
    rdi: RegistrationDataImport,
    records_ids: list[int],
) -> None:
    AsyncRetryJob.queue_task(
        instance=rdi,
        program=rdi.program,
        job_name=process_flex_records_async_task.__name__,
        action="hope.contrib.aurora.celery_tasks.process_flex_records_async_task_action",
        config={
            "registration_id": str(registration.id),
            "rdi_id": str(rdi.id),
            "records_ids": records_ids,
        },
        group_key="aurora",
        description=f"Process Aurora records for RDI {rdi.id}",
    )


def extract_records_async_task_action(job: AsyncJob) -> None:
    max_records = int(job.config["max_records"])
    records_ids = Record.objects.filter(data__isnull=True).only("pk").values_list("pk", flat=True)[:max_records]
    extract(records_ids)


@app.task()
@log_start_and_end
@sentry_tags
def extract_records_async_task(max_records: int = 500) -> None:
    AsyncJob.queue_task(
        job_name=extract_records_async_task.__name__,
        action="hope.contrib.aurora.celery_tasks.extract_records_async_task_action",
        config={"max_records": max_records},
        group_key="aurora",
        description=f"Extract Aurora records with limit {max_records}",
    )


def fresh_extract_records_async_task_action(job: AsyncJob) -> None:
    records_ids = job.config.get("records_ids")
    if not records_ids:
        records_ids = list(Record.objects.all().only("pk").values_list("pk", flat=True)[:5000])
    extract(records_ids)


@app.task()
@log_start_and_end
@sentry_tags
def fresh_extract_records_async_task(
    records_ids: list[int],
) -> None:
    AsyncJob.queue_task(
        job_name=fresh_extract_records_async_task.__name__,
        action="hope.contrib.aurora.celery_tasks.fresh_extract_records_async_task_action",
        config={"records_ids": records_ids},
        group_key="aurora",
        description="Fresh extract Aurora records",
    )


def automate_rdi_creation_async_task_action(job: AsyncRetryJob) -> list[Any]:
    registration_id = int(job.config["registration_id"])
    page_size = int(job.config["page_size"])
    template = str(job.config["template"])
    auto_merge = bool(job.config["auto_merge"])
    fix_tax_id = bool(job.config["fix_tax_id"])
    filters = dict(job.config.get("filters", {}))

    with locked_cache(key=f"automate_rdi_creation_async_task-{registration_id}") as locked:
        if not locked:
            logger.info(f"Automatic creation of RDI {registration_id} already running")
            return []

        try:
            registration = Registration.objects.get(source_id=registration_id)
        except Registration.DoesNotExist as exc:
            raise NonRetriableTaskError(f"Aurora registration {registration_id} does not exist") from exc

        organization = registration.project.organization
        service = registration.rdi_parser
        if service is None:
            raise NonRetriableTaskError(f"Aurora registration {registration_id} has no RDI parser")

        qs = (
            Record.objects.filter(registration=registration_id, **filters)
            .exclude(status__in=[Record.STATUS_IMPORTED, Record.STATUS_ERROR])
            .exclude(ignored=True)
        )
        if fix_tax_id:
            check_and_set_taxid(qs)

        all_records_ids = list(qs.values_list("id", flat=True))
        if not all_records_ids:
            return ["No Records found", 0]

        output: list[list[Any]] = []
        splitted_record_ids = [all_records_ids[i : i + page_size] for i in range(0, len(all_records_ids), page_size)]
        for page, records_ids in enumerate(splitted_record_ids, 1):
            rdi_name = template.format(
                page=page,
                date=timezone.now(),
                registration_id=registration_id,
                page_size=page_size,
                records=len(records_ids),
                business_area_name=organization.name,
            )
            rdi = service.create_rdi(imported_by=None, rdi_name=rdi_name)
            service.process_records(rdi_id=rdi.id, records_ids=records_ids)
            output.append([rdi_name, len(records_ids)])
            if auto_merge:
                merge_registration_data_import_async_task(rdi)

        return output


@app.task()
@log_start_and_end
@sentry_tags
def automate_rdi_creation_async_task(
    registration: Registration,
    page_size: int,
    template: str = "{business_area_name} rdi {date}",
    auto_merge: bool = False,
    fix_tax_id: bool = False,
    **filters: Any,
) -> None:
    AsyncRetryJob.queue_task(
        instance=registration,
        program=registration.project.programme,
        job_name=automate_rdi_creation_async_task.__name__,
        action="hope.contrib.aurora.celery_tasks.automate_rdi_creation_async_task_action",
        config={
            "registration_id": registration.source_id,
            "page_size": page_size,
            "template": template,
            "auto_merge": auto_merge,
            "fix_tax_id": fix_tax_id,
            "filters": filters,
        },
        group_key="aurora",
        description=f"Create RDIs from Aurora registration {registration.source_id}",
    )


def clean_old_record_files_async_task_action(job: AsyncJob) -> None:
    from datetime import timedelta

    time_threshold = timezone.now() - timedelta(int(job.config["clearing_record_files_timedelta"]))
    Record.objects.filter(timestamp__lt=time_threshold, status=Record.STATUS_IMPORTED).delete()
    logger.info("Record's files have been successfully cleared")


@app.task()
@log_start_and_end
@sentry_tags
def clean_old_record_files_async_task() -> None:
    AsyncJob.queue_task(
        job_name=clean_old_record_files_async_task.__name__,
        action="hope.contrib.aurora.celery_tasks.clean_old_record_files_async_task_action",
        config={"clearing_record_files_timedelta": config.CLEARING_RECORD_FILES_TIMEDELTA},
        group_key="aurora",
        description="Clean old Aurora record files",
    )
