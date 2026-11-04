import datetime as dt
import importlib
from typing import Any

from django.apps.registry import Apps
from django.db import connection
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.db.migrations.loader import MigrationLoader
import pytest

from extras.test_utils.factories import PaymentListFactory, PaymentPlanFactory, ProgramCycleFactory
from extras.test_utils.factories.payment import FollowUpInstructionFactory
from hope.models import FollowUpInstruction, PaymentList, PaymentPlan

pytestmark = pytest.mark.django_db

migration_module = importlib.import_module("hope.apps.payment.migrations.0084_migration")


@pytest.fixture
def schema_editor() -> BaseDatabaseSchemaEditor:
    return connection.schema_editor()


@pytest.fixture
def historical_apps(settings: Any) -> Apps:
    """The models the data step runs with: 0083 adds the owner fields, the plan columns are dropped only in 0085."""
    settings.MIGRATION_MODULES = {}
    state = MigrationLoader(connection).project_state(("payment", "0083_migration"))
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
def group(cycle: Any) -> PaymentPlan:
    return PaymentPlanFactory(cycle=cycle, dispersion_start_date=None, dispersion_end_date=None)


@pytest.fixture
def instruction(cycle: Any) -> FollowUpInstruction:
    return FollowUpInstructionFactory(program=cycle.program, dispersion_start_date=None, dispersion_end_date=None)


@pytest.fixture
def january_plan(historical_apps: Apps, cycle: Any, group: PaymentPlan) -> PaymentList:
    payment_list = PaymentListFactory(program_cycle=cycle, payment_plan=group)
    with connection.cursor() as cursor:
        cursor.execute(
            'UPDATE "payment_paymentplan" SET "dispersion_start_date" = %s, "dispersion_end_date" = %s WHERE "id" = %s',
            [dt.date(2026, 1, 1), dt.date(2026, 1, 31), payment_list.pk],
        )
    return payment_list


@pytest.fixture
def march_plan(historical_apps: Apps, cycle: Any, group: PaymentPlan) -> PaymentList:
    payment_list = PaymentListFactory(program_cycle=cycle, payment_plan=group)
    with connection.cursor() as cursor:
        cursor.execute(
            'UPDATE "payment_paymentplan" SET "dispersion_start_date" = %s, "dispersion_end_date" = %s WHERE "id" = %s',
            [dt.date(2026, 3, 1), dt.date(2026, 3, 31), payment_list.pk],
        )
    return payment_list


@pytest.fixture
def instruction_child(historical_apps: Apps, cycle: Any, instruction: FollowUpInstruction) -> PaymentList:
    payment_list = PaymentListFactory(
        program_cycle=cycle, follow_up_instruction=instruction, plan_type=PaymentList.PlanType.FOLLOW_UP
    )
    with connection.cursor() as cursor:
        cursor.execute(
            'UPDATE "payment_paymentplan" SET "dispersion_start_date" = %s, "dispersion_end_date" = %s WHERE "id" = %s',
            [dt.date(2026, 5, 1), dt.date(2026, 5, 31), payment_list.pk],
        )
    return payment_list


def test_group_takes_the_widest_dispersion_window_of_its_plans(
    historical_apps: Apps,
    schema_editor: BaseDatabaseSchemaEditor,
    group: PaymentPlan,
    january_plan: PaymentList,
    march_plan: PaymentList,
) -> None:
    migration_module.copy_dates_from_payment_plans(historical_apps, schema_editor)

    group.refresh_from_db()
    assert group.dispersion_start_date == dt.date(2026, 1, 1)
    assert group.dispersion_end_date == dt.date(2026, 3, 31)


def test_instruction_takes_the_dispersion_dates_of_its_plans(
    historical_apps: Apps,
    schema_editor: BaseDatabaseSchemaEditor,
    instruction: FollowUpInstruction,
    instruction_child: PaymentList,
) -> None:
    migration_module.copy_dates_from_payment_plans(historical_apps, schema_editor)

    instruction.refresh_from_db()
    assert instruction.dispersion_start_date == dt.date(2026, 5, 1)
    assert instruction.dispersion_end_date == dt.date(2026, 5, 31)


def test_removed_plan_does_not_count_towards_the_group_dispersion_window(
    historical_apps: Apps,
    schema_editor: BaseDatabaseSchemaEditor,
    group: PaymentPlan,
    january_plan: PaymentList,
    march_plan: PaymentList,
) -> None:
    PaymentList.all_objects.filter(pk=march_plan.pk).update(is_removed=True)

    migration_module.copy_dates_from_payment_plans(historical_apps, schema_editor)

    group.refresh_from_db()
    assert group.dispersion_start_date == dt.date(2026, 1, 1)
    assert group.dispersion_end_date == dt.date(2026, 1, 31)


def test_group_without_plans_keeps_no_dispersion_dates(
    historical_apps: Apps, schema_editor: BaseDatabaseSchemaEditor, group: PaymentPlan
) -> None:
    migration_module.copy_dates_from_payment_plans(historical_apps, schema_editor)

    group.refresh_from_db()
    assert group.dispersion_start_date is None
    assert group.dispersion_end_date is None
