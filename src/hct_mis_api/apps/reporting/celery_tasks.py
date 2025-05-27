import logging
from typing import Any
from uuid import UUID

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.utils.logs import log_start_and_end
from hct_mis_api.apps.utils.sentry import sentry_tags, set_sentry_business_area_tag

logger = logging.getLogger(__name__)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def report_export_task(self: Any, report_id: UUID) -> None:
    try:
        from hct_mis_api.apps.reporting.models import Report
        from hct_mis_api.apps.reporting.services.generate_report_service import (
            GenerateReportService,
        )

        report_obj = Report.objects.get(id=report_id)
        set_sentry_business_area_tag(report_obj.business_area.name)

        service = GenerateReportService(report=report_obj)
        service.generate_report()
    except Exception as e:
        logger.exception(e)
        raise self.retry(exc=e)
