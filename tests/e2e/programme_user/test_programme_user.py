import pytest
from e2e.helpers.fixtures import get_program_with_dct_type_and_name
from e2e.page_object.programme_users.programme_users import ProgrammeUsers

from hct_mis_api.apps.core.models import DataCollectingType
from hct_mis_api.apps.program.models import Program

pytestmark = pytest.mark.django_db()


@pytest.fixture
def test_program() -> Program:
    return get_program_with_dct_type_and_name("Test Program", "NORM", DataCollectingType.Type.STANDARD)


@pytest.mark.usefixtures("login")
class TestSmokeAccountabilitySurveys:
    def test_smoke_programme_users(
        self,
        test_program: Program,
        pageProgrammeUsers: ProgrammeUsers,
    ) -> None:
        pageProgrammeUsers.selectGlobalProgramFilter("Test Program")
        pageProgrammeUsers.getNavProgrammeUsers().click()
        assert "Users List" in pageProgrammeUsers.getTableTitle().text
        assert "Name" in pageProgrammeUsers.getTableLabel()[1].text
        assert "Status sorted descending" in pageProgrammeUsers.getTableLabel()[2].text.replace("\n", " ")
        assert "Partner" in pageProgrammeUsers.getTableLabel()[3].text
        assert "Email" in pageProgrammeUsers.getTableLabel()[4].text
        assert "Last Login" in pageProgrammeUsers.getTableLabel()[5].text
        assert "INVITED" in pageProgrammeUsers.getStatusContainer().text
        assert "Rows per page: 10 1–1 of 1" in pageProgrammeUsers.getTablePagination().text.replace("\n", " ")
        pageProgrammeUsers.getArrowDown().click()
        assert "Country / Role" in pageProgrammeUsers.getCountryRole().text
        assert "Afghanistan / Role" in pageProgrammeUsers.getMappedCountryRole().text
