from decimal import Decimal
from typing import Any
from unittest.mock import MagicMock

import pytest

from extras.test_utils.factories.payment import (
    ApprovalFactory,
    ApprovalProcessFactory,
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    FollowUpInstructionFactory,
    PaymentFactory,
    PaymentListFactory,
)
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.payment.pdf.payment_plan_export_pdf_service import (
    FollowUpInstructionPDFExportService,
    PaymentPlanPDFExportService,
)
from hope.models import Approval, DataCollectingType, FollowUpInstruction, Payment, PaymentList, PaymentPlan

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
def payment_list(
    delivery_mechanism_cash: Any,
    financial_service_provider: Any,
    program_and_cycle: dict[str, Any],
) -> PaymentList:
    program = program_and_cycle["program"]
    program_cycle = program_and_cycle["program_cycle"]
    payment_list = PaymentListFactory(
        program_cycle=program_cycle,
        business_area=program.business_area,
        delivery_mechanism=delivery_mechanism_cash,
        financial_service_provider=financial_service_provider,
    )
    PaymentFactory(
        parent=payment_list,
        entitlement_quantity=Decimal("10.00"),
        delivered_quantity=Decimal("0.00"),
        entitlement_quantity_usd=Decimal("20.00"),
        delivered_quantity_usd=Decimal("0.00"),
        status=Payment.STATUS_PENDING,
    )
    PaymentFactory(
        parent=payment_list,
        entitlement_quantity=Decimal("10.00"),
        delivered_quantity=Decimal("10.00"),
        entitlement_quantity_usd=Decimal("20.00"),
        delivered_quantity_usd=Decimal("20.00"),
        status=Payment.STATUS_DISTRIBUTION_SUCCESS,
    )
    PaymentFactory(
        parent=payment_list,
        entitlement_quantity=Decimal("10.00"),
        delivered_quantity=Decimal("5.00"),
        entitlement_quantity_usd=Decimal("20.00"),
        delivered_quantity_usd=Decimal("10.00"),
        status=Payment.STATUS_DISTRIBUTION_PARTIAL,
    )
    PaymentFactory(
        parent=payment_list,
        entitlement_quantity=Decimal("100.00"),
        delivered_quantity=Decimal("0.00"),
        entitlement_quantity_usd=Decimal("200.00"),
        delivered_quantity_usd=Decimal("0.00"),
        status=Payment.STATUS_NOT_DISTRIBUTED,
    )
    payment_list.update_money_fields()
    payment_list.unicef_id = "PP-0060-24-00000007"
    payment_list.save()
    payment_list.refresh_from_db()
    approval_process = ApprovalProcessFactory(payment_plan=payment_list.payment_plan)
    ApprovalFactory(type=Approval.APPROVAL, approval_process=approval_process)
    return payment_list


@pytest.fixture
def payment_plan(payment_list: PaymentList) -> PaymentPlan:
    group = payment_list.payment_plan
    group.status = PaymentPlan.Status.ACCEPTED
    group.save(update_fields=["status"])
    return group


@pytest.fixture
def second_payment_list_in_group(
    payment_plan: PaymentPlan, delivery_mechanism_cash: Any, program_and_cycle: dict[str, Any]
) -> PaymentList:
    second_plan = PaymentListFactory(
        program_cycle=program_and_cycle["program_cycle"],
        business_area=program_and_cycle["program"].business_area,
        payment_plan=payment_plan,
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
def group_approval_process(payment_plan: PaymentPlan) -> Any:
    approval_process = ApprovalProcessFactory(payment_plan=payment_plan)
    ApprovalFactory(approval_process=approval_process, type=Approval.APPROVAL, comment="group approved")
    return approval_process


def test_group_generate_web_links(payment_plan: PaymentPlan, mocker: Any) -> None:
    mocker.patch(
        "hope.apps.payment.pdf.payment_plan_export_pdf_service.get_link",
        side_effect=lambda path: f"http://www_link{path}",
    )
    pdf_export_service = PaymentPlanPDFExportService(payment_plan)

    pdf_export_service.generate_web_links()

    assert pdf_export_service.download_link == (
        f"http://www_link/api/download-payment-plan-summary-pdf/{payment_plan.id}"
    )
    assert pdf_export_service.payment_plan_link.endswith(f"/payment-module/payment-plans/{payment_plan.id}")


def test_group_generate_pdf_summary_returns_pdf_named_after_the_group(
    payment_plan: PaymentPlan, group_approval_process: Any, mocker: Any
) -> None:
    mocker.patch("hope.apps.payment.pdf.payment_plan_export_pdf_service.get_link", return_value="http://www_link")

    pdf, filename = PaymentPlanPDFExportService(payment_plan).generate_pdf_summary()

    assert isinstance(pdf, bytes)
    assert filename == f"PaymentPlanSummary-{payment_plan.unicef_id}.pdf"


def test_group_generate_pdf_summary_aggregates_every_plan_in_the_group(
    payment_plan: PaymentPlan,
    payment_list: PaymentList,
    second_payment_list_in_group: PaymentList,
    group_approval_process: Any,
    mocker: Any,
) -> None:
    mocker.patch("hope.apps.payment.pdf.payment_plan_export_pdf_service.get_link", return_value="http://www_link")
    generate_pdf_from_html_mock = mocker.patch(
        "hope.apps.payment.pdf.payment_plan_export_pdf_service.generate_pdf_from_html", return_value=b"pdf"
    )

    PaymentPlanPDFExportService(payment_plan).generate_pdf_summary()

    pdf_context_data = generate_pdf_from_html_mock.call_args.kwargs["data"]
    assert pdf_context_data["payment_lists"] == sorted(
        [payment_list, second_payment_list_in_group], key=lambda p: p.unicef_id
    )
    assert pdf_context_data["approval_process"] == group_approval_process
    assert pdf_context_data["approval"].comment == "group approved"
    assert pdf_context_data["authorization"] is None
    assert pdf_context_data["reconciliation"]["reconciled"] == 3
    assert pdf_context_data["reconciliation"]["pending"] == 1
    assert pdf_context_data["reconciliation"]["reconciled_usd"] == Decimal("50.00")


def test_group_get_email_context(payment_plan: PaymentPlan) -> None:
    user_mock = MagicMock()
    user_mock.first_name = "First"
    user_mock.last_name = "Last"
    user_mock.email = "first.last@email.com"

    context = PaymentPlanPDFExportService(payment_plan).get_email_context(user_mock)

    assert context == {
        "first_name": "First",
        "last_name": "Last",
        "email": "first.last@email.com",
        "message": "Payment Plan Summary PDF file has been generated, "
        "and below you will find the link to download the file.",
        "link": "",
        "title": "Payment Plan Summary file generated",
    }


@pytest.fixture
def instruction(program_and_cycle: dict[str, Any], financial_service_provider: Any) -> FollowUpInstruction:
    program = program_and_cycle["program"]
    return FollowUpInstructionFactory(
        program=program, business_area=program.business_area, financial_service_provider=financial_service_provider
    )


@pytest.fixture
def instruction_child(
    instruction: FollowUpInstruction, program_and_cycle: dict[str, Any], delivery_mechanism_cash: Any
) -> PaymentList:
    child = PaymentListFactory(
        program_cycle=program_and_cycle["program_cycle"],
        business_area=instruction.business_area,
        follow_up_instruction=instruction,
        plan_type=PaymentList.PlanType.FOLLOW_UP,
        delivery_mechanism=delivery_mechanism_cash,
        status=PaymentList.Status.ACCEPTED,
    )
    PaymentFactory(
        parent=child,
        entitlement_quantity=Decimal("10.00"),
        entitlement_quantity_usd=Decimal("20.00"),
        delivered_quantity=Decimal("10.00"),
        delivered_quantity_usd=Decimal("20.00"),
        status=Payment.STATUS_DISTRIBUTION_SUCCESS,
    )
    return child


@pytest.fixture
def instruction_approval_process(instruction: FollowUpInstruction) -> Any:
    approval_process = ApprovalProcessFactory(follow_up_instruction=instruction)
    ApprovalFactory(approval_process=approval_process, type=Approval.APPROVAL, comment="instruction approved")
    return approval_process


def test_instruction_generate_web_links(instruction: FollowUpInstruction, mocker: Any) -> None:
    mocker.patch(
        "hope.apps.payment.pdf.payment_plan_export_pdf_service.get_link",
        side_effect=lambda path: f"http://www_link{path}",
    )
    pdf_export_service = FollowUpInstructionPDFExportService(instruction)

    pdf_export_service.generate_web_links()

    assert pdf_export_service.download_link == (
        f"http://www_link/api/download-follow-up-instruction-summary-pdf/{instruction.id}"
    )
    assert pdf_export_service.instruction_link.endswith(f"/payment-module/follow-up-instructions/{instruction.id}")


def test_instruction_generate_pdf_summary_returns_pdf_named_after_the_instruction(
    instruction: FollowUpInstruction,
    instruction_child: PaymentList,
    instruction_approval_process: Any,
    mocker: Any,
) -> None:
    mocker.patch("hope.apps.payment.pdf.payment_plan_export_pdf_service.get_link", return_value="http://www_link")

    pdf, filename = FollowUpInstructionPDFExportService(instruction).generate_pdf_summary()

    assert isinstance(pdf, bytes)
    assert filename == f"FollowUpInstructionSummary-{instruction.unicef_id}.pdf"


def test_instruction_generate_pdf_summary_uses_the_instruction_approvals_and_payments(
    instruction: FollowUpInstruction,
    instruction_child: PaymentList,
    instruction_approval_process: Any,
    program_and_cycle: dict[str, Any],
    mocker: Any,
) -> None:
    mocker.patch("hope.apps.payment.pdf.payment_plan_export_pdf_service.get_link", return_value="http://www_link")
    generate_pdf_from_html_mock = mocker.patch(
        "hope.apps.payment.pdf.payment_plan_export_pdf_service.generate_pdf_from_html", return_value=b"pdf"
    )

    FollowUpInstructionPDFExportService(instruction).generate_pdf_summary()

    pdf_context_data = generate_pdf_from_html_mock.call_args.kwargs["data"]
    assert pdf_context_data["payment_lists"] == [instruction_child]
    assert pdf_context_data["status"] == "Accepted"
    assert pdf_context_data["cycle_title"] == program_and_cycle["program_cycle"].title
    assert pdf_context_data["approval"].comment == "instruction approved"
    assert pdf_context_data["reconciliation"]["reconciled"] == 1
    assert pdf_context_data["reconciliation"]["reconciled_usd"] == Decimal("20.00")


def test_instruction_get_email_context(instruction: FollowUpInstruction) -> None:
    user_mock = MagicMock()
    user_mock.first_name = "First"
    user_mock.last_name = "Last"
    user_mock.email = "first.last@email.com"

    context = FollowUpInstructionPDFExportService(instruction).get_email_context(user_mock)

    assert context == {
        "first_name": "First",
        "last_name": "Last",
        "email": "first.last@email.com",
        "message": "Follow-Up Instruction Summary PDF file has been generated, "
        "and below you will find the link to download the file.",
        "link": "",
        "title": "Follow-Up Instruction Summary file generated",
    }
