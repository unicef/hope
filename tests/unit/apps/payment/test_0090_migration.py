import datetime
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

migration_module = importlib.import_module("hope.apps.payment.migrations.0090_migration")


@pytest.fixture
def historical_apps(settings: Any) -> Apps:
    """The models the data step runs with: 0089 plus the four new fields, the plan columns not yet dropped."""
    settings.MIGRATION_MODULES = {}
    state = MigrationLoader(connection).project_state(("payment", "0089_migration"))
    for operation in migration_module.Migration.operations[:4]:
        operation.state_forwards("payment", state)
    with connection.cursor() as cursor:
        cursor.execute(
            'ALTER TABLE "payment_paymentplan" ADD COLUMN "dispersion_start_date" date NULL, '
            'ADD COLUMN "dispersion_end_date" date NULL'
        )
    return state.apps


@pytest.fixture
def cycle() -> Any:
    return ProgramCycleFactory()


@pytest.fixture
def group(cycle: Any) -> PaymentPlanGroup:
    return PaymentPlanGroupFactory(cycle=cycle, dispersion_start_date=None, dispersion_end_date=None)


@pytest.fixture
def instruction(cycle: Any) -> FollowUpInstruction:
    return FollowUpInstructionFactory(program=cycle.program, dispersion_start_date=None, dispersion_end_date=None)


@pytest.fixture
def january_plan(historical_apps: Apps, cycle: Any, group: PaymentPlanGroup) -> PaymentPlan:
    payment_plan = PaymentPlanFactory(program_cycle=cycle, payment_plan_group=group)
    with connection.cursor() as cursor:
        cursor.execute(
            'UPDATE "payment_paymentplan" SET "dispersion_start_date" = %s, "dispersion_end_date" = %s WHERE "id" = %s',
            [datetime.date(2026, 1, 1), datetime.date(2026, 1, 31), payment_plan.pk],
        )
    return payment_plan


@pytest.fixture
def march_plan(historical_apps: Apps, cycle: Any, group: PaymentPlanGroup) -> PaymentPlan:
    payment_plan = PaymentPlanFactory(program_cycle=cycle, payment_plan_group=group)
    with connection.cursor() as cursor:
        cursor.execute(
            'UPDATE "payment_paymentplan" SET "dispersion_start_date" = %s, "dispersion_end_date" = %s WHERE "id" = %s',
            [datetime.date(2026, 3, 1), datetime.date(2026, 3, 31), payment_plan.pk],
        )
    return payment_plan


@pytest.fixture
def instruction_child(historical_apps: Apps, cycle: Any, instruction: FollowUpInstruction) -> PaymentPlan:
    payment_plan = PaymentPlanFactory(
        program_cycle=cycle, follow_up_instruction=instruction, plan_type=PaymentPlan.PlanType.FOLLOW_UP
    )
    with connection.cursor() as cursor:
        cursor.execute(
            'UPDATE "payment_paymentplan" SET "dispersion_start_date" = %s, "dispersion_end_date" = %s WHERE "id" = %s',
            [datetime.date(2026, 5, 1), datetime.date(2026, 5, 31), payment_plan.pk],
        )
    return payment_plan


def test_group_takes_the_widest_dispersion_window_of_its_plans(
    historical_apps: Apps, group: PaymentPlanGroup, january_plan: PaymentPlan, march_plan: PaymentPlan
) -> None:
    migration_module.copy_dates_from_payment_plans(historical_apps, schema_editor=None)

    group.refresh_from_db()
    assert group.dispersion_start_date == datetime.date(2026, 1, 1)
    assert group.dispersion_end_date == datetime.date(2026, 3, 31)


def test_instruction_takes_the_dispersion_dates_of_its_plans(
    historical_apps: Apps, instruction: FollowUpInstruction, instruction_child: PaymentPlan
) -> None:
    migration_module.copy_dates_from_payment_plans(historical_apps, schema_editor=None)

    instruction.refresh_from_db()
    assert instruction.dispersion_start_date == datetime.date(2026, 5, 1)
    assert instruction.dispersion_end_date == datetime.date(2026, 5, 31)


def test_removed_plan_does_not_count_towards_the_group_dispersion_window(
    historical_apps: Apps, group: PaymentPlanGroup, january_plan: PaymentPlan, march_plan: PaymentPlan
) -> None:
    PaymentPlan.all_objects.filter(pk=march_plan.pk).update(is_removed=True)

    migration_module.copy_dates_from_payment_plans(historical_apps, schema_editor=None)

    group.refresh_from_db()
    assert group.dispersion_start_date == datetime.date(2026, 1, 1)
    assert group.dispersion_end_date == datetime.date(2026, 1, 31)


def test_group_without_plans_keeps_no_dispersion_dates(historical_apps: Apps, group: PaymentPlanGroup) -> None:
    migration_module.copy_dates_from_payment_plans(historical_apps, schema_editor=None)

    group.refresh_from_db()
    assert group.dispersion_start_date is None
    assert group.dispersion_end_date is None
