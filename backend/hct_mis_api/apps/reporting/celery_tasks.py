import logging

from hct_mis_api.apps.core.celery import app

logger = logging.getLogger(__name__)


@app.task
def report_export_task(report_id):
    logger.info("report_export_task start")

    try:
        from hct_mis_api.apps.reporting.generate_report_service import (
            GenerateReportService,
        )
        from hct_mis_api.apps.reporting.models import Report

        report_obj = Report.objects.get(id=report_id)
        service = GenerateReportService(report=report_obj)
        service.generate_report()
    except Exception as e:
        logger.exception(e)
        raise

    logger.info("report_export_task end")


@app.task
def dashboard_report_export_task(dashboard_report_id):
    logger.info("dashboard_report_export_task start")

    try:
        from hct_mis_api.apps.reporting.generate_dashboard_report_service import (
            GenerateDashboardReportService,
        )
        from hct_mis_api.apps.reporting.models import DashboardReport

        report_obj = DashboardReport.objects.get(id=dashboard_report_id)
        service = GenerateDashboardReportService(report=report_obj)
        service.generate_report()
    except Exception as e:
        logger.exception(e)
        raise

    logger.info("dashboard_report_export_task end")
