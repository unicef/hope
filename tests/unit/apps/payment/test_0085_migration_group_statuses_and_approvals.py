from datetime import timedelta
from decimal import Decimal
import importlib
from types import SimpleNamespace
from typing import Any

from django.apps.registry import Apps
from django.db import connection
from django.db.backends.postgresql.psycopg_any import NumericRange
from django.db.migrations.loader import MigrationLoader
from django.utils import timezone
import pytest

from extras.test_utils.factories import (
    ApprovalProcessFactory,
    PaymentListFactory,
    PaymentPlanFactory,
    ProgramCycleFactory,
)
from extras.test_utils.factories.core import CurrencyFactory
from extras.test_utils.factories.payment import FinancialServiceProviderFactory, FollowUpInstructionFactory
from hope.models import AcceptanceProcessThreshold, ApprovalProcess, PaymentList, PaymentPlan

pytestmark = pytest.mark.django_db

migration_module = importlib.import_module("hope.apps.payment.migrations.0085_migration")


@pytest.fixture
def historical_apps(settings: Any) -> SimpleNamespace:
    """The models just before the payment list rename, under the names 0085 uses for them."""
    settings.MIGRATION_MODULES = {}
    apps = MigrationLoader(connection).project_state(("payment", "0087_migration")).apps
    names_in_0085 = {"PaymentPlan": "PaymentList", "PaymentPlanGroup": "PaymentPlan"}
    return SimpleNamespace(
        get_model=lambda app_label, model_name: apps.get_model(app_label, names_in_0085.get(model_name, model_name))
    )


@pytest.fixture
def historical_apps_with_plan_columns(settings: Any) -> Apps:
    """The models as they are when 0085 runs, with the old plan columns it reads put back on the test table.

    The test database has the final schema, where 0086 has already dropped FSP, currency, payment gateway flag and
    exchange rate from the plan.
    """
    settings.MIGRATION_MODULES = {}
    state = MigrationLoader(connection).project_state(("payment", "0084_migration"))
    with connection.cursor() as cursor:
        cursor.execute(
            'ALTER TABLE "payment_paymentplan" ADD COLUMN "financial_service_provider_id" uuid NULL, '
            'ADD COLUMN "currency_id" bigint NULL, ADD COLUMN "use_payment_gateway" boolean NOT NULL DEFAULT false, '
            'ADD COLUMN "exchange_rate" numeric(15, 8) NULL, '
            'ADD COLUMN "custom_exchange_rate" boolean NOT NULL DEFAULT false, '
            'ADD COLUMN "custom_exchange_rate_set_by_id" uuid NULL'
        )
    return state.apps


@pytest.fixture
def cycle() -> Any:
    return ProgramCycleFactory()


@pytest.fixture
def group(cycle: Any) -> PaymentPlan:
    return PaymentPlanFactory(
        cycle=cycle,
        name="Main Group",
        currency=CurrencyFactory(code="EUR", name="Euro"),
        financial_service_provider=FinancialServiceProviderFactory(),
    )


@pytest.fixture
def accepted_plans(cycle: Any, group: PaymentPlan) -> list[PaymentList]:
    first = PaymentListFactory(program_cycle=cycle, payment_plan=group, status=PaymentList.Status.ACCEPTED)
    second = PaymentListFactory(program_cycle=cycle, payment_plan=group, status=PaymentList.Status.ACCEPTED)
    PaymentList.objects.filter(pk=second.pk).update(status_date=first.status_date + timedelta(days=1))
    return [first, second]


def test_group_takes_accepted_status_and_latest_status_date_from_its_plans(
    historical_apps: SimpleNamespace, group: PaymentPlan, accepted_plans: list[PaymentList]
) -> None:
    migration_module.set_group_statuses_from_plans(historical_apps, schema_editor=None)

    group.refresh_from_db()
    assert group.status == PaymentPlan.Status.ACCEPTED
    assert group.status_date == accepted_plans[0].status_date + timedelta(days=1)


def test_group_with_locked_fsp_plans_becomes_locked(
    historical_apps: SimpleNamespace, cycle: Any, group: PaymentPlan
) -> None:
    PaymentListFactory(program_cycle=cycle, payment_plan=group, status=PaymentList.Status.LOCKED_FSP)

    migration_module.set_group_statuses_from_plans(historical_apps, schema_editor=None)

    group.refresh_from_db()
    assert group.status == PaymentPlan.Status.LOCKED


def test_group_with_plans_before_fsp_lock_stays_open(
    historical_apps: SimpleNamespace, cycle: Any, group: PaymentPlan
) -> None:
    PaymentListFactory(program_cycle=cycle, payment_plan=group, status=PaymentList.Status.TP_OPEN)
    PaymentListFactory(program_cycle=cycle, payment_plan=group, status=PaymentList.Status.LOCKED)

    migration_module.set_group_statuses_from_plans(historical_apps, schema_editor=None)

    group.refresh_from_db()
    assert group.status == PaymentPlan.Status.OPEN


def test_empty_group_stays_open(historical_apps: SimpleNamespace, group: PaymentPlan) -> None:
    migration_module.set_group_statuses_from_plans(historical_apps, schema_editor=None)

    group.refresh_from_db()
    assert group.status == PaymentPlan.Status.OPEN


def test_group_with_mixed_plan_statuses_is_refused_by_name(
    historical_apps: SimpleNamespace, cycle: Any, group: PaymentPlan
) -> None:
    PaymentListFactory(program_cycle=cycle, payment_plan=group, status=PaymentList.Status.ACCEPTED)
    PaymentListFactory(program_cycle=cycle, payment_plan=group, status=PaymentList.Status.OPEN)

    with pytest.raises(RuntimeError, match=f"must be aligned before this migration can run: {group.unicef_id}"):
        migration_module.set_group_statuses_from_plans(historical_apps, schema_editor=None)


@pytest.fixture
def plan_level_approval_process(accepted_plans: list[PaymentList]) -> ApprovalProcess:
    return ApprovalProcessFactory(payment_list=accepted_plans[0], approval_number_required=3)


def test_plan_approval_process_moves_to_the_group(
    historical_apps: SimpleNamespace, group: PaymentPlan, plan_level_approval_process: ApprovalProcess
) -> None:
    migration_module.move_approval_processes_to_groups(historical_apps, schema_editor=None)

    plan_level_approval_process.refresh_from_db()
    assert plan_level_approval_process.payment_plan == group
    assert plan_level_approval_process.payment_list is None


def test_finished_approval_process_keeps_its_required_numbers(
    historical_apps: SimpleNamespace, group: PaymentPlan, plan_level_approval_process: ApprovalProcess
) -> None:
    group.status = PaymentPlan.Status.ACCEPTED
    group.save(update_fields=["status"])

    migration_module.move_approval_processes_to_groups(historical_apps, schema_editor=None)

    plan_level_approval_process.refresh_from_db()
    assert plan_level_approval_process.approval_number_required == 3


@pytest.fixture
def threshold_for_large_amounts(group: PaymentPlan) -> AcceptanceProcessThreshold:
    return AcceptanceProcessThreshold.objects.create(
        business_area=group.business_area,
        payments_range_usd=NumericRange(150, None),
        approval_number_required=2,
        authorization_number_required=2,
        finance_release_number_required=2,
    )


def test_newest_open_approval_process_is_sized_from_the_group_total(
    historical_apps: SimpleNamespace,
    cycle: Any,
    group: PaymentPlan,
    accepted_plans: list[PaymentList],
    threshold_for_large_amounts: AcceptanceProcessThreshold,
) -> None:
    group.status = PaymentPlan.Status.IN_APPROVAL
    group.save(update_fields=["status"])
    PaymentList.objects.filter(pk__in=[plan.pk for plan in accepted_plans]).update(
        total_entitled_quantity_usd=Decimal("100.00")
    )
    older_process = ApprovalProcessFactory(payment_list=accepted_plans[0], approval_number_required=1)
    newest_process = ApprovalProcessFactory(payment_list=accepted_plans[1], approval_number_required=1)
    ApprovalProcess.objects.filter(pk=newest_process.pk).update(created_at=timezone.now() + timedelta(minutes=1))

    migration_module.move_approval_processes_to_groups(historical_apps, schema_editor=None)

    older_process.refresh_from_db()
    newest_process.refresh_from_db()
    assert newest_process.payment_plan == group
    assert newest_process.approval_number_required == 2
    assert newest_process.finance_release_number_required == 2
    assert older_process.payment_plan == group
    assert older_process.approval_number_required == 1


def test_instruction_child_approval_process_is_untouched(historical_apps: SimpleNamespace, cycle: Any) -> None:
    instruction_child = PaymentListFactory(
        program_cycle=cycle,
        follow_up_instruction=FollowUpInstructionFactory(program=cycle.program),
        plan_type=PaymentList.PlanType.FOLLOW_UP,
    )
    process = ApprovalProcessFactory(payment_list=instruction_child)

    migration_module.move_approval_processes_to_groups(historical_apps, schema_editor=None)

    process.refresh_from_db()
    assert process.payment_list == instruction_child
    assert process.payment_plan is None


@pytest.fixture
def source_plan(cycle: Any, group: PaymentPlan) -> PaymentList:
    return PaymentListFactory(
        name="Source Plan", program_cycle=cycle, payment_plan=group, status=PaymentList.Status.FINISHED
    )


@pytest.fixture
def legacy_children(cycle: Any, group: PaymentPlan, source_plan: PaymentList) -> dict[str, PaymentList]:
    return {
        "follow_up_one": PaymentListFactory(
            program_cycle=cycle,
            payment_plan=group,
            source_payment_list=source_plan,
            plan_type=PaymentList.PlanType.FOLLOW_UP,
            status=PaymentList.Status.ACCEPTED,
        ),
        "follow_up_two": PaymentListFactory(
            program_cycle=cycle,
            payment_plan=group,
            source_payment_list=source_plan,
            plan_type=PaymentList.PlanType.FOLLOW_UP,
            status=PaymentList.Status.ACCEPTED,
        ),
        "top_up": PaymentListFactory(
            program_cycle=cycle,
            payment_plan=group,
            source_payment_list=source_plan,
            plan_type=PaymentList.PlanType.TOP_UP,
            status=PaymentList.Status.OPEN,
        ),
    }


def test_legacy_children_move_to_one_linked_group_per_type_and_status(
    historical_apps_with_plan_columns: Apps, group: PaymentPlan, legacy_children: dict[str, PaymentList]
) -> None:
    migration_module.move_legacy_child_plans_into_linked_groups(historical_apps_with_plan_columns, schema_editor=None)

    follow_up_group = group.linked_payment_plans.get(plan_type=PaymentList.PlanType.FOLLOW_UP)
    top_up_group = group.linked_payment_plans.get(plan_type=PaymentList.PlanType.TOP_UP)
    assert follow_up_group.name == "Main Group Follow Up 1"
    assert follow_up_group.status == PaymentPlan.Status.ACCEPTED
    assert set(follow_up_group.payment_lists.all()) == {
        legacy_children["follow_up_one"],
        legacy_children["follow_up_two"],
    }
    assert top_up_group.name == "Main Group Top Up 1"
    assert top_up_group.status == PaymentPlan.Status.OPEN
    assert list(top_up_group.payment_lists.all()) == [legacy_children["top_up"]]


def test_linked_group_takes_cycle_currency_and_fsp_from_the_source_group(
    historical_apps_with_plan_columns: Apps, group: PaymentPlan, legacy_children: dict[str, PaymentList]
) -> None:
    migration_module.move_legacy_child_plans_into_linked_groups(historical_apps_with_plan_columns, schema_editor=None)

    follow_up_group = group.linked_payment_plans.get(plan_type=PaymentList.PlanType.FOLLOW_UP)
    assert follow_up_group.cycle == group.cycle
    assert follow_up_group.currency == group.currency
    assert follow_up_group.financial_service_provider == group.financial_service_provider
    assert follow_up_group.source_payment_plan == group


def test_source_plan_stays_in_its_group(
    historical_apps_with_plan_columns: Apps,
    group: PaymentPlan,
    source_plan: PaymentList,
    legacy_children: dict[str, PaymentList],
) -> None:
    migration_module.move_legacy_child_plans_into_linked_groups(historical_apps_with_plan_columns, schema_editor=None)

    assert list(group.payment_lists.all()) == [source_plan]


def test_legacy_follow_ups_in_different_statuses_are_split_into_separate_linked_groups(
    historical_apps_with_plan_columns: Apps,
    cycle: Any,
    group: PaymentPlan,
    source_plan: PaymentList,
    legacy_children: dict[str, PaymentList],
) -> None:
    PaymentListFactory(
        program_cycle=cycle,
        payment_plan=group,
        source_payment_list=source_plan,
        plan_type=PaymentList.PlanType.FOLLOW_UP,
        status=PaymentList.Status.FINISHED,
    )

    migration_module.move_legacy_child_plans_into_linked_groups(historical_apps_with_plan_columns, schema_editor=None)

    names = sorted(
        group.linked_payment_plans.filter(plan_type=PaymentList.PlanType.FOLLOW_UP).values_list("name", flat=True)
    )
    assert names == ["Main Group Follow Up 1", "Main Group Follow Up 2"]


def test_instruction_child_gets_no_linked_group(historical_apps_with_plan_columns: Apps, cycle: Any) -> None:
    instruction_child = PaymentListFactory(
        program_cycle=cycle,
        follow_up_instruction=FollowUpInstructionFactory(program=cycle.program),
        plan_type=PaymentList.PlanType.FOLLOW_UP,
    )

    migration_module.move_legacy_child_plans_into_linked_groups(historical_apps_with_plan_columns, schema_editor=None)

    instruction_child.refresh_from_db()
    assert instruction_child.payment_plan_id is None
    assert PaymentPlan.objects.filter(plan_type=PaymentList.PlanType.FOLLOW_UP).count() == 0


@pytest.fixture
def follow_ups_with_different_rates(
    historical_apps_with_plan_columns: Apps, legacy_children: dict[str, PaymentList]
) -> dict[str, PaymentList]:
    with connection.cursor() as cursor:
        cursor.execute(
            'UPDATE "payment_paymentplan" SET "exchange_rate" = %s WHERE "id" = %s',
            [Decimal("1.5"), legacy_children["follow_up_one"].pk],
        )
        cursor.execute(
            'UPDATE "payment_paymentplan" SET "exchange_rate" = %s WHERE "id" = %s',
            [Decimal("1.6"), legacy_children["follow_up_two"].pk],
        )
    return legacy_children


def test_legacy_follow_ups_with_different_exchange_rates_get_separate_linked_groups(
    historical_apps_with_plan_columns: Apps,
    group: PaymentPlan,
    follow_ups_with_different_rates: dict[str, PaymentList],
) -> None:
    migration_module.move_legacy_child_plans_into_linked_groups(historical_apps_with_plan_columns, schema_editor=None)

    follow_up_groups = group.linked_payment_plans.filter(plan_type=PaymentList.PlanType.FOLLOW_UP).order_by("name")
    assert [list(follow_up_group.payment_lists.all()) for follow_up_group in follow_up_groups] == [
        [follow_ups_with_different_rates["follow_up_one"]],
        [follow_ups_with_different_rates["follow_up_two"]],
    ]


def test_linked_groups_of_follow_ups_with_different_exchange_rates_each_take_their_rate(
    historical_apps_with_plan_columns: Apps,
    group: PaymentPlan,
    follow_ups_with_different_rates: dict[str, PaymentList],
) -> None:
    migration_module.move_legacy_child_plans_into_linked_groups(historical_apps_with_plan_columns, schema_editor=None)

    migration_module.copy_exchange_rates_from_payment_plans(
        historical_apps_with_plan_columns, schema_editor=connection.schema_editor()
    )

    rates = group.linked_payment_plans.filter(plan_type=PaymentList.PlanType.FOLLOW_UP).order_by("name")
    assert list(rates.values_list("exchange_rate", flat=True)) == [Decimal("1.5"), Decimal("1.6")]


@pytest.fixture
def follow_ups_one_without_a_rate(
    historical_apps_with_plan_columns: Apps, legacy_children: dict[str, PaymentList]
) -> dict[str, PaymentList]:
    with connection.cursor() as cursor:
        cursor.execute(
            'UPDATE "payment_paymentplan" SET "exchange_rate" = %s WHERE "id" = %s',
            [Decimal("1.5"), legacy_children["follow_up_one"].pk],
        )
    return legacy_children


def test_legacy_follow_up_without_an_exchange_rate_joins_the_one_with_a_rate(
    historical_apps_with_plan_columns: Apps,
    group: PaymentPlan,
    follow_ups_one_without_a_rate: dict[str, PaymentList],
) -> None:
    migration_module.move_legacy_child_plans_into_linked_groups(historical_apps_with_plan_columns, schema_editor=None)

    follow_up_group = group.linked_payment_plans.get(plan_type=PaymentList.PlanType.FOLLOW_UP)
    assert set(follow_up_group.payment_lists.all()) == {
        follow_ups_one_without_a_rate["follow_up_one"],
        follow_ups_one_without_a_rate["follow_up_two"],
    }
