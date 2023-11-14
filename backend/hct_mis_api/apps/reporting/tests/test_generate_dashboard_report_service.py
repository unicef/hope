from parameterized import parameterized

from hct_mis_api.apps.core.base_test_case import DefaultTestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.reporting.fixtures import DashboardReportFactory
from hct_mis_api.apps.reporting.models import DashboardReport
from hct_mis_api.apps.reporting.services.generate_dashboard_report_service import (
    GenerateDashboardReportService,
)


class TestGenerateDashboardReportService(DefaultTestCase):
    @parameterized.expand(
        [
            (DashboardReport.TOTAL_TRANSFERRED_BY_COUNTRY,),
            (DashboardReport.TOTAL_TRANSFERRED_BY_ADMIN_AREA,),
            (DashboardReport.BENEFICIARIES_REACHED,),
            (DashboardReport.INDIVIDUALS_REACHED,),
            (DashboardReport.VOLUME_BY_DELIVERY_MECHANISM,),
            (DashboardReport.GRIEVANCES_AND_FEEDBACK,),
            (DashboardReport.PROGRAMS,),
            (DashboardReport.PAYMENT_VERIFICATION,),
        ]
    )
    def test_generate_report_successfully(self, report_type: str) -> None:
        create_afghanistan()
        report = DashboardReportFactory(status=DashboardReport.IN_PROGRESS, report_type=[report_type])
        service = GenerateDashboardReportService(report=report)
        service.generate_report()

        self.assertEqual(report.status, DashboardReport.COMPLETED)
