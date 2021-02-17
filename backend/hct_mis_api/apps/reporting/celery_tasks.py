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
