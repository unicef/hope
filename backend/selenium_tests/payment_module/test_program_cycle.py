from datetime import datetime

import pytest
from dateutil.relativedelta import relativedelta

from hct_mis_api.apps.core.fixtures import DataCollectingTypeFactory
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program, ProgramCycle

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def create_test_program() -> Program:
    BusinessArea.objects.filter(slug="afghanistan").update(is_payment_plan_applicable=True)
    dct = DataCollectingTypeFactory(type=DataCollectingType.Type.STANDARD)
    yield ProgramFactory(
        name="Test Program",
        programme_code="1234",
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
        data_collecting_type=dct,
        status=Program.ACTIVE,
        cycle__title="Default Programme Cycle",
        cycle__start_date=datetime.now() - relativedelta(days=25),
        cycle__end_date=datetime.now() - relativedelta(days=20),
    )


@pytest.fixture
def create_program_cycle(create_test_program: Program) -> ProgramCycle:
    program_cycle = ProgramCycle.objects.create(
        title="Test Programme Cycle 001",
        start_date=datetime.now(),
        end_date=datetime.now() + relativedelta(days=5),
        status=ProgramCycle.ACTIVE,
        program=create_test_program,
    )
    # TODO: add PaymentPlan maybe to have some total amount numbers in the table
    yield program_cycle


# @pytest.mark.usefixtures("login")
# class TestSmokeProgramCycle:
#     def test_smoke_program_cycle(self, create_program_cycle: ProgramCycle, pageProgramCycle: ProgramCycleModule) -> None:
#         pageProgramCycle.selectGlobalProgramFilter("Test Program").click()
#         pageProgramCycle.getNavPaymentModule().click()
#         assert "Payment cycle" in pageProgramCycle.getPageHeaderTitle().text
#
#
#     def test_smoke_new_program_cycle(
#         self, create_test_program: Program, pageProgramCycle: ProgramCycleModule, pageNewProgramCycle: NewProgramCycle
#     ) -> None:
#         pageProgramCycle.selectGlobalProgramFilter("Test Program").click()
#         pageProgramCycle.getNavProgramCycleModule().click()
#         pageProgramCycle.getButtonNewProgramCycle().click()
#
#     def test_smoke_details_program_cycle(
#         self,
#         create_program_cycle: ProgramCycle,
#         pageProgramCycle: ProgramCycleModule,
#         pageProgramCycleDetails: ProgramCycleModuleDetails,
#     ) -> None:
#         pagePaymentModule.selectGlobalProgramFilter("Test Program").click()
#         pagePaymentModule.getNavPaymentModule().click()
#
#     def test_program_cycle_happy_path(
#         self,
#         pageProgramCycle: ProgramCycleModule,
#     ) -> None:
#         program_cycle = ProgramCycle.objects.first()
#         program = Program.objects.get(name="Test Program")
#         pageProgramCycle.selectGlobalProgramFilter("Test Program").click()
#         pageProgramCycle.getNavProgramCycle().click()
