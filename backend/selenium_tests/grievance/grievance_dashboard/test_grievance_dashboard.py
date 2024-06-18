import pytest

from page_object.grievance.grievance_dashboard import GrievanceDashboard

from hct_mis_api.apps.program.models import Program
from selenium_tests.helpers.fixtures import get_program_with_dct_type_and_name

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def active_program() -> Program:
    return get_program_with_dct_type_and_name("Test Program", "1234")


@pytest.mark.usefixtures("login")
class TestSmokeGrievanceTickets:
    def test_check_grievance_tickets_user_generated_page(
            self,
            active_program: Program,
            pageGrievanceDashboard: GrievanceDashboard,
    ) -> None:
        pageGrievanceDashboard.getNavGrievance().click()
        pageGrievanceDashboard.getNavGrievanceDashboard().click()
        pageGrievanceDashboard.screenshot("123")
