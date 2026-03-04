from decimal import Decimal
from typing import Any
from unittest.mock import MagicMock

import pytest

from extras.test_utils.factories.payment import (
    ApprovalFactory,
    ApprovalProcessFactory,
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    PaymentFactory,
    PaymentPlanFactory,
)
from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory
from hope.apps.payment.pdf.payment_plan_export_pdf_service import PaymentPlanPDFExportService
from hope.models import Approval, DataCollectingType, Payment, PaymentPlan

pytestmark = pytest.mark.django_db


@pytest.fixture
def delivery_mechanism_cash() -> Any:
    return DeliveryMechanismFactory(code="cash", name="Cash", payment_gateway_id="dm-cash")


@pytest.fixture
def financial_service_provider(delivery_mechanism_cash: Any) -> Any:
    financial_service_provider = FinancialServiceProviderFactory()
    financial_service_provider.delivery_mechanisms.add(delivery_mechanism_cash)
    return financial_service_provider


@pytest.fixture
def program_and_cycle() -> dict[str, Any]:
    program = ProgramFactory(data_collecting_type__type=DataCollectingType.Type.STANDARD)
    program_cycle = ProgramCycleFactory(program=program)
    return {"program": program, "program_cycle": program_cycle}


@pytest.fixture
def payment_plan(
    delivery_mechanism_cash: Any,
    financial_service_provider: Any,
    program_and_cycle: dict[str, Any],
) -> PaymentPlan:
    program = program_and_cycle["program"]
    program_cycle = program_and_cycle["program_cycle"]
    payment_plan = PaymentPlanFactory(
        program_cycle=program_cycle,
        business_area=program.business_area,
        delivery_mechanism=delivery_mechanism_cash,
        financial_service_provider=financial_service_provider,
    )
    PaymentFactory(
        parent=payment_plan,
        entitlement_quantity=Decimal("10.00"),
        delivered_quantity=Decimal("0.00"),
        entitlement_quantity_usd=Decimal("20.00"),
        delivered_quantity_usd=Decimal("0.00"),
        currency="PLN",
        status=Payment.STATUS_PENDING,
    )
    PaymentFactory(
        parent=payment_plan,
        entitlement_quantity=Decimal("10.00"),
        delivered_quantity=Decimal("10.00"),
        entitlement_quantity_usd=Decimal("20.00"),
        delivered_quantity_usd=Decimal("20.00"),
        currency="PLN",
        status=Payment.STATUS_DISTRIBUTION_SUCCESS,
    )
    PaymentFactory(
        parent=payment_plan,
        entitlement_quantity=Decimal("10.00"),
        delivered_quantity=Decimal("5.00"),
        entitlement_quantity_usd=Decimal("20.00"),
        delivered_quantity_usd=Decimal("10.00"),
        currency="PLN",
        status=Payment.STATUS_DISTRIBUTION_PARTIAL,
    )
    PaymentFactory(
        parent=payment_plan,
        entitlement_quantity=Decimal("100.00"),
        delivered_quantity=Decimal("0.00"),
        entitlement_quantity_usd=Decimal("200.00"),
        delivered_quantity_usd=Decimal("0.00"),
        currency="PLN",
        status=Payment.STATUS_NOT_DISTRIBUTED,
    )
    payment_plan.update_money_fields()
    payment_plan.unicef_id = "PP-0060-24-00000007"
    payment_plan.save()
    payment_plan.refresh_from_db()
    approval_process = ApprovalProcessFactory(payment_plan=payment_plan)
    ApprovalFactory(type=Approval.APPROVAL, approval_process=approval_process)
    return payment_plan


def test_generate_web_links(payment_plan: PaymentPlan, mocker: Any) -> None:
    expected_download_link = "http://www_link/download-payment-plan-summary-pdf/111"
    mocker.patch(
        "hope.apps.payment.pdf.payment_plan_export_pdf_service.get_link",
        return_value=expected_download_link,
    )
    pdf_export_service = PaymentPlanPDFExportService(payment_plan)

    pdf_export_service.generate_web_links()

    assert pdf_export_service.download_link == expected_download_link
    assert pdf_export_service.payment_plan_link == expected_download_link


def test_generate_pdf_summary(payment_plan: PaymentPlan, mocker: Any) -> None:
    mocker.patch(
        "hope.apps.payment.pdf.payment_plan_export_pdf_service.get_link",
        return_value="http://www_link/download-payment-plan-summary-pdf/111",
    )
    pdf_export_service = PaymentPlanPDFExportService(payment_plan)

    pdf1, filename1 = pdf_export_service.generate_pdf_summary()

    assert payment_plan.program.data_collecting_type.type == DataCollectingType.Type.STANDARD

    assert isinstance(pdf1, bytes)
    assert filename1 == "PaymentPlanSummary-PP-0060-24-00000007.pdf"

    payment_plan.program.data_collecting_type.type = DataCollectingType.Type.SOCIAL
    payment_plan.program.data_collecting_type.save()
    payment_plan.program.data_collecting_type.refresh_from_db(fields=["type"])

    assert payment_plan.program.data_collecting_type.type == DataCollectingType.Type.SOCIAL
    pdf2, filename2 = pdf_export_service.generate_pdf_summary()
    assert isinstance(pdf2, bytes)
    assert filename2 == "PaymentPlanSummary-PP-0060-24-00000007.pdf"


def test_generate_pdf_summary_reconciliation(
    payment_plan: PaymentPlan,
    mocker: Any,
) -> None:
    mocker.patch(
        "hope.apps.payment.pdf.payment_plan_export_pdf_service.get_link",
        return_value="http://www_link/download-payment-plan-summary-pdf/111",
    )
    generate_pdf_from_html_mock = mocker.patch(
        "hope.apps.payment.pdf.payment_plan_export_pdf_service.generate_pdf_from_html",
        return_value="http://www_link/download-payment-plan-summary-pdf/111",
    )
    pdf_export_service = PaymentPlanPDFExportService(payment_plan)

    pdf_export_service.generate_pdf_summary()

    generate_pdf_from_html_mock.assert_called_once()
    _args, kwargs = generate_pdf_from_html_mock.call_args
    pdf_context_data = kwargs["data"]
    pdf_reconciliation_qs = pdf_context_data["reconciliation"]

    assert pdf_reconciliation_qs["pending"] == 1
    assert pdf_reconciliation_qs["reconciled"] == 2
    assert pdf_reconciliation_qs["reconciled_usd"] == 30.0
    assert pdf_reconciliation_qs["reconciled_local"] == 15.0
    assert pdf_reconciliation_qs["failed_usd"] == 210.0
    assert pdf_reconciliation_qs["failed_local"] == 105.0
    assert payment_plan.total_entitled_quantity == (
        pdf_reconciliation_qs["failed_local"] + pdf_reconciliation_qs["reconciled_local"] + 10
    )
    assert payment_plan.total_entitled_quantity_usd == (
        pdf_reconciliation_qs["failed_usd"] + pdf_reconciliation_qs["reconciled_usd"] + 20
    )


def test_get_email_context(
    payment_plan: PaymentPlan,
) -> None:
    pdf_export_service = PaymentPlanPDFExportService(payment_plan)
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

    context = pdf_export_service.get_email_context(user_mock)

    assert context == expected_context
