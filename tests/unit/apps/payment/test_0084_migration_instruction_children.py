import importlib
from types import SimpleNamespace
from typing import Any

from django.db import connection
from django.db.migrations.loader import MigrationLoader
import pytest

from extras.test_utils.factories import PaymentListFactory, PaymentPlanFactory, ProgramCycleFactory
from extras.test_utils.factories.core import CurrencyFactory
from extras.test_utils.factories.payment import FinancialServiceProviderFactory, FollowUpInstructionFactory
from hope.models import FollowUpInstruction, PaymentList, PaymentPlan

pytestmark = pytest.mark.django_db

migration_module = importlib.import_module("hope.apps.payment.migrations.0084_migration")


@pytest.fixture
def historical_apps(settings: Any) -> SimpleNamespace:
    """The models just before the payment list rename, under the names 0084 uses for them."""
    settings.MIGRATION_MODULES = {}
    apps = MigrationLoader(connection).project_state(("payment", "0086_migration")).apps
    names_in_0084 = {"PaymentPlan": "PaymentList", "PaymentPlanGroup": "PaymentPlan"}
    return SimpleNamespace(
        get_model=lambda app_label, model_name: apps.get_model(app_label, names_in_0084.get(model_name, model_name))
    )


@pytest.fixture
def without_plan_owner_constraint() -> None:
    """The state the data step runs in: 0083 drops the old constraint and 0085 adds the new one."""
    with connection.cursor() as cursor:
        cursor.execute(
            'ALTER TABLE "payment_paymentplan" DROP CONSTRAINT "payment_plan_in_group_or_instruction_unless_removed"'
        )


@pytest.fixture
def source_payment_plan(without_plan_owner_constraint: None) -> PaymentPlan:
    return PaymentPlanFactory(
        cycle=ProgramCycleFactory(),
        currency=CurrencyFactory(code="EUR", name="Euro"),
        financial_service_provider=FinancialServiceProviderFactory(),
    )


@pytest.fixture
def source_payment_list(source_payment_plan: PaymentPlan) -> PaymentList:
    return PaymentListFactory(program_cycle=source_payment_plan.cycle, payment_plan=source_payment_plan)


@pytest.fixture
def instruction(source_payment_plan: PaymentPlan) -> FollowUpInstruction:
    return FollowUpInstructionFactory(program=source_payment_plan.cycle.program)


@pytest.fixture
def instruction_child_in_source_group(
    source_payment_plan: PaymentPlan, source_payment_list: PaymentList, instruction: FollowUpInstruction
) -> PaymentList:
    child_plan = PaymentListFactory(
        program_cycle=source_payment_plan.cycle,
        follow_up_instruction=instruction,
        source_payment_list=source_payment_list,
        plan_type=PaymentList.PlanType.FOLLOW_UP,
    )
    PaymentList.objects.filter(pk=child_plan.pk).update(payment_plan=source_payment_plan)
    return child_plan


@pytest.fixture
def instruction_child_outside_group(
    source_payment_plan: PaymentPlan, source_payment_list: PaymentList, instruction: FollowUpInstruction
) -> PaymentList:
    return PaymentListFactory(
        program_cycle=source_payment_plan.cycle,
        follow_up_instruction=instruction,
        source_payment_list=source_payment_list,
        plan_type=PaymentList.PlanType.FOLLOW_UP,
    )


def test_migration_gives_instruction_the_fsp_and_currency_of_its_childs_group(
    historical_apps: SimpleNamespace,
    instruction_child_in_source_group: PaymentList,
    instruction: FollowUpInstruction,
    source_payment_plan: PaymentPlan,
) -> None:
    migration_module.move_instruction_children_out_of_groups(historical_apps, schema_editor=None)

    instruction.refresh_from_db()
    assert instruction.financial_service_provider == source_payment_plan.financial_service_provider
    assert instruction.currency == source_payment_plan.currency


def test_migration_takes_instruction_child_out_of_its_group(
    historical_apps: SimpleNamespace,
    instruction_child_in_source_group: PaymentList,
) -> None:
    migration_module.move_instruction_children_out_of_groups(historical_apps, schema_editor=None)

    instruction_child_in_source_group.refresh_from_db()
    assert instruction_child_in_source_group.payment_plan_id is None


def test_migration_leaves_plan_of_the_group_in_it(
    historical_apps: SimpleNamespace,
    instruction_child_in_source_group: PaymentList,
    source_payment_list: PaymentList,
    source_payment_plan: PaymentPlan,
) -> None:
    migration_module.move_instruction_children_out_of_groups(historical_apps, schema_editor=None)

    source_payment_list.refresh_from_db()
    assert source_payment_list.payment_plan == source_payment_plan


def test_reverse_migration_returns_instruction_child_to_its_source_plans_group(
    historical_apps: SimpleNamespace, instruction_child_outside_group: PaymentList, source_payment_plan: PaymentPlan
) -> None:
    with connection.cursor() as cursor:
        migration_module.put_instruction_children_back_into_groups(historical_apps, schema_editor=cursor)

    instruction_child_outside_group.refresh_from_db()
    assert instruction_child_outside_group.payment_plan == source_payment_plan
