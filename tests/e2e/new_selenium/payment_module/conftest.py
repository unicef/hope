import pytest

from extras.test_utils.factories import PaymentPlanFactory, PaymentPlanGroupFactory
from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory
from hope.models import BusinessArea, PaymentPlan, PaymentPlanGroup, Program, ProgramCycle


@pytest.fixture
def payment_module_program(business_area: BusinessArea) -> Program:
    return ProgramFactory(
        name="Payment Module Program",
        status=Program.ACTIVE,
        business_area=business_area,
    )


@pytest.fixture
def program_cycle(payment_module_program: Program) -> ProgramCycle:
    return ProgramCycleFactory(program=payment_module_program)


@pytest.fixture
def payment_plan_group(program_cycle: ProgramCycle) -> PaymentPlanGroup:
    return PaymentPlanGroupFactory(cycle=program_cycle, name="Original Group Name")


@pytest.fixture
def group_with_payment_plan(program_cycle: ProgramCycle) -> PaymentPlanGroup:
    group = program_cycle.payment_plan_groups.first()
    PaymentPlanFactory(
        program_cycle=program_cycle,
        payment_plan_group=group,
        business_area=program_cycle.program.business_area,
        status=PaymentPlan.Status.OPEN,
    )
    return group
