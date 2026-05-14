import pytest

from extras.test_utils.factories import PaymentPlanGroupFactory
from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory
from hope.models import BusinessArea, PaymentPlanGroup, Program, ProgramCycle


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
