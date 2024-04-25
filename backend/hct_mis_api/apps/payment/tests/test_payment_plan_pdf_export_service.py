from unittest.mock import MagicMock, patch

from django.test import TestCase

from hct_mis_api.apps.payment.pdf.payment_plan_export_pdf_service import (
    PaymentPlanPDFExportService,
)


class TestPaymentPlanPDFExportService(TestCase):
    def setUp(self) -> None:
        self.payment_plan_mock = MagicMock()
        self.payment_plan_mock.id = 111
        self.payment_plan_mock.program.id = 333
        self.payment_plan_mock.business_area.slug = "afghanistan"
        self.payment_plan_mock.unicef_id = "PP-0060-24-00000007"
        self.payment_plan_mock.program.is_social_worker_program = False
        self.pdf_export_service = PaymentPlanPDFExportService(self.payment_plan_mock)

    @patch("django.conf.settings")
    @patch("hct_mis_api.apps.core.utils.encode_id_base64")
    def test_generate_web_links(self, mock_encode_id_base64, mock_settings):
        mock_encode_id_base64.side_effect = lambda x, y: f"{x}_{y}"
        mock_settings.SOCIAL_AUTH_REDIRECT_IS_HTTPS = False
        expected_download_link = "http://www_link/download-payment-plan-summary-pdf/111"
        expected_payment_plan_link = "http://test_frontend_host/afghanistan/programs/333/payment-module/payment-plans/111"

        with patch.object(self.pdf_export_service, 'get_link') as mock_get_link:
            mock_get_link.return_value = "http://www_link/download-payment-plan-summary-pdf/111"

            self.pdf_export_service.generate_web_links()
            self.assertEqual(self.pdf_export_service.download_link, expected_download_link)
            self.assertEqual(self.pdf_export_service.payment_plan_link, expected_payment_plan_link)

    @patch("django.conf.settings")
    @patch("hct_mis_api.apps.utils.pdf_generator.generate_pdf_from_html")
    def test_generate_pdf_summary(self, mock_generate_pdf_from_html, mock_settings):
        mock_settings.SOCIAL_AUTH_REDIRECT_IS_HTTPS = False
        mock_generate_pdf_from_html.return_value = "pp_summary_pdf"
        reconciliation_qs_mock = MagicMock()
        reconciliation_qs_mock.aggregate.return_value = {
            "pending": 11,
            "pending_usd": 11,
            "pending_local": 5,
            "reconciled": 8,
            "reconciled_usd": 8,
            "reconciled_local": 4
        }
        self.pdf_export_service.payment_plan.eligible_payments.aggregate.return_value = reconciliation_qs_mock

        pdf, filename = self.pdf_export_service.generate_pdf_summary()
        mock_generate_pdf_from_html.assert_called_once()

        self.assertEqual(pdf, "pp_summary_pdf")
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
