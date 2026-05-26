from datetime import timedelta
from decimal import Decimal
from typing import Any
import uuid

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


def test_init_raises_value_error_when_no_program_or_instruction() -> None:
    with pytest.raises(ValueError, match="Program or instruction is required."):
        FollowUpInstructionService()


def test_get_source_groups_raises_when_group_not_in_program(
    program: Any,
    business_area: Any,
) -> None:
    other_program = ProgramFactory(business_area=business_area)
    other_cycle = ProgramCycleFactory(program=other_program)
    group = PaymentPlanGroupFactory(cycle=other_cycle)

    with pytest.raises(ValidationError, match="One or more Payment Plan Groups do not exist"):
        FollowUpInstructionService(program)._get_source_groups([str(group.id)])


def test_validate_shared_configuration_raises_for_mixed_fsp(
    cycle: Any,
    business_area: Any,
    currency: Any,
    delivery_mechanism: Any,
) -> None:
    fsp_one = FinancialServiceProviderFactory()
    fsp_two = FinancialServiceProviderFactory()
    plan_one = PaymentPlanFactory(
        program_cycle=cycle,
        business_area=business_area,
        currency=currency,
        delivery_mechanism=delivery_mechanism,
        financial_service_provider=fsp_one,
    )
    plan_two = PaymentPlanFactory(
        program_cycle=cycle,
        business_area=business_area,
        currency=currency,
        delivery_mechanism=delivery_mechanism,
        financial_service_provider=fsp_two,
    )

    with pytest.raises(ValidationError, match="same Financial Service Provider"):
        FollowUpInstructionService._validate_shared_configuration([plan_one, plan_two])


def test_validate_shared_configuration_raises_for_mixed_delivery_mechanism(
    cycle: Any,
    business_area: Any,
    currency: Any,
    delivery_mechanism: Any,
    fsp: Any,
) -> None:
    second_delivery_mechanism = DeliveryMechanismFactory()
    plan_one = PaymentPlanFactory(
        program_cycle=cycle,
        business_area=business_area,
        currency=currency,
        delivery_mechanism=delivery_mechanism,
        financial_service_provider=fsp,
    )
    plan_two = PaymentPlanFactory(
        program_cycle=cycle,
        business_area=business_area,
        currency=currency,
        delivery_mechanism=second_delivery_mechanism,
        financial_service_provider=fsp,
    )

    with pytest.raises(ValidationError, match="same Delivery Mechanism"):
        FollowUpInstructionService._validate_shared_configuration([plan_one, plan_two])


def test_require_instruction_raises_when_instruction_is_none(
    program: Any,
) -> None:
    service = FollowUpInstructionService(program=program)

    with pytest.raises(ValueError, match="Instruction is required."):
        service._require_instruction()


def test_validate_child_payment_plans_statuses_raises_when_no_child_plans(
    user: Any,
    program: Any,
    business_area: Any,
) -> None:
    instruction = FollowUpInstruction.objects.create(
        business_area=business_area,
        program=program,
        created_by=user,
    )
    service = FollowUpInstructionService(instruction=instruction)

    with pytest.raises(ValidationError, match="no child Payment Plans"):
        service._validate_child_payment_plans_statuses({PaymentPlan.Status.LOCKED}, "Test action")


def test_validate_child_payment_plans_statuses_raises_for_wrong_status(
    user: Any,
    program: Any,
    cycle: Any,
    business_area: Any,
    currency: Any,
    delivery_mechanism: Any,
    fsp: Any,
) -> None:
    instruction = FollowUpInstruction.objects.create(
        business_area=business_area,
        program=program,
        created_by=user,
    )
    _create_instruction_child_payment_plan(
        instruction=instruction,
        cycle=cycle,
        business_area=business_area,
        currency=currency,
        delivery_mechanism=delivery_mechanism,
        fsp=fsp,
        status=PaymentPlan.Status.OPEN,
    )
    service = FollowUpInstructionService(instruction=instruction)

    with pytest.raises(ValidationError, match="not available for child Payment Plans outside statuses"):
        service._validate_child_payment_plans_statuses({PaymentPlan.Status.LOCKED}, "Test action")


def test_validate_instruction_has_eligible_payments_raises_when_no_payments(
    user: Any,
    program: Any,
    business_area: Any,
) -> None:
    instruction = FollowUpInstruction.objects.create(
        business_area=business_area,
        program=program,
        created_by=user,
    )
    service = FollowUpInstructionService(instruction=instruction)

    with pytest.raises(ValidationError, match="Export failed: The Payment List is empty."):
        service._validate_instruction_has_eligible_payments()


def test_validate_delivery_template_exists_raises_when_fsp_is_none(
    user: Any,
    program: Any,
    cycle: Any,
    business_area: Any,
    currency: Any,
) -> None:
    instruction = FollowUpInstruction.objects.create(
        business_area=business_area,
        program=program,
        created_by=user,
    )
    PaymentPlanFactory(
        program_cycle=cycle,
        business_area=business_area,
        currency=currency,
        follow_up_instruction=instruction,
        plan_type=PaymentPlan.PlanType.FOLLOW_UP,
        financial_service_provider=None,
    )
    service = FollowUpInstructionService(instruction=instruction)

    with pytest.raises(ValidationError, match="Financial Service Provider and Delivery Mechanism"):
        service._validate_delivery_template_exists()


def test_validate_delivery_template_exists_raises_when_no_xlsx_template(
    user: Any,
    program: Any,
    cycle: Any,
    business_area: Any,
    currency: Any,
    delivery_mechanism: Any,
    fsp: Any,
) -> None:
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
    )
    service = FollowUpInstructionService(instruction=instruction)

    with pytest.raises(ValidationError, match="FSP XLSX Template"):
        service._validate_delivery_template_exists()


def test_validate_no_background_action_in_progress_raises_when_exporting(
    user: Any,
    program: Any,
    business_area: Any,
) -> None:
    instruction = FollowUpInstruction.objects.create(
        business_area=business_area,
        program=program,
        created_by=user,
        background_action_status=FollowUpInstruction.BackgroundActionStatus.XLSX_EXPORTING,
    )
    service = FollowUpInstructionService(instruction=instruction)

    with pytest.raises(ValidationError, match="background action is in progress"):
        service._validate_no_background_action_in_progress("Test action")


def test_abort_transitions_child_payment_plans_to_aborted(
    user: Any,
    program: Any,
    cycle: Any,
    business_area: Any,
    currency: Any,
    delivery_mechanism: Any,
    fsp: Any,
) -> None:
    instruction = FollowUpInstruction.objects.create(
        business_area=business_area,
        program=program,
        created_by=user,
    )
    child_plan = _create_instruction_child_payment_plan(
        instruction=instruction,
        cycle=cycle,
        business_area=business_area,
        currency=currency,
        delivery_mechanism=delivery_mechanism,
        fsp=fsp,
        status=PaymentPlan.Status.LOCKED,
    )

    result = FollowUpInstructionService(instruction=instruction).abort(user=user, abort_comment="stopping")

    child_plan.refresh_from_db()
    assert result == instruction
    assert child_plan.status == PaymentPlan.Status.ABORTED


def test_reactivate_abort_transitions_child_payment_plans_to_open(
    user: Any,
    program: Any,
    cycle: Any,
    business_area: Any,
    currency: Any,
    delivery_mechanism: Any,
    fsp: Any,
) -> None:
    instruction = FollowUpInstruction.objects.create(
        business_area=business_area,
        program=program,
        created_by=user,
    )
    child_plan = _create_instruction_child_payment_plan(
        instruction=instruction,
        cycle=cycle,
        business_area=business_area,
        currency=currency,
        delivery_mechanism=delivery_mechanism,
        fsp=fsp,
        status=PaymentPlan.Status.ABORTED,
    )

    result = FollowUpInstructionService(instruction=instruction).reactivate_abort(user=user)

    child_plan.refresh_from_db()
    assert result == instruction
    assert child_plan.status == PaymentPlan.Status.OPEN


def test_status_returns_first_status_when_no_precedence_match(user, program, business_area, cycle) -> None:
    instruction = FollowUpInstruction.objects.create(
        business_area=business_area,
        program=program,
        created_by=user,
    )
    PaymentPlanFactory(
        follow_up_instruction=instruction,
        program_cycle=cycle,
        status=PaymentPlan.Status.DRAFT,
    )

    assert instruction.status == PaymentPlan.Status.DRAFT


def test_export_file_link_returns_none_when_file_not_found(user, program, business_area) -> None:
    instruction = FollowUpInstruction.objects.create(
        business_area=business_area,
        program=program,
        created_by=user,
    )
    instruction.export_file_id = uuid.uuid4()

    assert instruction.export_file_link is None
