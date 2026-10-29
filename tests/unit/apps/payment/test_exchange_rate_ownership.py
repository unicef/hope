from decimal import Decimal

import pytest

from extras.test_utils.factories.payment import (
    FollowUpInstructionFactory,
    PaymentPlanFactory,
    PaymentPlanGroupFactory,
)
from extras.test_utils.factories.program import ProgramCycleFactory


@pytest.fixture
def grouped_plans(db):
    group = PaymentPlanGroupFactory(exchange_rate=Decimal("1.25000000"), custom_exchange_rate=True)
    first = PaymentPlanFactory(program_cycle=group.cycle, payment_plan_group=group)
    second = PaymentPlanFactory(program_cycle=group.cycle, payment_plan_group=group)
    return group, first, second


@pytest.fixture
def instruction_plan(db):
    instruction = FollowUpInstructionFactory(exchange_rate=Decimal("2.50000000"), custom_exchange_rate=True)
    cycle = ProgramCycleFactory(program=instruction.program)
    plan = PaymentPlanFactory(program_cycle=cycle, payment_plan_group=None, follow_up_instruction=instruction)
    return instruction, plan


def test_grouped_plans_read_the_same_owner_rate(grouped_plans, django_assert_num_queries) -> None:
    group, first, second = grouped_plans

    with django_assert_num_queries(0):
        assert first.exchange_rate_owner is group
        assert first.exchange_rate == Decimal("1.25000000")
        assert second.exchange_rate == Decimal("1.25000000")
        assert first.get_exchange_rate() == 1.25


def test_instruction_child_reads_instruction_rate(instruction_plan, django_assert_num_queries) -> None:
    instruction, plan = instruction_plan

    with django_assert_num_queries(0):
        assert plan.payment_plan_group_id is None
        assert plan.exchange_rate_owner is instruction
        assert plan.exchange_rate == Decimal("2.50000000")
        assert plan.get_exchange_rate() == 2.5
