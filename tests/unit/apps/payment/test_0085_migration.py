from datetime import timedelta
from decimal import Decimal
import importlib
from types import SimpleNamespace
from typing import Any

from django.db.backends.postgresql.psycopg_any import NumericRange
from django.utils import timezone
import pytest

from extras.test_utils.factories import (
    ApprovalProcessFactory,
    PaymentPlanFactory,
    PaymentPlanGroupFactory,
    ProgramCycleFactory,
)
from extras.test_utils.factories.core import CurrencyFactory
from extras.test_utils.factories.payment import FinancialServiceProviderFactory, FollowUpInstructionFactory
from hope.models import AcceptanceProcessThreshold, ApprovalProcess, PaymentPlan, PaymentPlanGroup

pytestmark = pytest.mark.django_db

migration_module = importlib.import_module("hope.apps.payment.migrations.0085_migration")


def build_apps() -> SimpleNamespace:
    return SimpleNamespace(
        get_model=lambda app_label, model_name: {
            ("payment", "PaymentPlan"): PaymentPlan,
            ("payment", "PaymentPlanGroup"): PaymentPlanGroup,
            ("payment", "ApprovalProcess"): ApprovalProcess,
            ("payment", "AcceptanceProcessThreshold"): AcceptanceProcessThreshold,
        }[(app_label, model_name)]
    )


@pytest.fixture
def cycle() -> Any:
    return ProgramCycleFactory()


@pytest.fixture
def group(cycle: Any) -> PaymentPlanGroup:
    return PaymentPlanGroupFactory(
        cycle=cycle,
        name="Main Group",
        currency=CurrencyFactory(code="EUR", name="Euro"),
        financial_service_provider=FinancialServiceProviderFactory(),
    )


@pytest.fixture
def accepted_plans(cycle: Any, group: PaymentPlanGroup) -> list[PaymentPlan]:
    first = PaymentPlanFactory(program_cycle=cycle, payment_plan_group=group, status=PaymentPlan.Status.ACCEPTED)
    second = PaymentPlanFactory(program_cycle=cycle, payment_plan_group=group, status=PaymentPlan.Status.ACCEPTED)
    PaymentPlan.objects.filter(pk=second.pk).update(status_date=first.status_date + timedelta(days=1))
    return [first, second]


def test_group_takes_accepted_status_and_latest_status_date_from_its_plans(
    group: PaymentPlanGroup, accepted_plans: list[PaymentPlan]
) -> None:
    migration_module.set_group_statuses_from_plans(build_apps(), schema_editor=None)

    group.refresh_from_db()
    assert group.status == PaymentPlanGroup.Status.ACCEPTED
    assert group.status_date == accepted_plans[0].status_date + timedelta(days=1)


def test_group_with_locked_fsp_plans_becomes_locked(cycle: Any, group: PaymentPlanGroup) -> None:
    PaymentPlanFactory(program_cycle=cycle, payment_plan_group=group, status=PaymentPlan.Status.LOCKED_FSP)

    migration_module.set_group_statuses_from_plans(build_apps(), schema_editor=None)

    group.refresh_from_db()
    assert group.status == PaymentPlanGroup.Status.LOCKED


def test_group_with_plans_before_fsp_lock_stays_open(cycle: Any, group: PaymentPlanGroup) -> None:
    PaymentPlanFactory(program_cycle=cycle, payment_plan_group=group, status=PaymentPlan.Status.TP_OPEN)
    PaymentPlanFactory(program_cycle=cycle, payment_plan_group=group, status=PaymentPlan.Status.LOCKED)

    migration_module.set_group_statuses_from_plans(build_apps(), schema_editor=None)

    group.refresh_from_db()
    assert group.status == PaymentPlanGroup.Status.OPEN


def test_empty_group_stays_open(group: PaymentPlanGroup) -> None:
    migration_module.set_group_statuses_from_plans(build_apps(), schema_editor=None)

    group.refresh_from_db()
    assert group.status == PaymentPlanGroup.Status.OPEN


def test_group_with_mixed_plan_statuses_is_refused_by_name(cycle: Any, group: PaymentPlanGroup) -> None:
    PaymentPlanFactory(program_cycle=cycle, payment_plan_group=group, status=PaymentPlan.Status.ACCEPTED)
    PaymentPlanFactory(program_cycle=cycle, payment_plan_group=group, status=PaymentPlan.Status.OPEN)

    with pytest.raises(RuntimeError, match=f"must be aligned before this migration can run: {group.unicef_id}"):
        migration_module.set_group_statuses_from_plans(build_apps(), schema_editor=None)


@pytest.fixture
def plan_level_approval_process(accepted_plans: list[PaymentPlan]) -> ApprovalProcess:
    return ApprovalProcessFactory(payment_plan=accepted_plans[0], approval_number_required=3)


def test_plan_approval_process_moves_to_the_group(
    group: PaymentPlanGroup, plan_level_approval_process: ApprovalProcess
) -> None:
    migration_module.move_approval_processes_to_groups(build_apps(), schema_editor=None)

    plan_level_approval_process.refresh_from_db()
    assert plan_level_approval_process.payment_plan_group == group
    assert plan_level_approval_process.payment_plan is None


def test_finished_approval_process_keeps_its_required_numbers(
    group: PaymentPlanGroup, plan_level_approval_process: ApprovalProcess
) -> None:
    group.status = PaymentPlanGroup.Status.ACCEPTED
    group.save(update_fields=["status"])

    migration_module.move_approval_processes_to_groups(build_apps(), schema_editor=None)

    plan_level_approval_process.refresh_from_db()
    assert plan_level_approval_process.approval_number_required == 3


@pytest.fixture
def threshold_for_large_amounts(group: PaymentPlanGroup) -> AcceptanceProcessThreshold:
    return AcceptanceProcessThreshold.objects.create(
        business_area=group.business_area,
        payments_range_usd=NumericRange(150, None),
        approval_number_required=2,
        authorization_number_required=2,
        finance_release_number_required=2,
    )


def test_newest_open_approval_process_is_sized_from_the_group_total(
    cycle: Any,
    group: PaymentPlanGroup,
    accepted_plans: list[PaymentPlan],
    threshold_for_large_amounts: AcceptanceProcessThreshold,
) -> None:
    group.status = PaymentPlanGroup.Status.IN_APPROVAL
    group.save(update_fields=["status"])
    PaymentPlan.objects.filter(pk__in=[plan.pk for plan in accepted_plans]).update(
        total_entitled_quantity_usd=Decimal("100.00")
    )
    older_process = ApprovalProcessFactory(payment_plan=accepted_plans[0], approval_number_required=1)
    newest_process = ApprovalProcessFactory(payment_plan=accepted_plans[1], approval_number_required=1)
    ApprovalProcess.objects.filter(pk=newest_process.pk).update(created_at=timezone.now() + timedelta(minutes=1))

    migration_module.move_approval_processes_to_groups(build_apps(), schema_editor=None)

    older_process.refresh_from_db()
    newest_process.refresh_from_db()
    assert newest_process.payment_plan_group == group
    assert newest_process.approval_number_required == 2
    assert newest_process.finance_release_number_required == 2
    assert older_process.payment_plan_group == group
    assert older_process.approval_number_required == 1


def test_instruction_child_approval_process_is_untouched(cycle: Any) -> None:
    instruction_child = PaymentPlanFactory(
        program_cycle=cycle,
        follow_up_instruction=FollowUpInstructionFactory(program=cycle.program),
        plan_type=PaymentPlan.PlanType.FOLLOW_UP,
    )
    process = ApprovalProcessFactory(payment_plan=instruction_child)

    migration_module.move_approval_processes_to_groups(build_apps(), schema_editor=None)

    process.refresh_from_db()
    assert process.payment_plan == instruction_child
    assert process.payment_plan_group is None


@pytest.fixture
def source_plan(cycle: Any, group: PaymentPlanGroup) -> PaymentPlan:
    return PaymentPlanFactory(
        name="Source Plan", program_cycle=cycle, payment_plan_group=group, status=PaymentPlan.Status.FINISHED
    )


@pytest.fixture
def legacy_children(cycle: Any, group: PaymentPlanGroup, source_plan: PaymentPlan) -> dict[str, PaymentPlan]:
    return {
        "follow_up_one": PaymentPlanFactory(
            program_cycle=cycle,
            payment_plan_group=group,
            source_payment_plan=source_plan,
            plan_type=PaymentPlan.PlanType.FOLLOW_UP,
            status=PaymentPlan.Status.ACCEPTED,
        ),
        "follow_up_two": PaymentPlanFactory(
            program_cycle=cycle,
            payment_plan_group=group,
            source_payment_plan=source_plan,
            plan_type=PaymentPlan.PlanType.FOLLOW_UP,
            status=PaymentPlan.Status.ACCEPTED,
        ),
        "top_up": PaymentPlanFactory(
            program_cycle=cycle,
            payment_plan_group=group,
            source_payment_plan=source_plan,
            plan_type=PaymentPlan.PlanType.TOP_UP,
            status=PaymentPlan.Status.OPEN,
        ),
    }


def test_legacy_children_move_to_one_linked_group_per_type_and_status(
    group: PaymentPlanGroup, legacy_children: dict[str, PaymentPlan]
) -> None:
    migration_module.move_legacy_child_plans_into_linked_groups(build_apps(), schema_editor=None)

    follow_up_group = group.linked_groups.get(plan_type=PaymentPlan.PlanType.FOLLOW_UP)
    top_up_group = group.linked_groups.get(plan_type=PaymentPlan.PlanType.TOP_UP)
    assert follow_up_group.name == "Main Group Follow Up 1"
    assert follow_up_group.status == PaymentPlanGroup.Status.ACCEPTED
    assert set(follow_up_group.payment_plans.all()) == {
        legacy_children["follow_up_one"],
        legacy_children["follow_up_two"],
    }
    assert top_up_group.name == "Main Group Top Up 1"
    assert top_up_group.status == PaymentPlanGroup.Status.OPEN
    assert list(top_up_group.payment_plans.all()) == [legacy_children["top_up"]]


def test_linked_group_takes_cycle_currency_and_fsp_from_the_source_group(
    group: PaymentPlanGroup, legacy_children: dict[str, PaymentPlan]
) -> None:
    migration_module.move_legacy_child_plans_into_linked_groups(build_apps(), schema_editor=None)

    follow_up_group = group.linked_groups.get(plan_type=PaymentPlan.PlanType.FOLLOW_UP)
    assert follow_up_group.cycle == group.cycle
    assert follow_up_group.currency == group.currency
    assert follow_up_group.financial_service_provider == group.financial_service_provider
    assert follow_up_group.source_group == group


def test_source_plan_stays_in_its_group(
    group: PaymentPlanGroup, source_plan: PaymentPlan, legacy_children: dict[str, PaymentPlan]
) -> None:
    migration_module.move_legacy_child_plans_into_linked_groups(build_apps(), schema_editor=None)

    assert list(group.payment_plans.all()) == [source_plan]


def test_legacy_follow_ups_in_different_statuses_are_split_into_separate_linked_groups(
    cycle: Any, group: PaymentPlanGroup, source_plan: PaymentPlan, legacy_children: dict[str, PaymentPlan]
) -> None:
    PaymentPlanFactory(
        program_cycle=cycle,
        payment_plan_group=group,
        source_payment_plan=source_plan,
        plan_type=PaymentPlan.PlanType.FOLLOW_UP,
        status=PaymentPlan.Status.FINISHED,
    )

    migration_module.move_legacy_child_plans_into_linked_groups(build_apps(), schema_editor=None)

    names = sorted(group.linked_groups.filter(plan_type=PaymentPlan.PlanType.FOLLOW_UP).values_list("name", flat=True))
    assert names == ["Main Group Follow Up 1", "Main Group Follow Up 2"]


def test_instruction_child_gets_no_linked_group(cycle: Any) -> None:
    instruction_child = PaymentPlanFactory(
        program_cycle=cycle,
        follow_up_instruction=FollowUpInstructionFactory(program=cycle.program),
        plan_type=PaymentPlan.PlanType.FOLLOW_UP,
    )

    migration_module.move_legacy_child_plans_into_linked_groups(build_apps(), schema_editor=None)

    instruction_child.refresh_from_db()
    assert instruction_child.payment_plan_group_id is None
    assert PaymentPlanGroup.objects.filter(plan_type=PaymentPlan.PlanType.FOLLOW_UP).count() == 0
