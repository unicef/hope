from datetime import timedelta
from decimal import Decimal
from typing import Any

import pytest
from rest_framework.exceptions import ValidationError

from extras.test_utils.factories import (
    BusinessAreaFactory,
    CurrencyFactory,
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PaymentPlanGroupFactory,
    ProgramCycleFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.payment.services.follow_up_instruction_service import FollowUpInstructionService
from hope.models import FollowUpInstruction, Payment, PaymentPlan

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
def second_cycle(program):
    return ProgramCycleFactory(program=program)


@pytest.fixture
def currency():
    return CurrencyFactory(code="AFN")


@pytest.fixture
def second_currency():
    return CurrencyFactory(code="USD")


@pytest.fixture
def delivery_mechanism():
    return DeliveryMechanismFactory(code="cash", name="Cash", payment_gateway_id="dm-cash")


@pytest.fixture
def fsp(delivery_mechanism):
    fsp = FinancialServiceProviderFactory()
    fsp.delivery_mechanisms.add(delivery_mechanism)
    return fsp


def _create_source_payment_plan(
    *,
    cycle: Any,
    group: Any,
    business_area: Any,
    currency: Any,
    delivery_mechanism: Any,
    fsp: Any,
    with_failed_payment: bool,
) -> PaymentPlan:
    payment_plan = PaymentPlanFactory(
        name=f"Source payment plan {group.id}",
        program_cycle=cycle,
        payment_plan_group=group,
        business_area=business_area,
        currency=currency,
        delivery_mechanism=delivery_mechanism,
        financial_service_provider=fsp,
        status=PaymentPlan.Status.FINISHED,
    )
    PaymentFactory(
        parent=payment_plan,
        program=payment_plan.program,
        currency=currency,
        delivery_type=delivery_mechanism,
        financial_service_provider=fsp,
        entitlement_quantity=Decimal("100.00"),
        entitlement_quantity_usd=Decimal("100.00"),
        status=Payment.STATUS_ERROR if with_failed_payment else Payment.STATUS_SUCCESS,
    )
    return payment_plan


def _create_instruction_child_payment_plan(
    *,
    instruction: FollowUpInstruction,
    cycle: Any,
    business_area: Any,
    currency: Any,
    delivery_mechanism: Any,
    fsp: Any,
    status: str,
) -> PaymentPlan:
    payment_plan = PaymentPlanFactory(
        program_cycle=cycle,
        business_area=business_area,
        currency=currency,
        delivery_mechanism=delivery_mechanism,
        financial_service_provider=fsp,
        follow_up_instruction=instruction,
        plan_type=PaymentPlan.PlanType.FOLLOW_UP,
        status=status,
        exchange_rate=Decimal("1.00"),
    )
    PaymentFactory(
        parent=payment_plan,
        program=payment_plan.program,
        currency=currency,
        delivery_type=delivery_mechanism,
        financial_service_provider=fsp,
        entitlement_quantity=Decimal("10.00"),
        entitlement_quantity_usd=Decimal("10.00"),
        status=Payment.STATUS_PENDING,
    )
    return payment_plan


def test_create_creates_follow_up_instruction_from_multiple_groups(
    user,
    program,
    cycle,
    second_cycle,
    business_area,
    currency,
    delivery_mechanism,
    fsp,
):
    group_one = PaymentPlanGroupFactory(cycle=cycle)
    group_two = PaymentPlanGroupFactory(cycle=second_cycle)
    source_one = _create_source_payment_plan(
        cycle=cycle,
        group=group_one,
        business_area=business_area,
        currency=currency,
        delivery_mechanism=delivery_mechanism,
        fsp=fsp,
        with_failed_payment=True,
    )
    source_two = _create_source_payment_plan(
        cycle=second_cycle,
        group=group_two,
        business_area=business_area,
        currency=currency,
        delivery_mechanism=delivery_mechanism,
        fsp=fsp,
        with_failed_payment=True,
    )

    instruction = FollowUpInstructionService(program).create(
        user=user,
        payment_plan_group_ids=[str(group_one.id), str(group_two.id)],
        dispersion_start_date=source_one.dispersion_start_date + timedelta(days=1),
        dispersion_end_date=source_one.dispersion_end_date + timedelta(days=1),
    )

    child_plans = list(instruction.payment_plans.order_by("created_at"))
    assert len(child_plans) == 2
    assert {child.source_payment_plan_id for child in child_plans} == {source_one.id, source_two.id}
    assert all(child.plan_type == PaymentPlan.PlanType.FOLLOW_UP for child in child_plans)


def test_create_excludes_source_plans_already_used_by_another_instruction(
    user,
    program,
    cycle,
    business_area,
    currency,
    delivery_mechanism,
    fsp,
):
    group = PaymentPlanGroupFactory(cycle=cycle)
    source_one = _create_source_payment_plan(
        cycle=cycle,
        group=group,
        business_area=business_area,
        currency=currency,
        delivery_mechanism=delivery_mechanism,
        fsp=fsp,
        with_failed_payment=True,
    )
    source_two = _create_source_payment_plan(
        cycle=cycle,
        group=group,
        business_area=business_area,
        currency=currency,
        delivery_mechanism=delivery_mechanism,
        fsp=fsp,
        with_failed_payment=True,
    )
    existing_instruction = FollowUpInstruction.objects.create(
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
        follow_up_instruction=existing_instruction,
        plan_type=PaymentPlan.PlanType.FOLLOW_UP,
        source_payment_plan=source_one,
    )

    instruction = FollowUpInstructionService(program).create(
        user=user,
        payment_plan_group_ids=[str(group.id)],
        dispersion_start_date=source_two.dispersion_start_date + timedelta(days=1),
        dispersion_end_date=source_two.dispersion_end_date + timedelta(days=1),
    )

    child_plans = list(instruction.payment_plans.all())
    assert len(child_plans) == 1
    assert child_plans[0].source_payment_plan_id == source_two.id


def test_create_raises_validation_error_when_no_applicable_source_plans(
    user,
    program,
    cycle,
    business_area,
    currency,
    delivery_mechanism,
    fsp,
):
    group = PaymentPlanGroupFactory(cycle=cycle)
    _create_source_payment_plan(
        cycle=cycle,
        group=group,
        business_area=business_area,
        currency=currency,
        delivery_mechanism=delivery_mechanism,
        fsp=fsp,
        with_failed_payment=False,
    )

    with pytest.raises(ValidationError, match="No applicable Payment Plans were found"):
        FollowUpInstructionService(program).create(
            user=user,
            payment_plan_group_ids=[str(group.id)],
            dispersion_start_date=cycle.start_date + timedelta(days=1),
            dispersion_end_date=cycle.start_date + timedelta(days=2),
        )


def test_create_raises_validation_error_for_mixed_currency(
    user,
    program,
    cycle,
    business_area,
    currency,
    second_currency,
    delivery_mechanism,
    fsp,
):
    group = PaymentPlanGroupFactory(cycle=cycle)
    _create_source_payment_plan(
        cycle=cycle,
        group=group,
        business_area=business_area,
        currency=currency,
        delivery_mechanism=delivery_mechanism,
        fsp=fsp,
        with_failed_payment=True,
    )
    _create_source_payment_plan(
        cycle=cycle,
        group=group,
        business_area=business_area,
        currency=second_currency,
        delivery_mechanism=delivery_mechanism,
        fsp=fsp,
        with_failed_payment=True,
    )

    with pytest.raises(ValidationError, match="must share the same Currency"):
        FollowUpInstructionService(program).create(
            user=user,
            payment_plan_group_ids=[str(group.id)],
            dispersion_start_date=cycle.start_date + timedelta(days=1),
            dispersion_end_date=cycle.start_date + timedelta(days=2),
        )


def test_export_xlsx_allows_retry_after_background_error(
    user,
    program,
    cycle,
    business_area,
    currency,
    delivery_mechanism,
    fsp,
):
    instruction = FollowUpInstruction.objects.create(
        business_area=business_area,
        program=program,
        created_by=user,
        background_action_status=FollowUpInstruction.BackgroundActionStatus.XLSX_EXPORT_ERROR,
    )
    _create_instruction_child_payment_plan(
        instruction=instruction,
        cycle=cycle,
        business_area=business_area,
        currency=currency,
        delivery_mechanism=delivery_mechanism,
        fsp=fsp,
        status=PaymentPlan.Status.LOCKED,
    )
