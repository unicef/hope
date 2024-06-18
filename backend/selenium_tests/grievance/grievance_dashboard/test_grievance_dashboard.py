import pytest

from page_object.grievance.grievance_dashboard import GrievanceDashboard

from hct_mis_api.apps.program.models import Program
from selenium_tests.helpers.fixtures import get_program_with_dct_type_and_name

from hct_mis_api.apps.grievance.models import GrievanceTicket

from hct_mis_api.apps.core.models import BusinessArea

from hct_mis_api.apps.account.models import User

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def active_program() -> Program:
    return get_program_with_dct_type_and_name("Test Program", "1234")


@pytest.fixture
def add_grievances() -> None:
    generate_grievance("GRV-0000001")


def generate_grievance(unicef_id: str,
                       status: str = GrievanceTicket.STATUS_NEW,
                       category: str = GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
                       created_by: User = User.objects.first(),
                       assigned_to: User = User.objects.first(),
                       business_area: BusinessArea = BusinessArea.objects.filter(slug="afghanistan").first(),
                       priority: int = 1,
                       urgency: int = 1,
                       household_unicef_id: str = "HH-20-0000.0001",
                       ):
    GrievanceTicket.objects.create(
        **{
            "business_area": business_area,
            "unicef_id": unicef_id,
            "language": "Polish",
            "consent": True,
            "description": "grievance_ticket_1",
            "category": category,
            "status": status,
            "created_by": created_by,
            "assigned_to": assigned_to,
            "created_at": "2022-04-30T09:54:07.827000",
            "household_unicef_id": household_unicef_id,
            "priority": priority,
            "urgency": urgency,
        }
    )


@pytest.mark.usefixtures("login")
class TestSmokeGrievanceTickets:
    def test_check_grievance_dashboard(
            self,
            active_program: Program,
            add_grievance: None,
            pageGrievanceDashboard: GrievanceDashboard,
    ) -> None:
        pageGrievanceDashboard.getNavGrievance().click()
        pageGrievanceDashboard.getNavGrievanceDashboard().click()
        pageGrievanceDashboard.screenshot("123")
