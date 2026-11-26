from decimal import Decimal

from django.core.management import call_command
import pytest

from extras.test_utils.factories import (
    ApprovalFactory,
    ApprovalProcessFactory,
    CurrencyFactory,
    FinancialServiceProviderFactory,
    FollowUpInstructionFactory,
    PaymentPlanFactory,
    PaymentPlanGroupFactory,
)
from hope.models import FinancialServiceProvider, PaymentPlan, PaymentPlanGroup

pytestmark = pytest.mark.django_db


@pytest.fixture
def group() -> PaymentPlanGroup:
    return PaymentPlanGroupFactory()


@pytest.fixture
def other_group(group: PaymentPlanGroup) -> PaymentPlanGroup:
    return PaymentPlanGroupFactory(cycle=group.cycle)


@pytest.fixture
def fsp() -> FinancialServiceProvider:
    return FinancialServiceProviderFactory()


@pytest.fixture
def other_fsp() -> FinancialServiceProvider:
    return FinancialServiceProviderFactory()


@pytest.fixture
def aligned_plans(group: PaymentPlanGroup) -> list[PaymentPlan]:
    return [
        PaymentPlanFactory(payment_plan_group=group, program_cycle=group.cycle, status=PaymentPlan.Status.ACCEPTED),
        PaymentPlanFactory(payment_plan_group=group, program_cycle=group.cycle, status=PaymentPlan.Status.ACCEPTED),
    ]


@pytest.fixture
def plans_in_different_statuses(group: PaymentPlanGroup) -> list[PaymentPlan]:
    return [
        PaymentPlanFactory(payment_plan_group=group, program_cycle=group.cycle, status=PaymentPlan.Status.ACCEPTED),
        PaymentPlanFactory(payment_plan_group=group, program_cycle=group.cycle, status=PaymentPlan.Status.FINISHED),
    ]


@pytest.fixture
def plans_before_fsp_lock(group: PaymentPlanGroup) -> list[PaymentPlan]:
    return [
        PaymentPlanFactory(payment_plan_group=group, program_cycle=group.cycle, status=PaymentPlan.Status.TP_OPEN),
        PaymentPlanFactory(payment_plan_group=group, program_cycle=group.cycle, status=PaymentPlan.Status.LOCKED),
    ]


@pytest.fixture
def plans_with_different_fsps(
    group: PaymentPlanGroup, fsp: FinancialServiceProvider, other_fsp: FinancialServiceProvider
) -> list[PaymentPlan]:
    return [
        PaymentPlanFactory(payment_plan_group=group, program_cycle=group.cycle, financial_service_provider=fsp),
        PaymentPlanFactory(payment_plan_group=group, program_cycle=group.cycle, financial_service_provider=other_fsp),
    ]


@pytest.fixture
def plans_with_different_currencies(group: PaymentPlanGroup) -> list[PaymentPlan]:
    return [
        PaymentPlanFactory(
            payment_plan_group=group, program_cycle=group.cycle, currency=CurrencyFactory(code="PLN", name="Zloty")
        ),
        PaymentPlanFactory(
            payment_plan_group=group, program_cycle=group.cycle, currency=CurrencyFactory(code="UAH", name="Hryvnia")
        ),
    ]


@pytest.fixture
def plans_mid_approval(group: PaymentPlanGroup) -> list[PaymentPlan]:
    first = PaymentPlanFactory(
        payment_plan_group=group, program_cycle=group.cycle, status=PaymentPlan.Status.IN_AUTHORIZATION
    )
    second = PaymentPlanFactory(
        payment_plan_group=group, program_cycle=group.cycle, status=PaymentPlan.Status.IN_AUTHORIZATION
    )
    ApprovalFactory(approval_process=ApprovalProcessFactory(payment_plan=first))
    ApprovalProcessFactory(payment_plan=second)
    return [first, second]


@pytest.fixture
def legacy_follow_up_plan(group: PaymentPlanGroup) -> PaymentPlan:
    source = PaymentPlanFactory(payment_plan_group=group, program_cycle=group.cycle, status=PaymentPlan.Status.FINISHED)
    return PaymentPlanFactory(
        payment_plan_group=group,
        program_cycle=group.cycle,
        status=PaymentPlan.Status.OPEN,
        plan_type=PaymentPlan.PlanType.FOLLOW_UP,
        source_payment_plan=source,
    )


@pytest.fixture
def instruction_children_in_groups_with_different_fsps(
    group: PaymentPlanGroup,
    other_group: PaymentPlanGroup,
    fsp: FinancialServiceProvider,
    other_fsp: FinancialServiceProvider,
) -> list[PaymentPlan]:
    instruction = FollowUpInstructionFactory(program=group.cycle.program)
    return [
        PaymentPlanFactory(
            payment_plan_group=group,
            program_cycle=group.cycle,
            financial_service_provider=fsp,
            follow_up_instruction=instruction,
            plan_type=PaymentPlan.PlanType.FOLLOW_UP,
        ),
        PaymentPlanFactory(
            payment_plan_group=other_group,
            program_cycle=group.cycle,
            financial_service_provider=other_fsp,
            follow_up_instruction=instruction,
            plan_type=PaymentPlan.PlanType.FOLLOW_UP,
        ),
    ]


@pytest.fixture
def plans_with_mixed_payment_gateway_flag(group: PaymentPlanGroup) -> list[PaymentPlan]:
    return [
        PaymentPlanFactory(payment_plan_group=group, program_cycle=group.cycle, use_payment_gateway=True),
        PaymentPlanFactory(payment_plan_group=group, program_cycle=group.cycle, use_payment_gateway=False),
    ]


@pytest.fixture
def instruction_children_with_different_flags(group: PaymentPlanGroup) -> list[PaymentPlan]:
    instruction = FollowUpInstructionFactory(program=group.cycle.program)
    return [
        PaymentPlanFactory(
            payment_plan_group=group,
            program_cycle=group.cycle,
            follow_up_instruction=instruction,
            plan_type=PaymentPlan.PlanType.FOLLOW_UP,
            use_payment_gateway=True,
        ),
        PaymentPlanFactory(
            payment_plan_group=group,
            program_cycle=group.cycle,
            follow_up_instruction=instruction,
            plan_type=PaymentPlan.PlanType.FOLLOW_UP,
            use_payment_gateway=False,
        ),
    ]


@pytest.fixture
def instruction_child_with_other_flag_than_its_group(group: PaymentPlanGroup) -> list[PaymentPlan]:
    return [
        PaymentPlanFactory(payment_plan_group=group, program_cycle=group.cycle, use_payment_gateway=False),
        PaymentPlanFactory(
            payment_plan_group=group,
            program_cycle=group.cycle,
            follow_up_instruction=FollowUpInstructionFactory(program=group.cycle.program),
            plan_type=PaymentPlan.PlanType.FOLLOW_UP,
            use_payment_gateway=True,
        ),
    ]


@pytest.fixture
def legacy_follow_up_with_other_flag_than_its_group(group: PaymentPlanGroup) -> list[PaymentPlan]:
    source = PaymentPlanFactory(payment_plan_group=group, program_cycle=group.cycle, use_payment_gateway=False)
    return [
        source,
        PaymentPlanFactory(
            payment_plan_group=group,
            program_cycle=group.cycle,
            plan_type=PaymentPlan.PlanType.FOLLOW_UP,
            source_payment_plan=source,
            use_payment_gateway=True,
        ),
    ]


@pytest.fixture
def instruction_children_with_different_dispersion_dates(group: PaymentPlanGroup) -> list[PaymentPlan]:
    instruction = FollowUpInstructionFactory(program=group.cycle.program)
    first = PaymentPlanFactory(
        payment_plan_group=group,
        program_cycle=group.cycle,
        follow_up_instruction=instruction,
        plan_type=PaymentPlan.PlanType.FOLLOW_UP,
    )
    return [
        first,
        PaymentPlanFactory(
            payment_plan_group=group,
            program_cycle=group.cycle,
            follow_up_instruction=instruction,
            plan_type=PaymentPlan.PlanType.FOLLOW_UP,
            dispersion_end_date=first.dispersion_end_date.replace(year=first.dispersion_end_date.year + 1),
        ),
    ]


@pytest.fixture
def plans_with_different_exchange_rates(group: PaymentPlanGroup) -> list[PaymentPlan]:
    return [
        PaymentPlanFactory(payment_plan_group=group, program_cycle=group.cycle, exchange_rate=Decimal("4.1")),
        PaymentPlanFactory(
            payment_plan_group=group,
            program_cycle=group.cycle,
            exchange_rate=Decimal("4.5"),
            custom_exchange_rate=True,
        ),
    ]


@pytest.fixture
def plans_with_different_dispersion_dates(group: PaymentPlanGroup) -> list[PaymentPlan]:
    first = PaymentPlanFactory(payment_plan_group=group, program_cycle=group.cycle)
    return [
        first,
        PaymentPlanFactory(
            payment_plan_group=group,
            program_cycle=group.cycle,
            dispersion_end_date=first.dispersion_end_date.replace(year=first.dispersion_end_date.year + 1),
        ),
    ]


@pytest.fixture
def instruction_child_with_other_exchange_rate_than_its_group(group: PaymentPlanGroup) -> list[PaymentPlan]:
    return [
        PaymentPlanFactory(payment_plan_group=group, program_cycle=group.cycle, exchange_rate=Decimal("4.1")),
        PaymentPlanFactory(
            payment_plan_group=group,
            program_cycle=group.cycle,
            follow_up_instruction=FollowUpInstructionFactory(program=group.cycle.program),
            plan_type=PaymentPlan.PlanType.FOLLOW_UP,
            exchange_rate=Decimal("4.5"),
        ),
    ]


@pytest.fixture
def plans_with_different_vision_statuses(group: PaymentPlanGroup) -> list[PaymentPlan]:
    return [
        PaymentPlanFactory(
            payment_plan_group=group,
            program_cycle=group.cycle,
            status=PaymentPlan.Status.ACCEPTED,
            internal_data={"vision": {"status": "RELEASED"}},
        ),
        PaymentPlanFactory(payment_plan_group=group, program_cycle=group.cycle, status=PaymentPlan.Status.ACCEPTED),
    ]


@pytest.fixture
def plan_mid_vision(group: PaymentPlanGroup) -> PaymentPlan:
    return PaymentPlanFactory(
        payment_plan_group=group,
        program_cycle=group.cycle,
        status=PaymentPlan.Status.IN_REVIEW,
        internal_data={"vision": {"status": "WAITING_FOR_CALLBACK"}},
    )


@pytest.fixture
def removed_plan_in_other_status(aligned_plans: list[PaymentPlan], group: PaymentPlanGroup) -> PaymentPlan:
    return PaymentPlanFactory(
        payment_plan_group=group, program_cycle=group.cycle, status=PaymentPlan.Status.FINISHED, is_removed=True
    )


@pytest.fixture
def mixed_group_in_another_business_area() -> PaymentPlanGroup:
    group = PaymentPlanGroupFactory()
    PaymentPlanFactory(payment_plan_group=group, program_cycle=group.cycle, status=PaymentPlan.Status.ACCEPTED)
    PaymentPlanFactory(payment_plan_group=group, program_cycle=group.cycle, status=PaymentPlan.Status.FINISHED)
    return group


def test_aligned_group_has_no_findings(aligned_plans: list[PaymentPlan], capsys: pytest.CaptureFixture[str]) -> None:
    call_command("check_payment_plan_groups_before_release")
    out = capsys.readouterr().out

    assert " groups, 2 plans." in out
    assert ": 1 ---" not in out
    assert out.strip().endswith("Blocking findings: 0")


def test_reports_group_with_plans_in_different_statuses(
    plans_in_different_statuses: list[PaymentPlan], capsys: pytest.CaptureFixture[str]
) -> None:
    call_command("check_payment_plan_groups_before_release")
    out = capsys.readouterr().out

    assert "--- Plans in different statuses: 1 ---" in out
    assert "=ACCEPTED" in out
    assert "=FINISHED" in out
    assert out.strip().endswith("Blocking findings: 1")


def test_counts_statuses_before_fsp_lock_as_one(
    plans_before_fsp_lock: list[PaymentPlan], capsys: pytest.CaptureFixture[str]
) -> None:
    call_command("check_payment_plan_groups_before_release")
    out = capsys.readouterr().out

    assert "--- Plans in different statuses: 0 ---" in out


def test_reports_group_with_different_fsps(
    plans_with_different_fsps: list[PaymentPlan], capsys: pytest.CaptureFixture[str]
) -> None:
    call_command("check_payment_plan_groups_before_release")
    out = capsys.readouterr().out

    assert "--- Plans with different FSP: 1 ---" in out
    assert out.strip().endswith("Blocking findings: 1")


def test_reports_group_with_different_currencies(
    plans_with_different_currencies: list[PaymentPlan], capsys: pytest.CaptureFixture[str]
) -> None:
    call_command("check_payment_plan_groups_before_release")
    out = capsys.readouterr().out

    assert "--- Plans with different currency: 1 ---" in out
    assert out.strip().endswith("Blocking findings: 1")


def test_reports_several_plans_mid_approval_with_their_approvals(
    plans_mid_approval: list[PaymentPlan], capsys: pytest.CaptureFixture[str]
) -> None:
    call_command("check_payment_plan_groups_before_release")
    out = capsys.readouterr().out

    assert "--- Several plans mid-approval in one group: 1 ---" in out
    assert "IN_AUTHORIZATION (1 approvals)" in out
    assert "IN_AUTHORIZATION (0 approvals)" in out


def test_skips_status_of_legacy_follow_up_that_moves_to_a_linked_group(
    legacy_follow_up_plan: PaymentPlan, capsys: pytest.CaptureFixture[str]
) -> None:
    call_command("check_payment_plan_groups_before_release")
    out = capsys.readouterr().out

    assert "--- Plans in different statuses: 0 ---" in out
    assert out.strip().endswith("Blocking findings: 0")


def test_reports_instruction_whose_plans_sit_in_groups_with_different_fsps(
    instruction_children_in_groups_with_different_fsps: list[PaymentPlan], capsys: pytest.CaptureFixture[str]
) -> None:
    call_command("check_payment_plan_groups_before_release")
    out = capsys.readouterr().out

    assert "--- Follow-Up Instructions whose plans sit in groups with different FSP or currency: 1 ---" in out


def test_reports_group_with_mixed_payment_gateway_flag(
    plans_with_mixed_payment_gateway_flag: list[PaymentPlan], capsys: pytest.CaptureFixture[str]
) -> None:
    call_command("check_payment_plan_groups_before_release")
    out = capsys.readouterr().out

    assert "--- Plans with different use_payment_gateway flag: 1 ---" in out
    assert out.strip().endswith("Blocking findings: 1")


def test_reports_instruction_whose_plans_have_different_flags(
    instruction_children_with_different_flags: list[PaymentPlan], capsys: pytest.CaptureFixture[str]
) -> None:
    call_command("check_payment_plan_groups_before_release")
    out = capsys.readouterr().out

    assert "--- Plans with different use_payment_gateway flag: 1 ---" in out
    assert f"| instruction {instruction_children_with_different_flags[0].follow_up_instruction.unicef_id}:" in out
    assert out.strip().endswith("Blocking findings: 1")


def test_skips_flag_of_instruction_child_that_leaves_the_group(
    instruction_child_with_other_flag_than_its_group: list[PaymentPlan], capsys: pytest.CaptureFixture[str]
) -> None:
    call_command("check_payment_plan_groups_before_release")
    out = capsys.readouterr().out

    assert "--- Plans with different use_payment_gateway flag: 0 ---" in out
    assert out.strip().endswith("Blocking findings: 0")


def test_skips_flag_of_legacy_follow_up_that_moves_to_a_linked_group(
    legacy_follow_up_with_other_flag_than_its_group: list[PaymentPlan], capsys: pytest.CaptureFixture[str]
) -> None:
    call_command("check_payment_plan_groups_before_release")
    out = capsys.readouterr().out

    assert "--- Plans with different use_payment_gateway flag: 0 ---" in out
    assert out.strip().endswith("Blocking findings: 0")


def test_reports_group_with_different_exchange_rates(
    plans_with_different_exchange_rates: list[PaymentPlan], capsys: pytest.CaptureFixture[str]
) -> None:
    call_command("check_payment_plan_groups_before_release")
    out = capsys.readouterr().out

    assert "--- Plans with different exchange rates: 1 ---" in out
    assert "=4.5" in out
    assert " custom" in out
    assert out.strip().endswith("Blocking findings: 1")


def test_reports_group_with_different_dispersion_dates(
    plans_with_different_dispersion_dates: list[PaymentPlan], capsys: pytest.CaptureFixture[str]
) -> None:
    call_command("check_payment_plan_groups_before_release")
    out = capsys.readouterr().out

    assert "--- Plans with different dispersion dates: 1 ---" in out
    assert out.strip().endswith("Blocking findings: 0")


def test_reports_instruction_whose_plans_have_different_dispersion_dates(
    instruction_children_with_different_dispersion_dates: list[PaymentPlan], capsys: pytest.CaptureFixture[str]
) -> None:
    call_command("check_payment_plan_groups_before_release")
    out = capsys.readouterr().out

    assert "--- Plans with different dispersion dates: 1 ---" in out
    assert "| instruction " in out


def test_skips_exchange_rate_of_instruction_child_that_leaves_the_group(
    instruction_child_with_other_exchange_rate_than_its_group: list[PaymentPlan], capsys: pytest.CaptureFixture[str]
) -> None:
    call_command("check_payment_plan_groups_before_release")
    out = capsys.readouterr().out

    assert "--- Plans with different exchange rates: 0 ---" in out


def test_reports_group_with_different_vision_statuses(
    plans_with_different_vision_statuses: list[PaymentPlan], capsys: pytest.CaptureFixture[str]
) -> None:
    call_command("check_payment_plan_groups_before_release")
    out = capsys.readouterr().out

    assert "--- Plans with different Vision status: 1 ---" in out
    assert "=RELEASED" in out
    assert "=NOT_SENT" in out
    assert out.strip().endswith("Blocking findings: 1")


def test_reports_plan_in_the_middle_of_the_vision_flow(
    plan_mid_vision: PaymentPlan, capsys: pytest.CaptureFixture[str]
) -> None:
    call_command("check_payment_plan_groups_before_release")
    out = capsys.readouterr().out

    assert "--- Plans in the middle of the Vision flow: 1 ---" in out
    assert "=WAITING_FOR_CALLBACK" in out
    assert out.strip().endswith("Blocking findings: 1")


def test_ignores_removed_plans(removed_plan_in_other_status: PaymentPlan, capsys: pytest.CaptureFixture[str]) -> None:
    call_command("check_payment_plan_groups_before_release")
    out = capsys.readouterr().out

    assert " groups, 2 plans." in out
    assert "--- Plans in different statuses: 0 ---" in out


def test_business_area_option_checks_only_that_business_area(
    aligned_plans: list[PaymentPlan],
    group: PaymentPlanGroup,
    mixed_group_in_another_business_area: PaymentPlanGroup,
    capsys: pytest.CaptureFixture[str],
) -> None:
    call_command("check_payment_plan_groups_before_release", "--business-area", group.cycle.program.business_area.slug)
    out = capsys.readouterr().out

    assert " groups, 2 plans." in out
    assert "--- Plans in different statuses: 0 ---" in out
