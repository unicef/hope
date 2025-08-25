import pytest
from e2e.helpers.fixtures import get_program_with_dct_type_and_name
from e2e.page_object.programme_users.programme_users import ProgrammeUsers

from hope.models.core import DataCollectingType
from hope.models.program import Program

pytestmark = pytest.mark.django_db()


@pytest.fixture
def test_program() -> Program:
    return get_program_with_dct_type_and_name("Test Program", "NORM", DataCollectingType.Type.STANDARD)


@pytest.mark.usefixtures("login")
class TestSmokeAccountabilitySurveys:
    def test_smoke_programme_users(
        self,
        test_program: Program,
        page_programme_users: ProgrammeUsers,
    ) -> None:
        page_programme_users.select_global_program_filter("Test Program")
        page_programme_users.get_nav_programme_users().click()
        assert "Users List" in page_programme_users.get_table_title().text
        assert "Name" in page_programme_users.get_table_label()[1].text
        assert "Status sorted descending" in page_programme_users.get_table_label()[2].text.replace("\n", " ")
        assert "Partner" in page_programme_users.get_table_label()[3].text
        assert "Email" in page_programme_users.get_table_label()[4].text
        assert "Last Login" in page_programme_users.get_table_label()[5].text
        assert "INVITED" in page_programme_users.get_status_container().text
        assert "Rows per page: 10 1–1 of 1" in page_programme_users.get_table_pagination().text.replace("\n", " ")
        page_programme_users.get_arrow_down().click()
        assert "Country / Program / Role" in page_programme_users.get_country_role().text
        assert "Afghanistan / All / Role" in page_programme_users.get_mapped_country_role().text
