from datetime import datetime
from typing import Generator

from django.conf import settings
from django.core.management import call_command

import pytest
from dateutil.relativedelta import relativedelta
from page_object.grievance.details_grievance_page import GrievanceDetailsPage
from page_object.grievance.grievance_tickets import GrievanceTickets
from page_object.grievance.new_ticket import NewTicket
from pytest_django import DjangoDbBlocker

from hct_mis_api.apps.core.fixtures import DataCollectingTypeFactory
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.household.models import HOST, Household
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def add_grievance(django_db_setup: Generator[None, None, None], django_db_blocker: DjangoDbBlocker) -> None:
    with django_db_blocker.unblock():
        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/grievance/fixtures/data-cypress.json")
    yield


@pytest.fixture
def add_households(django_db_setup: Generator[None, None, None], django_db_blocker: DjangoDbBlocker) -> None:
    with django_db_blocker.unblock():
        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/registration_data/fixtures/data-cypress.json")
        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/household/fixtures/data-cypress.json")
    yield


@pytest.fixture
def create_programs(django_db_setup: Generator[None, None, None], django_db_blocker: DjangoDbBlocker) -> None:
    with django_db_blocker.unblock():
        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/core/fixtures/data-selenium.json")
        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/program/fixtures/data-cypress.json")
    yield


@pytest.fixture
def household_without_disabilities() -> Household:
    yield create_custom_household(observed_disability=[])


def create_program(
    name: str, dct_type: str = DataCollectingType.Type.STANDARD, status: str = Program.ACTIVE
) -> Program:
    BusinessArea.objects.filter(slug="afghanistan").update(is_payment_plan_applicable=True)
    dct = DataCollectingTypeFactory(type=dct_type)
    program = ProgramFactory(
        name=name,
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
        data_collecting_type=dct,
        status=status,
    )
    return program


def create_custom_household(observed_disability: list[str], residence_status: str = HOST) -> Household:
    program = create_program("Test Programm")
    household, _ = create_household_and_individuals(
        household_data={
            "unicef_id": "HH-00-0000.0442",
            "rdi_merge_status": "MERGED",
            "business_area": program.business_area,
            "program": program,
            "residence_status": residence_status,
        },
        individuals_data=[
            {
                "rdi_merge_status": "MERGED",
                "business_area": program.business_area,
                "observed_disability": observed_disability,
            },
        ],
    )
    return household


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
        Go to Grievance tickets user generated page
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
        Go to Grievance tickets system generated page
        Check if all elements on page exist
        """
        # Go to Grievance Tickets
        pageGrievanceTickets.getNavGrievance().click()
        assert "Grievance Tickets" in pageGrievanceTickets.getGrievanceTitle().text
        pageGrievanceTickets.getTicketListRow()
        pageGrievanceTickets.getTabSystemGenerated().click()
        assert 1 == len(pageGrievanceTickets.getTicketListRow())
        pageGrievanceTickets.getSelectAll().click()
        assert "ASSIGN" in pageGrievanceTickets.getButtonAssign().text
        assert "SET PRIORITY" in pageGrievanceTickets.getButtonSetPriority().text
        assert "SET URGENCY" in pageGrievanceTickets.getButtonSetUrgency().text
        assert "ADD NOTE" in pageGrievanceTickets.getButtonAddNote().text
        assert "NEW TICKET" in pageGrievanceTickets.getButtonNewTicket().text

    def test_check_grievance_tickets_details_page(
        self,
        create_programs: None,
        add_households: None,
        add_grievance: None,
        pageGrievanceTickets: GrievanceTickets,
        pageGrievanceDetailsPage: GrievanceDetailsPage,
    ) -> None:
        """
        Go to Grievance tickets details page
        Check if all elements on page exist
        """
        # Go to Grievance Tickets
        pageGrievanceTickets.getNavGrievance().click()
        assert "Grievance Tickets" in pageGrievanceTickets.getGrievanceTitle().text
        pageGrievanceTickets.getTicketListRow()[0].click()
        pageGrievanceDetailsPage.getTicketStatus()
        assert "Ticket ID" in pageGrievanceDetailsPage.getTitle().text
        assert "EDIT" in pageGrievanceDetailsPage.getButtonEdit().text
        assert "SEND BACK" in pageGrievanceDetailsPage.getButtonSendBack().text
        assert "CLOSE TICKET" in pageGrievanceDetailsPage.getButtonCloseTicket().text
        assert "For Approval" in pageGrievanceDetailsPage.getTicketStatus().text
        assert "Medium" in pageGrievanceDetailsPage.getTicketPriority().text
        assert "Urgent" in pageGrievanceDetailsPage.getTicketUrgency().text
        assert "-" in pageGrievanceDetailsPage.getTicketAssigment().text
        assert "Referral" in pageGrievanceDetailsPage.getTicketCategory().text
        assert "HH-20-0000.0002" in pageGrievanceDetailsPage.getTicketHouseholdID().text
        assert "IND-74-0000.0001" in pageGrievanceDetailsPage.getTicketIndividualID().text
        assert "-" in pageGrievanceDetailsPage.getTicketPaymentLabel().text
        assert "-" in pageGrievanceDetailsPage.getLabelPaymentPlan().text
        assert "-" in pageGrievanceDetailsPage.getLabelPaymentPlanVerification().text
        assert "Test Programm" in pageGrievanceDetailsPage.getLabelProgramme().text
        assert "Andarab" in pageGrievanceDetailsPage.getAdministrativeLevel().text
        assert "-" in pageGrievanceDetailsPage.getAreaVillage().text
        assert "English | English" in pageGrievanceDetailsPage.getLanguagesSpoken().text
        assert "-" in pageGrievanceDetailsPage.getDocumentation().text
        assert "Test 4" in pageGrievanceDetailsPage.getTicketDescription().text
        assert "-" in pageGrievanceDetailsPage.getLabelComments().text
        assert "" in pageGrievanceDetailsPage.getNewNoteField().text
        assert "ADD NEW NOTE" in pageGrievanceDetailsPage.getButtonNewNote().text


@pytest.mark.usefixtures("login")
class TestGrievanceTicketsHappyPath:
    def test_grievance_tickets_create_new_ticket_referral(
        self,
        pageGrievanceTickets: GrievanceTickets,
        pageGrievanceNewTicket: NewTicket,
        pageGrievanceDetailsPage: GrievanceDetailsPage,
    ) -> None:
        pageGrievanceTickets.getNavGrievance().click()
        assert "Grievance Tickets" in pageGrievanceTickets.getGrievanceTitle().text
        pageGrievanceTickets.getButtonNewTicket().click()
        pageGrievanceNewTicket.getSelectCategory().click()
        pageGrievanceNewTicket.select_option_by_name("Referral")
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceNewTicket.getHouseholdTab()
        assert pageGrievanceNewTicket.waitForNoResults()
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceNewTicket.getReceivedConsent().click()
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceNewTicket.getDescription().send_keys("Happy path test 1234!")
        pageGrievanceNewTicket.getButtonNext().click()
        assert "Happy path test 1234!" in pageGrievanceDetailsPage.getTicketDescription().text
        assert "Referral" in pageGrievanceDetailsPage.getTicketCategory().text
        assert "New" in pageGrievanceDetailsPage.getTicketStatus().text
        assert "Not set" in pageGrievanceDetailsPage.getTicketPriority().text
        assert "Not set" in pageGrievanceDetailsPage.getTicketUrgency().text


@pytest.mark.usefixtures("login")
class TestGrievanceTickets:
    @pytest.mark.parametrize(
        "test_data",
        [
            pytest.param({"category": "Sensitive Grievance", "type": "Miscellaneous"}, id="Sensitive Grievance"),
            pytest.param({"category": "Sensitive Grievance", "type": "Personal disputes"}, id="Sensitive Grievance"),
            pytest.param(
                {"category": "Grievance Complaint", "type": "Other Complaint"}, id="Grievance Complaint Other Complaint"
            ),
            pytest.param(
                {"category": "Grievance Complaint", "type": "Registration Related Complaint"},
                id="Grievance Complaint Registration Related Complaint",
            ),
            pytest.param(
                {"category": "Data Change", "type": "Withdraw Individual"}, id="Data Change Withdraw Individual"
            ),
            pytest.param(
                {"category": "Data Change", "type": "Withdraw Household"}, id="Data Change Withdraw Household"
            ),
        ],
    )
    def test_grievance_tickets_create_new_tickets(
        self,
        pageGrievanceTickets: GrievanceTickets,
        pageGrievanceNewTicket: NewTicket,
        pageGrievanceDetailsPage: GrievanceDetailsPage,
        test_data: dict,
        household_without_disabilities: Household,
    ) -> None:
        pageGrievanceTickets.getNavGrievance().click()
        assert "Grievance Tickets" in pageGrievanceTickets.getGrievanceTitle().text
        pageGrievanceTickets.getButtonNewTicket().click()
        pageGrievanceNewTicket.getSelectCategory().click()
        pageGrievanceNewTicket.select_option_by_name(test_data["category"])
        pageGrievanceNewTicket.getIssueType().click()
        pageGrievanceNewTicket.select_option_by_name(test_data["type"])
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceNewTicket.getHouseholdTab()
        pageGrievanceNewTicket.getHouseholdTableRows(0).click()
        if test_data["type"] not in ["Withdraw Household", "Household Data Update", "Add Individual"]:
            pageGrievanceNewTicket.getIndividualTab().click()
            pageGrievanceNewTicket.getIndividualTableRows(0).click()
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceNewTicket.getReceivedConsent().click()
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceNewTicket.getDescription().send_keys("Happy path test 1234!")
        pageGrievanceNewTicket.getButtonNext().click()
        assert "Happy path test 1234!" in pageGrievanceDetailsPage.getTicketDescription().text
        assert test_data["category"] in pageGrievanceDetailsPage.getTicketCategory().text
        assert test_data["type"] in pageGrievanceDetailsPage.getLabelIssueType().text
        assert "New" in pageGrievanceDetailsPage.getTicketStatus().text
        assert "Not set" in pageGrievanceDetailsPage.getTicketPriority().text
        assert "Not set" in pageGrievanceDetailsPage.getTicketUrgency().text
        pageGrievanceNewTicket.screenshot(f"out-{test_data['type']}")

    @pytest.mark.parametrize(
        "test_data",
        [
            pytest.param({"category": "Data Change", "type": "Add Individual"}, id="Data Change Add Individual"),
        ],
    )
    def test_grievance_tickets_create_new_ticket(
        self,
        pageGrievanceTickets: GrievanceTickets,
        pageGrievanceNewTicket: NewTicket,
        pageGrievanceDetailsPage: GrievanceDetailsPage,
        test_data: dict,
        household_without_disabilities: Household,
    ) -> None:
        pageGrievanceTickets.getNavGrievance().click()
        assert "Grievance Tickets" in pageGrievanceTickets.getGrievanceTitle().text
        pageGrievanceTickets.getButtonNewTicket().click()
        pageGrievanceNewTicket.getSelectCategory().click()
        pageGrievanceNewTicket.select_option_by_name(test_data["category"])
        pageGrievanceNewTicket.getIssueType().click()
        pageGrievanceNewTicket.select_option_by_name(test_data["type"])
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceNewTicket.getHouseholdTab()
        pageGrievanceNewTicket.getHouseholdTableRows(0).click()
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceNewTicket.getReceivedConsent().click()
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceNewTicket.getDescription().send_keys("Add Individual - TEST")
        pageGrievanceNewTicket.getButtonNext().click()
        assert "Add Individual - TEST" in pageGrievanceDetailsPage.getTicketDescription().text
        assert test_data["category"] in pageGrievanceDetailsPage.getTicketCategory().text
        assert test_data["type"] in pageGrievanceDetailsPage.getLabelIssueType().text
        assert "New" in pageGrievanceDetailsPage.getTicketStatus().text
        assert "Not set" in pageGrievanceDetailsPage.getTicketPriority().text
        assert "Not set" in pageGrievanceDetailsPage.getTicketUrgency().text
        pageGrievanceNewTicket.screenshot(f"out-{test_data['type']}")

    # pytest.param(
    #     {"category": "Data Change", "type": "Individual Data Update"}, id="Data Change Individual Data Update"
    # ),
    # pytest.param(
    #     {"category": "Data Change", "type": "Household Data Update"}, id="Data Change Household Data Update"
    # ),
