import importlib
from typing import Any

from django.apps.registry import Apps
from django.db import connection
from django.db.migrations.loader import MigrationLoader
import pytest

from extras.test_utils.factories import PaymentListFactory, PaymentPlanFactory, ProgramCycleFactory
from extras.test_utils.factories.payment import FollowUpInstructionFactory
from hope.models import FollowUpInstruction, PaymentList, PaymentPlan

pytestmark = pytest.mark.django_db

migration_module = importlib.import_module("hope.apps.payment.migrations.0084_migration")


@pytest.fixture
def historical_apps(settings: Any) -> Apps:
    """The models the data step runs with: 0083 adds the owner fields, the plan column is dropped only in 0085."""
    settings.MIGRATION_MODULES = {}
    state = MigrationLoader(connection).project_state(("payment", "0083_migration"))
    with connection.cursor() as cursor:
        cursor.execute(
            'ALTER TABLE "payment_paymentplan" ADD COLUMN "use_payment_gateway" boolean NOT NULL DEFAULT false'
        )
    return state.apps


@pytest.fixture
def cycle() -> Any:
    return ProgramCycleFactory()


@pytest.fixture
def group(cycle: Any) -> PaymentPlan:
    return PaymentPlanFactory(cycle=cycle)


@pytest.fixture
def gateway_plan(historical_apps: Apps, cycle: Any, group: PaymentPlan) -> PaymentList:
    payment_list = PaymentListFactory(program_cycle=cycle, payment_plan=group)
    with connection.cursor() as cursor:
        cursor.execute(
            'UPDATE "payment_paymentplan" SET "use_payment_gateway" = true WHERE "id" = %s', [payment_list.pk]
        )
    return payment_list


@pytest.fixture
def plan_without_gateway(historical_apps: Apps, cycle: Any, group: PaymentPlan) -> PaymentList:
    return PaymentListFactory(program_cycle=cycle, payment_plan=group)


@pytest.fixture
def instruction(cycle: Any) -> FollowUpInstruction:
    return FollowUpInstructionFactory(program=cycle.program)


@pytest.fixture
def gateway_instruction_child(historical_apps: Apps, cycle: Any, instruction: FollowUpInstruction) -> PaymentList:
    payment_list = PaymentListFactory(
        program_cycle=cycle, follow_up_instruction=instruction, plan_type=PaymentList.PlanType.FOLLOW_UP
    )
    with connection.cursor() as cursor:
        cursor.execute(
            'UPDATE "payment_paymentplan" SET "use_payment_gateway" = true WHERE "id" = %s', [payment_list.pk]
        )
    return payment_list


def test_group_takes_use_payment_gateway_from_its_plans(
    historical_apps: Apps, group: PaymentPlan, gateway_plan: PaymentList
) -> None:
    migration_module.copy_flag_from_payment_plans(historical_apps, schema_editor=None)

    group.refresh_from_db()
    assert group.use_payment_gateway is True


def test_instruction_takes_use_payment_gateway_from_its_plans(
    historical_apps: Apps, instruction: FollowUpInstruction, gateway_instruction_child: PaymentList
) -> None:
    migration_module.copy_flag_from_payment_plans(historical_apps, schema_editor=None)

    instruction.refresh_from_db()
    assert instruction.use_payment_gateway is True


def test_migration_refuses_group_whose_plans_disagree(
    historical_apps: Apps,
    group: PaymentPlan,
    gateway_plan: PaymentList,
    plan_without_gateway: PaymentList,
) -> None:
    with pytest.raises(RuntimeError, match=group.unicef_id):
        migration_module.copy_flag_from_payment_plans(historical_apps, schema_editor=None)


def test_removed_plan_does_not_count_towards_the_group_flag(
    historical_apps: Apps,
    group: PaymentPlan,
    gateway_plan: PaymentList,
    plan_without_gateway: PaymentList,
) -> None:
    PaymentList.all_objects.filter(pk=gateway_plan.pk).update(is_removed=True)

    migration_module.copy_flag_from_payment_plans(historical_apps, schema_editor=None)

    group.refresh_from_db()
    assert group.use_payment_gateway is False
