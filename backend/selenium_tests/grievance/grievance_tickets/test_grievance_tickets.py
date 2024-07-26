from time import sleep
from typing import Generator

from django.conf import settings
from django.core.management import call_command

import pytest
from page_object.grievance.details_grievance_page import GrievanceDetailsPage
from page_object.grievance.grievance_tickets import GrievanceTickets
from page_object.grievance.new_ticket import NewTicket
from pytest_django import DjangoDbBlocker
from selenium.webdriver.common.by import By

from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketNeedsAdjudicationDetails,
)
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.household.models import HOST, Household, Individual
from selenium_tests.drawer.test_drawer import get_program_with_dct_type_and_name
from selenium_tests.page_object.programme_population.individuals import Individuals

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


def create_custom_household(observed_disability: list[str], residence_status: str = HOST) -> Household:
    program = get_program_with_dct_type_and_name("Test Program", "1234")
    household, _ = create_household_and_individuals(
        household_data={
            "unicef_id": "HH-20-0000.0001",
            "rdi_merge_status": "MERGED",
            "business_area": program.business_area,
            "program": program,
            "residence_status": residence_status,
        },
        individuals_data=[
            {
                "unicef_id": "IND-00-0000.0011",
                "rdi_merge_status": "MERGED",
                "business_area": program.business_area,
                "observed_disability": observed_disability,
            },
            {
                "unicef_id": "IND-00-0000.0022",
                "rdi_merge_status": "MERGED",
                "business_area": program.business_area,
                "observed_disability": observed_disability,
            },
            {
                "unicef_id": "IND-00-0000.0033",
                "rdi_merge_status": "MERGED",
                "business_area": program.business_area,
                "observed_disability": observed_disability,
            },
        ],
    )
    return household


@pytest.fixture
def add_grievance_needs_adjudication() -> None:
    GrievanceTicket._meta.get_field("created_at").auto_now_add = False
    GrievanceTicket._meta.get_field("updated_at").auto_now = False
    generate_grievance(status=GrievanceTicket.STATUS_FOR_APPROVAL)
    GrievanceTicket._meta.get_field("created_at").auto_now_add = True
    GrievanceTicket._meta.get_field("updated_at").auto_now = True
    yield


def generate_grievance(
    unicef_id: str = "GRV-0000001",
    status: int = GrievanceTicket.STATUS_NEW,
    category: int = GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
    created_by: User | None = None,
    assigned_to: User | None = None,
    business_area: BusinessArea | None = None,
    priority: int = 1,
    urgency: int = 1,
    household_unicef_id: str = "HH-20-0000.0001",
    updated_at: str = "2023-09-27T11:26:33.846Z",
    created_at: str = "2022-04-30T09:54:07.827000",
) -> GrievanceTicket:
    created_by = User.objects.first() if created_by is None else created_by
    assigned_to = User.objects.first() if assigned_to is None else assigned_to
    business_area = BusinessArea.objects.filter(slug="afghanistan").first() if business_area is None else business_area
    grievance_ticket = GrievanceTicket.objects.create(
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
            "created_at": created_at,
            "updated_at": updated_at,
            "household_unicef_id": household_unicef_id,
            "priority": priority,
            "urgency": urgency,
        }
    )

    hh = create_custom_household(observed_disability=[])

    individual_qs = Individual.objects.filter(household=hh)

    # list of possible duplicates in the ticket
    possible_duplicates = [individual_qs[1], individual_qs[2]]
    # list of distinct Individuals
    selected_distinct = [individual_qs[0]]
    # list of duplicate Individuals
    selected_individuals = []

    ticket_detail = TicketNeedsAdjudicationDetails.objects.create(
        ticket=grievance_ticket,
        is_multiple_duplicates_version=True,
        golden_records_individual=individual_qs[0],
    )
    # list of possible duplicates in the ticket
    ticket_detail.possible_duplicates.add(*possible_duplicates)
    # list of distinct Individuals
    ticket_detail.selected_distinct.add(*selected_distinct)
    # list of duplicate Individuals
    ticket_detail.selected_individuals.add(*selected_individuals)

    return grievance_ticket


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
    @pytest.mark.parametrize(
        "test_data",
        [
            pytest.param({"category": "Sensitive Grievance", "type": "Miscellaneous"}, id="Sensitive Grievance"),
            pytest.param({"category": "Grievance Complaint", "type": "Other Complaint"}, id="Grievance Complaint"),
        ],
    )
    @pytest.mark.skip(reason="ToDo")
    def test_grievance_tickets_create_new_ticket(
        self,
        pageGrievanceTickets: GrievanceTickets,
        pageGrievanceNewTicket: NewTicket,
        pageGrievanceDetailsPage: GrievanceDetailsPage,
        test_data: dict,
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
        assert pageGrievanceNewTicket.waitForNoResults()
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

    def test_grievance_tickets_needs_adjudication(
        self,
        add_grievance_needs_adjudication: None,
        pageGrievanceTickets: GrievanceTickets,
        pageGrievanceDetailsPage: GrievanceDetailsPage,
        pageIndividuals: Individuals,
    ) -> None:
        pageGrievanceTickets.getNavGrievance().click()
        assert "Grievance Tickets" in pageGrievanceTickets.getGrievanceTitle().text
        pageGrievanceTickets.getTabSystemGenerated().click()
        pageGrievanceTickets.getTicketListRow()[0].click()
        pageGrievanceDetailsPage.getSelectAllCheckbox().click()
        pageGrievanceDetailsPage.getPersonIcon()
        assert "person-icon" in [
            ii.get_attribute("data-cy")
            for ii in pageGrievanceDetailsPage.getPossibleDuplicateGoldenRow().find_elements(By.TAG_NAME, "svg")
        ]
        assert "people-icon" not in [
            ii.get_attribute("data-cy")
            for ii in pageGrievanceDetailsPage.getPossibleDuplicateRow()[0].find_elements(By.TAG_NAME, "svg")
        ]
        assert "person-icon" not in [
            ii.get_attribute("data-cy")
            for ii in pageGrievanceDetailsPage.getPossibleDuplicateRow()[0].find_elements(By.TAG_NAME, "svg")
        ]
        assert "people-icon" not in [
            ii.get_attribute("data-cy")
            for ii in pageGrievanceDetailsPage.getPossibleDuplicateRow()[1].find_elements(By.TAG_NAME, "svg")
        ]
        assert "person-icon" not in [
            ii.get_attribute("data-cy")
            for ii in pageGrievanceDetailsPage.getPossibleDuplicateRow()[1].find_elements(By.TAG_NAME, "svg")
        ]
        pageGrievanceDetailsPage.getButtonClear().click()
        pageGrievanceDetailsPage.getButtonConfirm().click()
        pageGrievanceDetailsPage.disappearPersonIcon()
        pageGrievanceDetailsPage.disappearPeopleIcon()
        try:
            assert "person-icon" not in [
                ii.get_attribute("data-cy")
                for ii in pageGrievanceDetailsPage.getPossibleDuplicateGoldenRow().find_elements(By.TAG_NAME, "svg")
            ]
        except BaseException:
            sleep(4)
            assert "person-icon" not in [
                ii.get_attribute("data-cy")
                for ii in pageGrievanceDetailsPage.getPossibleDuplicateGoldenRow().find_elements(By.TAG_NAME, "svg")
            ]
        assert "person-icon" not in [
            ii.get_attribute("data-cy")
            for ii in pageGrievanceDetailsPage.getPossibleDuplicateGoldenRow().find_elements(By.TAG_NAME, "svg")
        ]
        assert "people-icon" not in [
            ii.get_attribute("data-cy")
            for ii in pageGrievanceDetailsPage.getPossibleDuplicateRow()[0].find_elements(By.TAG_NAME, "svg")
        ]
        assert "person-icon" not in [
            ii.get_attribute("data-cy")
            for ii in pageGrievanceDetailsPage.getPossibleDuplicateRow()[0].find_elements(By.TAG_NAME, "svg")
        ]
        assert "people-icon" not in [
            ii.get_attribute("data-cy")
            for ii in pageGrievanceDetailsPage.getPossibleDuplicateRow()[1].find_elements(By.TAG_NAME, "svg")
        ]
        assert "person-icon" not in [
            ii.get_attribute("data-cy")
            for ii in pageGrievanceDetailsPage.getPossibleDuplicateRow()[1].find_elements(By.TAG_NAME, "svg")
        ]
        pageGrievanceDetailsPage.getSelectCheckbox()[0].click()
        pageGrievanceDetailsPage.getButtonMarkDistinct().click()
        pageGrievanceDetailsPage.getButtonConfirm().click()
        pageGrievanceDetailsPage.getPersonIcon()
        pageGrievanceDetailsPage.getCheckboxIndividual().click()
        pageGrievanceDetailsPage.getSelectCheckbox()[1].click()
        pageGrievanceDetailsPage.getButtonMarkDuplicate().click()
        pageGrievanceDetailsPage.getButtonConfirm().click()
        pageGrievanceDetailsPage.getPeopleIcon()
        assert "people-icon" in [
            ii.get_attribute("data-cy")
            for ii in pageGrievanceDetailsPage.getPossibleDuplicateGoldenRow().find_elements(By.TAG_NAME, "svg")
        ]
        assert "person-icon" in [
            ii.get_attribute("data-cy")
            for ii in pageGrievanceDetailsPage.getPossibleDuplicateRow()[0].find_elements(By.TAG_NAME, "svg")
        ]
        assert "people-icon" in [
            ii.get_attribute("data-cy")
            for ii in pageGrievanceDetailsPage.getPossibleDuplicateRow()[1].find_elements(By.TAG_NAME, "svg")
        ]
        duplicated_individual_unicef_id = pageGrievanceDetailsPage.getPossibleDuplicateRow()[1].text.split(" ")[0]
        pageGrievanceDetailsPage.getButtonCloseTicket().click()
        pageGrievanceDetailsPage.getButtonConfirm().click()
        pageGrievanceDetailsPage.disappearButtonConfirm()

        pageGrievanceDetailsPage.selectGlobalProgramFilter("Test Program").click()
        pageGrievanceDetailsPage.getNavProgrammePopulation().click()
        pageIndividuals.getNavIndividuals().click()
        pageIndividuals.getIndividualTableRow()
        assert 3 == len(pageIndividuals.getIndividualTableRow())
        for icon in pageIndividuals.getIndividualTableRow()[0].find_elements(By.TAG_NAME, "svg"):
            assert "Confirmed Duplicate" in icon.get_attribute("aria-label")
            break
        else:
            raise AssertionError(f"Icon for {pageIndividuals.getIndividualTableRow()[0].text} does not appear")
        for individual_row in pageIndividuals.getIndividualTableRow():
            if duplicated_individual_unicef_id in individual_row.text:
                for icon in individual_row.find_elements(By.TAG_NAME, "svg"):
                    assert "Confirmed Duplicate" in icon.get_attribute("aria-label")
