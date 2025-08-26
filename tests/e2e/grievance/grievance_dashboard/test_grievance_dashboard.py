from datetime import timedelta
from random import choice
from typing import Optional

import pytest
from django.utils import timezone
from e2e.helpers.fixtures import get_program_with_dct_type_and_name
from e2e.page_object.grievance.details_grievance_page import GrievanceDetailsPage
from e2e.page_object.grievance.grievance_dashboard import GrievanceDashboard
from e2e.page_object.grievance.grievance_tickets import GrievanceTickets

from hope.apps.account.models import User
from hope.apps.core.models import BusinessArea
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.program.models import Program

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
    grievances = []
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
        business_area=business_area,
        unicef_id=unicef_id,
        language="Polish",
        consent=True,
        description="grievance_ticket_1",
        category=category,
        issue_type=issue_type,
        status=status,
        created_by=created_by,
        assigned_to=assigned_to,
        created_at=created_at,
        updated_at=updated_at,
        household_unicef_id=household_unicef_id,
        priority=priority,
        urgency=urgency,
    )

    from hope.apps.grievance.models import TicketReferralDetails

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
        page_grievance_dashboard: GrievanceDashboard,
    ) -> None:
        page_grievance_dashboard.get_nav_grievance().click()
        page_grievance_dashboard.get_nav_grievance_dashboard().click()

        assert "Grievance Dashboard" in page_grievance_dashboard.get_page_header_title().text
        assert "100" in page_grievance_dashboard.get_total_number_of_tickets_top_number().text
        assert (
            "25"
            in page_grievance_dashboard.get_labelized_field_container_total_number_of_tickets_system_generated().text
        )
        assert (
            "75" in page_grievance_dashboard.get_labelized_field_container_total_number_of_tickets_user_generated().text
        )
        assert "40" in page_grievance_dashboard.get_total_number_of_closed_tickets_top_number().text
        assert (
            "15"
            in page_grievance_dashboard.get_labelized_field_container_total_number_of_closed_tickets_system_generated().text
        )
        assert (
            "25"
            in page_grievance_dashboard.get_labelized_field_container_total_number_of_closed_tickets_user_generated().text
        )
        assert "421.25 days" in page_grievance_dashboard.get_tickets_average_resolution_top_number().text
        assert (
            "515 days"
            in page_grievance_dashboard.get_labelized_field_container_tickets_average_resolution_system_generated().text
        )
        assert (
            "365 days"
            in page_grievance_dashboard.get_labelized_field_container_tickets_average_resolution_user_generated().text
        )
        GrievanceTicket._meta.get_field("updated_at").auto_now = True

    def test_grievance_dashboard_happy_path(
        self,
        active_program: Program,
        grievances: [GrievanceTicket],
        page_grievance_dashboard: GrievanceDashboard,
        page_grievance_tickets: GrievanceTickets,
        page_grievance_details_page: GrievanceDetailsPage,
        download_path: str,
    ) -> None:
        page_grievance_tickets.get_nav_grievance().click()
        page_grievance_dashboard.get_nav_grievance_dashboard().click()
        assert "Grievance Dashboard" in page_grievance_dashboard.get_page_header_title().text
        assert "3" in page_grievance_dashboard.get_total_number_of_tickets_top_number().text
        assert (
            "1"
            in page_grievance_dashboard.get_labelized_field_container_total_number_of_tickets_system_generated().text
        )
        assert (
            "2" in page_grievance_dashboard.get_labelized_field_container_total_number_of_tickets_user_generated().text
        )
        assert "0" in page_grievance_dashboard.get_total_number_of_closed_tickets_top_number().text
        assert (
            "0"
            in page_grievance_dashboard.get_labelized_field_container_total_number_of_closed_tickets_system_generated().text
        )
        assert (
            "0"
            in page_grievance_dashboard.get_labelized_field_container_total_number_of_closed_tickets_user_generated().text
        )
        assert "0 days" in page_grievance_dashboard.get_tickets_average_resolution_top_number().text
        assert (
            "0 days"
            in page_grievance_dashboard.get_labelized_field_container_tickets_average_resolution_system_generated().text
        )
        assert (
            "0 days"
            in page_grievance_dashboard.get_labelized_field_container_tickets_average_resolution_user_generated().text
        )

        page_grievance_tickets.get_nav_grievance().click()
        page_grievance_tickets.get_ticket_list_row()[0].click()
        page_grievance_details_page.get_button_assign_to_me().click()
        page_grievance_details_page.get_button_set_in_progress().click()
        page_grievance_details_page.get_button_close_ticket().click()
        page_grievance_tickets.get_button_confirm().click()
        page_grievance_tickets.wait_for_text("Closed", page_grievance_tickets.status_container)
        page_grievance_tickets.get_nav_grievance().click()
        page_grievance_dashboard.get_nav_grievance_dashboard().click()
        assert "3" in page_grievance_dashboard.get_total_number_of_tickets_top_number().text
        assert (
            "1"
            in page_grievance_dashboard.get_labelized_field_container_total_number_of_tickets_system_generated().text
        )
        assert (
            "2" in page_grievance_dashboard.get_labelized_field_container_total_number_of_tickets_user_generated().text
        )
        assert (
            "0"
            in page_grievance_dashboard.get_labelized_field_container_total_number_of_closed_tickets_system_generated().text
        )
        assert (
            "1"
            in page_grievance_dashboard.get_labelized_field_container_total_number_of_closed_tickets_user_generated().text
        )
        assert "20.00 days" in page_grievance_dashboard.get_tickets_average_resolution_top_number().text
        assert (
            "0 days"
            in page_grievance_dashboard.get_labelized_field_container_tickets_average_resolution_system_generated().text
        )
        assert (
            "20 days"
            in page_grievance_dashboard.get_labelized_field_container_tickets_average_resolution_user_generated().text
        )
        assert "1" in page_grievance_dashboard.get_total_number_of_closed_tickets_top_number().text
