import datetime
import logging
from typing import Any

from django.contrib.admin.options import get_content_type_for_model
from django.core.cache import cache
from django.db import transaction
from django_celery_boost.models import AsyncJobModel

from hope.apps.core.celery import app
from hope.apps.periodic_data_update.service.periodic_data_update_export_template_service import (
    PDUXlsxExportTemplateService,
)
from hope.apps.periodic_data_update.service.periodic_data_update_import_service import PDUXlsxImportService
from hope.apps.periodic_data_update.service.periodic_data_update_online_edit_generate_data_service import (
    PDUOnlineEditGenerateDataService,
)
from hope.apps.periodic_data_update.service.periodic_data_update_online_edit_merge_service import (
    PDUOnlineEditMergeService,
)
from hope.apps.periodic_data_update.signals import (
    increment_periodic_data_update_template_version_cache_function,
)
from hope.apps.utils.logs import log_start_and_end
from hope.apps.utils.sentry import sentry_tags, set_sentry_business_area_tag
from hope.models import AsyncJob, AsyncRetryJob, FileTemp, PDUOnlineEdit, PDUXlsxTemplate, PDUXlsxUpload, User

logger = logging.getLogger(__name__)


def import_periodic_data_update_action(job: AsyncJob) -> bool:
    periodic_data_update_upload = PDUXlsxUpload.objects.get(id=job.config["periodic_data_update_upload_id"])
    service = PDUXlsxImportService(periodic_data_update_upload)
    service.import_data()
    return True


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def import_periodic_data_update(self: Any, periodic_data_update_upload_id: str) -> None:
    config = {"periodic_data_update_upload_id": str(periodic_data_update_upload_id)}
    job = AsyncJob.objects.create(
        type=AsyncJobModel.JobType.JOB_TASK,
        repeatable=True,
        action="hope.apps.periodic_data_update.celery_tasks.import_periodic_data_update_action",
        config=config,
        group_key=f"import_periodic_data_update:{periodic_data_update_upload_id}",
        description=f"Import periodic data update upload {periodic_data_update_upload_id}",
    )
    job.queue()


def export_periodic_data_update_export_template_service_action(job: AsyncJob) -> bool:
    periodic_data_update_template = PDUXlsxTemplate.objects.get(id=job.config["periodic_data_update_template_id"])
    service = PDUXlsxExportTemplateService(periodic_data_update_template)
    service.generate_workbook()
    service.save_xlsx_file()
    return True


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def export_periodic_data_update_export_template_service(self: Any, periodic_data_update_template_id: str) -> None:
    config = {"periodic_data_update_template_id": str(periodic_data_update_template_id)}
    job = AsyncJob.objects.create(
        type=AsyncJobModel.JobType.JOB_TASK,
        repeatable=True,
        action="hope.apps.periodic_data_update.celery_tasks.export_periodic_data_update_export_template_service_action",
        config=config,
        group_key=f"export_periodic_data_update_export_template_service:{periodic_data_update_template_id}",
        description=f"Export periodic data update template {periodic_data_update_template_id}",
    )
    job.queue()


def generate_pdu_online_edit_data_task_action(job: AsyncJob) -> bool:
    pdu_online_edit = PDUOnlineEdit.objects.get(id=job.config["pdu_online_edit_id"])
    try:
        service = PDUOnlineEditGenerateDataService(
            program=pdu_online_edit.program,
            filters=job.config["filters"],
            rounds_data=job.config["rounds_data"],
        )
        edit_data = service.generate_edit_data()
        pdu_online_edit.edit_data = edit_data
        pdu_online_edit.number_of_records = len(edit_data)
        pdu_online_edit.status = PDUOnlineEdit.Status.NEW
        pdu_online_edit.save(update_fields=["edit_data", "number_of_records", "status"])
    except Exception:
        logger.exception("Failed to generate PDU online edit data")
        pdu_online_edit.status = PDUOnlineEdit.Status.FAILED_CREATE
        pdu_online_edit.save(update_fields=["status"])
        raise
    return True


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def generate_pdu_online_edit_data_task(self: Any, pdu_online_edit_id: int, filters: dict, rounds_data: list) -> None:
    config = {
        "pdu_online_edit_id": pdu_online_edit_id,
        "filters": filters,
        "rounds_data": rounds_data,
    }
    job = AsyncJob.objects.create(
        type=AsyncJobModel.JobType.JOB_TASK,
        repeatable=True,
        action="hope.apps.periodic_data_update.celery_tasks.generate_pdu_online_edit_data_task_action",
        config=config,
        group_key=f"generate_pdu_online_edit_data_task:{pdu_online_edit_id}",
        description=f"Generate online edit data for PDU {pdu_online_edit_id}",
    )
    job.queue()


def merge_pdu_online_edit_task_action(job: AsyncJob) -> bool:
    with cache.lock(
        "pdu_online_edit_merge",
        blocking_timeout=60 * 10,
        timeout=60 * 60 * 2,
    ):
        pdu_online_edit = PDUOnlineEdit.objects.get(id=job.config["pdu_online_edit_id"])
        try:
            service = PDUOnlineEditMergeService(pdu_online_edit)
            service.merge_edit_data()
            pdu_online_edit.status = PDUOnlineEdit.Status.MERGED
            pdu_online_edit.save(update_fields=["status"])
        except Exception:
            logger.exception("Failed to merge PDU online edit")
            pdu_online_edit.status = PDUOnlineEdit.Status.FAILED_MERGE
            pdu_online_edit.save(update_fields=["status"])
            raise
        return True


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def merge_pdu_online_edit_task(self: Any, pdu_online_edit_id: int) -> None:
    config = {"pdu_online_edit_id": pdu_online_edit_id}
    job = AsyncJob.objects.create(
        type=AsyncJobModel.JobType.JOB_TASK,
        repeatable=True,
        action="hope.apps.periodic_data_update.celery_tasks.merge_pdu_online_edit_task_action",
        config=config,
        group_key=f"merge_pdu_online_edit_task:{pdu_online_edit_id}",
        description=f"Merge online edit data for PDU {pdu_online_edit_id}",
    )
    job.queue()


def remove_old_pdu_template_files_task_action(job: AsyncRetryJob) -> None:
    with transaction.atomic():
        days = datetime.datetime.now() - datetime.timedelta(days=int(job.config["expiration_days"]))
        file_qs = FileTemp.objects.filter(
            content_type=get_content_type_for_model(PDUXlsxTemplate),
            created__lt=days,
        )
        removed_count = file_qs.count()
        if not removed_count:
            return

        templates_qs = PDUXlsxTemplate.objects.filter(file__in=file_qs)
        templates_qs.update(status=PDUXlsxTemplate.Status.TO_EXPORT)
        templates_qs.update(celery_tasks_results_ids={})
        for business_area_slug, program_id in templates_qs.values_list("business_area__slug", "program_id"):
            increment_periodic_data_update_template_version_cache_function(business_area_slug, program_id)

        for xlsx_obj in file_qs.iterator(chunk_size=1000):
            xlsx_obj.file.delete(save=False)
            xlsx_obj.delete()

        logger.info(f"Removed old PDU FileTemp: {removed_count}")


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def remove_old_pdu_template_files_task(self: Any, expiration_days: int = 30) -> None:
    config = {"expiration_days": expiration_days}
    job = AsyncRetryJob.objects.create(
        type=AsyncJobModel.JobType.JOB_TASK,
        repeatable=True,
        action="hope.apps.periodic_data_update.celery_tasks.remove_old_pdu_template_files_task_action",
        config=config,
        group_key=f"remove_old_pdu_template_files_task:{expiration_days}",
        description=f"Remove PDU template files older than {expiration_days} days",
    )
    job.queue()


def send_pdu_online_edit_notification_emails_action(job: AsyncJob) -> None:
    from hope.apps.periodic_data_update.notifications import PDUOnlineEditNotification

    pdu_online_edit = PDUOnlineEdit.objects.get(id=job.config["pdu_online_edit_id"])
    action_user = User.objects.get(id=job.config["action_user_id"])
    set_sentry_business_area_tag(pdu_online_edit.business_area.name)
    PDUOnlineEditNotification(
        pdu_online_edit,
        job.config["action"],
        action_user,
        job.config["action_date_formatted"],
    ).send_email_notification()


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def send_pdu_online_edit_notification_emails(
    self: Any,
    pdu_online_edit_id: int,
    action: str,
    action_user_id: str,
    action_date_formatted: str,
) -> None:
    config = {
        "pdu_online_edit_id": pdu_online_edit_id,
        "action": action,
        "action_user_id": str(action_user_id),
        "action_date_formatted": action_date_formatted,
    }
    job = AsyncJob.objects.create(
        type=AsyncJobModel.JobType.JOB_TASK,
        repeatable=True,
        action="hope.apps.periodic_data_update.celery_tasks.send_pdu_online_edit_notification_emails_action",
        config=config,
        group_key=f"send_pdu_online_edit_notification_emails:{pdu_online_edit_id}:{action}",
        description=f"Send PDU online edit notification for {pdu_online_edit_id}",
    )
    job.queue()
