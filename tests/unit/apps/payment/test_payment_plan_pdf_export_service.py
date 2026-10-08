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
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.payment.pdf.payment_plan_export_pdf_service import PaymentPlanGroupPDFExportService
from hope.models import Approval, DataCollectingType, Payment, PaymentPlan, PaymentPlanGroup

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
    program_cycle = program.cycles.first()
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
        status=Payment.STATUS_PENDING,
    )
    PaymentFactory(
        parent=payment_plan,
        entitlement_quantity=Decimal("10.00"),
        delivered_quantity=Decimal("10.00"),
        entitlement_quantity_usd=Decimal("20.00"),
        delivered_quantity_usd=Decimal("20.00"),
        status=Payment.STATUS_DISTRIBUTION_SUCCESS,
    )
    PaymentFactory(
        parent=payment_plan,
        entitlement_quantity=Decimal("10.00"),
        delivered_quantity=Decimal("5.00"),
        entitlement_quantity_usd=Decimal("20.00"),
        delivered_quantity_usd=Decimal("10.00"),
        status=Payment.STATUS_DISTRIBUTION_PARTIAL,
    )
    PaymentFactory(
        parent=payment_plan,
        entitlement_quantity=Decimal("100.00"),
        delivered_quantity=Decimal("0.00"),
        entitlement_quantity_usd=Decimal("200.00"),
        delivered_quantity_usd=Decimal("0.00"),
        status=Payment.STATUS_NOT_DISTRIBUTED,
    )
    payment_plan.update_money_fields()
    payment_plan.unicef_id = "PP-0060-24-00000007"
    payment_plan.save()
    payment_plan.refresh_from_db()
    approval_process = ApprovalProcessFactory(payment_plan_group=payment_plan.payment_plan_group)
    ApprovalFactory(type=Approval.APPROVAL, approval_process=approval_process)
    return payment_plan


@pytest.fixture
def payment_plan_group(payment_plan: PaymentPlan) -> PaymentPlanGroup:
    group = payment_plan.payment_plan_group
    group.status = PaymentPlanGroup.Status.ACCEPTED
    group.save(update_fields=["status"])
    return group


@pytest.fixture
def second_payment_plan_in_group(
    payment_plan_group: PaymentPlanGroup, delivery_mechanism_cash: Any, program_and_cycle: dict[str, Any]
) -> PaymentPlan:
    second_plan = PaymentPlanFactory(
        program_cycle=program_and_cycle["program_cycle"],
        business_area=program_and_cycle["program"].business_area,
        payment_plan_group=payment_plan_group,
        delivery_mechanism=delivery_mechanism_cash,
    )
    PaymentFactory(
        parent=second_plan,
        entitlement_quantity=Decimal("10.00"),
        delivered_quantity=Decimal("10.00"),
        entitlement_quantity_usd=Decimal("20.00"),
        delivered_quantity_usd=Decimal("20.00"),
        status=Payment.STATUS_DISTRIBUTION_SUCCESS,
    )
    return second_plan


@pytest.fixture
def group_approval_process(payment_plan_group: PaymentPlanGroup) -> Any:
    approval_process = ApprovalProcessFactory(payment_plan_group=payment_plan_group)
    ApprovalFactory(approval_process=approval_process, type=Approval.APPROVAL, comment="group approved")
    return approval_process


def test_group_generate_web_links(payment_plan_group: PaymentPlanGroup, mocker: Any) -> None:
    mocker.patch(
        "hope.apps.payment.pdf.payment_plan_export_pdf_service.get_link",
        side_effect=lambda path: f"http://www_link{path}",
    )
    pdf_export_service = PaymentPlanGroupPDFExportService(payment_plan_group)

    pdf_export_service.generate_web_links()

    assert pdf_export_service.download_link == (
        f"http://www_link/api/download-payment-plan-group-summary-pdf/{payment_plan_group.id}"
    )
    assert pdf_export_service.payment_plan_group_link.endswith(f"/payment-module/groups/{payment_plan_group.id}")


def test_group_generate_pdf_summary_returns_pdf_named_after_the_group(
    payment_plan_group: PaymentPlanGroup, group_approval_process: Any, mocker: Any
) -> None:
    mocker.patch("hope.apps.payment.pdf.payment_plan_export_pdf_service.get_link", return_value="http://www_link")

    pdf, filename = PaymentPlanGroupPDFExportService(payment_plan_group).generate_pdf_summary()

    assert isinstance(pdf, bytes)
    assert filename == f"PaymentPlanGroupSummary-{payment_plan_group.unicef_id}.pdf"


def test_group_generate_pdf_summary_aggregates_every_plan_in_the_group(
    payment_plan_group: PaymentPlanGroup,
    payment_plan: PaymentPlan,
    second_payment_plan_in_group: PaymentPlan,
    group_approval_process: Any,
    mocker: Any,
) -> None:
    mocker.patch("hope.apps.payment.pdf.payment_plan_export_pdf_service.get_link", return_value="http://www_link")
    generate_pdf_from_html_mock = mocker.patch(
        "hope.apps.payment.pdf.payment_plan_export_pdf_service.generate_pdf_from_html", return_value=b"pdf"
    )

    PaymentPlanGroupPDFExportService(payment_plan_group).generate_pdf_summary()

    pdf_context_data = generate_pdf_from_html_mock.call_args.kwargs["data"]
    assert pdf_context_data["payment_plans"] == sorted(
        [payment_plan, second_payment_plan_in_group], key=lambda p: p.unicef_id
    )
    assert pdf_context_data["approval_process"] == group_approval_process
    assert pdf_context_data["approval"].comment == "group approved"
    assert pdf_context_data["authorization"] is None
    assert pdf_context_data["reconciliation"]["reconciled"] == 3
    assert pdf_context_data["reconciliation"]["pending"] == 1
    assert pdf_context_data["reconciliation"]["reconciled_usd"] == Decimal("50.00")


def test_group_get_email_context(payment_plan_group: PaymentPlanGroup) -> None:
    user_mock = MagicMock()
    user_mock.first_name = "First"
    user_mock.last_name = "Last"
    user_mock.email = "first.last@email.com"

    context = PaymentPlanGroupPDFExportService(payment_plan_group).get_email_context(user_mock)

    assert context == {
        "first_name": "First",
        "last_name": "Last",
        "email": "first.last@email.com",
        "message": "Payment Plan Group Summary PDF file has been generated, "
        "and below you will find the link to download the file.",
        "link": "",
        "title": "Payment Plan Group Summary file generated",
    }
