from hct_mis_api.apps.core.celery import app


@app.task
def report_export_task(report_id):
    from hct_mis_api.apps.reporting.generate_report_service import (
        GenerateReportService,
    )
    from hct_mis_api.apps.reporting.models import Report

    report_obj = Report.objects.get(id=report_id)
    service = GenerateReportService(report=report_obj)
    service.generate_report()


@app.task
def dashboard_report_export_task(dashboard_report_id):
    from hct_mis_api.apps.reporting.generate_dashboard_report_service import (
        GenerateDashboardReportService,
    )
    from hct_mis_api.apps.reporting.models import DashboardReport

    report_obj = DashboardReport.objects.get(id=dashboard_report_id)
    service = GenerateDashboardReportService(report=report_obj)
    service.generate_report()
