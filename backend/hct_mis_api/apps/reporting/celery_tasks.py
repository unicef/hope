import logging
from typing import Any
from uuid import UUID

from sentry_sdk import configure_scope

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.utils.logs import log_start_and_end
from hct_mis_api.apps.utils.sentry import sentry_tags

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
        with configure_scope() as scope:
            scope.set_tag("business_area", report_obj.business_area)

            service = GenerateReportService(report=report_obj)
            service.generate_report()
    except Exception as e:
        logger.exception(e)
        raise self.retry(exc=e)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def dashboard_report_export_task(self: Any, dashboard_report_id: UUID) -> None:
    try:
        from hct_mis_api.apps.reporting.models import DashboardReport
        from hct_mis_api.apps.reporting.services.generate_dashboard_report_service import (
            GenerateDashboardReportService,
        )

        report_obj = DashboardReport.objects.get(id=dashboard_report_id)
        with configure_scope() as scope:
            scope.set_tag("business_area", report_obj.business_area)
            service = GenerateDashboardReportService(report=report_obj)
            service.generate_report()
    except Exception as e:
        logger.exception(e)
        raise self.retry(exc=e)
