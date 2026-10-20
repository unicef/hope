import importlib
from typing import Any

from django.apps.registry import Apps
from django.db import connection
from django.db.migrations.loader import MigrationLoader
import pytest

from extras.test_utils.factories import PaymentPlanFactory, PaymentPlanGroupFactory, ProgramCycleFactory
from extras.test_utils.factories.payment import FollowUpInstructionFactory
from hope.models import FollowUpInstruction, PaymentPlan, PaymentPlanGroup

pytestmark = pytest.mark.django_db

migration_module = importlib.import_module("hope.apps.payment.migrations.0093_migration")


@pytest.fixture
def historical_apps(settings: Any) -> Apps:
    """The models the data step runs with: 0090 plus the two new fields, the plan column not yet dropped."""
    settings.MIGRATION_MODULES = {}
    state = MigrationLoader(connection).project_state(("payment", "0092_migration"))
    for operation in migration_module.Migration.operations[:2]:
        operation.state_forwards("payment", state)
    with connection.cursor() as cursor:
        cursor.execute(
            'ALTER TABLE "payment_paymentplan" ADD COLUMN "use_payment_gateway" boolean NOT NULL DEFAULT false'
        )
    return state.apps


@pytest.fixture
def cycle() -> Any:
    return ProgramCycleFactory()


@pytest.fixture
def group(cycle: Any) -> PaymentPlanGroup:
    return PaymentPlanGroupFactory(cycle=cycle)


@pytest.fixture
def gateway_plan(historical_apps: Apps, cycle: Any, group: PaymentPlanGroup) -> PaymentPlan:
    payment_plan = PaymentPlanFactory(program_cycle=cycle, payment_plan_group=group)
    with connection.cursor() as cursor:
        cursor.execute(
            'UPDATE "payment_paymentplan" SET "use_payment_gateway" = true WHERE "id" = %s', [payment_plan.pk]
        )
    return payment_plan


@pytest.fixture
def plan_without_gateway(historical_apps: Apps, cycle: Any, group: PaymentPlanGroup) -> PaymentPlan:
    return PaymentPlanFactory(program_cycle=cycle, payment_plan_group=group)


@pytest.fixture
def instruction(cycle: Any) -> FollowUpInstruction:
    return FollowUpInstructionFactory(program=cycle.program)


@pytest.fixture
def gateway_instruction_child(historical_apps: Apps, cycle: Any, instruction: FollowUpInstruction) -> PaymentPlan:
    payment_plan = PaymentPlanFactory(
        program_cycle=cycle, follow_up_instruction=instruction, plan_type=PaymentPlan.PlanType.FOLLOW_UP
    )
    with connection.cursor() as cursor:
        cursor.execute(
            'UPDATE "payment_paymentplan" SET "use_payment_gateway" = true WHERE "id" = %s', [payment_plan.pk]
        )
    return payment_plan


def test_group_takes_use_payment_gateway_from_its_plans(
    historical_apps: Apps, group: PaymentPlanGroup, gateway_plan: PaymentPlan
) -> None:
    migration_module.copy_flag_from_payment_plans(historical_apps, schema_editor=None)

    group.refresh_from_db()
    assert group.use_payment_gateway is True


def test_instruction_takes_use_payment_gateway_from_its_plans(
    historical_apps: Apps, instruction: FollowUpInstruction, gateway_instruction_child: PaymentPlan
) -> None:
    migration_module.copy_flag_from_payment_plans(historical_apps, schema_editor=None)

    instruction.refresh_from_db()
    assert instruction.use_payment_gateway is True


def test_migration_refuses_group_whose_plans_disagree(
    historical_apps: Apps, group: PaymentPlanGroup, gateway_plan: PaymentPlan, plan_without_gateway: PaymentPlan
) -> None:
    with pytest.raises(RuntimeError, match=group.unicef_id):
        migration_module.copy_flag_from_payment_plans(historical_apps, schema_editor=None)


def test_removed_plan_does_not_count_towards_the_group_flag(
    historical_apps: Apps, group: PaymentPlanGroup, gateway_plan: PaymentPlan, plan_without_gateway: PaymentPlan
) -> None:
    PaymentPlan.all_objects.filter(pk=gateway_plan.pk).update(is_removed=True)

    migration_module.copy_flag_from_payment_plans(historical_apps, schema_editor=None)

    group.refresh_from_db()
    assert group.use_payment_gateway is False
