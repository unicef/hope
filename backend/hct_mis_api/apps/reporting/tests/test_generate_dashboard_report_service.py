from django.test import TestCase

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.reporting.fixtures import DashboardReportFactory
from hct_mis_api.apps.reporting.models import DashboardReport
from hct_mis_api.apps.reporting.services.generate_dashboard_report_service import (
    GenerateDashboardReportService,
)


class TestGenerateDashboardReportService(TestCase):
    def test_generate_report_successfully(self) -> None:
        create_afghanistan()
        report = DashboardReportFactory(status=DashboardReport.IN_PROGRESS)
        service = GenerateDashboardReportService(report=report)

        service.generate_report()

        self.assertEqual(report.status, DashboardReport.COMPLETED)
