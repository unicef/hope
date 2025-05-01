import logging
from typing import TYPE_CHECKING, Any, Optional

from django.utils import timezone

from constance import config

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.registration_datahub.celery_tasks import (
    check_and_set_taxid,
    locked_cache,
    merge_registration_data_import_task,
)
from hct_mis_api.apps.utils.logs import log_start_and_end
from hct_mis_api.apps.utils.sentry import sentry_tags
from hct_mis_api.contrib.aurora.models import Record, Registration
from hct_mis_api.contrib.aurora.services.extract_record import extract

if TYPE_CHECKING:
    from uuid import UUID

    from django.db.models import _QuerySet

logger = logging.getLogger(__name__)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def process_flex_records_task(self: Any, reg_id: "UUID", rdi_id: "UUID", records_ids: list) -> None:
    registration = Registration.objects.get(id=reg_id)
    try:
        if service := registration.rdi_parser:
            service.process_records(rdi_id, records_ids)
        else:
            logger.warning("Not Implemented Service for Registration")
            raise NotImplementedError
    except Exception as e:
        logger.warning("Process Flex Records Task error")
        raise self.retry(exc=e)


@app.task
@log_start_and_end
@sentry_tags
def extract_records_task(max_records: int = 500) -> None:
    records_ids = Record.objects.filter(data__isnull=True).only("pk").values_list("pk", flat=True)[:max_records]
    extract(records_ids)


@app.task
@log_start_and_end
@sentry_tags
def fresh_extract_records_task(records_ids: Optional["_QuerySet[Any, Any]"] = None) -> None:
    if not records_ids:
        records_ids = Record.objects.all().only("pk").values_list("pk", flat=True)[:5000]
    extract(records_ids)


@app.task(autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 30})
@log_start_and_end
@sentry_tags
def automate_rdi_creation_task(
    registration_id: int,
    page_size: int,
    template: str = "{business_area_name} rdi {date}",
    auto_merge: bool = False,
    fix_tax_id: bool = False,
    **filters: Any,
) -> list:
    try:
        with locked_cache(key=f"automate_rdi_creation_task-{registration_id}") as locked:
            if not locked:
                return []
            output = []
            try:
                registration = Registration.objects.get(id=registration_id)
            except Registration.DoesNotExist:
                raise NotImplementedError
            project = registration.project
            # programme = project.programme TODO programme refactoring
            organization = project.organization
            service: Any | None = registration.rdi_parser
            if service is None:
                raise NotImplementedError

            qs = Record.objects.filter(registration=registration_id, **filters).exclude(
                status__in=[Record.STATUS_IMPORTED, Record.STATUS_ERROR]
            )
            if fix_tax_id:
                check_and_set_taxid(qs)
            all_records_ids = qs.values_list("id", flat=True)
            if len(all_records_ids) == 0:
                return ["No Records found", 0]

            splitted_record_ids = [
                all_records_ids[i : i + page_size] for i in range(0, len(all_records_ids), page_size)
            ]
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
                    merge_registration_data_import_task.delay(rdi.id)

            return output

    except Exception:
        raise


@app.task
@log_start_and_end
@sentry_tags
def clean_old_record_files_task(default_timedelta: int = 60) -> None:
    """This task once a month clears (sets to null) Record's files field."""
    from datetime import timedelta

    try:
        time_threshold = max(
            timezone.now() - timedelta(config.CLEARING_RECORD_FILES_TIMEDELTA),
            timezone.now() - timedelta(default_timedelta),
        )
        Record.objects.filter(timestamp__lt=time_threshold, status=Record.STATUS_IMPORTED).exclude(files=None).update(
            files=None
        )
        logger.info("Record's files have benn successfully cleared")
    except Exception as e:
        logger.warning(e)
        raise
