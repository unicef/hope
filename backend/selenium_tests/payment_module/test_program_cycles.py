from datetime import datetime

import pytest
from dateutil.relativedelta import relativedelta
from page_object.payment_module.program_cycle import ProgramCyclePage
from selenium.webdriver.common.by import By

from hct_mis_api.apps.core.fixtures import DataCollectingTypeFactory
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.payment.fixtures import PaymentPlanFactory
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
        cycle__start_date=(datetime.now() - relativedelta(days=25)).date(),
        cycle__end_date=(datetime.now() - relativedelta(days=20)).date(),
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
    # second draft cycle
    ProgramCycle.objects.create(
        title="Programme Cycle in Draft",
        start_date=datetime.now() + relativedelta(days=6),
        end_date=datetime.now() + relativedelta(days=16),
        status=ProgramCycle.DRAFT,
        program=create_test_program,
    )
    PaymentPlanFactory(program_cycle=program_cycle, total_entitled_quantity_usd=333.99)
    PaymentPlanFactory(program_cycle=program_cycle, total_entitled_quantity_usd=1500.00)
    yield program_cycle


@pytest.mark.usefixtures("login")
class TestSmokeProgramCycle:
    def test_smoke_program_cycles(self, create_program_cycle: ProgramCycle, pageProgramCycle: ProgramCyclePage) -> None:
        pageProgramCycle.selectGlobalProgramFilter("Test Program")
        pageProgramCycle.getNavPaymentModule().click()
        pageProgramCycle.getNavProgrammeCycles().click()
        assert "Payment Module" in pageProgramCycle.getPageHeaderContainer().text
        assert "Payment Module" in pageProgramCycle.getPageHeaderTitle().text
        assert "Status" in pageProgramCycle.getSelectFilter().text
        assert "" in pageProgramCycle.getDatePickerFilter().text
        assert "CLEAR" in pageProgramCycle.getButtonFiltersClear().text
        assert "APPLY" in pageProgramCycle.getButtonFiltersApply().text
        assert "Programme Cycles" in pageProgramCycle.getTableTitle().text
        # assert "Programme Cycle ID" in pageProgramCycle.getHeadCellId().text
        assert "Programme Cycle Title" in pageProgramCycle.getHeadCellProgrammeCyclesTitle().text
        assert "Status" in pageProgramCycle.getHeadCellStatus().text
        assert "Total Entitled Quantity" in pageProgramCycle.getHeadCellTotalEntitledQuantity().text
        assert "Start Date" in pageProgramCycle.getHeadCellStartDate().text
        assert "End Date" in pageProgramCycle.getHeadCellEndDate().text
        assert "Rows per page: 5 1–3 of 3" in pageProgramCycle.getTablePagination().text.replace("\n", " ")
        first_cycle = pageProgramCycle.getProgramCycleRow()[0]
        second_cycle = pageProgramCycle.getProgramCycleRow()[1]
        third_cycle = pageProgramCycle.getProgramCycleRow()[2]
        assert (
            "Default Programme Cycle"
            in first_cycle.find_element(By.CSS_SELECTOR, 'td[data-cy="program-cycle-title"]').text
        )
        assert "Active" in first_cycle.find_element(By.CSS_SELECTOR, 'td[data-cy="program-cycle-status"]').text
        assert (
            "-" in first_cycle.find_element(By.CSS_SELECTOR, 'td[data-cy="program-cycle-total-entitled-quantity"]').text
        )
        assert (
            "Test Programme Cycle 001"
            in second_cycle.find_element(By.CSS_SELECTOR, 'td[data-cy="program-cycle-title"]').text
        )
        assert "Active" in second_cycle.find_element(By.CSS_SELECTOR, 'td[data-cy="program-cycle-status"]').text
        assert (
            "1833.99"
            in second_cycle.find_element(By.CSS_SELECTOR, 'td[data-cy="program-cycle-total-entitled-quantity"]').text
        )
        assert (
            "Programme Cycle in Draft"
            in third_cycle.find_element(By.CSS_SELECTOR, 'td[data-cy="program-cycle-title"]').text
        )
        assert "Draft" in third_cycle.find_element(By.CSS_SELECTOR, 'td[data-cy="program-cycle-status"]').text
        assert (
            "-" in third_cycle.find_element(By.CSS_SELECTOR, 'td[data-cy="program-cycle-total-entitled-quantity"]').text
        )
