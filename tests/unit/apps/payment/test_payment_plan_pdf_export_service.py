from decimal import Decimal
from typing import Any
from unittest.mock import MagicMock, patch

from django.test import TestCase

from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.payment import (
    ApprovalFactory,
    ApprovalProcessFactory,
    FinancialServiceProviderFactory,
    Payment,
    PaymentFactory,
    PaymentPlanFactory,
    generate_delivery_mechanisms,
)
from extras.test_utils.factories.program import ProgramFactory

from hct_mis_api.apps.core.models import DataCollectingType
from hct_mis_api.apps.payment.models import Approval, DeliveryMechanism
from hct_mis_api.apps.payment.pdf.payment_plan_export_pdf_service import (
    PaymentPlanPDFExportService,
)


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
        PaymentFactory(
            parent=self.payment_plan,
            entitlement_quantity=Decimal(10.00),
            delivered_quantity=Decimal(0.0),
            entitlement_quantity_usd=Decimal(20.00),
            delivered_quantity_usd=Decimal(0.0),
            currency="PLN",
            status=Payment.STATUS_PENDING,
        )
        PaymentFactory(
            parent=self.payment_plan,
            entitlement_quantity=Decimal(10.00),
            delivered_quantity=Decimal(10.00),
            entitlement_quantity_usd=Decimal(20.00),
            delivered_quantity_usd=Decimal(20.00),
            currency="PLN",
            status=Payment.STATUS_DISTRIBUTION_SUCCESS,
        )
        PaymentFactory(
            parent=self.payment_plan,
            entitlement_quantity=Decimal(10.00),
            delivered_quantity=Decimal(5.00),
            entitlement_quantity_usd=Decimal(20.00),
            delivered_quantity_usd=Decimal(10.00),
            currency="PLN",
            status=Payment.STATUS_DISTRIBUTION_PARTIAL,
        )
        PaymentFactory(
            parent=self.payment_plan,
            entitlement_quantity=Decimal(100.00),
            delivered_quantity=Decimal(0.00),
            entitlement_quantity_usd=Decimal(200.00),
            delivered_quantity_usd=Decimal(0.00),
            currency="PLN",
            status=Payment.STATUS_NOT_DISTRIBUTED,
        )
        self.payment_plan.update_money_fields()
        self.payment_plan.unicef_id = "PP-0060-24-00000007"
        self.payment_plan.save()
        self.payment_plan.refresh_from_db()
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

    @patch(
        "hct_mis_api.apps.payment.pdf.payment_plan_export_pdf_service.PaymentPlanPDFExportService.get_link",
        return_value="http://www_link/download-payment-plan-summary-pdf/111",
    )
    @patch(
        "hct_mis_api.apps.payment.pdf.payment_plan_export_pdf_service.generate_pdf_from_html",
        return_value="http://www_link/download-payment-plan-summary-pdf/111",
    )
    def test_generate_pdf_summary_reconciliation(self, generate_pdf_from_html_mock: Any, get_link_mock: Any) -> None:
        self.pdf_export_service.generate_pdf_summary()

        generate_pdf_from_html_mock.assert_called_once()
        args, kwargs = generate_pdf_from_html_mock.call_args
        pdf_context_data = kwargs["data"]
        pdf_reconciliation_qs = pdf_context_data["reconciliation"]

        self.assertEqual(pdf_reconciliation_qs["pending_usd"], 20.0)
        self.assertEqual(pdf_reconciliation_qs["pending_local"], 10.0)
        self.assertEqual(pdf_reconciliation_qs["reconciled_usd"], 30.0)
        self.assertEqual(pdf_reconciliation_qs["reconciled_local"], 15.0)
        self.assertEqual(pdf_reconciliation_qs["failed_usd"], 210.0)
        self.assertEqual(pdf_reconciliation_qs["failed_local"], 105.0)
        self.assertEqual(
            pdf_reconciliation_qs["failed_local"]
            + pdf_reconciliation_qs["reconciled_local"]
            + pdf_reconciliation_qs["pending_local"],
            self.payment_plan.total_entitled_quantity,
        )
        self.assertEqual(
            pdf_reconciliation_qs["failed_usd"]
            + pdf_reconciliation_qs["reconciled_usd"]
            + pdf_reconciliation_qs["pending_usd"],
            self.payment_plan.total_entitled_quantity_usd,
        )

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
