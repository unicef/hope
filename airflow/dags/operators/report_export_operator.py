from .base import DjangoOperator


class ReportExportOperator(DjangoOperator):
    def execute(self, context, **kwargs):
        from hct_mis_api.apps.reporting.generate_report_service import (
            GenerateReportService,
        )
        from hct_mis_api.apps.reporting.models import Report

        dag_run = context["dag_run"]
        config_vars = dag_run.conf

        report_id = config_vars.get("report_id")
        report_obj = Report.objects.get(id=report_id)
        service = GenerateReportService(report=report_obj)
        service.generate_report()
