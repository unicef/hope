from datetime import timedelta
from decimal import Decimal
import re
from typing import Any
from unittest.mock import patch
import uuid

from django.contrib.contenttypes.models import ContentType
from django.db.backends.postgresql.psycopg_any import NumericRange
import pytest
from rest_framework.exceptions import ValidationError

from extras.test_utils.factories import (
    ApprovalFactory,
    ApprovalProcessFactory,
    BusinessAreaFactory,
    CurrencyFactory,
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    FollowUpInstructionFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PaymentPlanGroupFactory,
    ProgramCycleFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.payment.services.follow_up_instruction_service import FollowUpInstructionService
from hope.models import (
    AcceptanceProcessThreshold,
    Approval,
    ApprovalProcess,
    FollowUpInstruction,
    LogEntry,
    Payment,
    PaymentPlan,
)

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
def deprecated_syp():
    return CurrencyFactory(code="SYP", vision_code="SYP", name="Syrian Pound", active=False)


@pytest.fixture
def active_syp():
    return CurrencyFactory(code="SYP", vision_code="SYP01", name="Syrian Pound")


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


@pytest.fixture
def instruction_over_one_group(user, program, cycle, business_area, currency, delivery_mechanism, fsp):
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
    return FollowUpInstructionService(program).create(
        user=user,
        payment_plan_group_ids=[str(group.id)],
        dispersion_start_date=cycle.start_date + timedelta(days=1),
        dispersion_end_date=cycle.start_date + timedelta(days=2),
    )


def test_create_takes_fsp_and_currency_from_the_source_group(instruction_over_one_group, fsp, currency):
    assert instruction_over_one_group.financial_service_provider == fsp
    assert instruction_over_one_group.currency == currency


def test_create_stores_dispersion_dates_on_the_instruction(instruction_over_one_group, cycle):
    child_plan = instruction_over_one_group.payment_plans.get()

    assert instruction_over_one_group.dispersion_start_date == cycle.start_date + timedelta(days=1)
    assert instruction_over_one_group.dispersion_end_date == cycle.start_date + timedelta(days=2)
    assert child_plan.dispersion_start_date == instruction_over_one_group.dispersion_start_date
    assert child_plan.dispersion_end_date == instruction_over_one_group.dispersion_end_date


def test_create_leaves_child_payment_plans_outside_any_group(instruction_over_one_group, fsp, currency):
    child_plan = instruction_over_one_group.payment_plans.get()

    assert child_plan.payment_plan_group_id is None
    assert child_plan.financial_service_provider == fsp
    assert child_plan.currency == currency


@pytest.fixture
def instruction_over_one_payment_gateway_group(user, program, cycle, business_area, currency, delivery_mechanism, fsp):
    group = PaymentPlanGroupFactory(cycle=cycle, use_payment_gateway=True)
    _create_source_payment_plan(
        cycle=cycle,
        group=group,
        business_area=business_area,
        currency=currency,
        delivery_mechanism=delivery_mechanism,
        fsp=fsp,
        with_failed_payment=True,
    )
    return FollowUpInstructionService(program).create(
        user=user,
        payment_plan_group_ids=[str(group.id)],
        dispersion_start_date=cycle.start_date + timedelta(days=1),
        dispersion_end_date=cycle.start_date + timedelta(days=2),
    )


def test_create_takes_use_payment_gateway_from_the_source_group(instruction_over_one_payment_gateway_group):
    child_plan = instruction_over_one_payment_gateway_group.payment_plans.get()

    assert instruction_over_one_payment_gateway_group.use_payment_gateway is True
    assert child_plan.use_payment_gateway is True


@pytest.mark.enable_activity_log
def test_create_logs_activity_for_each_child_payment_plan(
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
    _create_source_payment_plan(
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

    child_ids = list(instruction.payment_plans.values_list("id", flat=True))
    create_logs = LogEntry.objects.filter(object_id__in=child_ids, action=LogEntry.CREATE)
    assert create_logs.count() == 2
    assert all(log.user == user for log in create_logs)


def test_create_excludes_source_plans_with_existing_follow_up_child(
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


def test_create_excludes_source_plans_with_manual_follow_up_child(
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
    PaymentPlanFactory(
        program_cycle=cycle,
        business_area=business_area,
        currency=currency,
        delivery_mechanism=delivery_mechanism,
        financial_service_provider=fsp,
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


def test_create_does_not_exclude_source_plans_with_top_up_child(
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
    PaymentPlanFactory(
        program_cycle=cycle,
        business_area=business_area,
        currency=currency,
        delivery_mechanism=delivery_mechanism,
        financial_service_provider=fsp,
        plan_type=PaymentPlan.PlanType.TOP_UP,
        source_payment_plan=source_one,
    )

    instruction = FollowUpInstructionService(program).create(
        user=user,
        payment_plan_group_ids=[str(group.id)],
        dispersion_start_date=source_one.dispersion_start_date + timedelta(days=1),
        dispersion_end_date=source_one.dispersion_end_date + timedelta(days=1),
    )

    child_plans = list(instruction.payment_plans.all())
    assert len(child_plans) == 2
    assert {child.source_payment_plan_id for child in child_plans} == {source_one.id, source_two.id}


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
    other_group = PaymentPlanGroupFactory(cycle=cycle)
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
        group=other_group,
        business_area=business_area,
        currency=second_currency,
        delivery_mechanism=delivery_mechanism,
        fsp=fsp,
        with_failed_payment=True,
    )

    with pytest.raises(ValidationError, match="must share the same Currency"):
        FollowUpInstructionService(program).create(
            user=user,
            payment_plan_group_ids=[str(group.id), str(other_group.id)],
            dispersion_start_date=cycle.start_date + timedelta(days=1),
            dispersion_end_date=cycle.start_date + timedelta(days=2),
        )


def test_create_raises_validation_error_for_mixed_use_payment_gateway(
    user,
    program,
    cycle,
    business_area,
    currency,
    delivery_mechanism,
    fsp,
):
    group = PaymentPlanGroupFactory(cycle=cycle, use_payment_gateway=True)
    other_group = PaymentPlanGroupFactory(cycle=cycle)
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
        group=other_group,
        business_area=business_area,
        currency=currency,
        delivery_mechanism=delivery_mechanism,
        fsp=fsp,
        with_failed_payment=True,
    )

    with pytest.raises(ValidationError, match="must share the same Use Payment Gateway setting"):
        FollowUpInstructionService(program).create(
            user=user,
            payment_plan_group_ids=[str(group.id), str(other_group.id)],
            dispersion_start_date=cycle.start_date + timedelta(days=1),
            dispersion_end_date=cycle.start_date + timedelta(days=2),
        )


@pytest.fixture
def group_ids_paid_in_both_syp_denominations(cycle, business_area, deprecated_syp, active_syp, delivery_mechanism, fsp):
    deprecated_group = PaymentPlanGroupFactory(cycle=cycle)
    _create_source_payment_plan(
        cycle=cycle,
        group=deprecated_group,
        business_area=business_area,
        currency=deprecated_syp,
        delivery_mechanism=delivery_mechanism,
        fsp=fsp,
        with_failed_payment=True,
    )
    active_group = PaymentPlanGroupFactory(cycle=cycle)
    _create_source_payment_plan(
        cycle=cycle,
        group=active_group,
        business_area=business_area,
        currency=active_syp,
        delivery_mechanism=delivery_mechanism,
        fsp=fsp,
        with_failed_payment=True,
    )
    return [str(deprecated_group.id), str(active_group.id)]


def test_create_rejects_currency_variants_sharing_a_code_and_names_both(
    user,
    program,
    cycle,
    group_ids_paid_in_both_syp_denominations,
):
    with pytest.raises(ValidationError, match=re.escape("Found: SYP (SYP01) - Syrian Pound, SYP - Syrian Pound.")):
        FollowUpInstructionService(program).create(
            user=user,
            payment_plan_group_ids=group_ids_paid_in_both_syp_denominations,
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


@patch("hope.apps.payment.services.payment_plan_services.send_payment_notification_emails_async_task")
def test_close_transitions_child_payment_plans_to_closed_without_notification(
    mock_notify: Any,
    user: Any,
    program: Any,
    cycle: Any,
    business_area: Any,
    currency: Any,
    delivery_mechanism: Any,
    fsp: Any,
) -> None:
    instruction = FollowUpInstructionFactory(program=program, created_by=user)
    child_plan = _create_instruction_child_payment_plan(
        instruction=instruction,
        cycle=cycle,
        business_area=business_area,
        currency=currency,
        delivery_mechanism=delivery_mechanism,
        fsp=fsp,
        status=PaymentPlan.Status.FINISHED,
    )

    result = FollowUpInstructionService(instruction=instruction).close(user=user, closure_comment="all paid")

    child_plan.refresh_from_db()
    assert result == instruction
    assert child_plan.status == PaymentPlan.Status.CLOSED
    mock_notify.assert_not_called()


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


def test_remove_export_file_does_nothing_when_no_export_file(user, program, business_area) -> None:
    instruction = FollowUpInstruction.objects.create(
        business_area=business_area,
        program=program,
        created_by=user,
    )

    instruction.remove_export_file()

    assert instruction.export_file is None


@pytest.fixture
def approval_instruction(user, program, business_area) -> FollowUpInstruction:
    return FollowUpInstructionFactory(program=program, business_area=business_area, created_by=user)


@pytest.fixture
def locked_fsp_children(approval_instruction, cycle, business_area, currency) -> list[PaymentPlan]:
    return [
        PaymentPlanFactory(
            program_cycle=cycle,
            business_area=business_area,
            currency=currency,
            follow_up_instruction=approval_instruction,
            plan_type=PaymentPlan.PlanType.FOLLOW_UP,
            status=PaymentPlan.Status.LOCKED_FSP,
            total_entitled_quantity_usd=Decimal("100.00"),
        )
        for _ in range(2)
    ]


@pytest.fixture
def threshold_above_one_child(business_area) -> AcceptanceProcessThreshold:
    return AcceptanceProcessThreshold.objects.create(
        business_area=business_area,
        payments_range_usd=NumericRange(150, None),
        approval_number_required=2,
        authorization_number_required=3,
        finance_release_number_required=4,
    )


@patch(
    "hope.apps.payment.services.follow_up_instruction_service.send_follow_up_instruction_notification_emails_async_task"
)
def test_send_for_approval_moves_every_child_to_in_approval(
    mock_notify: Any, user: Any, approval_instruction: FollowUpInstruction, locked_fsp_children: list[PaymentPlan]
) -> None:
    FollowUpInstructionService(instruction=approval_instruction).send_for_approval(user)

    assert set(approval_instruction.payment_plans.values_list("status", flat=True)) == {PaymentPlan.Status.IN_APPROVAL}


@patch(
    "hope.apps.payment.services.follow_up_instruction_service.send_follow_up_instruction_notification_emails_async_task"
)
def test_send_for_approval_creates_one_process_on_the_instruction_sized_by_its_total(
    mock_notify: Any,
    user: Any,
    approval_instruction: FollowUpInstruction,
    locked_fsp_children: list[PaymentPlan],
    threshold_above_one_child: AcceptanceProcessThreshold,
) -> None:
    FollowUpInstructionService(instruction=approval_instruction).send_for_approval(user)

    approval_process = ApprovalProcess.objects.get()
    assert approval_process.follow_up_instruction == approval_instruction
    assert approval_process.sent_for_approval_by == user
    assert approval_process.approval_number_required == 2
    assert approval_process.authorization_number_required == 3
    assert approval_process.finance_release_number_required == 4


@patch(
    "hope.apps.payment.services.follow_up_instruction_service.send_follow_up_instruction_notification_emails_async_task"
)
def test_send_for_approval_notifies_once_for_the_instruction(
    mock_notify: Any, user: Any, approval_instruction: FollowUpInstruction, locked_fsp_children: list[PaymentPlan]
) -> None:
    FollowUpInstructionService(instruction=approval_instruction).send_for_approval(user)

    mock_notify.assert_called_once()
    assert mock_notify.call_args.args[:3] == (
        approval_instruction,
        PaymentPlan.Action.SEND_FOR_APPROVAL.value,
        str(user.pk),
    )


@pytest.fixture
def locked_child(approval_instruction, cycle, business_area, currency) -> PaymentPlan:
    return PaymentPlanFactory(
        program_cycle=cycle,
        business_area=business_area,
        currency=currency,
        follow_up_instruction=approval_instruction,
        plan_type=PaymentPlan.PlanType.FOLLOW_UP,
        status=PaymentPlan.Status.LOCKED,
    )


def test_send_for_approval_rejects_children_outside_locked_fsp(
    user: Any,
    approval_instruction: FollowUpInstruction,
    locked_fsp_children: list[PaymentPlan],
    locked_child: PaymentPlan,
) -> None:
    with pytest.raises(ValidationError, match="Send for Approval is not available"):
        FollowUpInstructionService(instruction=approval_instruction).send_for_approval(user)


@pytest.fixture
def in_approval_children(approval_instruction, cycle, business_area, currency) -> list[PaymentPlan]:
    return [
        PaymentPlanFactory(
            program_cycle=cycle,
            business_area=business_area,
            currency=currency,
            follow_up_instruction=approval_instruction,
            plan_type=PaymentPlan.PlanType.FOLLOW_UP,
            status=PaymentPlan.Status.IN_APPROVAL,
        )
        for _ in range(2)
    ]


@pytest.fixture
def instruction_approval_process(approval_instruction) -> ApprovalProcess:
    return ApprovalProcessFactory(follow_up_instruction=approval_instruction, approval_number_required=2)


@patch(
    "hope.apps.payment.services.follow_up_instruction_service.send_follow_up_instruction_notification_emails_async_task"
)
def test_approve_below_the_required_count_keeps_children_in_approval(
    mock_notify: Any,
    user: Any,
    approval_instruction: FollowUpInstruction,
    in_approval_children: list[PaymentPlan],
    instruction_approval_process: ApprovalProcess,
) -> None:
    FollowUpInstructionService(instruction=approval_instruction).acceptance_process(
        PaymentPlan.Action.APPROVE.value, user, "looks good"
    )

    assert instruction_approval_process.approvals.get().comment == "looks good"
    assert set(approval_instruction.payment_plans.values_list("status", flat=True)) == {PaymentPlan.Status.IN_APPROVAL}
    mock_notify.assert_not_called()


@pytest.fixture
def first_approval(instruction_approval_process) -> Approval:
    return ApprovalFactory(approval_process=instruction_approval_process, type=Approval.APPROVAL)


@patch(
    "hope.apps.payment.services.follow_up_instruction_service.send_follow_up_instruction_notification_emails_async_task"
)
def test_approve_reaching_the_required_count_moves_every_child_to_in_authorization(
    mock_notify: Any,
    user: Any,
    approval_instruction: FollowUpInstruction,
    in_approval_children: list[PaymentPlan],
    first_approval: Approval,
) -> None:
    FollowUpInstructionService(instruction=approval_instruction).acceptance_process(
        PaymentPlan.Action.APPROVE.value, user
    )

    first_approval.approval_process.refresh_from_db()
    assert set(approval_instruction.payment_plans.values_list("status", flat=True)) == {
        PaymentPlan.Status.IN_AUTHORIZATION
    }
    assert first_approval.approval_process.sent_for_authorization_by == user
    mock_notify.assert_called_once()
    assert mock_notify.call_args.args[1] == PaymentPlan.Action.APPROVE.value


@pytest.mark.enable_activity_log
@patch(
    "hope.apps.payment.services.follow_up_instruction_service.send_follow_up_instruction_notification_emails_async_task"
)
def test_approve_logs_the_approval_on_the_instruction(
    mock_notify: Any,
    user: Any,
    approval_instruction: FollowUpInstruction,
    in_approval_children: list[PaymentPlan],
    instruction_approval_process: ApprovalProcess,
) -> None:
    FollowUpInstructionService(instruction=approval_instruction).acceptance_process(
        PaymentPlan.Action.APPROVE.value, user, "looks good"
    )

    log_entry = LogEntry.objects.get(
        content_type=ContentType.objects.get_for_model(FollowUpInstruction), object_id=approval_instruction.pk
    )
    assert log_entry.changes == {
        "acceptance_process": {"from": None, "to": Approval.APPROVAL},
        "comment": {"from": None, "to": "looks good"},
    }


@patch(
    "hope.apps.payment.services.follow_up_instruction_service.send_follow_up_instruction_notification_emails_async_task"
)
def test_reject_moves_every_child_back_to_locked_fsp(
    mock_notify: Any,
    user: Any,
    approval_instruction: FollowUpInstruction,
    in_approval_children: list[PaymentPlan],
    instruction_approval_process: ApprovalProcess,
) -> None:
    FollowUpInstructionService(instruction=approval_instruction).acceptance_process(
        PaymentPlan.Action.REJECT.value, user, "wrong amounts"
    )

    assert set(approval_instruction.payment_plans.values_list("status", flat=True)) == {PaymentPlan.Status.LOCKED_FSP}
    mock_notify.assert_not_called()


def test_authorize_outside_in_authorization_raises(
    user: Any,
    approval_instruction: FollowUpInstruction,
    in_approval_children: list[PaymentPlan],
    instruction_approval_process: ApprovalProcess,
) -> None:
    with pytest.raises(ValidationError, match="Not possible to create AUTHORIZE for Follow Up Instruction"):
        FollowUpInstructionService(instruction=approval_instruction).acceptance_process(
            PaymentPlan.Action.AUTHORIZE.value, user
        )


def test_approve_without_an_approval_process_raises(
    user: Any, approval_instruction: FollowUpInstruction, in_approval_children: list[PaymentPlan]
) -> None:
    with pytest.raises(ValidationError, match="Approval Process object not found for Follow Up Instruction"):
        FollowUpInstructionService(instruction=approval_instruction).acceptance_process(
            PaymentPlan.Action.APPROVE.value, user
        )


def test_abort_stores_the_comment_on_the_instruction(
    user: Any, approval_instruction: FollowUpInstruction, in_approval_children: list[PaymentPlan]
) -> None:
    FollowUpInstructionService(instruction=approval_instruction).abort(user=user, abort_comment="wrong list")

    approval_instruction.refresh_from_db()
    assert approval_instruction.abort_comment == "wrong list"


@pytest.fixture
def finished_children(approval_instruction, cycle, business_area, currency) -> list[PaymentPlan]:
    return [
        PaymentPlanFactory(
            program_cycle=cycle,
            business_area=business_area,
            currency=currency,
            follow_up_instruction=approval_instruction,
            plan_type=PaymentPlan.PlanType.FOLLOW_UP,
            status=PaymentPlan.Status.FINISHED,
        )
        for _ in range(2)
    ]


def test_close_stores_the_comment_and_user_on_the_instruction_and_its_children(
    user: Any, approval_instruction: FollowUpInstruction, finished_children: list[PaymentPlan]
) -> None:
    FollowUpInstructionService(instruction=approval_instruction).close(user=user, closure_comment="paid out")

    approval_instruction.refresh_from_db()
    assert approval_instruction.closure_comment == "paid out"
    assert approval_instruction.closed_by == user
    assert set(approval_instruction.payment_plans.values_list("closure_comment", flat=True)) == {"paid out"}


def test_close_without_a_comment_raises_when_nothing_was_verified(
    user: Any, approval_instruction: FollowUpInstruction, finished_children: list[PaymentPlan]
) -> None:
    with pytest.raises(ValidationError, match="Closure comment is required"):
        FollowUpInstructionService(instruction=approval_instruction).close(user=user, closure_comment=None)
