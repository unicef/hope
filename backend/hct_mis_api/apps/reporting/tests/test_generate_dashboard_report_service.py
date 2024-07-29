import json
from typing import Any
from unittest.mock import patch

from django.conf import settings
from django.template.loader import render_to_string
from django.test import TestCase, override_settings

from constance.test import override_config
from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.reporting.fixtures import DashboardReportFactory
from hct_mis_api.apps.reporting.models import DashboardReport
from hct_mis_api.apps.reporting.services.generate_dashboard_report_service import (
    GenerateDashboardReportService,
)

class TestGenerateDashboardReportService(TestCase):
    @parameterized.expand(
        [
            DashboardReport.TOTAL_TRANSFERRED_BY_COUNTRY,
            DashboardReport.TOTAL_TRANSFERRED_BY_ADMIN_AREA,
            DashboardReport.BENEFICIARIES_REACHED,
            DashboardReport.INDIVIDUALS_REACHED,
            DashboardReport.VOLUME_BY_DELIVERY_MECHANISM,
            DashboardReport.GRIEVANCES_AND_FEEDBACK,
            DashboardReport.PROGRAMS,
            DashboardReport.PAYMENT_VERIFICATION,
        ]
    )
    @patch("hct_mis_api.apps.utils.mailjet.requests.post")
    @override_config(ENABLE_MAILJET=True)
    def test_generate_report_successfully(self, report_type: str, mocked_requests_post: Any) -> None:
        create_afghanistan()
        report = DashboardReportFactory(status=DashboardReport.IN_PROGRESS, report_type=[report_type])
        service = GenerateDashboardReportService(report=report)

        service.generate_report()

        self.assertEqual(report.status, DashboardReport.COMPLETED)

        mocked_requests_post.assert_called_once()

    @patch("hct_mis_api.apps.utils.mailjet.requests.post")
    @override_config(ENABLE_MAILJET=True)
    def test_generate_report_successfully_ba_notification_disabled(self, mocked_requests_post: Any) -> None:
        afg = create_afghanistan()
        afg.enable_email_notification = False
        afg.save()
        report = DashboardReportFactory(
            status=DashboardReport.IN_PROGRESS, report_type=[DashboardReport.TOTAL_TRANSFERRED_BY_COUNTRY]
        )
        service = GenerateDashboardReportService(report=report)

        service.generate_report()

        self.assertEqual(report.status, DashboardReport.COMPLETED)

        mocked_requests_post.assert_not_called()

    @patch("hct_mis_api.apps.utils.mailjet.requests.post")
    @override_settings(EMAIL_SUBJECT_PREFIX="test")
    @override_config(ENABLE_MAILJET=True)
    def test_email_body_for_generate_report(self, mocked_requests_post: Any) -> None:
        create_afghanistan()
        user = UserFactory(email="testemail@email.com")
        report_type = DashboardReport.TOTAL_TRANSFERRED_BY_COUNTRY
        report = DashboardReportFactory(status=DashboardReport.IN_PROGRESS, report_type=[report_type], created_by=user)
        service = GenerateDashboardReportService(report=report)

        service.generate_report()

        self.assertEqual(report.status, DashboardReport.COMPLETED)

        mocked_requests_post.assert_called_once()

        context = {
            "report_type": dict(DashboardReport.REPORT_TYPES)[report_type],
            "created_at": report.created_at.strftime("%Y-%m-%d"),
            "report_url": f"http://example.com/api/dashboard-report/{report.id}",
            "title": "Report",
        }
        text_body = render_to_string("dashboard_report.txt", context=context)
        html_body = render_to_string("dashboard_report.html", context=context)

        expected_data = json.dumps(
            {
                "Messages": [
                    {
                        "From": {"Email": settings.DEFAULT_EMAIL, "Name": settings.DEFAULT_EMAIL_DISPLAY},
                        "Subject": "[test] HOPE report generated",
                        "To": [
                            {
                                "Email": "testemail@email.com",
                            },
                        ],
                        "Cc": [],
                        "HTMLPart": html_body,
                        "TextPart": text_body,
                    }
                ]
            }
        )

        mocked_requests_post.assert_called_with(
            "https://api.mailjet.com/v3.1/send",
            auth=(settings.MAILJET_API_KEY, settings.MAILJET_SECRET_KEY),
            data=expected_data,
        )
