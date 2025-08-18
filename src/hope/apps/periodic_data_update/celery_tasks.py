import datetime
import logging
from typing import Any

from django.contrib.admin.options import get_content_type_for_model
from django.db import transaction

from hope.apps.core.celery import app
from hope.apps.core.models import FileTemp
from hope.apps.periodic_data_update.models import (
    PDUXlsxTemplate,
    PDUXlsxUpload,
)
from hope.apps.periodic_data_update.service.periodic_data_update_export_template_service import (
    PDUXlsxExportTemplateService,
)
from hope.apps.periodic_data_update.service.periodic_data_update_import_service import (
    PDUXlsxImportService,
)
from hope.apps.periodic_data_update.signals import (
    increment_periodic_data_update_template_version_cache_function,
)
from hope.apps.utils.logs import log_start_and_end
from hope.apps.utils.sentry import sentry_tags

logger = logging.getLogger(__name__)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def import_periodic_data_update(self: Any, periodic_data_update_upload_id: str) -> bool:
    periodic_data_update_upload = PDUXlsxUpload.objects.get(id=periodic_data_update_upload_id)
    service = PDUXlsxImportService(periodic_data_update_upload)
    service.import_data()
    return True


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def export_periodic_data_update_export_template_service(self: Any, periodic_data_update_template_id: str) -> bool:
    periodic_data_update_template = PDUXlsxTemplate.objects.get(id=periodic_data_update_template_id)
    service = PDUXlsxExportTemplateService(periodic_data_update_template)
    service.generate_workbook()
    service.save_xlsx_file()
    return True


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def remove_old_pdu_template_files_task(self: Any, expiration_days: int = 30) -> None:
    """Remove old Periodic Data Update Template XLSX files."""
    try:
        with transaction.atomic():
            days = datetime.datetime.now() - datetime.timedelta(days=expiration_days)
            file_qs = FileTemp.objects.filter(
                content_type=get_content_type_for_model(PDUXlsxTemplate), created__lt=days
            )
            if file_qs:
                # update status
                templates_qs = PDUXlsxTemplate.objects.filter(file__in=file_qs).all()
                templates_qs.update(status=PDUXlsxTemplate.Status.TO_EXPORT)
                templates_qs.update(celery_tasks_results_ids={})
                # increase cache version, as it is a bulk action
                for business_area_slug, program_id in templates_qs.values_list("business_area__slug", "program_id"):
                    increment_periodic_data_update_template_version_cache_function(business_area_slug, program_id)

                for xlsx_obj in file_qs:
                    xlsx_obj.file.delete(save=False)
                    xlsx_obj.delete()

                logger.info(f"Removed old PDU FileTemp: {file_qs.count()}")

    except Exception as e:  # pragma: no cover
        logger.exception("Remove old PDU files Error")  # pragma: no cover
        raise self.retry(exc=e)  # pragma: no cover
