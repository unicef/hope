from datetime import timedelta
from random import choice
from typing import Optional

from django.utils import timezone

import pytest
from e2e.helpers.fixtures import get_program_with_dct_type_and_name
from e2e.page_object.grievance.details_grievance_page import GrievanceDetailsPage
from e2e.page_object.grievance.grievance_dashboard import GrievanceDashboard
from e2e.page_object.grievance.grievance_tickets import GrievanceTickets

from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.program.models import Program

pytestmark = pytest.mark.django_db()


@pytest.fixture
def active_program() -> Program:
    return get_program_with_dct_type_and_name("Test Program", "1234")


@pytest.fixture
def add_grievances() -> None:
    GrievanceTicket._meta.get_field("created_at").auto_now_add = False
    GrievanceTicket._meta.get_field("updated_at").auto_now = False
    for i in range(50):
        generate_grievance(f"GRV-000000{i}")
    for i in range(10):
        generate_grievance(
            f"GRV-00000{i + 50}",
            category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        )
    for i in range(25):
        generate_grievance(
            f"GRV-00000{i + 60}",
            created_at="2022-09-27T11:26:33.846Z",
            updated_at="2023-09-27T11:26:33.846Z",
            status=GrievanceTicket.STATUS_CLOSED,
        )
    for i in range(15):
        generate_grievance(
            f"GRV-0000{i + 100}",
            status=GrievanceTicket.STATUS_CLOSED,
            category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        )
    GrievanceTicket._meta.get_field("created_at").auto_now_add = True


@pytest.fixture
def grievances() -> [GrievanceTicket]:
    GrievanceTicket._meta.get_field("created_at").auto_now_add = False
    GrievanceTicket._meta.get_field("updated_at").auto_now = False
    grievances = list()
    grievances.append(
        generate_grievance(
            created_at=str(timezone.now() - timedelta(days=20)),
            updated_at=str(timezone.now()),
            status=GrievanceTicket.STATUS_NEW,
        )
    )
    grievances.append(
        generate_grievance(
            created_at=str(timezone.now() - timedelta(days=40)),
            status=GrievanceTicket.STATUS_NEW,
        )
    )
    grievances.append(
        generate_grievance(
            created_at=str(timezone.now() - timedelta(days=60)),
            status=GrievanceTicket.STATUS_NEW,
            category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        )
    )
    GrievanceTicket._meta.get_field("created_at").auto_now_add = True
    GrievanceTicket._meta.get_field("updated_at").auto_now = True
    return grievances


def generate_grievance(
    unicef_id: str = "GRV-0000001",
    status: int = GrievanceTicket.STATUS_NEW,
    category: int = GrievanceTicket.CATEGORY_REFERRAL,
    issue_type: Optional[int] = None,
    created_by: Optional[User] = None,
    assigned_to: Optional[User] = None,
    business_area: Optional[BusinessArea] = None,
    priority: int = 1,
    urgency: int = 1,
    household_unicef_id: str = "HH-20-0000.0001",
    updated_at: str = "2023-09-27T11:26:33.846Z",
    created_at: str = "2022-04-30T09:54:07.827000",
) -> GrievanceTicket:
    created_by = User.objects.first() if created_by is None else created_by
    assigned_to = User.objects.first() if assigned_to is None else assigned_to
    business_area = BusinessArea.objects.filter(slug="afghanistan").first() if business_area is None else business_area
    if issue_type is None:
        issue_type = (
            choice(list(GrievanceTicket.ISSUE_TYPES_CHOICES.get(category, {}).keys()))
            if GrievanceTicket.ISSUE_TYPES_CHOICES.get(category)
            else None
        )
    grievance_ticket = GrievanceTicket.objects.create(
        **{
            "business_area": business_area,
            "unicef_id": unicef_id,
            "language": "Polish",
            "consent": True,
            "description": "grievance_ticket_1",
            "category": category,
            "issue_type": issue_type,
            "status": status,
            "created_by": created_by,
            "assigned_to": assigned_to,
            "created_at": created_at,
            "updated_at": updated_at,
            "household_unicef_id": household_unicef_id,
            "priority": priority,
            "urgency": urgency,
        }
    )

    from hct_mis_api.apps.grievance.models import TicketReferralDetails

    TicketReferralDetails.objects.create(
        ticket=grievance_ticket,
    )

    return grievance_ticket


@pytest.mark.usefixtures("login")
class TestSmokeGrievanceDashboard:
    def test_smoke_grievance_dashboard(
        self,
        active_program: Program,
        add_grievances: None,
        pageGrievanceDashboard: GrievanceDashboard,
    ) -> None:
        pageGrievanceDashboard.getNavGrievance().click()
        pageGrievanceDashboard.getNavGrievanceDashboard().click()

        assert "Grievance Dashboard" in pageGrievanceDashboard.getPageHeaderTitle().text
        assert "100" in pageGrievanceDashboard.getTotalNumberOfTicketsTopNumber().text
        assert "25" in pageGrievanceDashboard.getLabelizedFieldContainerTotalNumberOfTicketsSystemGenerated().text
        assert "75" in pageGrievanceDashboard.getLabelizedFieldContainerTotalNumberOfTicketsUserGenerated().text
        assert "40" in pageGrievanceDashboard.getTotalNumberOfClosedTicketsTopNumber().text
        assert "15" in pageGrievanceDashboard.getLabelizedFieldContainerTotalNumberOfClosedTicketsSystemGenerated().text
        assert "25" in pageGrievanceDashboard.getLabelizedFieldContainerTotalNumberOfClosedTicketsUserGenerated().text
        assert "421.25 days" in pageGrievanceDashboard.getTicketsAverageResolutionTopNumber().text
        assert (
            "515 days"
            in pageGrievanceDashboard.getLabelizedFieldContainerTicketsAverageResolutionSystemGenerated().text
        )
        assert (
            "365 days" in pageGrievanceDashboard.getLabelizedFieldContainerTicketsAverageResolutionUserGenerated().text
        )
        GrievanceTicket._meta.get_field("updated_at").auto_now = True

    def test_grievance_dashboard_happy_path(
        self,
        active_program: Program,
        grievances: [GrievanceTicket],
        pageGrievanceDashboard: GrievanceDashboard,
        pageGrievanceTickets: GrievanceTickets,
        pageGrievanceDetailsPage: GrievanceDetailsPage,
        download_path: str,
    ) -> None:
        pageGrievanceTickets.getNavGrievance().click()
        pageGrievanceDashboard.getNavGrievanceDashboard().click()
        assert "Grievance Dashboard" in pageGrievanceDashboard.getPageHeaderTitle().text
        assert "3" in pageGrievanceDashboard.getTotalNumberOfTicketsTopNumber().text
        assert "1" in pageGrievanceDashboard.getLabelizedFieldContainerTotalNumberOfTicketsSystemGenerated().text
        assert "2" in pageGrievanceDashboard.getLabelizedFieldContainerTotalNumberOfTicketsUserGenerated().text
        assert "0" in pageGrievanceDashboard.getTotalNumberOfClosedTicketsTopNumber().text
        assert "0" in pageGrievanceDashboard.getLabelizedFieldContainerTotalNumberOfClosedTicketsSystemGenerated().text
        assert "0" in pageGrievanceDashboard.getLabelizedFieldContainerTotalNumberOfClosedTicketsUserGenerated().text
        assert "0 days" in pageGrievanceDashboard.getTicketsAverageResolutionTopNumber().text
        assert (
            "0 days" in pageGrievanceDashboard.getLabelizedFieldContainerTicketsAverageResolutionSystemGenerated().text
        )
        assert "0 days" in pageGrievanceDashboard.getLabelizedFieldContainerTicketsAverageResolutionUserGenerated().text

        pageGrievanceTickets.getNavGrievance().click()
        pageGrievanceTickets.getTicketListRow()[0].click()
        pageGrievanceDetailsPage.getButtonAssignToMe().click()
        pageGrievanceDetailsPage.getButtonSetInProgress().click()
        pageGrievanceDetailsPage.getButtonCloseTicket().click()
        pageGrievanceTickets.getButtonConfirm().click()
        pageGrievanceTickets.wait_for_text("Closed", pageGrievanceTickets.statusContainer)
        pageGrievanceTickets.getNavGrievance().click()
        pageGrievanceDashboard.getNavGrievanceDashboard().click()
        assert "3" in pageGrievanceDashboard.getTotalNumberOfTicketsTopNumber().text
        assert "1" in pageGrievanceDashboard.getLabelizedFieldContainerTotalNumberOfTicketsSystemGenerated().text
        assert "2" in pageGrievanceDashboard.getLabelizedFieldContainerTotalNumberOfTicketsUserGenerated().text
        assert "0" in pageGrievanceDashboard.getLabelizedFieldContainerTotalNumberOfClosedTicketsSystemGenerated().text
        assert "1" in pageGrievanceDashboard.getLabelizedFieldContainerTotalNumberOfClosedTicketsUserGenerated().text
        assert "20.00 days" in pageGrievanceDashboard.getTicketsAverageResolutionTopNumber().text
        assert (
            "0 days" in pageGrievanceDashboard.getLabelizedFieldContainerTicketsAverageResolutionSystemGenerated().text
        )
        assert (
            "20 days" in pageGrievanceDashboard.getLabelizedFieldContainerTicketsAverageResolutionUserGenerated().text
        )
        assert "1" in pageGrievanceDashboard.getTotalNumberOfClosedTicketsTopNumber().text
