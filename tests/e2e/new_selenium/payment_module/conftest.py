import pytest

from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory
from hope.models import BusinessArea, Program, ProgramCycle


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
