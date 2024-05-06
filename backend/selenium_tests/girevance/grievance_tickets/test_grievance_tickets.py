from typing import Generator

from django.conf import settings
from django.core.management import call_command

import pytest
from page_object.grievance.grievance_tickets import GrievanceTickets
from pytest_django import DjangoDbBlocker

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def add_grievance(django_db_setup: Generator[None, None, None], django_db_blocker: DjangoDbBlocker) -> None:
    with django_db_blocker.unblock():
        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/grievance/fixtures/data-cypress.json")
    return


@pytest.fixture
def add_households(django_db_setup: Generator[None, None, None], django_db_blocker: DjangoDbBlocker) -> None:
    with django_db_blocker.unblock():
        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/registration_data/fixtures/data-cypress.json")
        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/household/fixtures/documenttype.json")
        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/household/fixtures/data-cypress.json")
    return


@pytest.fixture
def create_programs(django_db_setup: Generator[None, None, None], django_db_blocker: DjangoDbBlocker) -> None:
    with django_db_blocker.unblock():
        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/core/fixtures/data-selenium.json")
        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/program/fixtures/data-cypress.json")
    return


@pytest.mark.usefixtures("login")
class TestSmokeGrievanceTickets:
    def test_check_grievance_tickets_user_generated_page(
        self,
        create_programs: None,
        add_households: None,
        add_grievance: None,
        pageGrievanceTickets: GrievanceTickets,
    ) -> None:
        """
        Go to Grievance page
        Check if all elements on page exist
        """
        # Go to Grievance Tickets
        pageGrievanceTickets.getNavGrievance().click()
        assert "Grievance Tickets" in pageGrievanceTickets.getGrievanceTitle().text
        pageGrievanceTickets.getSelectAll().click()
        assert "NEW TICKET" in pageGrievanceTickets.getButtonNewTicket().text
        assert "ASSIGN" in pageGrievanceTickets.getButtonAssign().text
        assert "SET PRIORITY" in pageGrievanceTickets.getButtonSetPriority().text
        assert "SET URGENCY" in pageGrievanceTickets.getButtonSetUrgency().text
        assert "ADD NOTE" in pageGrievanceTickets.getButtonAddNote().text
        assert 6 == len(pageGrievanceTickets.getTicketListRow())
        expected_labels = [
            "Ticket ID",
            "Status",
            "Assigned to",
            "Category",
            "Issue Type",
            "Household ID",
            "Priority",
            "Urgency",
            "Linked Tickets",
            "Creation Date\nsorted descending",
            "Last Modified Date",
            "Total Days",
            "Programmes",
        ]
        assert expected_labels == [i.text for i in pageGrievanceTickets.getTableLabel()]

    def test_check_grievance_tickets_system_generated_page(
        self,
        create_programs: None,
        add_households: None,
        add_grievance: None,
        pageGrievanceTickets: GrievanceTickets,
    ) -> None:
        """
        Go to Grievance page
        Check if all elements on page exist
        """
        # Go to Grievance Tickets
        pageGrievanceTickets.getNavGrievance().click()
        assert "Grievance Tickets" in pageGrievanceTickets.getGrievanceTitle().text
        print(pageGrievanceTickets.getTicketListRow()[0].text)
        pageGrievanceTickets.getTabSystemGenerated().click()
        pageGrievanceTickets.screenshot("system")