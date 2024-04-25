from typing import Any
from unittest.mock import MagicMock, patch

from django.test import TestCase

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.payment.fixtures import (
    ApprovalFactory,
    ApprovalProcessFactory,
    DeliveryMechanismPerPaymentPlanFactory,
    FinancialServiceProviderFactory,
    PaymentPlanFactory,
)
from hct_mis_api.apps.payment.models import Approval, GenericPayment
from hct_mis_api.apps.payment.pdf.payment_plan_export_pdf_service import (
    PaymentPlanPDFExportService,
)


class TestPaymentPlanPDFExportService(TestCase):
    def setUp(self) -> None:
        create_afghanistan()
        self.payment_plan = PaymentPlanFactory()
        self.payment_plan.unicef_id = "PP-0060-24-00000007"
        self.payment_plan.save()
        self.pdf_export_service = PaymentPlanPDFExportService(self.payment_plan)

        financial_service_provider1 = FinancialServiceProviderFactory(
            delivery_mechanisms=[GenericPayment.DELIVERY_TYPE_CASH]
        )

        DeliveryMechanismPerPaymentPlanFactory(
            payment_plan=self.payment_plan,
            delivery_mechanism=GenericPayment.DELIVERY_TYPE_CASH,
            financial_service_provider=financial_service_provider1,
            delivery_mechanism_order=1,
        )
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
        pdf, filename = self.pdf_export_service.generate_pdf_summary()

        self.assertTrue(isinstance(pdf, bytes))
        self.assertEqual(filename, "PaymentPlanSummary-PP-0060-24-00000007.pdf")

    def test_get_email_context(self) -> None:
        user_mock = MagicMock()
        user_mock.first_name = "First"
        user_mock.last_name = "Last"
        user_mock.email = "first.last@email_tivix.com"
        expected_context = {
            "first_name": "First",
            "last_name": "Last",
            "email": "first.last@email_tivix.com",
            "message": "Payment Plan Summary PDF file(s) have been generated, and below you will find the link to download the file(s).",
            "link": "",
            "title": "Payment Plan Payment List files generated",
        }

        context = self.pdf_export_service.get_email_context(user_mock)

        self.assertDictEqual(context, expected_context)
