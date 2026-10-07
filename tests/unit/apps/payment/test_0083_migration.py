import importlib
from types import SimpleNamespace

from django.db import connection
import pytest

from extras.test_utils.factories import PaymentPlanFactory, PaymentPlanGroupFactory, ProgramCycleFactory
from extras.test_utils.factories.core import CurrencyFactory
from extras.test_utils.factories.payment import FinancialServiceProviderFactory, FollowUpInstructionFactory
from hope.models import FollowUpInstruction, PaymentPlan, PaymentPlanGroup

pytestmark = pytest.mark.django_db

migration_module = importlib.import_module("hope.apps.payment.migrations.0083_migration")


def build_apps() -> SimpleNamespace:
    return SimpleNamespace(
        get_model=lambda app_label, model_name: {
            ("payment", "FollowUpInstruction"): FollowUpInstruction,
            ("payment", "PaymentPlan"): PaymentPlan,
        }[(app_label, model_name)]
    )


@pytest.fixture
def without_plan_owner_constraint() -> None:
    """The state the data step runs in: 0083 drops the old constraint before it and adds the new one after."""
    with connection.cursor() as cursor:
        cursor.execute(
            'ALTER TABLE "payment_paymentplan" DROP CONSTRAINT "payment_plan_in_group_or_instruction_unless_removed"'
        )


@pytest.fixture
def source_group(without_plan_owner_constraint: None) -> PaymentPlanGroup:
    return PaymentPlanGroupFactory(
        cycle=ProgramCycleFactory(),
        currency=CurrencyFactory(code="EUR", name="Euro"),
        financial_service_provider=FinancialServiceProviderFactory(),
    )


@pytest.fixture
def source_payment_plan(source_group: PaymentPlanGroup) -> PaymentPlan:
    return PaymentPlanFactory(program_cycle=source_group.cycle, payment_plan_group=source_group)


@pytest.fixture
def instruction(source_group: PaymentPlanGroup) -> FollowUpInstruction:
    return FollowUpInstructionFactory(program=source_group.cycle.program)


@pytest.fixture
def instruction_child_in_source_group(
    source_group: PaymentPlanGroup, source_payment_plan: PaymentPlan, instruction: FollowUpInstruction
) -> PaymentPlan:
    child_plan = PaymentPlanFactory(
        program_cycle=source_group.cycle,
        follow_up_instruction=instruction,
        source_payment_plan=source_payment_plan,
        plan_type=PaymentPlan.PlanType.FOLLOW_UP,
    )
    PaymentPlan.objects.filter(pk=child_plan.pk).update(payment_plan_group=source_group)
    return child_plan


@pytest.fixture
def instruction_child_outside_group(
    source_group: PaymentPlanGroup, source_payment_plan: PaymentPlan, instruction: FollowUpInstruction
) -> PaymentPlan:
    return PaymentPlanFactory(
        program_cycle=source_group.cycle,
        follow_up_instruction=instruction,
        source_payment_plan=source_payment_plan,
        plan_type=PaymentPlan.PlanType.FOLLOW_UP,
    )


def test_migration_gives_instruction_the_fsp_and_currency_of_its_childs_group(
    instruction_child_in_source_group: PaymentPlan, instruction: FollowUpInstruction, source_group: PaymentPlanGroup
) -> None:
    migration_module.move_instruction_children_out_of_groups(build_apps(), schema_editor=None)

    instruction.refresh_from_db()
    assert instruction.financial_service_provider == source_group.financial_service_provider
    assert instruction.currency == source_group.currency


def test_migration_takes_instruction_child_out_of_its_group(instruction_child_in_source_group: PaymentPlan) -> None:
    migration_module.move_instruction_children_out_of_groups(build_apps(), schema_editor=None)

    instruction_child_in_source_group.refresh_from_db()
    assert instruction_child_in_source_group.payment_plan_group_id is None


def test_migration_leaves_plan_of_the_group_in_it(
    instruction_child_in_source_group: PaymentPlan, source_payment_plan: PaymentPlan, source_group: PaymentPlanGroup
) -> None:
    migration_module.move_instruction_children_out_of_groups(build_apps(), schema_editor=None)

    source_payment_plan.refresh_from_db()
    assert source_payment_plan.payment_plan_group == source_group


def test_reverse_migration_returns_instruction_child_to_its_source_plans_group(
    instruction_child_outside_group: PaymentPlan, source_group: PaymentPlanGroup
) -> None:
    with connection.cursor() as cursor:
        migration_module.put_instruction_children_back_into_groups(build_apps(), schema_editor=cursor)

    instruction_child_outside_group.refresh_from_db()
    assert instruction_child_outside_group.payment_plan_group == source_group
