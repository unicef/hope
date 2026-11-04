import datetime as dt
from decimal import Decimal
import importlib
from typing import Any

from django.apps.registry import Apps
from django.db import connection
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.db.migrations.loader import MigrationLoader
import pytest

from extras.test_utils.factories import PaymentListFactory, PaymentPlanFactory, ProgramCycleFactory, UserFactory
from extras.test_utils.factories.payment import FollowUpInstructionFactory
from hope.models import FollowUpInstruction, PaymentList, PaymentPlan, User

pytestmark = pytest.mark.django_db

migration_module = importlib.import_module("hope.apps.payment.migrations.0085_migration")


@pytest.fixture
def schema_editor() -> BaseDatabaseSchemaEditor:
    return connection.schema_editor()


@pytest.fixture
def historical_apps(settings: Any) -> Apps:
    """The models the data step runs with: 0084 adds the owner fields, the plan columns are dropped only in 0086."""
    settings.MIGRATION_MODULES = {}
    state = MigrationLoader(connection).project_state(("payment", "0084_migration"))
    with connection.cursor() as cursor:
        cursor.execute(
            'ALTER TABLE "payment_paymentplan" ADD COLUMN "dispersion_start_date" date NULL, '
            'ADD COLUMN "dispersion_end_date" date NULL, ADD COLUMN "exchange_rate" numeric(15, 8) NULL, '
            'ADD COLUMN "custom_exchange_rate" boolean NOT NULL DEFAULT false, '
            'ADD COLUMN "custom_exchange_rate_set_by_id" uuid NULL'
        )
    return state.apps


def set_rate(payment_list: PaymentList, status: str, exchange_rate: Decimal | None, set_by: User | None = None) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            'UPDATE "payment_paymentplan" SET "status" = %s, "exchange_rate" = %s, "custom_exchange_rate" = %s, '
            '"custom_exchange_rate_set_by_id" = %s WHERE "id" = %s',
            [status, exchange_rate, set_by is not None, set_by.pk if set_by else None, payment_list.pk],
        )


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


@pytest.fixture
def accepted_plan(historical_apps: Apps, cycle: Any, group: PaymentPlan) -> PaymentList:
    payment_list = PaymentListFactory(program_cycle=cycle, payment_plan=group)
    set_rate(payment_list, PaymentList.Status.ACCEPTED, Decimal("1.5"))
    return payment_list


@pytest.fixture
def tp_locked_plan_without_rate(historical_apps: Apps, cycle: Any, group: PaymentPlan) -> PaymentList:
    payment_list = PaymentListFactory(program_cycle=cycle, payment_plan=group)
    set_rate(payment_list, PaymentList.Status.TP_LOCKED, None)
    return payment_list


@pytest.fixture
def tp_open_plan_with_stale_rate(historical_apps: Apps, cycle: Any, group: PaymentPlan) -> PaymentList:
    payment_list = PaymentListFactory(program_cycle=cycle, payment_plan=group)
    set_rate(payment_list, PaymentList.Status.TP_OPEN, Decimal(9))
    return payment_list


@pytest.fixture
def open_plan_without_rate(historical_apps: Apps, cycle: Any, group: PaymentPlan) -> PaymentList:
    payment_list = PaymentListFactory(program_cycle=cycle, payment_plan=group)
    set_rate(payment_list, PaymentList.Status.OPEN, None)
    return payment_list


@pytest.fixture
def accepted_plan_with_other_rate(historical_apps: Apps, cycle: Any, group: PaymentPlan) -> PaymentList:
    payment_list = PaymentListFactory(program_cycle=cycle, payment_plan=group)
    set_rate(payment_list, PaymentList.Status.ACCEPTED, Decimal("1.6"))
    return payment_list


@pytest.fixture
def rate_setter() -> User:
    return UserFactory()


@pytest.fixture
def plan_with_custom_rate(historical_apps: Apps, cycle: Any, group: PaymentPlan, rate_setter: User) -> PaymentList:
    payment_list = PaymentListFactory(program_cycle=cycle, payment_plan=group)
    set_rate(payment_list, PaymentList.Status.IN_REVIEW, Decimal(2), rate_setter)
    return payment_list


def test_group_takes_the_rate_of_its_opened_plan_when_another_plan_is_not_opened_yet(
    historical_apps: Apps,
    schema_editor: BaseDatabaseSchemaEditor,
    group: PaymentPlan,
    accepted_plan: PaymentList,
    tp_locked_plan_without_rate: PaymentList,
) -> None:
    migration_module.copy_exchange_rates_from_payment_plans(historical_apps, schema_editor)

    group.refresh_from_db()
    assert group.exchange_rate == Decimal("1.5")


def test_stale_rate_of_a_plan_before_open_is_ignored(
    historical_apps: Apps,
    schema_editor: BaseDatabaseSchemaEditor,
    group: PaymentPlan,
    accepted_plan: PaymentList,
    tp_open_plan_with_stale_rate: PaymentList,
) -> None:
    migration_module.copy_exchange_rates_from_payment_plans(historical_apps, schema_editor)

    group.refresh_from_db()
    assert group.exchange_rate == Decimal("1.5")


def test_opened_plan_without_rate_does_not_stop_the_rate_copy(
    historical_apps: Apps,
    schema_editor: BaseDatabaseSchemaEditor,
    group: PaymentPlan,
    accepted_plan: PaymentList,
    open_plan_without_rate: PaymentList,
) -> None:
    migration_module.copy_exchange_rates_from_payment_plans(historical_apps, schema_editor)

    group.refresh_from_db()
    assert group.exchange_rate == Decimal("1.5")


def test_opened_plans_with_different_rates_stop_the_migration_naming_the_group(
    historical_apps: Apps,
    schema_editor: BaseDatabaseSchemaEditor,
    group: PaymentPlan,
    accepted_plan: PaymentList,
    accepted_plan_with_other_rate: PaymentList,
) -> None:
    with pytest.raises(RuntimeError, match=f"different exchange rates: \\['{group.unicef_id}'\\]"):
        migration_module.copy_exchange_rates_from_payment_plans(historical_apps, schema_editor)


def test_group_takes_the_custom_rate_flag_and_user_of_its_rated_plan(
    historical_apps: Apps,
    schema_editor: BaseDatabaseSchemaEditor,
    group: PaymentPlan,
    plan_with_custom_rate: PaymentList,
    rate_setter: User,
) -> None:
    migration_module.copy_exchange_rates_from_payment_plans(historical_apps, schema_editor)

    group.refresh_from_db()
    assert group.exchange_rate == Decimal(2)
    assert group.custom_exchange_rate is True
    assert group.custom_exchange_rate_set_by == rate_setter
