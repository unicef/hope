from datetime import datetime
import base64
from time import sleep
from typing import Generator, List

from django.conf import settings
from django.core.management import call_command

import pytest
from dateutil.relativedelta import relativedelta
from page_object.grievance.details_grievance_page import GrievanceDetailsPage
from page_object.grievance.grievance_tickets import GrievanceTickets
from page_object.grievance.new_ticket import NewTicket
from pytest_django import DjangoDbBlocker
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.core.fixtures import DataCollectingTypeFactory
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.household.models import HOST, Household
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from selenium_tests.helpers.date_time_format import FormatTime
from selenium.webdriver.common.by import By

from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketNeedsAdjudicationDetails,
)
from hct_mis_api.apps.household.fixtures import (
    IndividualRoleInHouseholdFactory,
    create_household_and_individuals,
)
from hct_mis_api.apps.household.models import HOST, Household, Individual
from selenium_tests.drawer.test_drawer import get_program_with_dct_type_and_name
from selenium_tests.page_object.filters import Filters
from selenium_tests.page_object.programme_population.individuals import Individuals

pytestmark = pytest.mark.django_db(transaction=True)


def id_to_base64(object_id: str, name: str) -> str:
    return base64.b64encode(f"{name}:{str(object_id)}".encode()).decode()


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


def find_text_of_label(element: WebElement) -> str:
    return element.find_element(By.XPATH, "..").find_element(By.XPATH, "..").text


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

    role = IndividualRoleInHouseholdFactory(role="PRIMARY", household=hh, individual=individual_qs[0])

    role_data = {
        "HEAD": {
            "role": "HEAD",
            "household": id_to_base64(hh.id, "HouseholdNode"),
            "individual": id_to_base64(individual_qs[0].id, "IndividualNode"),
            "new_individual": id_to_base64(individual_qs[1].id, "IndividualNode"),
        },
        str(role.id): {
            "role": "PRIMARY",
            "household": id_to_base64(hh.id, "HouseholdNode"),
            "individual": id_to_base64(individual_qs[0].id, "IndividualNode"),
            "new_individual": id_to_base64(individual_qs[1].id, "IndividualNode"),
        },
    }

    ticket_detail = TicketNeedsAdjudicationDetails.objects.create(
        ticket=grievance_ticket,
        is_multiple_duplicates_version=True,
        golden_records_individual=individual_qs[0],
        role_reassign_data=role_data,
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
                {"category": "Grievance Complaint", "type": "FSP Related Complaint"},
                id="Grievance Complaint FSP Related Complaint",
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
        assert "Test Programm" in pageGrievanceDetailsPage.getLabelProgramme().text
        user = User.objects.first()
        assert f"{user.first_name} {user.last_name}" in pageGrievanceDetailsPage.getLabelCreatedBy().text
        assert test_data["category"] in pageGrievanceDetailsPage.getTicketCategory().text
        assert test_data["type"] in pageGrievanceDetailsPage.getLabelIssueType().text
        assert "New" in pageGrievanceDetailsPage.getTicketStatus().text
        assert "Not set" in pageGrievanceDetailsPage.getTicketPriority().text
        assert "Not set" in pageGrievanceDetailsPage.getTicketUrgency().text

    def test_grievance_tickets_create_new_ticket_Data_Change_Add_Individual_All_Fields(
            self,
            pageGrievanceTickets: GrievanceTickets,
            pageGrievanceNewTicket: NewTicket,
            pageGrievanceDetailsPage: GrievanceDetailsPage,
            household_without_disabilities: Household,
    ) -> None:
        pageGrievanceTickets.getNavGrievance().click()
        assert "Grievance Tickets" in pageGrievanceTickets.getGrievanceTitle().text
        pageGrievanceTickets.getButtonNewTicket().click()
        pageGrievanceNewTicket.getSelectCategory().click()
        pageGrievanceNewTicket.select_option_by_name("Data Change")
        pageGrievanceNewTicket.getIssueType().click()
        pageGrievanceNewTicket.select_option_by_name("Add Individual")
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceNewTicket.getHouseholdTab()
        pageGrievanceNewTicket.getHouseholdTableRows(0).click()
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceNewTicket.getReceivedConsent().click()
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceNewTicket.getDescription().send_keys("Add Individual - TEST")
        pageGrievanceNewTicket.getPhoneNoAlternative().send_keys("999 999 999")
        pageGrievanceNewTicket.getDatePickerFilter().click()
        pageGrievanceNewTicket.getDatePickerFilter().send_keys(FormatTime(1, 5, 1986).numerically_formatted_date)
        pageGrievanceNewTicket.getInputIndividualdataBlockchainName().send_keys("TEST")
        pageGrievanceNewTicket.getInputIndividualdataFamilyname().send_keys("Teria")
        pageGrievanceNewTicket.getInputIndividualdataFullname().send_keys("Krido")
        pageGrievanceNewTicket.getSelectIndividualdataSex().click()
        pageGrievanceNewTicket.select_listbox_element("Male").click()
        pageGrievanceNewTicket.getInputIndividualdataGivenname().send_keys("Krato")
        pageGrievanceNewTicket.getSelectIndividualdataCommsdisability().click()
        pageGrievanceNewTicket.select_listbox_element('A lot of difficulty').click()
        pageGrievanceNewTicket.getSelectIndividualdataHearingdisability().click()
        pageGrievanceNewTicket.select_listbox_element('A lot of difficulty').click()
        pageGrievanceNewTicket.getSelectIndividualdataMemorydisability().click()
        pageGrievanceNewTicket.select_listbox_element("Cannot do at all").click()
        pageGrievanceNewTicket.getSelectIndividualdataSeeingdisability().click()
        pageGrievanceNewTicket.select_listbox_element('Some difficulty').click()
        pageGrievanceNewTicket.getSelectIndividualdataPhysicaldisability().click()
        pageGrievanceNewTicket.select_listbox_element("None").click()
        pageGrievanceNewTicket.getInputIndividualdataEmail().send_keys("kridoteria@bukare.cz")
        pageGrievanceNewTicket.getSelectIndividualdataDisability().click()
        pageGrievanceNewTicket.select_listbox_element("disabled").click()
        pageGrievanceNewTicket.getSelectIndividualdataPregnant().click()
        pageGrievanceNewTicket.select_listbox_element("No").click()
        pageGrievanceNewTicket.getSelectIndividualdataMaritalstatus().click()
        pageGrievanceNewTicket.select_listbox_element("Married").click()
        pageGrievanceNewTicket.getInputIndividualdataMiddlename().send_keys("Batu")
        pageGrievanceNewTicket.getInputIndividualdataPaymentdeliveryphoneno().send_keys("123 456 789")
        pageGrievanceNewTicket.getInputIndividualdataPhoneno().send_keys("098 765 432")
        pageGrievanceNewTicket.getSelectIndividualdataPreferredlanguage().click()
        pageGrievanceNewTicket.select_listbox_element("English").click()
        pageGrievanceNewTicket.getSelectIndividualdataRelationship().click()
        pageGrievanceNewTicket.select_listbox_element('Wife / Husband').click()
        pageGrievanceNewTicket.getSelectIndividualdataRole().click()
        pageGrievanceNewTicket.select_listbox_element("Alternate collector").click()
        pageGrievanceNewTicket.getInputIndividualdataWalletaddress().send_keys("Wordoki")
        pageGrievanceNewTicket.getInputIndividualdataWalletname().send_keys("123")
        pageGrievanceNewTicket.getInputIndividualdataWhoanswersaltphone().send_keys("000 000 000")
        pageGrievanceNewTicket.getInputIndividualdataWhoanswersphone().send_keys("111 11 11")

        pageGrievanceNewTicket.getButtonNext().click()
        assert "Add Individual - TEST" in pageGrievanceDetailsPage.getTicketDescription().text
        assert "Data Change" in pageGrievanceDetailsPage.getTicketCategory().text
        assert "Add Individual" in pageGrievanceDetailsPage.getLabelIssueType().text
        assert "New" in pageGrievanceDetailsPage.getTicketStatus().text
        assert "Not set" in pageGrievanceDetailsPage.getTicketPriority().text
        assert "Not set" in pageGrievanceDetailsPage.getTicketUrgency().text

    def test_grievance_tickets_create_new_ticket_Data_Change_Add_Individual_Mandatory_Fields(
            self,
            pageGrievanceTickets: GrievanceTickets,
            pageGrievanceNewTicket: NewTicket,
            pageGrievanceDetailsPage: GrievanceDetailsPage,
            household_without_disabilities: Household,
    ) -> None:
        pageGrievanceTickets.getNavGrievance().click()
        assert "Grievance Tickets" in pageGrievanceTickets.getGrievanceTitle().text
        pageGrievanceTickets.getButtonNewTicket().click()
        pageGrievanceNewTicket.getSelectCategory().click()
        pageGrievanceNewTicket.select_option_by_name("Data Change")
        pageGrievanceNewTicket.getIssueType().click()
        pageGrievanceNewTicket.select_option_by_name("Add Individual")
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceNewTicket.getHouseholdTab()
        pageGrievanceNewTicket.getHouseholdTableRows(0).click()
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceNewTicket.getReceivedConsent().click()
        pageGrievanceNewTicket.getButtonNext().click()

        pageGrievanceNewTicket.getDescription().send_keys("Add Individual - TEST")
        pageGrievanceNewTicket.getDatePickerFilter().click()
        pageGrievanceNewTicket.getDatePickerFilter().send_keys(FormatTime(1, 5, 1986).numerically_formatted_date)

        pageGrievanceNewTicket.getInputIndividualdataFullname().send_keys("Krido")
        pageGrievanceNewTicket.getSelectIndividualdataSex().click()
        pageGrievanceNewTicket.select_listbox_element("Male").click()

        pageGrievanceNewTicket.getEstimatedBirthDate().click()
        pageGrievanceNewTicket.select_listbox_element("Yes").click()

        pageGrievanceNewTicket.getSelectIndividualdataRelationship().click()
        pageGrievanceNewTicket.select_listbox_element('Wife / Husband').click()
        pageGrievanceNewTicket.getSelectIndividualdataRole().click()
        pageGrievanceNewTicket.select_listbox_element("Alternate collector").click()
        pageGrievanceNewTicket.getButtonNext().click()
        assert "ASSIGN TO ME" in pageGrievanceDetailsPage.getButtonAssignToMe().text
        assert "New" in pageGrievanceDetailsPage.getTicketStatus().text
        assert "Not set" in pageGrievanceDetailsPage.getTicketPriority().text
        assert "Not set" in pageGrievanceDetailsPage.getTicketUrgency().text
        assert "-" in pageGrievanceDetailsPage.getTicketAssigment().text
        assert "Data Change" in pageGrievanceDetailsPage.getTicketCategory().text
        assert "Add Individual" in pageGrievanceDetailsPage.getLabelIssueType().text
        assert household_without_disabilities.unicef_id in pageGrievanceDetailsPage.getTicketHouseholdID().text
        assert "Test Programm" in pageGrievanceDetailsPage.getLabelProgramme().text
        assert datetime.now().strftime("%-d %b %Y") in pageGrievanceDetailsPage.getLabelDateCreation().text
        assert datetime.now().strftime("%-d %b %Y") in pageGrievanceDetailsPage.getLabelLastModifiedDate().text
        assert "-" in pageGrievanceDetailsPage.getLabelAdministrativeLevel2().text
        assert "-" in pageGrievanceDetailsPage.getLabelLanguagesSpoken().text
        assert "-" in pageGrievanceDetailsPage.getLabelDocumentation().text
        assert "Add Individual - TEST" in pageGrievanceDetailsPage.getLabelDescription().text
        assert "-" in pageGrievanceDetailsPage.getLabelComments().text
        assert "Male" in pageGrievanceDetailsPage.getLabelGender().text
        assert "Alternate collector" in pageGrievanceDetailsPage.getLabelRole().text
        assert "Krido" in pageGrievanceDetailsPage.getLabelFullName().text
        assert "1986-05-01" in pageGrievanceDetailsPage.getLabelBirthDate().text
        assert "Wife / Husband" in pageGrievanceDetailsPage.getLabelRelationship().text
        assert "Yes" in pageGrievanceDetailsPage.getLabelEstimatedBirthDate().text

    @pytest.mark.parametrize(
        "test_data",
        [
            pytest.param(
                {"category": "Data Change", "type": "Individual Data Update"}, id="Data Change Individual Data Update"
            ),
            pytest.param(
                {"category": "Data Change", "type": "Household Data Update"}, id="Data Change Household Data Update"
            ),
        ])
    def test_grievance_tickets_create_new_ticket(self,
                                                 pageGrievanceTickets: GrievanceTickets,
                                                 pageGrievanceNewTicket: NewTicket,
                                                 pageGrievanceDetailsPage: GrievanceDetailsPage,
                                                 household_without_disabilities: Household,
                                                 test_data: List[str]) -> None:
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
        if "Individual Data Update" in test_data["type"]:
            pageGrievanceNewTicket.getIndividualTab().click()
            pageGrievanceNewTicket.getIndividualTableRows(0).click()
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceNewTicket.getReceivedConsent().click()
        pageGrievanceNewTicket.getButtonNext().click()

        pageGrievanceNewTicket.getDescription().send_keys("Add Individual - TEST")
        pageGrievanceNewTicket.getButtonAddNewField()
        pageGrievanceNewTicket.driver.execute_script(
            """
            container = document.querySelector("div[data-cy='main-content']")
            container.scrollBy(0,600)
            """
        )
        sleep(2)
        pageGrievanceNewTicket.screenshot("0")
        from selenium_tests.tools.tag_name_finder import printing
        printing("Mapping", pageGrievanceNewTicket.driver)
        printing("Methods", pageGrievanceNewTicket.driver)
        printing("Assert", pageGrievanceNewTicket.driver, page_object_str="pageGrievanceNewTicket")

        pageGrievanceNewTicket.getSelectFieldName().click()
        pageGrievanceNewTicket.select_option_by_name("Females age 12 - 17 with disability")
        pageGrievanceNewTicket.screenshot("1")

    def test_grievance_tickets_create_new_tickets_Grievance_Complaint_Partner_Related_Complaint(self,
                                                                                                pageGrievanceTickets: GrievanceTickets,
                                                                                                pageGrievanceNewTicket: NewTicket,
                                                                                                pageGrievanceDetailsPage: GrievanceDetailsPage,
                                                                                                household_without_disabilities: Household) -> None:
        pageGrievanceTickets.getNavGrievance().click()
        assert "Grievance Tickets" in pageGrievanceTickets.getGrievanceTitle().text
        pageGrievanceTickets.getButtonNewTicket().click()

    def test_grievance_tickets_create_new_tickets_Grievance_Complaint_Payment_Related_Complaint(self,
                                                                                                pageGrievanceTickets: GrievanceTickets,
                                                                                                pageGrievanceNewTicket: NewTicket,
                                                                                                pageGrievanceDetailsPage: GrievanceDetailsPage,
                                                                                                household_without_disabilities: Household) -> None:
        pageGrievanceTickets.getNavGrievance().click()
        assert "Grievance Tickets" in pageGrievanceTickets.getGrievanceTitle().text
        pageGrievanceTickets.getButtonNewTicket().click()

    def test_grievance_tickets_look_up_linked_ticket(self,
                                                     pageGrievanceTickets: GrievanceTickets,
                                                     pageGrievanceNewTicket: NewTicket,
                                                     pageGrievanceDetailsPage: GrievanceDetailsPage,
                                                     household_without_disabilities: Household) -> None:
        pageGrievanceTickets.getNavGrievance().click()
        assert "Grievance Tickets" in pageGrievanceTickets.getGrievanceTitle().text
        pageGrievanceTickets.getButtonNewTicket().click()

    def test_grievance_tickets_add_documentation(self,
                                                 pageGrievanceTickets: GrievanceTickets,
                                                 pageGrievanceNewTicket: NewTicket,
                                                 pageGrievanceDetailsPage: GrievanceDetailsPage,
                                                 household_without_disabilities: Household) -> None:
        pageGrievanceTickets.getNavGrievance().click()
        assert "Grievance Tickets" in pageGrievanceTickets.getGrievanceTitle().text
        pageGrievanceTickets.getButtonNewTicket().click()

    def test_grievance_tickets_add_document_and_identity(self,
                                                         pageGrievanceTickets: GrievanceTickets,
                                                         pageGrievanceNewTicket: NewTicket,
                                                         pageGrievanceDetailsPage: GrievanceDetailsPage,
                                                         household_without_disabilities: Household) -> None:
        pageGrievanceTickets.getNavGrievance().click()
        assert "Grievance Tickets" in pageGrievanceTickets.getGrievanceTitle().text
        pageGrievanceTickets.getButtonNewTicket().click()

    def test_grievance_tickets_check_Identity_Verification(self,
                                                           pageGrievanceTickets: GrievanceTickets,
                                                           pageGrievanceNewTicket: NewTicket,
                                                           pageGrievanceDetailsPage: GrievanceDetailsPage,
                                                           household_without_disabilities: Household) -> None:
        pageGrievanceTickets.getNavGrievance().click()
        assert "Grievance Tickets" in pageGrievanceTickets.getGrievanceTitle().text
        pageGrievanceTickets.getButtonNewTicket().click()

    def test_grievance_tickets_filters_of_households_and_individuals(self,
                                                                     pageGrievanceTickets: GrievanceTickets,
                                                                     pageGrievanceNewTicket: NewTicket,
                                                                     pageGrievanceDetailsPage: GrievanceDetailsPage,
                                                                     household_without_disabilities: Household,
                                                                     filters: Filters) -> None:
        pageGrievanceTickets.getNavGrievance().click()
        assert "Grievance Tickets" in pageGrievanceTickets.getGrievanceTitle().text
        pageGrievanceTickets.getButtonNewTicket().click()

    def test_grievance_tickets_edit_tickets_from_main_grievance_page(self) -> None:
        # Assign, Set priority, Set urgency, Add note
        pass

    def test_grievance_tickets_process_tickets(self,
                                               pageGrievanceTickets: GrievanceTickets,
                                               pageGrievanceNewTicket: NewTicket,
                                               pageGrievanceDetailsPage: GrievanceDetailsPage,
                                               household_without_disabilities: Household) -> None:
        pageGrievanceTickets.getNavGrievance().click()
        assert "Grievance Tickets" in pageGrievanceTickets.getGrievanceTitle().text
        pageGrievanceTickets.getButtonNewTicket().click()

    def test_grievance_tickets_add_note(self,
                                        pageGrievanceTickets: GrievanceTickets,
                                        pageGrievanceNewTicket: NewTicket,
                                        pageGrievanceDetailsPage: GrievanceDetailsPage,
                                        household_without_disabilities: Household) -> None:
        pageGrievanceTickets.getNavGrievance().click()
        assert "Grievance Tickets" in pageGrievanceTickets.getGrievanceTitle().text
        pageGrievanceTickets.getButtonNewTicket().click()

    def test_grievance_tickets_activity_log(self,
                                            pageGrievanceTickets: GrievanceTickets,
                                            pageGrievanceNewTicket: NewTicket,
                                            pageGrievanceDetailsPage: GrievanceDetailsPage,
                                            household_without_disabilities: Household) -> None:
        pageGrievanceTickets.getNavGrievance().click()
        assert "Grievance Tickets" in pageGrievanceTickets.getGrievanceTitle().text
        pageGrievanceTickets.getButtonNewTicket().click()

    def test_grievance_tickets_go_to_admin_panel_button(self,
                                                        pageGrievanceTickets: GrievanceTickets,
                                                        pageGrievanceNewTicket: NewTicket,
                                                        pageGrievanceDetailsPage: GrievanceDetailsPage,
                                                        household_without_disabilities: Household) -> None:
        pageGrievanceTickets.getNavGrievance().click()
        assert "Grievance Tickets" in pageGrievanceTickets.getGrievanceTitle().text
        pageGrievanceTickets.getButtonNewTicket().click()

    def test_grievance_tickets_system_generated_tickets(self,
                                                        pageGrievanceTickets: GrievanceTickets,
                                                        pageGrievanceNewTicket: NewTicket,
                                                        pageGrievanceDetailsPage: GrievanceDetailsPage,
                                                        household_without_disabilities: Household) -> None:
        pageGrievanceTickets.getNavGrievance().click()
        assert "Grievance Tickets" in pageGrievanceTickets.getGrievanceTitle().text
        pageGrievanceTickets.getButtonNewTicket().click()

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
