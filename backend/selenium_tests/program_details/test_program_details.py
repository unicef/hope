from datetime import datetime

from django.conf import settings
from django.core.management import call_command

import pytest
from dateutil.relativedelta import relativedelta
from helpers.date_time_format import FormatTime
from page_object.programme_details.programme_details import ProgrammeDetails
from page_object.programme_management.programme_management import ProgrammeManagement
from selenium.webdriver import Keys

from hct_mis_api.apps.core.fixtures import DataCollectingTypeFactory
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def standard_program() -> Program:
    return get_program_with_dct_type_and_name("Test For Edit", "TEST")


def get_program_with_dct_type_and_name(
    name: str, programme_code: str, dct_type: str = DataCollectingType.Type.STANDARD, status: str = Program.DRAFT
) -> Program:
    BusinessArea.objects.filter(slug="afghanistan").update(is_payment_plan_applicable=True)
    dct = DataCollectingTypeFactory(type=dct_type)
    program = ProgramFactory(
        name=name,
        programme_code=programme_code,
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
        data_collecting_type=dct,
        status=status,
    )
    return program


@pytest.fixture
def create_programs() -> None:
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/core/fixtures/data-selenium.json")
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/program/fixtures/data-cypress.json")
    return


@pytest.mark.usefixtures("login")
class TestProgrammeDetails:
    def test_program_details(self, standard_program: Program, pageProgrammeDetails: ProgrammeDetails) -> None:
        program = Program.objects.get(name="Test For Edit")
        # Go to Programme Details
        pageProgrammeDetails.selectGlobalProgramFilter("Test For Edit").click()
        # Check Details page
        assert "Test For Edit" in pageProgrammeDetails.getHeaderTitle().text
        pageProgrammeDetails.screenshot("0")
        assert "DRAFT" in pageProgrammeDetails.getProgramStatus().text
        assert "Test For Edit" in pageProgrammeDetails.getHeaderTitle().text
        assert "REMOVE" in pageProgrammeDetails.getButtonRemoveProgram().text
        assert "EDIT PROGRAMME" in pageProgrammeDetails.getButtonEditProgram().text
        pageProgrammeDetails.screenshot("1")
        assert "ACTIVATE" in pageProgrammeDetails.getButtonActivateProgram().text
        assert "" in pageProgrammeDetails.getCopyProgram().text
        assert "DRAFT" in pageProgrammeDetails.getProgramStatus().text
        from datetime import date

        today = date.today()
        assert (
            FormatTime(today.day, today.month - 1, today.year).date_in_text_format
            in pageProgrammeDetails.getLabelStartDate().text
        )
        assert (
            FormatTime(today.day, today.month + 1, today.year).date_in_text_format
            in pageProgrammeDetails.getLabelEndDate().text
        )
        assert program.programme_code in pageProgrammeDetails.getLabelProgrammeCode().text
        assert program.sector.replace("_", " ").title() in pageProgrammeDetails.getLabelSelector().text
        assert program.data_collecting_type.label in pageProgrammeDetails.getLabelDataCollectingType().text
        assert (
            program.frequency_of_payments.replace("_", "-").capitalize()
            in pageProgrammeDetails.getLabelFreqOfPayment().text
        )
        assert program.administrative_areas_of_implementation in pageProgrammeDetails.getLabelAdministrativeAreas().text
        assert program.description in pageProgrammeDetails.getLabelDescription().text
        assert "Yes" if program.cash_plus else "No" in pageProgrammeDetails.getLabelCashPlus().text
        assert "Only selected partners within the business area" in pageProgrammeDetails.getLabelPartnerAccess().text
        assert "0" in pageProgrammeDetails.getLabelProgramSize().text

    @pytest.mark.skip("Unskip after fix bug")
    def test_edit_programme_from_details(
        self,
        create_programs: None,
        pageProgrammeDetails: ProgrammeDetails,
        pageProgrammeManagement: ProgrammeManagement,
    ) -> None:
        pageProgrammeDetails.selectGlobalProgramFilter("Test Programm").click()
        pageProgrammeDetails.getButtonEditProgram().click()
        pageProgrammeManagement.getInputProgrammeName().send_keys(Keys.CONTROL + "a")
        pageProgrammeManagement.getInputProgrammeName().send_keys("New name after Edit")
        pageProgrammeManagement.getInputProgrammeCode().send_keys(Keys.CONTROL + "a")
        pageProgrammeManagement.getInputProgrammeCode().send_keys("NEW1")
        pageProgrammeManagement.getInputStartDate().click()
        pageProgrammeManagement.getInputStartDate().send_keys(Keys.CONTROL + "a")
        pageProgrammeManagement.getInputStartDate().send_keys(str(FormatTime(1, 1, 2022).numerically_formatted_date))
        pageProgrammeManagement.getInputEndDate().click()
        pageProgrammeManagement.getInputStartDate().send_keys(Keys.CONTROL + "a")
        pageProgrammeManagement.getInputEndDate().send_keys(FormatTime(1, 10, 2022).numerically_formatted_date)
        pageProgrammeManagement.getButtonNext().click()
        programme_creation_url = pageProgrammeDetails.driver.current_url
        pageProgrammeManagement.getButtonSave().click()
        pageProgrammeManagement.getAccessToProgram().click()
        pageProgrammeManagement.selectWhoAccessToProgram("None of the partners should have access")
        # Check Details page
        assert "details" in pageProgrammeDetails.wait_for_new_url(programme_creation_url).split("/")
        assert "New name after Edit" in pageProgrammeDetails.getHeaderTitle().text
        assert FormatTime(1, 1, 2022).date_in_text_format in pageProgrammeDetails.getLabelStartDate().text
        assert FormatTime(1, 10, 2022).date_in_text_format in pageProgrammeDetails.getLabelEndDate().text

    @pytest.mark.skip("ToDo")
    def test_program_details_activate(self, standard_program: Program, pageProgrammeDetails: ProgrammeDetails) -> None:
        pass

    @pytest.mark.skip("ToDo")
    def test_program_details_finish(self, standard_program: Program, pageProgrammeDetails: ProgrammeDetails) -> None:
        pass

    @pytest.mark.skip("ToDo")
    def test_program_details_reactivate(
        self, standard_program: Program, pageProgrammeDetails: ProgrammeDetails
    ) -> None:
        pass
