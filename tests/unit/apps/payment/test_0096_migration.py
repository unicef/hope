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
    FollowUpInstructionFactory,
    PaymentPlanFactory,
    ProgramCycleFactory,
    UserFactory,
)
from hope.models import AcceptanceProcessThreshold, ApprovalProcess, FollowUpInstruction, PaymentPlan

pytestmark = pytest.mark.django_db

migration_module = importlib.import_module("hope.apps.payment.migrations.0095_migration")


@pytest.fixture
def migration_apps() -> SimpleNamespace:
    return SimpleNamespace(
        get_model=lambda app_label, model_name: {
            ("payment", "PaymentPlan"): PaymentPlan,
            ("payment", "FollowUpInstruction"): FollowUpInstruction,
            ("payment", "ApprovalProcess"): ApprovalProcess,
            ("payment", "AcceptanceProcessThreshold"): AcceptanceProcessThreshold,
        }[(app_label, model_name)]
    )


@pytest.fixture
def cycle() -> Any:
    return ProgramCycleFactory()


@pytest.fixture
def instruction(cycle: Any) -> FollowUpInstruction:
    return FollowUpInstructionFactory(program=cycle.program, business_area=cycle.program.business_area)


@pytest.fixture
def children_in_approval(cycle: Any, instruction: FollowUpInstruction) -> list[PaymentPlan]:
    return [
        PaymentPlanFactory(
            program_cycle=cycle,
            follow_up_instruction=instruction,
            plan_type=PaymentPlan.PlanType.FOLLOW_UP,
            status=PaymentPlan.Status.IN_APPROVAL,
            total_entitled_quantity_usd=Decimal("100.00"),
        )
        for _ in range(2)
    ]


@pytest.fixture
def child_processes(children_in_approval: list[PaymentPlan]) -> list[ApprovalProcess]:
    older_process = ApprovalProcessFactory(payment_plan=children_in_approval[0], approval_number_required=1)
    newest_process = ApprovalProcessFactory(payment_plan=children_in_approval[1], approval_number_required=1)
    ApprovalProcess.objects.filter(pk=newest_process.pk).update(created_at=timezone.now() + timedelta(minutes=1))
    return [older_process, newest_process]


@pytest.fixture
def threshold_for_large_amounts(instruction: FollowUpInstruction) -> AcceptanceProcessThreshold:
    return AcceptanceProcessThreshold.objects.create(
        business_area=instruction.business_area,
        payments_range_usd=NumericRange(150, None),
        approval_number_required=2,
        authorization_number_required=2,
        finance_release_number_required=2,
    )


def test_child_approval_processes_move_to_the_instruction(
    migration_apps: SimpleNamespace, instruction: FollowUpInstruction, child_processes: list[ApprovalProcess]
) -> None:
    migration_module.move_approval_processes_to_instructions(migration_apps, schema_editor=None)

    assert set(instruction.approval_process.all()) == set(child_processes)
    assert ApprovalProcess.objects.filter(payment_plan__isnull=False).count() == 0


def test_newest_open_process_is_sized_from_the_instruction_total(
    migration_apps: SimpleNamespace,
    child_processes: list[ApprovalProcess],
    threshold_for_large_amounts: AcceptanceProcessThreshold,
) -> None:
    migration_module.move_approval_processes_to_instructions(migration_apps, schema_editor=None)

    older_process, newest_process = child_processes
    older_process.refresh_from_db()
    newest_process.refresh_from_db()
    assert newest_process.approval_number_required == 2
    assert newest_process.authorization_number_required == 2
    assert newest_process.finance_release_number_required == 2
    assert older_process.approval_number_required == 1


@pytest.fixture
def finished_children(children_in_approval: list[PaymentPlan]) -> list[PaymentPlan]:
    PaymentPlan.objects.filter(pk__in=[plan.pk for plan in children_in_approval]).update(
        status=PaymentPlan.Status.FINISHED
    )
    return children_in_approval


def test_finished_instruction_keeps_its_required_numbers(
    migration_apps: SimpleNamespace,
    finished_children: list[PaymentPlan],
    child_processes: list[ApprovalProcess],
    threshold_for_large_amounts: AcceptanceProcessThreshold,
) -> None:
    migration_module.move_approval_processes_to_instructions(migration_apps, schema_editor=None)

    newest_process = child_processes[1]
    newest_process.refresh_from_db()
    assert newest_process.approval_number_required == 1


def test_mid_approval_instruction_without_a_process_is_skipped(
    migration_apps: SimpleNamespace, instruction: FollowUpInstruction, children_in_approval: list[PaymentPlan]
) -> None:
    migration_module.move_approval_processes_to_instructions(migration_apps, schema_editor=None)

    assert instruction.approval_process.count() == 0


@pytest.fixture
def newest_process_requiring_three(child_processes: list[ApprovalProcess]) -> ApprovalProcess:
    newest_process = child_processes[1]
    ApprovalProcess.objects.filter(pk=newest_process.pk).update(approval_number_required=3)
    return newest_process


def test_mid_approval_instruction_below_every_threshold_requires_one_of_each(
    migration_apps: SimpleNamespace, newest_process_requiring_three: ApprovalProcess
) -> None:
    migration_module.move_approval_processes_to_instructions(migration_apps, schema_editor=None)

    newest_process = newest_process_requiring_three
    newest_process.refresh_from_db()
    assert newest_process.approval_number_required == 1


@pytest.fixture
def plan_outside_instruction_process(cycle: Any) -> ApprovalProcess:
    return ApprovalProcessFactory(payment_plan=PaymentPlanFactory(program_cycle=cycle))


def test_plan_outside_an_instruction_keeps_its_approval_process(
    migration_apps: SimpleNamespace, plan_outside_instruction_process: ApprovalProcess
) -> None:
    migration_module.move_approval_processes_to_instructions(migration_apps, schema_editor=None)

    process = plan_outside_instruction_process
    process.refresh_from_db()
    assert process.payment_plan is not None
    assert process.follow_up_instruction is None


@pytest.fixture
def aborted_child(cycle: Any, instruction: FollowUpInstruction) -> PaymentPlan:
    return PaymentPlanFactory(
        program_cycle=cycle,
        follow_up_instruction=instruction,
        plan_type=PaymentPlan.PlanType.FOLLOW_UP,
        status=PaymentPlan.Status.ABORTED,
        abort_comment="wrong beneficiaries",
    )


def test_instruction_takes_the_abort_comment_of_its_aborted_children(
    migration_apps: SimpleNamespace, instruction: FollowUpInstruction, aborted_child: PaymentPlan
) -> None:
    migration_module.copy_abort_and_closure_to_instructions(migration_apps, schema_editor=None)

    instruction.refresh_from_db()
    assert instruction.abort_comment == "wrong beneficiaries"


@pytest.fixture
def closing_user() -> Any:
    return UserFactory()


@pytest.fixture
def closed_child(cycle: Any, instruction: FollowUpInstruction, closing_user: Any) -> PaymentPlan:
    return PaymentPlanFactory(
        program_cycle=cycle,
        follow_up_instruction=instruction,
        plan_type=PaymentPlan.PlanType.FOLLOW_UP,
        status=PaymentPlan.Status.CLOSED,
        closure_comment="Comment",
        closed_by=closing_user,
    )


def test_instruction_takes_the_closing_user_but_not_the_placeholder_comment(
    migration_apps: SimpleNamespace, instruction: FollowUpInstruction, closed_child: PaymentPlan, closing_user: Any
) -> None:
    migration_module.copy_abort_and_closure_to_instructions(migration_apps, schema_editor=None)

    instruction.refresh_from_db()
    assert instruction.closed_by == closing_user
    assert instruction.closure_comment is None
