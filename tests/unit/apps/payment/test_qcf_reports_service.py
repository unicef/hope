import io
import os
from datetime import datetime
from unittest import mock

from django.test import TestCase
from django.urls import reverse

import openpyxl
from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory
from extras.test_utils.factories.program import ProgramFactory

from hct_mis_api.apps.account.models import Role, User, UserRole
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.payment.models import (
    PaymentPlan,
    WesternUnionInvoice,
    WesternUnionInvoicePayment,
    WesternUnionPaymentPlanReport,
)
from hct_mis_api.apps.payment.services.qcf_reports_service import QCFReportsService
from hct_mis_api.apps.payment.services.western_union_ftp import WesternUnionFTPClient
from hct_mis_api.apps.program.models import Program


class WUClientMock(WesternUnionFTPClient):
    HOST = "fakehost"
    PORT = 2222
    USERNAME = "user"
    PASSWORD = "pass"

    def __init__(self) -> None:
        # Skip paramiko connection
        self.client = mock.MagicMock()  # type: ignore


class TestQCFReportsService(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        partner_unicef = PartnerFactory(name="UNICEF")
        cls.user = UserFactory.create(partner=partner_unicef)
        role, created = Role.objects.update_or_create(
            name="RECEIVE_PARSED_WU_QCF", defaults={"permissions": [Permissions.RECEIVE_PARSED_WU_QCF.value]}
        )
        cls.user_role, _ = UserRole.objects.get_or_create(user=cls.user, role=role, business_area=cls.business_area)
        cls.program = ProgramFactory(status=Program.ACTIVE)
        cls.cycle = cls.program.cycles.first()
        cls.payment_plan = PaymentPlanFactory(
            program_cycle=cls.cycle,
            created_by=cls.user,
            status=PaymentPlan.Status.ACCEPTED,
            business_area=cls.business_area,
        )
        cls.payment_plan.refresh_from_db()

        # TODO add 2 FCs

        cls.p1 = PaymentFactory(parent=cls.payment_plan, fsp_auth_code="0486455966")
        cls.p2 = PaymentFactory(parent=cls.payment_plan, fsp_auth_code="669")
        cls.p3 = PaymentFactory(parent=cls.payment_plan, fsp_auth_code=None)

        cls.p1.unicef_id = "RCPT-0520-25-0.000.145"
        cls.p1.save()
        cls.p2.unicef_id = "RCPT-0520-25-0.000.144"
        cls.p2.save()
        cls.p3.unicef_id = "RCPT-0520-25-0.000.135"
        cls.p3.save()

    @mock.patch(
        "hct_mis_api.apps.payment.services.qcf_reports_service.WesternUnionFTPClient",
        WUClientMock,
    )
    def test_process_files_since_with_real_zip(self) -> None:
        filename = "QCF-123-XYZ-20250101.zip"
        test_file_path = os.path.join(
            os.path.dirname(__file__),
            "test_file",
            filename,
        )

        with open(test_file_path, "rb") as f:
            file_bytes = f.read()
        fake_file_like = io.BytesIO(file_bytes)

        with mock.patch.object(
            WesternUnionFTPClient,
            "get_files_since",
            return_value=[(filename, fake_file_like)],
        ):
            service = QCFReportsService()
            service.process_files_since(datetime(2025, 1, 1))

            self.assertEqual(WesternUnionInvoice.objects.count(), 1)
            qcf_file = WesternUnionInvoice.objects.first()
            self.assertEqual(qcf_file.name, filename)
            self.assertEqual(WesternUnionInvoice.objects.count(), 1)
            self.assertEqual(str(qcf_file), qcf_file.name)

            self.assertEqual(WesternUnionInvoicePayment.objects.filter(transaction_status="2").count(), 3)

            self.assertEqual(WesternUnionPaymentPlanReport.objects.count(), 1)
            report = WesternUnionPaymentPlanReport.objects.first()
            self.assertEqual(report.qcf_file, qcf_file)
            self.assertEqual(report.payment_plan, self.payment_plan)
            self.assertEqual(str(report), f"{report.payment_plan.name} - sent: {report.sent}")

            report_file = report.report_file
            self.assertIsNotNone(report_file)

            # Read the XLSX file from the FileField
            file_field = report_file.file
            file_field.open("rb")
            wb = openpyxl.load_workbook(file_field)
            ws = wb.active

            # Check sheet title
            self.assertEqual(ws.title, f"QCF Report - {report.payment_plan.unicef_id}")

            # Check headers
            expected_headers = [
                "Payment ID",
                "MTCN",
                "MTCNs match",
                "HOPE MTCN",
                "Payment Plan ID",
                "Programme",
                "FC",
                "Principal Amount",
                "Charges Amount",
                "Fee Amount",
            ]
            actual_headers = [cell.value for cell in ws[1]]
            self.assertEqual(actual_headers, expected_headers)

            # Check 1st payment row
            row_values = [cell.value for cell in ws[2]]
            self.assertEqual(
                row_values,
                [
                    self.p1.unicef_id,
                    "0486455966",
                    True,
                    "0486455966",
                    self.p1.parent.unicef_id,
                    self.program.name,
                    None,
                    262.55,
                    7.88,
                    0,
                ],
            )

            # Check 2nd payment row
            row_values = [cell.value for cell in ws[3]]
            self.assertEqual(
                row_values,
                [
                    self.p2.unicef_id,
                    "1131933875",
                    False,
                    "669",
                    self.p2.parent.unicef_id,
                    self.program.name,
                    None,
                    262.55,
                    7.88,
                    0,
                ],
            )

            # Check 3rd payment row
            row_values = [cell.value for cell in ws[4]]
            self.assertEqual(
                row_values,
                [
                    self.p3.unicef_id,
                    "1389434830",
                    False,
                    None,
                    self.p3.parent.unicef_id,
                    self.program.name,
                    None,
                    665.22,
                    19.96,
                    0,
                ],
            )

            # Optionally, check totals
            last_row = ws.max_row
            principal_total = ws[f"E{last_row - 2}"].value
            charges_total = ws[f"E{last_row - 1}"].value
            refunds_total = ws[f"E{last_row}"].value

            self.assertEqual(principal_total, 1190.32)
            self.assertEqual(charges_total, 35.72)
            self.assertEqual(refunds_total, 0)

            with mock.patch.object(User, "email_user") as mock_email_user:
                with mock.patch(
                    "hct_mis_api.apps.payment.services.qcf_reports_service.render_to_string"
                ) as mock_render_to_string:
                    service.send_notification_emails(report)  # type: ignore
                    mock_email_user.assert_called_once()
                    assert mock_render_to_string.call_count == 2
                    args, kwargs = mock_render_to_string.call_args
                    context = kwargs["context"]
                    program_id = encode_id_base64(report.payment_plan.program.id, "Program")
                    payment_plan_id = encode_id_base64(report.payment_plan.id, "PaymentPlan")
                    plan_path = f"/{report.payment_plan.business_area.slug}/programs/{program_id}/payment-module/payment-plans/{payment_plan_id}"
                    plan_link = QCFReportsService.get_link(plan_path)
                    report_link = QCFReportsService.get_link(
                        reverse(
                            "download-payment-plan-invoice-report-pdf",
                            args=[encode_id_base64(report.id, "WesternUnionPaymentPlanReport")],
                        )
                    )

                    assert context == {
                        "first_name": getattr(self.user, "first_name", ""),
                        "last_name": getattr(self.user, "last_name", ""),
                        "email": getattr(self.user, "email", ""),
                        "message": f"Payment Plan: {plan_link}",
                        "title": f"Payment Plan {report.report_file.file.name} Western Union QCF Report",
                        "link": f"Western Union QCF Report file: {report_link}",
                    }

            download_link = reverse(
                "download-payment-plan-invoice-report-pdf",
                args=[encode_id_base64(report.id, "WesternUnionPaymentPlanReport")],
            )

            # test download with perm
            self.client.force_login(self.user)
            response = self.client.get(download_link)
            self.assertEqual(response.status_code, 302)
            self.assertIn(report.report_file.file.url, response.url)

            # test download wo perm
            self.user_role.delete()
            self.client.force_login(self.user)
            response = self.client.get(download_link)
            self.assertEqual(response.status_code, 403)
