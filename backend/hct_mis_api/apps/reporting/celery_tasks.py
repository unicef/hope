import logging

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.utils.logs import log_start_and_end

logger = logging.getLogger(__name__)


@log_start_and_end
@app.task
def report_export_task(report_id):
    try:
        from hct_mis_api.apps.reporting.services.generate_report_service import (
            GenerateReportService,
        )
        from hct_mis_api.apps.reporting.models import Report

        report_obj = Report.objects.get(id=report_id)
        service = GenerateReportService(report=report_obj)
        service.generate_report()
    except Exception as e:
        logger.exception(e)
        raise


@log_start_and_end
@app.task
def dashboard_report_export_task(dashboard_report_id):
    try:
        from hct_mis_api.apps.reporting.services.generate_dashboard_report_service import (
            GenerateDashboardReportService,
        )
        from hct_mis_api.apps.reporting.models import DashboardReport

        report_obj = DashboardReport.objects.get(id=dashboard_report_id)
        service = GenerateDashboardReportService(report=report_obj)
        service.generate_report()
    except Exception as e:
        logger.exception(e)
        raise
