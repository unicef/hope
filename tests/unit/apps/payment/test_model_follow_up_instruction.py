from decimal import Decimal

import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    CurrencyFactory,
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    FollowUpInstructionFactory,
    HouseholdFactory,
    PaymentFactory,
    PaymentPlanFactory,
    ProgramCycleFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.payment.flows import FollowUpInstructionFlow
from hope.models import FollowUpInstruction, PaymentPlan

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area():
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def program(business_area):
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def cycle(program):
    return ProgramCycleFactory(program=program)


@pytest.fixture
def currency():
    return CurrencyFactory(code="AFN")


@pytest.fixture
def delivery_mechanism():
    return DeliveryMechanismFactory(code="cash", name="Cash", payment_gateway_id="dm-cash")


@pytest.fixture
def fsp(delivery_mechanism):
    fsp = FinancialServiceProviderFactory()
    fsp.delivery_mechanisms.add(delivery_mechanism)
    return fsp


def test_follow_up_instruction_status_uses_child_payment_plan_precedence(
    user,
    business_area,
    program,
    cycle,
    currency,
    delivery_mechanism,
    fsp,
):
    instruction = FollowUpInstruction.objects.create(
        business_area=business_area,
        program=program,
        created_by=user,
    )
    PaymentPlanFactory(
        program_cycle=cycle,
        business_area=business_area,
        currency=currency,
        delivery_mechanism=delivery_mechanism,
        financial_service_provider=fsp,
        follow_up_instruction=instruction,
        plan_type=PaymentPlan.PlanType.FOLLOW_UP,
        status=PaymentPlan.Status.ACCEPTED,
    )
    PaymentPlanFactory(
        program_cycle=cycle,
        business_area=business_area,
        currency=currency,
        delivery_mechanism=delivery_mechanism,
        financial_service_provider=fsp,
        follow_up_instruction=instruction,
        plan_type=PaymentPlan.PlanType.FOLLOW_UP,
        status=PaymentPlan.Status.OPEN,
    )

    assert instruction.status == FollowUpInstruction.Status.OPEN


def test_follow_up_instruction_payments_summary_aggregates_only_eligible_payments(
    user,
    business_area,
    program,
    cycle,
    currency,
    delivery_mechanism,
    fsp,
):
    instruction = FollowUpInstruction.objects.create(
        business_area=business_area,
        program=program,
        created_by=user,
    )
    payment_plan_one = PaymentPlanFactory(
        program_cycle=cycle,
        business_area=business_area,
        currency=currency,
        delivery_mechanism=delivery_mechanism,
        financial_service_provider=fsp,
        follow_up_instruction=instruction,
        plan_type=PaymentPlan.PlanType.FOLLOW_UP,
    )
    payment_plan_two = PaymentPlanFactory(
        program_cycle=cycle,
        business_area=business_area,
        currency=currency,
        delivery_mechanism=delivery_mechanism,
        financial_service_provider=fsp,
        follow_up_instruction=instruction,
        plan_type=PaymentPlan.PlanType.FOLLOW_UP,
    )
    shared_household = HouseholdFactory(business_area=payment_plan_one.business_area, program=payment_plan_one.program)
    PaymentFactory(
        parent=payment_plan_one,
        household=shared_household,
        collector=shared_household.head_of_household,
        head_of_household=shared_household.head_of_household,
        program=payment_plan_one.program,
        currency=currency,
        delivery_type=delivery_mechanism,
        financial_service_provider=fsp,
        entitlement_quantity=Decimal("100.00"),
        delivered_quantity=Decimal("10.00"),
    )
    PaymentFactory(
        parent=payment_plan_two,
        household=shared_household,
        collector=shared_household.head_of_household,
        head_of_household=shared_household.head_of_household,
        program=payment_plan_two.program,
        currency=currency,
        delivery_type=delivery_mechanism,
        financial_service_provider=fsp,
        entitlement_quantity=Decimal("40.00"),
        delivered_quantity=Decimal("5.00"),
    )
    PaymentFactory(
        parent=payment_plan_two,
        program=payment_plan_two.program,
        currency=currency,
        delivery_type=delivery_mechanism,
        financial_service_provider=fsp,
        entitlement_quantity=Decimal("999.00"),
        delivered_quantity=Decimal("0.00"),
        excluded=True,
    )

    summary = instruction.payments_summary()

    assert summary["child_payment_plans_count"] == 2
    assert summary["households_count"] == 1
    assert summary["total_entitled_quantity"] == Decimal("140.00")
    assert summary["total_delivered_quantity"] == Decimal("15.00")
    assert summary["total_undelivered_quantity"] == Decimal("125.00")


def test_instruction_managed_payment_plan_exposes_no_conflict_annotations(
    user,
    business_area,
    program,
    cycle,
    currency,
    delivery_mechanism,
    fsp,
):
    instruction = FollowUpInstruction.objects.create(
        business_area=business_area,
        program=program,
        created_by=user,
    )
    payment_plan = PaymentPlanFactory(
        program_cycle=cycle,
        business_area=business_area,
        currency=currency,
        delivery_mechanism=delivery_mechanism,
        financial_service_provider=fsp,
        follow_up_instruction=instruction,
        plan_type=PaymentPlan.PlanType.FOLLOW_UP,
    )
    payment = PaymentFactory(
        parent=payment_plan,
        program=payment_plan.program,
        currency=currency,
        delivery_type=delivery_mechanism,
        financial_service_provider=fsp,
    )

    annotated_payment = payment_plan.eligible_payments_with_conflicts.get(pk=payment.pk)

    assert payment_plan.is_instruction_managed is True
    assert annotated_payment.payment_plan_hard_conflicted is False
    assert annotated_payment.payment_plan_hard_conflicted_data == []
    assert annotated_payment.payment_plan_soft_conflicted is False
    assert annotated_payment.payment_plan_soft_conflicted_data == []


def test_follow_up_instruction_flow_xlsx_export_error_from_exporting() -> None:
    instruction = FollowUpInstructionFactory(
        background_action_status=PaymentPlan.BackgroundActionStatus.XLSX_EXPORTING,
    )
    FollowUpInstructionFlow(instruction).background_action_status_xlsx_export_error()
    assert instruction.background_action_status == PaymentPlan.BackgroundActionStatus.XLSX_EXPORT_ERROR


def test_follow_up_instruction_flow_xlsx_import_error_from_importing_reconciliation() -> None:
    instruction = FollowUpInstructionFactory(
        background_action_status=PaymentPlan.BackgroundActionStatus.XLSX_IMPORTING_RECONCILIATION,
    )
    FollowUpInstructionFlow(instruction).background_action_status_xlsx_import_error()
    assert instruction.background_action_status == PaymentPlan.BackgroundActionStatus.XLSX_IMPORT_ERROR
