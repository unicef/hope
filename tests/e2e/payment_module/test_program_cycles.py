from datetime import datetime
from time import sleep

import pytest
from dateutil.relativedelta import relativedelta
from e2e.page_object.payment_module.program_cycle import ProgramCyclePage
from e2e.page_object.payment_module.program_cycle_details import ProgramCycleDetailsPage
from extras.test_utils.factories.core import DataCollectingTypeFactory
from extras.test_utils.factories.payment import PaymentPlanFactory
from extras.test_utils.factories.program import ProgramFactory
from selenium.webdriver.common.by import By

from hope.apps.core.models import DataCollectingType
from hope.apps.program.models import BeneficiaryGroup, Program, ProgramCycle

pytestmark = pytest.mark.django_db()


@pytest.fixture
def create_test_program() -> Program:
    dct = DataCollectingTypeFactory(type=DataCollectingType.Type.STANDARD)
    beneficiary_group = BeneficiaryGroup.objects.filter(name="Main Menu").first()
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
        beneficiary_group=beneficiary_group,
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


@pytest.fixture
def create_program_cycle_without_payment_plan(
    create_test_program: Program,
) -> ProgramCycle:
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
    yield program_cycle


@pytest.mark.usefixtures("login")
class TestSmokeProgramCycle:
    def test_smoke_program_cycles(
        self, create_program_cycle: ProgramCycle, page_program_cycle: ProgramCyclePage
    ) -> None:
        page_program_cycle.select_global_program_filter("Test Program")
        page_program_cycle.get_nav_payment_module().click()
        page_program_cycle.get_nav_programme_cycles().click()
        assert "Payment Module" in page_program_cycle.get_page_header_container().text
        assert "Payment Module" in page_program_cycle.get_page_header_title().text
        assert "Status" in page_program_cycle.get_select_filter().text
        assert "" in page_program_cycle.get_date_picker_filter().text
        assert "CLEAR" in page_program_cycle.get_button_filters_clear().text
        assert "APPLY" in page_program_cycle.get_button_filters_apply().text
        assert "Programme Cycles" in page_program_cycle.get_table_title().text
        assert "Programme Cycle Title" in page_program_cycle.get_head_cell_programme_cycles_title().text
        assert "Status" in page_program_cycle.get_head_cell_status().text
        assert "Total Entitled Quantity (USD)" in page_program_cycle.get_head_cell_total_entitled_quantity_usd().text
        assert "Start Date" in page_program_cycle.get_head_cell_start_date().text
        assert "End Date" in page_program_cycle.get_head_cell_end_date().text
        assert "Rows per page: 5 1–3 of 3" in page_program_cycle.get_table_pagination().text.replace("\n", " ")
        first_cycle = page_program_cycle.get_program_cycle_row()[0]
        second_cycle = page_program_cycle.get_program_cycle_row()[1]
        third_cycle = page_program_cycle.get_program_cycle_row()[2]
        assert (
            "Default Programme Cycle"
            in first_cycle.find_element(By.CSS_SELECTOR, 'td[data-cy="program-cycle-title"]').text
        )
        assert "Active" in first_cycle.find_element(By.CSS_SELECTOR, 'td[data-cy="program-cycle-status"]').text
        assert (
            "-"
            in first_cycle.find_element(
                By.CSS_SELECTOR,
                'td[data-cy="program-cycle-total-entitled-quantity-usd"]',
            ).text
        )
        assert (
            "Test Programme Cycle 001"
            in second_cycle.find_element(By.CSS_SELECTOR, 'td[data-cy="program-cycle-title"]').text
        )
        assert "Active" in second_cycle.find_element(By.CSS_SELECTOR, 'td[data-cy="program-cycle-status"]').text
        assert (
            "1833.99"
            in second_cycle.find_element(
                By.CSS_SELECTOR,
                'td[data-cy="program-cycle-total-entitled-quantity-usd"]',
            ).text
        )
        assert (
            "Programme Cycle in Draft"
            in third_cycle.find_element(By.CSS_SELECTOR, 'td[data-cy="program-cycle-title"]').text
        )
        assert "Draft" in third_cycle.find_element(By.CSS_SELECTOR, 'td[data-cy="program-cycle-status"]').text
        assert (
            "-"
            in third_cycle.find_element(
                By.CSS_SELECTOR,
                'td[data-cy="program-cycle-total-entitled-quantity-usd"]',
            ).text
        )

    def test_smoke_program_cycles_details(
        self,
        create_program_cycle: ProgramCycle,
        page_program_cycle: ProgramCyclePage,
        page_program_cycle_details: ProgramCycleDetailsPage,
    ) -> None:
        page_program_cycle.select_global_program_filter("Test Program")
        page_program_cycle.get_nav_payment_module().click()
        page_program_cycle.get_nav_programme_cycles().click()
        start_date = page_program_cycle.get_program_cycle_start_date_list()[1].text
        end_date = page_program_cycle.get_program_cycle_end_date_list()[1].text
        page_program_cycle.get_program_cycle_row()[1].find_element("tag name", "a").click()
        assert "Test Programme Cycle 001" in page_program_cycle_details.get_page_header_title().text
        assert "Active" in page_program_cycle_details.get_status_container().text
        assert start_date in page_program_cycle_details.get_label_start_date().text
        assert end_date in page_program_cycle_details.get_label_end_date().text


@pytest.mark.usefixtures("login")
class TestProgramCycle:
    def test_program_cycles_finish_and_reactivate(
        self,
        create_program_cycle_without_payment_plan: ProgramCycle,
        page_program_cycle: ProgramCyclePage,
        page_program_cycle_details: ProgramCycleDetailsPage,
    ) -> None:
        page_program_cycle.select_global_program_filter("Test Program")
        page_program_cycle.get_nav_payment_module().click()
        page_program_cycle.get_nav_programme_cycles().click()
        page_program_cycle.get_program_cycle_row()[1].find_element("tag name", "a").click()
        assert "Test Programme Cycle 001" in page_program_cycle_details.get_page_header_title().text
        for _ in range(100):
            if "Active" in page_program_cycle_details.get_status_container().text:
                break
            sleep(0.1)
        else:
            assert "Active" in page_program_cycle_details.get_status_container().text
        page_program_cycle_details.get_button_finish_programme_cycle().click()
        for _ in range(100):
            if "Finished" in page_program_cycle_details.get_status_container().text:
                break
            sleep(0.1)
        else:
            assert "Finished" in page_program_cycle_details.get_status_container().text
        page_program_cycle_details.get_button_reactivate_programme_cycle().click()
        for _ in range(100):
            if "Active" in page_program_cycle_details.get_status_container().text:
                break
            sleep(0.1)
        else:
            assert "Active" in page_program_cycle_details.get_status_container().text

    def test_program_cycles_finish_with_error(
        self,
        create_program_cycle: ProgramCycle,
        page_program_cycle: ProgramCyclePage,
        page_program_cycle_details: ProgramCycleDetailsPage,
    ) -> None:
        page_program_cycle.select_global_program_filter("Test Program")
        page_program_cycle.get_nav_payment_module().click()
        page_program_cycle.get_nav_programme_cycles().click()
        page_program_cycle.get_program_cycle_row()[1].find_element("tag name", "a").click()
        assert "Test Programme Cycle 001" in page_program_cycle_details.get_page_header_title().text
        assert "Active" in page_program_cycle_details.get_status_container().text
        page_program_cycle_details.get_button_finish_programme_cycle().click()
        page_program_cycle_details.check_alert("All Payment Plans and Follow-Up Payment Plans have to be Reconciled.")
        assert "Active" in page_program_cycle_details.get_status_container().text
