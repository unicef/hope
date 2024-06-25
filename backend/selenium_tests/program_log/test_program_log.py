import pytest

from hct_mis_api.apps.program.models import Program
from helpers.fixtures import get_program_with_dct_type_and_name

from page_object.program_log.payment_log import ProgramLog

from page_object.programme_details.programme_details import ProgrammeDetails

pytestmark = pytest.mark.django_db(transaction=True)

@pytest.fixture
def standard_program() -> Program:
    return get_program_with_dct_type_and_name("Test Program", "TEST")


@pytest.mark.usefixtures("login")
class TestProgrammeLog:
    def test_smoke_program_log(self, standard_program: Program, pageProgramLog: ProgramLog, pageProgrammeDetails: ProgrammeDetails) -> None:
        pageProgrammeDetails.selectGlobalProgramFilter("Test Program").click()
        pageProgrammeDetails.getButtonFinishProgram().click()
        pageProgrammeDetails.getButtonFinishProgramPopup().click()
        pageProgramLog.screenshot("1")
        pageProgramLog.getNavProgramLog().click()

        pageProgramLog.screenshot("2")
        from selenium_tests.tools.tag_name_finder import printing
        printing("Mapping", pageProgramLog.driver)
        printing("Methods", pageProgramLog.driver)
        printing("Assert", pageProgramLog.driver)
