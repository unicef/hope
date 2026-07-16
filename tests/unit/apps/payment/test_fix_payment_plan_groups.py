import pytest

from extras.test_utils.factories.payment import PaymentPlanFactory, PaymentPlanGroupFactory
from extras.test_utils.factories.program import ProgramCycleFactory
from hope.models import PaymentPlan, PaymentPlanGroup
from hope.one_time_scripts.fix_payment_plan_groups import fix_payment_plan_groups

pytestmark = pytest.mark.django_db


def test_follow_up_moves_to_source_group_and_its_own_group_is_deleted() -> None:
    cycle = ProgramCycleFactory()
    source_group = PaymentPlanGroupFactory(cycle=cycle, name="Src Group")
    source_pp = PaymentPlanFactory(
        program_cycle=cycle,
        payment_plan_group=source_group,
        plan_type=PaymentPlan.PlanType.REGULAR,
        name="Src",
    )
    follow_up_group = PaymentPlanGroupFactory(cycle=cycle, name="Src (follow-up-1) Group")
    follow_up_pp = PaymentPlanFactory(
        program_cycle=cycle,
        payment_plan_group=follow_up_group,
        plan_type=PaymentPlan.PlanType.FOLLOW_UP,
        source_payment_plan=source_pp,
        name="Src (follow-up-1)",
    )

    fix_payment_plan_groups()

    follow_up_pp.refresh_from_db()
    assert follow_up_pp.payment_plan_group_id == source_group.id
    assert PaymentPlanGroup.objects.filter(id=follow_up_group.id).exists() is False


def test_default_group_is_created_for_cycle_missing_one() -> None:
    cycle = ProgramCycleFactory()
    PaymentPlanGroup.objects.filter(cycle=cycle, name="Default Group").delete()
    non_default_group = PaymentPlanGroupFactory(cycle=cycle, name="Only Group")
    PaymentPlanFactory(program_cycle=cycle, payment_plan_group=non_default_group)

    fix_payment_plan_groups()

    assert PaymentPlanGroup.objects.filter(cycle=cycle, name="Default Group").exists() is True
