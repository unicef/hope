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
from selenium.webdriver import Keys

from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.program.models import BeneficiaryGroup, Program, ProgramCycle

pytestmark = pytest.mark.django_db()


@pytest.fixture
def standard_program() -> Program:
    yield get_program_with_dct_type_and_name("Test For Edit", "TEST")


@pytest.fixture
def program_with_three_cycles() -> Program:
    program = get_program_with_dct_type_and_name(
        "ThreeCyclesProgramme", "cycl", status=Program.ACTIVE, program_cycle_status=ProgramCycle.DRAFT
    )
    ProgramCycleFactory(program=program, status=ProgramCycle.DRAFT)
    ProgramCycleFactory(program=program, status=ProgramCycle.DRAFT)
    program.save()
    yield program


@pytest.fixture
def program_with_different_cycles() -> Program:
    program = get_program_with_dct_type_and_name(
        "ThreeCyclesProgramme", "cycl", status=Program.ACTIVE, program_cycle_status=ProgramCycle.DRAFT
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
        "Active Programme", "9876", status=Program.ACTIVE, program_cycle_status=ProgramCycle.DRAFT
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
    def test_program_details(self, standard_program: Program, pageProgrammeDetails: ProgrammeDetails) -> None:
        program = Program.objects.get(name="Test For Edit")
        # Go to Programme Details
        pageProgrammeDetails.selectGlobalProgramFilter("Test For Edit")
        # Check Details page
        assert "Test For Edit" in pageProgrammeDetails.getHeaderTitle().text
        assert "DRAFT" in pageProgrammeDetails.getProgramStatus().text
        assert "Test For Edit" in pageProgrammeDetails.getHeaderTitle().text
        assert "REMOVE" in pageProgrammeDetails.getButtonRemoveProgram().text
        assert "EDIT PROGRAMME" in pageProgrammeDetails.getButtonEditProgram().text
        assert "ACTIVATE" in pageProgrammeDetails.getButtonActivateProgram().text
        assert "" in pageProgrammeDetails.getCopyProgram().text
        assert "DRAFT" in pageProgrammeDetails.getProgramStatus().text
        assert (datetime.now() - relativedelta(months=1)).strftime(
            "%-d %b %Y"
        ) in pageProgrammeDetails.getLabelStartDate().text
        assert (datetime.now() + relativedelta(months=1)).strftime(
            "%-d %b %Y"
        ) in pageProgrammeDetails.getLabelEndDate().text
        assert program.programme_code in pageProgrammeDetails.getLabelProgrammeCode().text
        assert program.sector.replace("_", " ").title() in pageProgrammeDetails.getLabelSelector().text.title()
        assert program.data_collecting_type.label in pageProgrammeDetails.getLabelDataCollectingType().text
        assert (
            program.frequency_of_payments.replace("_", "-").capitalize()
            in pageProgrammeDetails.getLabelFreqOfPayment().text
        )
        assert program.administrative_areas_of_implementation in pageProgrammeDetails.getLabelAdministrativeAreas().text
        assert program.description in pageProgrammeDetails.getLabelDescription().text
        assert "Yes" if program.cash_plus else "No" in pageProgrammeDetails.getLabelCashPlus().text
        assert "Only Selected Partners within the business area" in pageProgrammeDetails.getLabelPartnerAccess().text
        assert "0" in pageProgrammeDetails.getLabelProgramSize().text

    @pytest.mark.skip(reason="Unskip after REST refactoring is complete")
    def test_edit_programme_from_details(
        self,
        create_programs: None,
        pageProgrammeDetails: ProgrammeDetails,
        pageProgrammeManagement: ProgrammeManagement,
    ) -> None:
        pageProgrammeDetails.selectGlobalProgramFilter("Test Programm")
        pageProgrammeDetails.getButtonEditProgram().click()
        pageProgrammeDetails.getSelectEditProgramDetails().click()
        pageProgrammeManagement.clear_input(pageProgrammeManagement.getInputProgrammeName())
        pageProgrammeManagement.getInputProgrammeName().send_keys("New name after Edit")
        pageProgrammeManagement.clear_input(pageProgrammeManagement.getInputProgrammeCode())
        pageProgrammeManagement.getInputProgrammeCode().send_keys("NEW1")
        pageProgrammeManagement.clear_input(pageProgrammeManagement.getInputStartDate())
        pageProgrammeManagement.getInputStartDate().send_keys(str(FormatTime(1, 1, 2022).numerically_formatted_date))
        pageProgrammeManagement.clear_input(pageProgrammeManagement.getInputEndDate())
        pageProgrammeManagement.getInputEndDate().send_keys(FormatTime(1, 10, 2099).numerically_formatted_date)
        pageProgrammeManagement.getButtonNext().click()
        pageProgrammeManagement.getButtonAddTimeSeriesField()
        pageProgrammeManagement.getButtonSave().click()
        # Check Details page
        pageProgrammeDetails.wait_for_text("New name after Edit", pageProgrammeDetails.headerTitle)
        assert FormatTime(1, 1, 2022).date_in_text_format in pageProgrammeDetails.getLabelStartDate().text
        assert FormatTime(1, 10, 2099).date_in_text_format in pageProgrammeDetails.getLabelEndDate().text

    @pytest.mark.skip(reason="Unskip after REST refactoring is complete")
    def test_program_details_happy_path(
        self, create_payment_plan: Program, pageProgrammeDetails: ProgrammeDetails
    ) -> None:
        pageProgrammeDetails.selectGlobalProgramFilter("Test For Edit")
        assert "DRAFT" in pageProgrammeDetails.getProgramStatus().text
        assert "0" in pageProgrammeDetails.getLabelProgramSize().text
        pageProgrammeDetails.getButtonActivateProgram().click()
        pageProgrammeDetails.getButtonActivateProgramModal().click()
        for _ in range(10):
            if "ACTIVE" in pageProgrammeDetails.getProgramStatus().text:
                break
            sleep(1)
        else:
            assert "ACTIVE" in pageProgrammeDetails.getProgramStatus().text
        create_custom_household()
        pageProgrammeDetails.driver.refresh()
        assert "1" in pageProgrammeDetails.getLabelProgramSize().text
        assert "Programme Cycles" in pageProgrammeDetails.getTableTitle().text
        assert "Rows per page: 5 1–1 of 1" in pageProgrammeDetails.getTablePagination().text.replace("\n", " ")
        pageProgrammeDetails.getButtonFinishProgram().click()
        pageProgrammeDetails.clickButtonFinishProgramPopup()
        for _ in range(10):
            if "FINISHED" in pageProgrammeDetails.getProgramStatus().text:
                break
            sleep(1)
        else:
            assert "FINISHED" in pageProgrammeDetails.getProgramStatus().text
        assert "1" in pageProgrammeDetails.getLabelProgramSize().text


@pytest.mark.usefixtures("login")
class TestProgrammeDetails:
    @pytest.mark.xfail(reason="UNSTABLE")
    def test_program_details_check_default_cycle(
        self, pageProgrammeManagement: ProgrammeManagement, pageProgrammeDetails: ProgrammeDetails
    ) -> None:
        # Go to Programme Management
        pageProgrammeManagement.getNavProgrammeManagement().click()
        # Create Programme
        pageProgrammeManagement.getButtonNewProgram().click()
        pageProgrammeManagement.getInputProgrammeName().send_keys("Test 1234 Program")
        pageProgrammeManagement.getInputStartDate().click()
        pageProgrammeManagement.getInputStartDate().send_keys(FormatTime(1, 1, 2022).numerically_formatted_date)
        pageProgrammeManagement.getInputEndDate().click()
        pageProgrammeManagement.getInputEndDate().send_keys(FormatTime(1, 2, 2032).numerically_formatted_date)
        pageProgrammeManagement.chooseOptionSelector("Health")
        pageProgrammeManagement.chooseOptionDataCollectingType("Partial")
        pageProgrammeManagement.getInputBeneficiaryGroup().click()
        pageProgrammeManagement.select_listbox_element("Main Menu")
        pageProgrammeManagement.getButtonNext().click()
        # 2nd step (Time Series Fields)
        pageProgrammeManagement.getButtonAddTimeSeriesField()
        pageProgrammeManagement.getButtonNext().click()
        # 3rd step (Partners)
        programme_creation_url = pageProgrammeManagement.driver.current_url
        pageProgrammeManagement.getButtonSave().click()
        # Check Details page
        assert "details" in pageProgrammeDetails.wait_for_new_url(programme_creation_url).split("/")
        pageProgrammeDetails.getButtonActivateProgram().click()
        pageProgrammeDetails.getButtonActivateProgramModal().click()
        assert 1 == len(pageProgrammeDetails.getProgramCycleRow())
        assert "Draft" in pageProgrammeDetails.getProgramCycleStatus()[0].text
        assert "-" in pageProgrammeDetails.getProgramCycleEndDate()[0].text
        assert "Default Programme Cycle" in pageProgrammeDetails.getProgramCycleTitle()[0].text

    def test_program_details_edit_default_cycle_by_add_new(
        self, standard_program_with_draft_programme_cycle: Program, pageProgrammeDetails: ProgrammeDetails
    ) -> None:
        pageProgrammeDetails.selectGlobalProgramFilter("Active Programme")
        assert "ACTIVE" in pageProgrammeDetails.getProgramStatus().text
        assert "0" in pageProgrammeDetails.getLabelProgramSize().text
        assert "Programme Cycles" in pageProgrammeDetails.getTableTitle().text
        pageProgrammeDetails.getButtonAddNewProgrammeCycle().click()
        pageProgrammeDetails.getDataPickerFilter().click()
        pageProgrammeDetails.getDataPickerFilter().send_keys(datetime.now().strftime("%Y-%m-%d"))
        pageProgrammeDetails.getButtonNext().click()
        pageProgrammeDetails.getInputTitle().send_keys("Test Title")
        pageProgrammeDetails.getStartDateCycle().click()
        pageProgrammeDetails.getStartDateCycle().send_keys(
            (datetime.now() + relativedelta(days=1)).strftime("%Y-%m-%d")
        )
        pageProgrammeDetails.getEndDateCycle().click()
        pageProgrammeDetails.getEndDateCycle().send_keys((datetime.now() + relativedelta(days=1)).strftime("%Y-%m-%d"))
        pageProgrammeDetails.getButtonCreateProgramCycle().click()
        pageProgrammeDetails.getProgramCycleRow()
        for _ in range(50):
            if 2 == len(pageProgrammeDetails.getProgramCycleRow()):
                break
            sleep(0.1)
        else:
            assert 2 == len(pageProgrammeDetails.getProgramCycleRow())

        assert "Draft" in pageProgrammeDetails.getProgramCycleStatus()[0].text
        assert datetime.now().strftime("%-d %b %Y") in pageProgrammeDetails.getProgramCycleEndDate()[0].text
        assert "Default Programme Cycle" in pageProgrammeDetails.getProgramCycleTitle()[0].text

        assert "Draft" in pageProgrammeDetails.getProgramCycleStatus()[1].text
        assert (datetime.now() + relativedelta(days=1)).strftime(
            "%-d %b %Y"
        ) in pageProgrammeDetails.getProgramCycleEndDate()[1].text
        assert (datetime.now() + relativedelta(days=1)).strftime(
            "%-d %b %Y"
        ) in pageProgrammeDetails.getProgramCycleStartDate()[1].text
        assert "Test Title" in pageProgrammeDetails.getProgramCycleTitle()[1].text

    def test_program_details_add_new_programme_cycle_without_end_date(
        self, standard_active_program: Program, pageProgrammeDetails: ProgrammeDetails
    ) -> None:
        pageProgrammeDetails.selectGlobalProgramFilter("Active Programme")
        assert "ACTIVE" in pageProgrammeDetails.getProgramStatus().text
        pageProgrammeDetails.getButtonAddNewProgrammeCycle().click()
        pageProgrammeDetails.getInputTitle().send_keys("123")
        pageProgrammeDetails.getStartDateCycle().click()
        pageProgrammeDetails.getStartDateCycle().send_keys(
            (datetime.now() + relativedelta(days=1)).strftime("%Y-%m-%d")
        )
        pageProgrammeDetails.getEndDateCycle().click()
        pageProgrammeDetails.getEndDateCycle().send_keys((datetime.now() + relativedelta(days=10)).strftime("%Y-%m-%d"))
        pageProgrammeDetails.getButtonCreateProgramCycle().click()

        pageProgrammeDetails.getButtonAddNewProgrammeCycle().click()
        pageProgrammeDetails.getInputTitle().send_keys("Test %$ What?")
        pageProgrammeDetails.getStartDateCycle().click()
        pageProgrammeDetails.getStartDateCycle().send_keys(
            (datetime.now() + relativedelta(days=11)).strftime("%Y-%m-%d")
        )
        pageProgrammeDetails.getButtonCreateProgramCycle().click()

        pageProgrammeDetails.getProgramCycleRow()

        # TODO TEST REFACTOR
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait

        WebDriverWait(pageProgrammeDetails.driver, 10).until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, pageProgrammeDetails.programCycleRow)) == 3
        )

        assert "Draft" in pageProgrammeDetails.getProgramCycleStatus()[1].text
        assert (datetime.now() + relativedelta(days=1)).strftime(
            "%-d %b %Y"
        ) in pageProgrammeDetails.getProgramCycleStartDate()[1].text
        assert (datetime.now() + relativedelta(days=10)).strftime(
            "%-d %b %Y"
        ) in pageProgrammeDetails.getProgramCycleEndDate()[1].text
        assert "123" in pageProgrammeDetails.getProgramCycleTitle()[1].text

        assert "Draft" in pageProgrammeDetails.getProgramCycleStatus()[2].text
        assert (datetime.now() + relativedelta(days=11)).strftime(
            "%-d %b %Y"
        ) in pageProgrammeDetails.getProgramCycleStartDate()[2].text
        assert "-" in pageProgrammeDetails.getProgramCycleEndDate()[2].text
        assert "Test %$ What?" in pageProgrammeDetails.getProgramCycleTitle()[2].text

    def test_program_details_add_new_programme_cycle(
        self, standard_active_program: Program, pageProgrammeDetails: ProgrammeDetails
    ) -> None:
        pageProgrammeDetails.selectGlobalProgramFilter("Active Programme")
        assert "ACTIVE" in pageProgrammeDetails.getProgramStatus().text
        pageProgrammeDetails.getButtonAddNewProgrammeCycle().click()
        pageProgrammeDetails.getInputTitle().send_keys("123")
        pageProgrammeDetails.getStartDateCycle().click()
        pageProgrammeDetails.getStartDateCycle().send_keys(
            (datetime.now() + relativedelta(days=1)).strftime("%Y-%m-%d")
        )
        pageProgrammeDetails.getEndDateCycle().click()
        pageProgrammeDetails.getEndDateCycle().send_keys((datetime.now() + relativedelta(days=10)).strftime("%Y-%m-%d"))
        pageProgrammeDetails.getButtonCreateProgramCycle().click()

        pageProgrammeDetails.getButtonAddNewProgrammeCycle().click()
        pageProgrammeDetails.getInputTitle().send_keys("Test %$ What?")
        pageProgrammeDetails.getStartDateCycle().click()
        pageProgrammeDetails.getStartDateCycle().send_keys(
            (datetime.now() + relativedelta(days=11)).strftime("%Y-%m-%d")
        )
        pageProgrammeDetails.getEndDateCycle().click()
        pageProgrammeDetails.getEndDateCycle().send_keys((datetime.now() + relativedelta(days=21)).strftime("%Y-%m-%d"))
        pageProgrammeDetails.getButtonCreateProgramCycle().click()
        # TODO TEST REFACTOR
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait

        WebDriverWait(pageProgrammeDetails.driver, 10).until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, pageProgrammeDetails.programCycleRow)) == 3
        )
        pageProgrammeDetails.getProgramCycleRow()

        assert "Draft" in pageProgrammeDetails.getProgramCycleStatus()[1].text
        assert (datetime.now() + relativedelta(days=1)).strftime(
            "%-d %b %Y"
        ) in pageProgrammeDetails.getProgramCycleStartDate()[1].text
        assert (datetime.now() + relativedelta(days=10)).strftime(
            "%-d %b %Y"
        ) in pageProgrammeDetails.getProgramCycleEndDate()[1].text
        assert "123" in pageProgrammeDetails.getProgramCycleTitle()[1].text

        assert "Draft" in pageProgrammeDetails.getProgramCycleStatus()[2].text
        assert (datetime.now() + relativedelta(days=11)).strftime(
            "%-d %b %Y"
        ) in pageProgrammeDetails.getProgramCycleStartDate()[2].text
        assert (datetime.now() + relativedelta(days=21)).strftime(
            "%-d %b %Y"
        ) in pageProgrammeDetails.getProgramCycleEndDate()[2].text
        assert "Test %$ What?" in pageProgrammeDetails.getProgramCycleTitle()[2].text

    @pytest.mark.skip(reason="Unskip after REST refactoring is complete")
    def test_program_details_edit_programme_cycle(
        self, standard_active_program_with_draft_program_cycle: Program, pageProgrammeDetails: ProgrammeDetails
    ) -> None:
        pageProgrammeDetails.selectGlobalProgramFilter("Active Programme")
        pageProgrammeDetails.getButtonEditProgramCycle()[0].click()
        pageProgrammeDetails.getInputTitle().send_keys(Keys.CONTROL, "a")
        pageProgrammeDetails.getInputTitle().send_keys("Edited title check")
        pageProgrammeDetails.getStartDateCycle().click()
        pageProgrammeDetails.getStartDateCycle().send_keys(
            (datetime.now() + relativedelta(days=11)).strftime("%Y-%m-%d")
        )
        pageProgrammeDetails.getEndDateCycle().click()
        pageProgrammeDetails.getEndDateCycle().send_keys((datetime.now() + relativedelta(days=12)).strftime("%Y-%m-%d"))
        pageProgrammeDetails.getButtonSave().click()
        assert "Draft" in pageProgrammeDetails.getProgramCycleStatus()[0].text
        start_date = (datetime.now() + relativedelta(days=11)).strftime("%-d %b %Y")
        for _ in range(50):
            if start_date in pageProgrammeDetails.getProgramCycleStartDate()[0].text:
                break
            sleep(0.1)
        else:
            assert start_date in pageProgrammeDetails.getProgramCycleStartDate()[0].text
        assert (datetime.now() + relativedelta(days=12)).strftime(
            "%-d %b %Y"
        ) in pageProgrammeDetails.getProgramCycleEndDate()[0].text
        assert "Edited title check" in pageProgrammeDetails.getProgramCycleTitle()[0].text

    @pytest.mark.xfail(reason="UNSTABLE")
    def test_program_details_delete_programme_cycle(
        self, program_with_three_cycles: Program, pageProgrammeDetails: ProgrammeDetails
    ) -> None:
        pageProgrammeDetails.selectGlobalProgramFilter("ThreeCyclesProgramme")
        for _ in range(50):
            if 3 == len(pageProgrammeDetails.getProgramCycleTitle()):
                break
            sleep(0.1)
        else:
            assert 3 == len(pageProgrammeDetails.getProgramCycleTitle())
        program_cycle_1 = pageProgrammeDetails.getProgramCycleTitle()[0].text
        program_cycle_3 = pageProgrammeDetails.getProgramCycleTitle()[2].text
        pageProgrammeDetails.getDeleteProgrammeCycle()[1].click()
        pageProgrammeDetails.getButtonDelete().click()
        for _ in range(50):
            if 3 == len(pageProgrammeDetails.getProgramCycleTitle()):
                break
            sleep(0.1)
        else:
            assert 2 == len(pageProgrammeDetails.getProgramCycleTitle())

        assert program_cycle_1 in pageProgrammeDetails.getProgramCycleTitle()[0].text
        for _ in range(50):
            if program_cycle_3 in pageProgrammeDetails.getProgramCycleTitle()[1].text:
                break
            sleep(0.1)
        else:
            assert program_cycle_3 in pageProgrammeDetails.getProgramCycleTitle()[1].text

    def test_program_details_buttons_vs_programme_cycle_status(
        self, program_with_different_cycles: Program, pageProgrammeDetails: ProgrammeDetails
    ) -> None:
        pageProgrammeDetails.selectGlobalProgramFilter("ThreeCyclesProgramme")
        for _ in range(50):
            if 3 == len(pageProgrammeDetails.getProgramCycleRow()):
                break
            sleep(0.1)
        else:
            assert 3 == len(pageProgrammeDetails.getProgramCycleRow())
        assert pageProgrammeDetails.getButtonEditProgramCycle()[0]
        assert pageProgrammeDetails.getButtonEditProgramCycle()[1]
        with pytest.raises(Exception):
            assert pageProgrammeDetails.getButtonEditProgramCycle()[2]

        assert pageProgrammeDetails.getDeleteProgrammeCycle()[0]
        with pytest.raises(Exception):
            assert pageProgrammeDetails.getDeleteProgrammeCycle()[1]
        with pytest.raises(Exception):
            assert pageProgrammeDetails.getDeleteProgrammeCycle()[2]

    @pytest.mark.skip(reason="Unskip after fix 211823")
    def test_program_details_edit_default_cycle_by_add_new_cancel(
        self, standard_program_with_draft_programme_cycle: Program, pageProgrammeDetails: ProgrammeDetails
    ) -> None:
        pageProgrammeDetails.selectGlobalProgramFilter("Active Programme")
        assert "ACTIVE" in pageProgrammeDetails.getProgramStatus().text
        assert "0" in pageProgrammeDetails.getLabelProgramSize().text
        assert "Programme Cycles" in pageProgrammeDetails.getTableTitle().text
        pageProgrammeDetails.getButtonAddNewProgrammeCycle().click()
        pageProgrammeDetails.getDataPickerFilter().click()
        pageProgrammeDetails.getDataPickerFilter().send_keys(datetime.now().strftime("%Y-%m-%d"))
        pageProgrammeDetails.getButtonNext().click()
        pageProgrammeDetails.getButtonCancel().click()

        assert "Draft" in pageProgrammeDetails.getProgramCycleStatus()[0].text
        assert datetime.now().strftime("%-d %b %Y") in pageProgrammeDetails.getProgramCycleEndDate()[0].text
        assert "Default Programme Cycle" in pageProgrammeDetails.getProgramCycleTitle()[0].text

        pageProgrammeDetails.getButtonAddNewProgrammeCycle().click()
        pageProgrammeDetails.getInputTitle().send_keys("Test %$ What?")
        pageProgrammeDetails.getStartDateCycle().click()
        pageProgrammeDetails.getStartDateCycle().send_keys(
            (datetime.now() + relativedelta(days=11)).strftime("%Y-%m-%d")
        )
        pageProgrammeDetails.getEndDateCycle().click()
        pageProgrammeDetails.getEndDateCycle().send_keys((datetime.now() + relativedelta(days=21)).strftime("%Y-%m-%d"))
        pageProgrammeDetails.getButtonCreateProgramCycle().click()

        assert "Draft" in pageProgrammeDetails.getProgramCycleStatus()[2].text
        assert (datetime.now() + relativedelta(days=11)).strftime(
            "%-d %b %Y"
        ) in pageProgrammeDetails.getProgramCycleStartDate()[2].text
        assert (datetime.now() + relativedelta(days=21)).strftime(
            "%-d %b %Y"
        ) in pageProgrammeDetails.getProgramCycleEndDate()[2].text
        assert "Test %$ What?" in pageProgrammeDetails.getProgramCycleTitle()[2].text

    @pytest.mark.skip("Unskip after fixing")
    def test_program_details_add_new_cycle_with_wrong_date(
        self, standard_active_program_cycle_draft: Program, pageProgrammeDetails: ProgrammeDetails
    ) -> None:
        pageProgrammeDetails.selectGlobalProgramFilter("Active Programme")
        assert "ACTIVE" in pageProgrammeDetails.getProgramStatus().text
        pageProgrammeDetails.getButtonAddNewProgrammeCycle().click()
        pageProgrammeDetails.clear_input(pageProgrammeDetails.getInputTitle())
        pageProgrammeDetails.getInputTitle().send_keys("New cycle with wrong date")
        pageProgrammeDetails.getStartDateCycle().click()
        pageProgrammeDetails.getStartDateCycle().send_keys(
            (datetime.now() - relativedelta(days=40)).strftime("%Y-%m-%d")
        )
        pageProgrammeDetails.getButtonCreateProgramCycle().click()
        for _ in range(50):
            if "Start Date cannot be before Programme Start Date" in pageProgrammeDetails.getStartDateCycleDiv().text:
                break
            sleep(0.1)
        assert "Start Date cannot be before Programme Start Date" in pageProgrammeDetails.getStartDateCycleDiv().text

        pageProgrammeDetails.clear_input(pageProgrammeDetails.getStartDateCycle())
        pageProgrammeDetails.getStartDateCycle().send_keys(
            (datetime.now() - relativedelta(days=1)).strftime("%Y-%m-%d")
        )
        pageProgrammeDetails.getEndDateCycle().click()
        pageProgrammeDetails.getEndDateCycle().send_keys(
            (datetime.now() + relativedelta(days=121)).strftime("%Y-%m-%d")
        )
        pageProgrammeDetails.getButtonCreateProgramCycle().click()
        for _ in range(50):
            if "End Date cannot be after Programme End Date" in pageProgrammeDetails.getEndDateCycleDiv().text:
                break
            sleep(0.1)
        assert "End Date cannot be after Programme End Date" in pageProgrammeDetails.getEndDateCycleDiv().text
        pageProgrammeDetails.clear_input(pageProgrammeDetails.getEndDateCycle())

        pageProgrammeDetails.getEndDateCycle().send_keys((datetime.now() + relativedelta(days=1)).strftime("%Y-%m-%d"))
        pageProgrammeDetails.getButtonCreateProgramCycle().click()

        for _ in range(50):
            if "Start date must be after the latest cycle." in pageProgrammeDetails.getStartDateCycleDiv().text:
                break
            sleep(0.1)
        assert (
            "Start Date*\nStart date must be after the latest cycle end date."
            in pageProgrammeDetails.getStartDateCycleDiv().text
        )
        pageProgrammeDetails.getStartDateCycle().click()
        pageProgrammeDetails.getStartDateCycle().send_keys(
            (datetime.now() + relativedelta(days=1)).strftime("%Y-%m-%d")
        )
        pageProgrammeDetails.getButtonCreateProgramCycle().click()

        pageProgrammeDetails.getButtonAddNewProgrammeCycle()
        pageProgrammeDetails.getProgramCycleRow()

        for _ in range(50):
            if 2 == len(pageProgrammeDetails.getProgramCycleStatus()):
                break
            sleep(0.1)

        assert "Draft" in pageProgrammeDetails.getProgramCycleStatus()[1].text
        assert (datetime.now() + relativedelta(days=1)).strftime(
            "%-d %b %Y"
        ) in pageProgrammeDetails.getProgramCycleStartDate()[1].text
        assert (datetime.now() + relativedelta(days=1)).strftime(
            "%-d %b %Y"
        ) in pageProgrammeDetails.getProgramCycleEndDate()[1].text
        assert "New cycle with wrong date" in pageProgrammeDetails.getProgramCycleTitle()[1].text

    @pytest.mark.skip("Unskip after fixing")
    def test_program_details_edit_cycle_with_wrong_date(
        self, program_with_different_cycles: Program, pageProgrammeDetails: ProgrammeDetails
    ) -> None:
        pageProgrammeDetails.selectGlobalProgramFilter("ThreeCyclesProgramme")
        assert "ACTIVE" in pageProgrammeDetails.getProgramStatus().text
        pageProgrammeDetails.getButtonEditProgramCycle()[1].click()
        pageProgrammeDetails.clear_input(pageProgrammeDetails.getInputTitle())
        pageProgrammeDetails.getInputTitle().send_keys("New cycle with wrong date")
        pageProgrammeDetails.getStartDateCycle().click()
        pageProgrammeDetails.getStartDateCycle().send_keys(
            (datetime.now() - relativedelta(days=40)).strftime("%Y-%m-%d")
        )
        pageProgrammeDetails.getButtonSave().click()
        for _ in range(50):
            if (
                "Start Date*\nStart Date cannot be before Programme Start Date"
                in pageProgrammeDetails.getStartDateCycleDiv().text
            ):
                break
            sleep(0.1)
        assert (
            "Start Date*\nStart Date cannot be before Programme Start Date"
            in pageProgrammeDetails.getStartDateCycleDiv().text
        )

        pageProgrammeDetails.getStartDateCycle().click()
        pageProgrammeDetails.getStartDateCycle().send_keys(
            (datetime.now() - relativedelta(days=24)).strftime("%Y-%m-%d")
        )
        pageProgrammeDetails.getEndDateCycle().click()
        pageProgrammeDetails.getEndDateCycle().send_keys(
            (datetime.now() + relativedelta(days=121)).strftime("%Y-%m-%d")
        )
        pageProgrammeDetails.getButtonSave().click()
        for _ in range(50):
            if "End Date cannot be after Programme End Date" in pageProgrammeDetails.getEndDateCycleDiv().text:
                break
            sleep(0.1)
        assert "End Date cannot be after Programme End Date" in pageProgrammeDetails.getEndDateCycleDiv().text
        pageProgrammeDetails.clear_input(pageProgrammeDetails.getEndDateCycle())

        pageProgrammeDetails.getEndDateCycle().send_keys((datetime.now() + relativedelta(days=12)).strftime("%Y-%m-%d"))
        pageProgrammeDetails.getButtonSave().click()

        # ToDo: Lack of information about wrong date 212579
        # for _ in range(50):
        #     if "Programme Cycles' timeframes must not overlap with the provided start date." in pageProgrammeDetails.getStartDateCycleDiv().text:
        #         break
        #     sleep(0.1)
        # assert "Programme Cycles' timeframes must not overlap with the provided start date." in pageProgrammeDetails.getStartDateCycleDiv().text

        pageProgrammeDetails.getStartDateCycle().click()
        pageProgrammeDetails.getStartDateCycle().send_keys(
            (datetime.now() + relativedelta(days=12)).strftime("%Y-%m-%d")
        )
        pageProgrammeDetails.getButtonSave().click()

        pageProgrammeDetails.getButtonAddNewProgrammeCycle()
        pageProgrammeDetails.getProgramCycleRow()
        assert "Active" in pageProgrammeDetails.getProgramCycleStatus()[1].text
        for _ in range(50):
            if (datetime.now() + relativedelta(days=12)).strftime(
                "%-d %b %Y"
            ) in pageProgrammeDetails.getProgramCycleStartDate()[1].text:
                break
            sleep(0.1)
        else:
            assert (datetime.now() + relativedelta(days=12)).strftime(
                "%-d %b %Y"
            ) in pageProgrammeDetails.getProgramCycleStartDate()[1].text
        assert (datetime.now() + relativedelta(days=12)).strftime(
            "%-d %b %Y"
        ) in pageProgrammeDetails.getProgramCycleEndDate()[1].text
        assert "New cycle with wrong date" in pageProgrammeDetails.getProgramCycleTitle()[1].text

    @pytest.mark.skip("Unskip after fix: 212581")
    def test_edit_program_details_with_wrong_date(
        self,
        program_with_different_cycles: Program,
        pageProgrammeDetails: ProgrammeDetails,
        pageProgrammeManagement: ProgrammeManagement,
    ) -> None:
        pageProgrammeDetails.selectGlobalProgramFilter("ThreeCyclesProgramme")
        assert "ACTIVE" in pageProgrammeDetails.getProgramStatus().text
        pageProgrammeDetails.getButtonEditProgram().click()
        pageProgrammeDetails.getSelectEditProgramDetails().click()
        pageProgrammeManagement.getInputProgrammeName()
        pageProgrammeManagement.clear_input(pageProgrammeManagement.getInputStartDate())
        pageProgrammeManagement.getInputStartDate().send_keys(str(FormatTime(1, 1, 2022).numerically_formatted_date))
        pageProgrammeManagement.clear_input(pageProgrammeManagement.getInputEndDate())
        pageProgrammeManagement.getInputEndDate().send_keys(FormatTime(1, 10, 2022).numerically_formatted_date)
        pageProgrammeManagement.getButtonNext().click()
        pageProgrammeManagement.getButtonAddTimeSeriesField()
        programme_creation_url = pageProgrammeDetails.driver.current_url
        pageProgrammeManagement.getButtonSave().click()
        # Check Details page
        with pytest.raises(Exception):
            assert "details" in pageProgrammeDetails.wait_for_new_url(programme_creation_url).split("/")

    def test_program_details_program_cycle_total_quantities(
        self, standard_program_with_draft_programme_cycle: Program, pageProgrammeDetails: ProgrammeDetails
    ) -> None:
        pageProgrammeDetails.selectGlobalProgramFilter("Active Programme")
        assert "ACTIVE" in pageProgrammeDetails.getProgramStatus().text
        assert "1234.99" in pageProgrammeDetails.getProgramCycleTotalEntitledQuantityUSD()[0].text
        assert "1184.98" in pageProgrammeDetails.getProgramCycleTotalUndeliveredQuantityUSD()[0].text
        assert "50.01" in pageProgrammeDetails.getProgramCycleTotalDeliveredQuantityUSD()[0].text
