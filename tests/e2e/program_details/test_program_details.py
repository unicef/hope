from datetime import datetime
from decimal import Decimal
from time import sleep

import pytest
from dateutil.relativedelta import relativedelta
from e2e.helpers.date_time_format import FormatTime
from e2e.page_object.programme_details.programme_details import ProgrammeDetails
from e2e.page_object.programme_management.programme_management import (
    ProgrammeManagement,
)
from extras.test_utils.factories.core import (
    DataCollectingTypeFactory,
    create_afghanistan,
)
from extras.test_utils.factories.household import create_household
from extras.test_utils.factories.payment import PaymentPlanFactory
from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from selenium.common.exceptions import NoSuchElementException

from hope.models.user import User
from hope.models.business_area import BusinessArea
from hope.models.data_collecting_type import DataCollectingType
from hope.models.area import Area
from hope.models.household import Household
from hope.models import PaymentPlan
from hope.models.program import Program
from hope.models.program_cycle import ProgramCycle
from hope.models.beneficiary_group import BeneficiaryGroup

pytestmark = pytest.mark.django_db()


@pytest.fixture
def standard_program() -> Program:
    yield get_program_with_dct_type_and_name("Test For Edit", "TEST")


@pytest.fixture
def program_with_three_cycles() -> Program:
    program = get_program_with_dct_type_and_name(
        "ThreeCyclesProgramme",
        "cycl",
        status=Program.ACTIVE,
        program_cycle_status=ProgramCycle.DRAFT,
    )
    ProgramCycleFactory(program=program, status=ProgramCycle.DRAFT)
    ProgramCycleFactory(program=program, status=ProgramCycle.DRAFT)
    program.save()
    yield program


@pytest.fixture
def program_with_different_cycles() -> Program:
    program = get_program_with_dct_type_and_name(
        "ThreeCyclesProgramme",
        "cycl",
        status=Program.ACTIVE,
        program_cycle_status=ProgramCycle.DRAFT,
    )
    ProgramCycleFactory(
        program=program,
        status=ProgramCycle.ACTIVE,
        start_date=datetime.now() + relativedelta(days=11),
        end_date=datetime.now() + relativedelta(days=17),
    )
    ProgramCycleFactory(
        program=program,
        status=ProgramCycle.FINISHED,
        start_date=datetime.now() + relativedelta(days=18),
        end_date=datetime.now() + relativedelta(days=20),
    )
    program.save()
    yield program


def get_program_with_dct_type_and_name(
    name: str,
    programme_code: str,
    dct_type: str = DataCollectingType.Type.STANDARD,
    status: str = Program.DRAFT,
    program_cycle_status: str = ProgramCycle.FINISHED,
    cycle_start_date: datetime | bool = False,
    cycle_end_date: datetime | bool = False,
) -> Program:
    if not cycle_start_date:
        cycle_start_date = datetime.now() - relativedelta(days=25)
    if not cycle_end_date:
        cycle_end_date = datetime.now() + relativedelta(days=10)
    dct = DataCollectingTypeFactory(type=dct_type)
    beneficiary_group = BeneficiaryGroup.objects.filter(name="Main Menu").first()
    return ProgramFactory(
        name=name,
        programme_code=programme_code,
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
        data_collecting_type=dct,
        status=status,
        budget=100,
        cycle__status=program_cycle_status,
        cycle__start_date=cycle_start_date,
        cycle__end_date=cycle_end_date,
        beneficiary_group=beneficiary_group,
    )


@pytest.fixture
def standard_program_with_draft_programme_cycle() -> Program:
    yield get_program_without_cycle_end_date(
        "Active Programme",
        "9876",
        status=Program.ACTIVE,
        program_cycle_status=ProgramCycle.DRAFT,
    )


@pytest.fixture
def standard_active_program() -> Program:
    yield get_program_with_dct_type_and_name(
        "Active Programme",
        "9876",
        status=Program.ACTIVE,
        program_cycle_status=ProgramCycle.FINISHED,
        cycle_end_date=datetime.now(),
    )


@pytest.fixture
def standard_active_program_cycle_draft() -> Program:
    yield get_program_with_dct_type_and_name(
        "Active Programme",
        "9876",
        status=Program.ACTIVE,
        program_cycle_status=ProgramCycle.ACTIVE,
        cycle_end_date=datetime.now(),
    )


@pytest.fixture
def standard_active_program_with_draft_program_cycle() -> Program:
    yield get_program_with_dct_type_and_name(
        "Active Programme And DRAFT Programme Cycle",
        "LILI",
        status=Program.ACTIVE,
        program_cycle_status=ProgramCycle.DRAFT,
        cycle_end_date=datetime.now(),
    )


def get_program_without_cycle_end_date(
    name: str,
    programme_code: str,
    dct_type: str = DataCollectingType.Type.STANDARD,
    status: str = Program.ACTIVE,
    program_cycle_status: str = ProgramCycle.FINISHED,
    cycle_start_date: datetime | bool = False,
) -> Program:
    if not cycle_start_date:
        cycle_start_date = datetime.now() - relativedelta(days=25)
    dct = DataCollectingTypeFactory(type=dct_type)
    beneficiary_group = BeneficiaryGroup.objects.filter(name="Main Menu").first()
    program = ProgramFactory(
        name=name,
        programme_code=programme_code,
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
        data_collecting_type=dct,
        status=status,
        cycle__title="Default Programme Cycle",
        cycle__status=program_cycle_status,
        cycle__start_date=cycle_start_date,
        cycle__end_date=None,
        beneficiary_group=beneficiary_group,
    )
    program_cycle = ProgramCycle.objects.get(program=program)
    PaymentPlanFactory(
        program_cycle=program_cycle,
        total_entitled_quantity_usd=Decimal(1234.99),
        total_delivered_quantity_usd=Decimal(50.01),
        total_undelivered_quantity_usd=Decimal(1184.98),
    )
    return program


def create_custom_household() -> Household:
    program = Program.objects.get(name="Test For Edit")

    registration_data_import = RegistrationDataImportFactory(
        imported_by=User.objects.first(), business_area=BusinessArea.objects.first()
    )

    household, _ = create_household(
        {
            "registration_data_import": registration_data_import,
            "admin2": Area.objects.order_by("?").first(),
            "program": program,
        },
        {"registration_data_import": registration_data_import},
    )

    household.unicef_id = "HH-00-0000.1380"
    household.save()
    program.adjust_program_size()
    program.save()
    return household


@pytest.fixture
def create_payment_plan(standard_program: Program) -> PaymentPlan:
    cycle = standard_program.cycles.first()
    payment_plan = PaymentPlan.objects.update_or_create(
        name="Test Payment Plan",
        business_area=BusinessArea.objects.get(slug="afghanistan"),
        start_date=datetime.now(),
        end_date=datetime.now() + relativedelta(days=30),
        currency="USD",
        dispersion_start_date=datetime.now(),
        dispersion_end_date=datetime.now() + relativedelta(days=14),
        status_date=datetime.now(),
        status=PaymentPlan.Status.ACCEPTED,
        created_by=User.objects.first(),
        total_delivered_quantity=999,
        total_entitled_quantity=2999,
        is_follow_up=False,
        program_cycle=cycle,
    )
    yield payment_plan[0]


@pytest.fixture
def create_programs() -> None:
    business_area = create_afghanistan()
    dct = DataCollectingTypeFactory(type=DataCollectingType.Type.STANDARD)
    beneficiary_group = BeneficiaryGroup.objects.filter(name="Main Menu").first()
    ProgramFactory(
        budget=10000,
        name="Test Programm",
        status=Program.ACTIVE,
        business_area=business_area,
        data_collecting_type=dct,
        beneficiary_group=beneficiary_group,
    )


@pytest.mark.usefixtures("login")
class TestSmokeProgrammeDetails:
    def test_program_details(self, standard_program: Program, page_programme_details: ProgrammeDetails) -> None:
        program = Program.objects.get(name="Test For Edit")
        # Go to Programme Details
        page_programme_details.select_global_program_filter("Test For Edit")
        # Check Details page
        assert "Test For Edit" in page_programme_details.get_header_title().text
        assert "DRAFT" in page_programme_details.get_program_status().text
        assert "Test For Edit" in page_programme_details.get_header_title().text
        assert "REMOVE" in page_programme_details.get_button_remove_program().text
        assert "EDIT PROGRAMME" in page_programme_details.get_button_edit_program().text
        assert "ACTIVATE" in page_programme_details.get_button_activate_program().text
        assert "" in page_programme_details.get_copy_program().text
        assert "DRAFT" in page_programme_details.get_program_status().text
        assert (datetime.now() - relativedelta(months=1)).strftime(
            "%-d %b %Y"
        ) in page_programme_details.get_label_start_date().text
        assert (datetime.now() + relativedelta(months=1)).strftime(
            "%-d %b %Y"
        ) in page_programme_details.get_label_end_date().text
        assert program.programme_code in page_programme_details.get_label_programme_code().text
        assert program.sector.replace("_", " ").title() in page_programme_details.get_label_selector().text.title()
        assert program.data_collecting_type.label in page_programme_details.get_label_data_collecting_type().text
        assert (
            program.frequency_of_payments.replace("_", "-").capitalize()
            in page_programme_details.get_label_freq_of_payment().text
        )
        assert (
            program.administrative_areas_of_implementation
            in page_programme_details.get_label_administrative_areas().text
        )
        assert program.description in page_programme_details.get_label_description().text
        assert "Yes" if program.cash_plus else "No" in page_programme_details.get_label_cash_plus().text
        assert (
            "Only Selected Partners within the business area" in page_programme_details.get_label_partner_access().text
        )
        assert "0" in page_programme_details.get_label_program_size().text

    def test_edit_programme_from_details(
        self,
        create_programs: None,
        page_programme_details: ProgrammeDetails,
        page_programme_management: ProgrammeManagement,
    ) -> None:
        page_programme_details.select_global_program_filter("Test Programm")
        page_programme_details.get_button_edit_program().click()
        page_programme_details.get_select_edit_program_details().click()
        page_programme_management.clear_input(page_programme_management.get_input_programme_name())
        page_programme_management.get_input_programme_name().send_keys("New name after Edit")
        page_programme_management.clear_input(page_programme_management.get_input_programme_code())
        page_programme_management.get_input_programme_code().send_keys("NEW1")
        page_programme_management.clear_input(page_programme_management.get_input_start_date())
        page_programme_management.get_input_start_date().send_keys(
            str(FormatTime(1, 1, 2022).numerically_formatted_date)
        )
        page_programme_management.clear_input(page_programme_management.get_input_end_date())
        page_programme_management.get_input_end_date().send_keys(FormatTime(1, 10, 2099).numerically_formatted_date)
        page_programme_management.get_button_next().click()
        page_programme_management.get_button_add_time_series_field()
        page_programme_management.get_button_save().click()
        # Check Details page
        page_programme_details.wait_for_text("New name after Edit", page_programme_details.header_title)
        assert FormatTime(1, 1, 2022).date_in_text_format in page_programme_details.get_label_start_date().text
        assert FormatTime(1, 10, 2099).date_in_text_format in page_programme_details.get_label_end_date().text

    def test_program_details_happy_path(
        self, create_payment_plan: Program, page_programme_details: ProgrammeDetails
    ) -> None:
        page_programme_details.select_global_program_filter("Test For Edit")
        assert "DRAFT" in page_programme_details.get_program_status().text
        assert "0" in page_programme_details.get_label_program_size().text
        page_programme_details.get_button_activate_program().click()
        page_programme_details.get_button_activate_program_modal().click()
        for _ in range(10):
            if "ACTIVE" in page_programme_details.get_program_status().text:
                break
            sleep(1)
        else:
            assert "ACTIVE" in page_programme_details.get_program_status().text
        create_custom_household()
        page_programme_details.driver.refresh()
        assert "1" in page_programme_details.get_label_program_size().text
        assert "Programme Cycles" in page_programme_details.get_table_title().text
        assert "Rows per page: 5 1–1 of 1" in page_programme_details.get_table_pagination().text.replace("\n", " ")
        page_programme_details.get_button_finish_program().click()
        page_programme_details.click_button_finish_program_popup()
        for _ in range(10):
            if "FINISHED" in page_programme_details.get_program_status().text:
                break
            sleep(1)
        else:
            assert "FINISHED" in page_programme_details.get_program_status().text
        assert "1" in page_programme_details.get_label_program_size().text


@pytest.mark.usefixtures("login")
class TestProgrammeDetails:
    @pytest.mark.xfail(reason="UNSTABLE")
    def test_program_details_check_default_cycle(
        self,
        page_programme_management: ProgrammeManagement,
        page_programme_details: ProgrammeDetails,
    ) -> None:
        # Go to Programme Management
        page_programme_management.get_nav_programme_management().click()
        # Create Programme
        page_programme_management.get_button_new_program().click()
        page_programme_management.get_input_programme_name().send_keys("Test 1234 Program")
        page_programme_management.get_input_start_date().click()
        page_programme_management.get_input_start_date().send_keys(FormatTime(1, 1, 2022).numerically_formatted_date)
        page_programme_management.get_input_end_date().click()
        page_programme_management.get_input_end_date().send_keys(FormatTime(1, 2, 2032).numerically_formatted_date)
        page_programme_management.choose_option_selector("Health")
        page_programme_management.choose_option_data_collecting_type("Partial")
        page_programme_management.get_input_beneficiary_group().click()
        page_programme_management.select_listbox_element("Main Menu")
        page_programme_management.get_button_next().click()
        # 2nd step (Time Series Fields)
        page_programme_management.get_button_add_time_series_field()
        page_programme_management.get_button_next().click()
        # 3rd step (Partners)
        programme_creation_url = page_programme_management.driver.current_url
        page_programme_management.get_button_save().click()
        # Check Details page
        assert "details" in page_programme_details.wait_for_new_url(programme_creation_url).split("/")
        page_programme_details.get_button_activate_program().click()
        page_programme_details.get_button_activate_program_modal().click()
        assert len(page_programme_details.get_program_cycle_row()) == 1
        assert "Draft" in page_programme_details.get_program_cycle_status()[0].text
        assert "-" in page_programme_details.get_program_cycle_end_date()[0].text
        assert "Default Programme Cycle" in page_programme_details.get_program_cycle_title()[0].text

    def test_program_details_edit_default_cycle_by_add_new(
        self,
        standard_program_with_draft_programme_cycle: Program,
        page_programme_details: ProgrammeDetails,
    ) -> None:
        page_programme_details.select_global_program_filter("Active Programme")
        assert "ACTIVE" in page_programme_details.get_program_status().text
        assert "0" in page_programme_details.get_label_program_size().text
        assert "Programme Cycles" in page_programme_details.get_table_title().text
        page_programme_details.get_button_add_new_programme_cycle().click()
        page_programme_details.get_data_picker_filter().click()
        page_programme_details.get_data_picker_filter().send_keys(datetime.now().strftime("%Y-%m-%d"))
        page_programme_details.get_button_next().click()
        page_programme_details.get_input_title().send_keys("Test Title")
        page_programme_details.get_start_date_cycle().click()
        page_programme_details.get_start_date_cycle().send_keys(
            (datetime.now() + relativedelta(days=1)).strftime("%Y-%m-%d")
        )
        page_programme_details.get_end_date_cycle().click()
        page_programme_details.get_end_date_cycle().send_keys(
            (datetime.now() + relativedelta(days=1)).strftime("%Y-%m-%d")
        )
        page_programme_details.get_button_create_program_cycle().click()
        page_programme_details.get_program_cycle_row()
        for _ in range(50):
            if len(page_programme_details.get_program_cycle_row()) == 2:
                break
            sleep(0.1)
        else:
            assert len(page_programme_details.get_program_cycle_row()) == 2

        assert "Draft" in page_programme_details.get_program_cycle_status()[0].text
        assert datetime.now().strftime("%-d %b %Y") in page_programme_details.get_program_cycle_end_date()[0].text
        assert "Default Programme Cycle" in page_programme_details.get_program_cycle_title()[0].text

        assert "Draft" in page_programme_details.get_program_cycle_status()[1].text
        assert (datetime.now() + relativedelta(days=1)).strftime(
            "%-d %b %Y"
        ) in page_programme_details.get_program_cycle_end_date()[1].text
        assert (datetime.now() + relativedelta(days=1)).strftime(
            "%-d %b %Y"
        ) in page_programme_details.get_program_cycle_start_date()[1].text
        assert "Test Title" in page_programme_details.get_program_cycle_title()[1].text

    def test_program_details_add_new_programme_cycle_without_end_date(
        self, standard_active_program: Program, page_programme_details: ProgrammeDetails
    ) -> None:
        page_programme_details.select_global_program_filter("Active Programme")
        assert "ACTIVE" in page_programme_details.get_program_status().text
        page_programme_details.get_button_add_new_programme_cycle().click()
        page_programme_details.get_input_title().send_keys("123")
        page_programme_details.get_start_date_cycle().click()
        page_programme_details.get_start_date_cycle().send_keys(
            (datetime.now() + relativedelta(days=1)).strftime("%Y-%m-%d")
        )
        page_programme_details.get_end_date_cycle().click()
        page_programme_details.get_end_date_cycle().send_keys(
            (datetime.now() + relativedelta(days=10)).strftime("%Y-%m-%d")
        )
        page_programme_details.get_button_create_program_cycle().click()

        page_programme_details.get_button_add_new_programme_cycle().click()
        page_programme_details.get_input_title().send_keys("Test %$ What?")
        page_programme_details.get_start_date_cycle().click()
        page_programme_details.get_start_date_cycle().send_keys(
            (datetime.now() + relativedelta(days=11)).strftime("%Y-%m-%d")
        )
        page_programme_details.get_button_create_program_cycle().click()

        page_programme_details.get_program_cycle_row()

        # TODO TEST REFACTOR
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait

        WebDriverWait(page_programme_details.driver, 10).until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, page_programme_details.program_cycle_row)) == 3
        )

        assert "Draft" in page_programme_details.get_program_cycle_status()[1].text
        assert (datetime.now() + relativedelta(days=1)).strftime(
            "%-d %b %Y"
        ) in page_programme_details.get_program_cycle_start_date()[1].text
        assert (datetime.now() + relativedelta(days=10)).strftime(
            "%-d %b %Y"
        ) in page_programme_details.get_program_cycle_end_date()[1].text
        assert "123" in page_programme_details.get_program_cycle_title()[1].text

        assert "Draft" in page_programme_details.get_program_cycle_status()[2].text
        assert (datetime.now() + relativedelta(days=11)).strftime(
            "%-d %b %Y"
        ) in page_programme_details.get_program_cycle_start_date()[2].text
        assert "-" in page_programme_details.get_program_cycle_end_date()[2].text
        assert "Test %$ What?" in page_programme_details.get_program_cycle_title()[2].text

    def test_program_details_add_new_programme_cycle(
        self, standard_active_program: Program, page_programme_details: ProgrammeDetails
    ) -> None:
        page_programme_details.select_global_program_filter("Active Programme")
        assert "ACTIVE" in page_programme_details.get_program_status().text
        page_programme_details.get_button_add_new_programme_cycle().click()
        page_programme_details.get_input_title().send_keys("123")
        page_programme_details.get_start_date_cycle().click()
        page_programme_details.get_start_date_cycle().send_keys(
            (datetime.now() + relativedelta(days=1)).strftime("%Y-%m-%d")
        )
        page_programme_details.get_end_date_cycle().click()
        page_programme_details.get_end_date_cycle().send_keys(
            (datetime.now() + relativedelta(days=10)).strftime("%Y-%m-%d")
        )
        page_programme_details.get_button_create_program_cycle().click()

        page_programme_details.get_button_add_new_programme_cycle().click()
        page_programme_details.get_input_title().send_keys("Test %$ What?")
        page_programme_details.get_start_date_cycle().click()
        page_programme_details.get_start_date_cycle().send_keys(
            (datetime.now() + relativedelta(days=11)).strftime("%Y-%m-%d")
        )
        page_programme_details.get_end_date_cycle().click()
        page_programme_details.get_end_date_cycle().send_keys(
            (datetime.now() + relativedelta(days=21)).strftime("%Y-%m-%d")
        )
        page_programme_details.get_button_create_program_cycle().click()
        # TODO TEST REFACTOR
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait

        WebDriverWait(page_programme_details.driver, 10).until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, page_programme_details.program_cycle_row)) == 3
        )
        page_programme_details.get_program_cycle_row()

        assert "Draft" in page_programme_details.get_program_cycle_status()[1].text
        assert (datetime.now() + relativedelta(days=1)).strftime(
            "%-d %b %Y"
        ) in page_programme_details.get_program_cycle_start_date()[1].text
        assert (datetime.now() + relativedelta(days=10)).strftime(
            "%-d %b %Y"
        ) in page_programme_details.get_program_cycle_end_date()[1].text
        assert "123" in page_programme_details.get_program_cycle_title()[1].text

        assert "Draft" in page_programme_details.get_program_cycle_status()[2].text
        assert (datetime.now() + relativedelta(days=11)).strftime(
            "%-d %b %Y"
        ) in page_programme_details.get_program_cycle_start_date()[2].text
        assert (datetime.now() + relativedelta(days=21)).strftime(
            "%-d %b %Y"
        ) in page_programme_details.get_program_cycle_end_date()[2].text
        assert "Test %$ What?" in page_programme_details.get_program_cycle_title()[2].text

    def test_program_details_edit_programme_cycle(
        self,
        standard_active_program_with_draft_program_cycle: Program,
        page_programme_details: ProgrammeDetails,
    ) -> None:
        page_programme_details.select_global_program_filter("Active Programme")
        page_programme_details.get_button_edit_program_cycle()[0].click()
        page_programme_details.clear_input(page_programme_details.get_input_title())
        page_programme_details.get_input_title().send_keys("Edited title check")
        page_programme_details.get_start_date_cycle().click()
        page_programme_details.get_start_date_cycle().send_keys(
            (datetime.now() + relativedelta(days=11)).strftime("%Y-%m-%d")
        )
        page_programme_details.get_end_date_cycle().click()
        page_programme_details.get_end_date_cycle().send_keys(
            (datetime.now() + relativedelta(days=12)).strftime("%Y-%m-%d")
        )
        page_programme_details.get_button_save().click()
        assert "Draft" in page_programme_details.get_program_cycle_status()[0].text
        start_date = (datetime.now() + relativedelta(days=11)).strftime("%-d %b %Y")
        for _ in range(50):
            if start_date in page_programme_details.get_program_cycle_start_date()[0].text:
                break
            sleep(0.1)
        else:
            assert start_date in page_programme_details.get_program_cycle_start_date()[0].text
        assert (datetime.now() + relativedelta(days=12)).strftime(
            "%-d %b %Y"
        ) in page_programme_details.get_program_cycle_end_date()[0].text
        assert "Edited title check" in page_programme_details.get_program_cycle_title()[0].text

    @pytest.mark.xfail(reason="UNSTABLE")
    def test_program_details_delete_programme_cycle(
        self,
        program_with_three_cycles: Program,
        page_programme_details: ProgrammeDetails,
    ) -> None:
        page_programme_details.select_global_program_filter("ThreeCyclesProgramme")
        for _ in range(50):
            if len(page_programme_details.get_program_cycle_title()) == 3:
                break
            sleep(0.1)
        else:
            assert len(page_programme_details.get_program_cycle_title()) == 3
        program_cycle_1 = page_programme_details.get_program_cycle_title()[0].text
        program_cycle_3 = page_programme_details.get_program_cycle_title()[2].text
        page_programme_details.get_delete_programme_cycle()[1].click()
        page_programme_details.get_button_delete().click()
        for _ in range(50):
            if len(page_programme_details.get_program_cycle_title()) == 3:
                break
            sleep(0.1)
        else:
            assert len(page_programme_details.get_program_cycle_title()) == 2

        assert program_cycle_1 in page_programme_details.get_program_cycle_title()[0].text
        for _ in range(50):
            if program_cycle_3 in page_programme_details.get_program_cycle_title()[1].text:
                break
            sleep(0.1)
        else:
            assert program_cycle_3 in page_programme_details.get_program_cycle_title()[1].text

    def test_program_details_buttons_vs_programme_cycle_status(
        self,
        program_with_different_cycles: Program,
        page_programme_details: ProgrammeDetails,
    ) -> None:
        page_programme_details.select_global_program_filter("ThreeCyclesProgramme")
        for _ in range(50):
            if len(page_programme_details.get_program_cycle_row()) == 3:
                break
            sleep(0.1)
        else:
            assert len(page_programme_details.get_program_cycle_row()) == 3
        assert page_programme_details.get_button_edit_program_cycle()[0]
        assert page_programme_details.get_button_edit_program_cycle()[1]
        with pytest.raises(IndexError):
            assert page_programme_details.get_button_edit_program_cycle()[2]

        assert page_programme_details.get_delete_programme_cycle()[0]
        with pytest.raises(IndexError):
            assert page_programme_details.get_delete_programme_cycle()[1]
        with pytest.raises(IndexError):
            assert page_programme_details.get_delete_programme_cycle()[2]

    @pytest.mark.skip(reason="Unskip after fix 211823")
    def test_program_details_edit_default_cycle_by_add_new_cancel(
        self,
        standard_program_with_draft_programme_cycle: Program,
        page_programme_details: ProgrammeDetails,
    ) -> None:
        page_programme_details.select_global_program_filter("Active Programme")
        assert "ACTIVE" in page_programme_details.get_program_status().text
        assert "0" in page_programme_details.get_label_program_size().text
        assert "Programme Cycles" in page_programme_details.get_table_title().text
        page_programme_details.get_button_add_new_programme_cycle().click()
        page_programme_details.get_data_picker_filter().click()
        page_programme_details.get_data_picker_filter().send_keys(datetime.now().strftime("%Y-%m-%d"))
        page_programme_details.get_button_next().click()
        page_programme_details.get_button_cancel().click()

        assert "Draft" in page_programme_details.get_program_cycle_status()[0].text
        assert datetime.now().strftime("%-d %b %Y") in page_programme_details.get_program_cycle_end_date()[0].text
        assert "Default Programme Cycle" in page_programme_details.get_program_cycle_title()[0].text

        page_programme_details.get_button_add_new_programme_cycle().click()
        page_programme_details.get_input_title().send_keys("Test %$ What?")
        page_programme_details.get_start_date_cycle().click()
        page_programme_details.get_start_date_cycle().send_keys(
            (datetime.now() + relativedelta(days=11)).strftime("%Y-%m-%d")
        )
        page_programme_details.get_end_date_cycle().click()
        page_programme_details.get_end_date_cycle().send_keys(
            (datetime.now() + relativedelta(days=21)).strftime("%Y-%m-%d")
        )
        page_programme_details.get_button_create_program_cycle().click()

        assert "Draft" in page_programme_details.get_program_cycle_status()[2].text
        assert (datetime.now() + relativedelta(days=11)).strftime(
            "%-d %b %Y"
        ) in page_programme_details.get_program_cycle_start_date()[2].text
        assert (datetime.now() + relativedelta(days=21)).strftime(
            "%-d %b %Y"
        ) in page_programme_details.get_program_cycle_end_date()[2].text
        assert "Test %$ What?" in page_programme_details.get_program_cycle_title()[2].text

    @pytest.mark.skip("Unskip after fixing")
    def test_program_details_add_new_cycle_with_wrong_date(
        self,
        standard_active_program_cycle_draft: Program,
        page_programme_details: ProgrammeDetails,
    ) -> None:
        page_programme_details.select_global_program_filter("Active Programme")
        assert "ACTIVE" in page_programme_details.get_program_status().text
        page_programme_details.get_button_add_new_programme_cycle().click()
        page_programme_details.clear_input(page_programme_details.get_input_title())
        page_programme_details.get_input_title().send_keys("New cycle with wrong date")
        page_programme_details.get_start_date_cycle().click()
        page_programme_details.get_start_date_cycle().send_keys(
            (datetime.now() - relativedelta(days=40)).strftime("%Y-%m-%d")
        )
        page_programme_details.get_button_create_program_cycle().click()
        for _ in range(50):
            if (
                "Start Date cannot be before Programme Start Date"
                in page_programme_details.get_start_date_cycle_div().text
            ):
                break
            sleep(0.1)
        assert (
            "Start Date cannot be before Programme Start Date" in page_programme_details.get_start_date_cycle_div().text
        )

        page_programme_details.clear_input(page_programme_details.get_start_date_cycle())
        page_programme_details.get_start_date_cycle().send_keys(
            (datetime.now() - relativedelta(days=1)).strftime("%Y-%m-%d")
        )
        page_programme_details.get_end_date_cycle().click()
        page_programme_details.get_end_date_cycle().send_keys(
            (datetime.now() + relativedelta(days=121)).strftime("%Y-%m-%d")
        )
        page_programme_details.get_button_create_program_cycle().click()
        for _ in range(50):
            if "End Date cannot be after Programme End Date" in page_programme_details.get_end_date_cycle_div().text:
                break
            sleep(0.1)
        assert "End Date cannot be after Programme End Date" in page_programme_details.get_end_date_cycle_div().text
        page_programme_details.clear_input(page_programme_details.get_end_date_cycle())

        page_programme_details.get_end_date_cycle().send_keys(
            (datetime.now() + relativedelta(days=1)).strftime("%Y-%m-%d")
        )
        page_programme_details.get_button_create_program_cycle().click()

        for _ in range(50):
            if "Start date must be after the latest cycle." in page_programme_details.get_start_date_cycle_div().text:
                break
            sleep(0.1)
        assert (
            "Start Date*\nStart date must be after the latest cycle end date."
            in page_programme_details.get_start_date_cycle_div().text
        )
        page_programme_details.get_start_date_cycle().click()
        page_programme_details.get_start_date_cycle().send_keys(
            (datetime.now() + relativedelta(days=1)).strftime("%Y-%m-%d")
        )
        page_programme_details.get_button_create_program_cycle().click()

        page_programme_details.get_button_add_new_programme_cycle()
        page_programme_details.get_program_cycle_row()

        for _ in range(50):
            if len(page_programme_details.get_program_cycle_status()) == 2:
                break
            sleep(0.1)

        assert "Draft" in page_programme_details.get_program_cycle_status()[1].text
        assert (datetime.now() + relativedelta(days=1)).strftime(
            "%-d %b %Y"
        ) in page_programme_details.get_program_cycle_start_date()[1].text
        assert (datetime.now() + relativedelta(days=1)).strftime(
            "%-d %b %Y"
        ) in page_programme_details.get_program_cycle_end_date()[1].text
        assert "New cycle with wrong date" in page_programme_details.get_program_cycle_title()[1].text

    @pytest.mark.skip("Unskip after fixing")
    def test_program_details_edit_cycle_with_wrong_date(
        self,
        program_with_different_cycles: Program,
        page_programme_details: ProgrammeDetails,
    ) -> None:
        page_programme_details.select_global_program_filter("ThreeCyclesProgramme")
        assert "ACTIVE" in page_programme_details.get_program_status().text
        page_programme_details.get_button_edit_program_cycle()[1].click()
        page_programme_details.clear_input(page_programme_details.get_input_title())
        page_programme_details.get_input_title().send_keys("New cycle with wrong date")
        page_programme_details.get_start_date_cycle().click()
        page_programme_details.get_start_date_cycle().send_keys(
            (datetime.now() - relativedelta(days=40)).strftime("%Y-%m-%d")
        )
        page_programme_details.get_button_save().click()
        for _ in range(50):
            if (
                "Start Date*\nStart Date cannot be before Programme Start Date"
                in page_programme_details.get_start_date_cycle_div().text
            ):
                break
            sleep(0.1)
        assert (
            "Start Date*\nStart Date cannot be before Programme Start Date"
            in page_programme_details.get_start_date_cycle_div().text
        )

        page_programme_details.get_start_date_cycle().click()
        page_programme_details.get_start_date_cycle().send_keys(
            (datetime.now() - relativedelta(days=24)).strftime("%Y-%m-%d")
        )
        page_programme_details.get_end_date_cycle().click()
        page_programme_details.get_end_date_cycle().send_keys(
            (datetime.now() + relativedelta(days=121)).strftime("%Y-%m-%d")
        )
        page_programme_details.get_button_save().click()
        for _ in range(50):
            if "End Date cannot be after Programme End Date" in page_programme_details.get_end_date_cycle_div().text:
                break
            sleep(0.1)
        assert "End Date cannot be after Programme End Date" in page_programme_details.get_end_date_cycle_div().text
        page_programme_details.clear_input(page_programme_details.get_end_date_cycle())

        page_programme_details.get_end_date_cycle().send_keys(
            (datetime.now() + relativedelta(days=12)).strftime("%Y-%m-%d")
        )
        page_programme_details.get_button_save().click()

        # ToDo: Lack of information about wrong date 212579
        # for _ in range(50):
        #     if "Programme Cycles' timeframes must not overlap with the provided start date." in page_programme_details.get_start_date_cycle_div().text:
        #         break
        #     sleep(0.1)
        # assert "Programme Cycles' timeframes must not overlap with the provided start date." in page_programme_details.get_start_date_cycle_div().text

        page_programme_details.get_start_date_cycle().click()
        page_programme_details.get_start_date_cycle().send_keys(
            (datetime.now() + relativedelta(days=12)).strftime("%Y-%m-%d")
        )
        page_programme_details.get_button_save().click()

        page_programme_details.get_button_add_new_programme_cycle()
        page_programme_details.get_program_cycle_row()
        assert "Active" in page_programme_details.get_program_cycle_status()[1].text
        for _ in range(50):
            if (datetime.now() + relativedelta(days=12)).strftime(
                "%-d %b %Y"
            ) in page_programme_details.get_program_cycle_start_date()[1].text:
                break
            sleep(0.1)
        else:
            assert (datetime.now() + relativedelta(days=12)).strftime(
                "%-d %b %Y"
            ) in page_programme_details.get_program_cycle_start_date()[1].text
        assert (datetime.now() + relativedelta(days=12)).strftime(
            "%-d %b %Y"
        ) in page_programme_details.get_program_cycle_end_date()[1].text
        assert "New cycle with wrong date" in page_programme_details.get_program_cycle_title()[1].text

    @pytest.mark.skip("Unskip after fix: 212581")
    def test_edit_program_details_with_wrong_date(
        self,
        program_with_different_cycles: Program,
        page_programme_details: ProgrammeDetails,
        page_programme_management: ProgrammeManagement,
    ) -> None:
        page_programme_details.select_global_program_filter("ThreeCyclesProgramme")
        assert "ACTIVE" in page_programme_details.get_program_status().text
        page_programme_details.get_button_edit_program().click()
        page_programme_details.get_select_edit_program_details().click()
        page_programme_management.get_input_programme_name()
        page_programme_management.clear_input(page_programme_management.get_input_start_date())
        page_programme_management.get_input_start_date().send_keys(
            str(FormatTime(1, 1, 2022).numerically_formatted_date)
        )
        page_programme_management.clear_input(page_programme_management.get_input_end_date())
        page_programme_management.get_input_end_date().send_keys(FormatTime(1, 10, 2022).numerically_formatted_date)
        page_programme_management.get_button_next().click()
        page_programme_management.get_button_add_time_series_field()
        programme_creation_url = page_programme_details.driver.current_url
        page_programme_management.get_button_save().click()
        # Check Details page
        with pytest.raises(NoSuchElementException):
            assert "details" in page_programme_details.wait_for_new_url(programme_creation_url).split("/")

    def test_program_details_program_cycle_total_quantities(
        self,
        standard_program_with_draft_programme_cycle: Program,
        page_programme_details: ProgrammeDetails,
    ) -> None:
        page_programme_details.select_global_program_filter("Active Programme")
        assert "ACTIVE" in page_programme_details.get_program_status().text
        assert "1234.99" in page_programme_details.get_program_cycle_total_entitled_quantity_usd()[0].text
        assert "1184.98" in page_programme_details.get_program_cycle_total_undelivered_quantity_usd()[0].text
        assert "50.01" in page_programme_details.get_program_cycle_total_delivered_quantity_usd()[0].text
