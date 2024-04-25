from unittest.mock import MagicMock

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
