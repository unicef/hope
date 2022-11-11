import logging

from sentry_sdk import configure_scope

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.utils.logs import log_start_and_end
from hct_mis_api.apps.utils.sentry import sentry_tags

logger = logging.getLogger(__name__)


@app.task
@log_start_and_end
@sentry_tags
def report_export_task(report_id):
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
        raise


@app.task
@log_start_and_end
@sentry_tags
def dashboard_report_export_task(dashboard_report_id) -> None:
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
        raise
