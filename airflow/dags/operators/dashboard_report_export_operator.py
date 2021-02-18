from .base import DjangoOperator


class DashboardReportExportOperator(DjangoOperator):
    def try_execute(self, context, **kwargs):
        from hct_mis_api.apps.reporting.generate_dashboard_report_service import (
            GenerateDashboardReportService,
        )
        from hct_mis_api.apps.reporting.models import DashboardReport

        dag_run = context["dag_run"]
        config_vars = dag_run.conf

        report_id = config_vars.get("dashboard_report_id")
        report_obj = DashboardReport.objects.get(id=report_id)
        service = GenerateDashboardReportService(report=report_obj)
        service.generate_report()
