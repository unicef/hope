from typing import Any

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.periodic_data_update.models import (
    PeriodicDataUpdateTemplate,
    PeriodicDataUpdateUpload,
)
from hct_mis_api.apps.periodic_data_update.service.periodic_data_update_export_template_service import (
    PeriodicDataUpdateExportTemplateService,
)
from hct_mis_api.apps.periodic_data_update.service.periodic_data_update_import_service import (
    PeriodicDataUpdateImportService,
)
from hct_mis_api.apps.utils.logs import log_start_and_end
from hct_mis_api.apps.utils.sentry import sentry_tags


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def import_periodic_data_update(self: Any, periodic_data_update_upload_id: str) -> bool:
    periodic_data_update_upload = PeriodicDataUpdateUpload.objects.get(id=periodic_data_update_upload_id)
    service = PeriodicDataUpdateImportService(periodic_data_update_upload)
    service.import_data()
    return True


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def export_periodic_data_update_export_template_service(self: Any, periodic_data_update_template_id: str) -> bool:
    periodic_data_update_template = PeriodicDataUpdateTemplate.objects.get(id=periodic_data_update_template_id)
    service = PeriodicDataUpdateExportTemplateService(periodic_data_update_template)
    service.generate_workbook()
    service.save_xlsx_file()
    return True
