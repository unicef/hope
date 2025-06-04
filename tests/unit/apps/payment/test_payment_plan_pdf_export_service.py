from typing import Any
from unittest.mock import MagicMock, patch

from django.test import TestCase

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import DataCollectingType
from hct_mis_api.apps.payment.fixtures import (
    ApprovalFactory,
    ApprovalProcessFactory,
    FinancialServiceProviderFactory,
    PaymentPlanFactory,
    generate_delivery_mechanisms,
)
from hct_mis_api.apps.payment.models import Approval, DeliveryMechanism
from hct_mis_api.apps.payment.pdf.payment_plan_export_pdf_service import (
    PaymentPlanPDFExportService,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory


class TestPaymentPlanPDFExportService(TestCase):
    def setUp(self) -> None:
        generate_delivery_mechanisms()
        create_afghanistan()
        self.dm_cash = DeliveryMechanism.objects.get(code="cash")
        financial_service_provider1 = FinancialServiceProviderFactory()
        financial_service_provider1.delivery_mechanisms.add(self.dm_cash)
        program = ProgramFactory(data_collecting_type__type=DataCollectingType.Type.STANDARD)
        self.payment_plan = PaymentPlanFactory(
            program_cycle=program.cycles.first(),
            delivery_mechanism=self.dm_cash,
            financial_service_provider=financial_service_provider1,
        )
        self.payment_plan.unicef_id = "PP-0060-24-00000007"
        self.payment_plan.save()
        self.pdf_export_service = PaymentPlanPDFExportService(self.payment_plan)
        approval_process = ApprovalProcessFactory(
            payment_plan=self.payment_plan,
        )
        ApprovalFactory(type=Approval.APPROVAL, approval_process=approval_process)

    @patch(
        "hct_mis_api.apps.payment.pdf.payment_plan_export_pdf_service.PaymentPlanPDFExportService.get_link",
        return_value="http://www_link/download-payment-plan-summary-pdf/111",
    )
    def test_generate_web_links(self, get_link_mock: Any) -> None:
        expected_download_link = "http://www_link/download-payment-plan-summary-pdf/111"
        self.pdf_export_service.generate_web_links()
        self.assertEqual(self.pdf_export_service.download_link, expected_download_link)
        self.assertEqual(self.pdf_export_service.payment_plan_link, expected_download_link)

    @patch(
        "hct_mis_api.apps.payment.pdf.payment_plan_export_pdf_service.PaymentPlanPDFExportService.get_link",
        return_value="http://www_link/download-payment-plan-summary-pdf/111",
    )
    def test_generate_pdf_summary(self, get_link_mock: Any) -> None:
        pdf1, filename1 = self.pdf_export_service.generate_pdf_summary()

        self.assertEqual(self.payment_plan.program.data_collecting_type.type, DataCollectingType.Type.STANDARD)

        self.assertTrue(isinstance(pdf1, bytes))
        self.assertEqual(filename1, "PaymentPlanSummary-PP-0060-24-00000007.pdf")

        self.payment_plan.program.data_collecting_type.type = DataCollectingType.Type.SOCIAL
        self.payment_plan.program.data_collecting_type.save()
        self.payment_plan.program.data_collecting_type.refresh_from_db(fields=["type"])

        self.assertEqual(self.payment_plan.program.data_collecting_type.type, DataCollectingType.Type.SOCIAL)
        pdf2, filename2 = self.pdf_export_service.generate_pdf_summary()
        self.assertTrue(isinstance(pdf2, bytes))
        self.assertEqual(filename2, "PaymentPlanSummary-PP-0060-24-00000007.pdf")

    def test_get_email_context(self) -> None:
        user_mock = MagicMock()
        user_mock.first_name = "First"
        user_mock.last_name = "Last"
        user_mock.email = "first.last@email_tivix.com"
        expected_context = {
            "first_name": "First",
            "last_name": "Last",
            "email": "first.last@email_tivix.com",
            "message": "Payment Plan Summary PDF file(s) have been generated, "
            "and below you will find the link to download the file(s).",
            "link": "",
            "title": "Payment Plan Payment List files generated",
        }

        context = self.pdf_export_service.get_email_context(user_mock)

        self.assertDictEqual(context, expected_context)
