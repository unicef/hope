import base64
from datetime import datetime
from time import sleep
from typing import Optional

import pytest
from dateutil.relativedelta import relativedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from hct_mis_api.apps.account.models import User
from tests.extras.test_utils.factories.core import DataCollectingTypeFactory, create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketNeedsAdjudicationDetails,
)
from tests.extras.test_utils.factories.household import (
    IndividualRoleInHouseholdFactory,
    create_household,
    create_household_and_individuals,
)
from hct_mis_api.apps.household.models import HOST, Household, Individual
from tests.extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory
from hct_mis_api.apps.payment.models import Payment
from tests.extras.test_utils.factories.program import ProgramFactory
from hct_mis_api.apps.program.models import BeneficiaryGroup, Program
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from tests.selenium.drawer.test_drawer import get_program_with_dct_type_and_name
from tests.selenium.filters.test_filters import create_grievance
from tests.selenium.helpers.date_time_format import FormatTime
from tests.selenium.page_object.admin_panel.admin_panel import AdminPanel
from tests.selenium.page_object.grievance.details_grievance_page import (
    GrievanceDetailsPage,
)
from tests.selenium.page_object.grievance.grievance_tickets import GrievanceTickets
from tests.selenium.page_object.grievance.new_ticket import NewTicket
from tests.selenium.page_object.programme_population.households import Households
from tests.selenium.page_object.programme_population.households_details import (
    HouseholdsDetails,
)
from tests.selenium.page_object.programme_population.individuals import Individuals

pytestmark = pytest.mark.django_db()


def id_to_base64(object_id: str, name: str) -> str:
    return base64.b64encode(f"{name}:{str(object_id)}".encode()).decode()


@pytest.fixture
def add_grievance() -> None:
    create_grievance("GRV-0000123")
    create_grievance("GRV-0000666")


@pytest.fixture
def add_households() -> None:
    registration_data_import = RegistrationDataImportFactory(
        imported_by=User.objects.first(), business_area=BusinessArea.objects.first()
    )
    household, _ = create_household(
        {
            "registration_data_import": registration_data_import,
            "admin_area": Area.objects.order_by("?").first(),
            "program": Program.objects.filter(name="Test Programm").first(),
        },
        {"registration_data_import": registration_data_import},
    )

    household.unicef_id = "HH-00-0000.1380"
    household.save()


@pytest.fixture
def create_programs() -> None:
    business_area = create_afghanistan()
    dct = DataCollectingTypeFactory(type=DataCollectingType.Type.STANDARD)
    beneficiary_group = BeneficiaryGroup.objects.filter(name="Main Menu").first()
    ProgramFactory(
        name="Test Programm",
        status=Program.ACTIVE,
        business_area=business_area,
        data_collecting_type=dct,
        beneficiary_group=beneficiary_group,
    )


@pytest.fixture
def household_without_disabilities() -> Household:
    yield create_custom_household(observed_disability=[])


@pytest.fixture
def household_social_worker() -> Household:
    yield create_custom_household(
        observed_disability=[],
        program_name="Social Program",
        dct_type=DataCollectingType.Type.SOCIAL,
        beneficiary_group_name="People",
    )


@pytest.fixture
def hh_with_payment_record(household_without_disabilities: Household) -> Payment:
    payment_plan = PaymentPlanFactory(
        program_cycle=household_without_disabilities.program.cycles.first(),
        business_area=household_without_disabilities.business_area,
        created_by=User.objects.first(),
    )
    payment = PaymentFactory(
        parent=payment_plan,
        household=household_without_disabilities,
        delivered_quantity_usd=None,
        business_area=household_without_disabilities.business_area,
    )
    return payment


def find_text_of_label(element: WebElement) -> str:
    return element.find_element(By.XPATH, "..").find_element(By.XPATH, "..").text


@pytest.fixture
def social_worker_program() -> Program:
    yield create_program("Social Program", dct_type=DataCollectingType.Type.SOCIAL, beneficiary_group="People")


def create_program(
    name: str,
    dct_type: str = DataCollectingType.Type.STANDARD,
    status: str = Program.ACTIVE,
    beneficiary_group: str = "Main Menu",
) -> Program:
    dct = DataCollectingTypeFactory(type=dct_type)
    beneficiary_group = BeneficiaryGroup.objects.filter(name=beneficiary_group).first()
    program = ProgramFactory(
        name=name,
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
        data_collecting_type=dct,
        status=status,
        beneficiary_group=beneficiary_group,
    )
    return program


def create_custom_household(
    observed_disability: list[str],
    residence_status: str = HOST,
    program_name: str = "Test Program",
    dct_type: str = DataCollectingType.Type.STANDARD,
    beneficiary_group_name: str = "Main Menu",
) -> Household:
    program = get_program_with_dct_type_and_name(
        program_name, "1234", dct_type=dct_type, beneficiary_group_name=beneficiary_group_name
    )
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
            "issue_type": GrievanceTicket.ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY,
        }
    )

    hh = create_custom_household(observed_disability=[])

    individual_qs = [
        Individual.objects.get(unicef_id="IND-00-0000.0011"),
        Individual.objects.get(unicef_id="IND-00-0000.0022"),
        Individual.objects.get(unicef_id="IND-00-0000.0033"),
    ]

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
            "new_individual": id_to_base64(individual_qs[2].id, "IndividualNode"),
        },
        str(role.id): {
            "role": "PRIMARY",
            "household": id_to_base64(hh.id, "HouseholdNode"),
            "individual": id_to_base64(individual_qs[0].id, "IndividualNode"),
            "new_individual": id_to_base64(individual_qs[2].id, "IndividualNode"),
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


@pytest.fixture
def add_grievance_tickets() -> GrievanceTicket:
    GrievanceTicket._meta.get_field("created_at").auto_now_add = False
    GrievanceTicket._meta.get_field("updated_at").auto_now = False
    grievance = create_grievance_referral()
    GrievanceTicket._meta.get_field("created_at").auto_now_add = True
    GrievanceTicket._meta.get_field("updated_at").auto_now = True
    yield grievance


@pytest.fixture
def create_four_grievance_tickets() -> [GrievanceTicket]:
    GrievanceTicket._meta.get_field("created_at").auto_now_add = False
    GrievanceTicket._meta.get_field("updated_at").auto_now = False
    grievance = list()
    for _ in range(4):
        grievance.append(create_grievance_referral(assigned_to=""))
    GrievanceTicket._meta.get_field("created_at").auto_now_add = True
    GrievanceTicket._meta.get_field("updated_at").auto_now = True
    yield grievance


@pytest.fixture
def create_grievance_tickets_social_program() -> GrievanceTicket:
    grievance = create_grievance_referral(assigned_to="", household_unicef_id="HH-20-0000.0001")
    grievance.programs.add(Program.objects.filter(name="Social Program").first())
    grievance.save()
    yield grievance


def create_grievance_referral(
    unicef_id: str = "GRV-0000001",
    status: int = GrievanceTicket.STATUS_NEW,
    category: int = GrievanceTicket.CATEGORY_REFERRAL,
    created_by: User | None = None,
    assigned_to: User | None | str = None,
    business_area: BusinessArea | None = None,
    priority: int = 1,
    urgency: int = 1,
    household_unicef_id: str = "HH-20-0000.0001",
    updated_at: str = "2023-09-27T11:26:33.846Z",
    created_at: str = "2022-04-30T09:54:07.827000",
) -> GrievanceTicket:
    created_by = User.objects.first() if created_by is None else created_by
    business_area = BusinessArea.objects.filter(slug="afghanistan").first() if business_area is None else business_area

    ticket_data = {
        "business_area": business_area,
        "unicef_id": unicef_id,
        "language": "Polish",
        "consent": True,
        "description": "grievance_ticket_1",
        "category": category,
        "status": status,
        "created_by": created_by,
        "created_at": created_at,
        "updated_at": updated_at,
        "household_unicef_id": household_unicef_id,
        "priority": priority,
        "urgency": urgency,
    }
    if assigned_to is None:
        assigned_to = User.objects.first()
        ticket_data["assigned_to"] = assigned_to
    elif isinstance(assigned_to, User):
        ticket_data["assigned_to"] = assigned_to

    grievance_ticket = GrievanceTicket.objects.create(**ticket_data)

    from hct_mis_api.apps.grievance.models import TicketReferralDetails

    TicketReferralDetails.objects.create(
        ticket=grievance_ticket, individual=Individual.objects.filter(unicef_id="IND-00-0000.0011").first()
    )

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
        assert 2 == len(pageGrievanceTickets.getTicketListRow())
        expected_labels = [
            "Ticket ID",
            "Status",
            "Assigned to",
            "Category",
            "Issue Type",
            "Target ID",
            "Priority",
            "Urgency",
            "Linked Tickets",
            "Creation Date\nsorted descending",
            "Last Modified Date",
            "Total Days",
            "Programmes",
        ]
        assert expected_labels == [i.text for i in pageGrievanceTickets.getTableLabel()]

    @pytest.mark.xfail(reason="UNSTABLE")
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

    @pytest.mark.xfail(reason="UNSTABLE")
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
        assert "HH-20-0000.0002" in pageGrievanceDetailsPage.getTicketTargetID().text
        assert "-" in pageGrievanceDetailsPage.getTicketPaymentLabel().text
        assert "-" in pageGrievanceDetailsPage.getLabelPaymentPlan().text
        assert "-" in pageGrievanceDetailsPage.getLabelPaymentPlanVerification().text
        assert "Andarab" in pageGrievanceDetailsPage.getAdministrativeLevel().text
        assert "English | English" in pageGrievanceDetailsPage.getLanguagesSpoken().text
        assert "-" in pageGrievanceDetailsPage.getDocumentation().text
        assert "Test 4" in pageGrievanceDetailsPage.getTicketDescription().text
        assert "" in pageGrievanceDetailsPage.getNewNoteField().text
        assert "ADD NEW NOTE" in pageGrievanceDetailsPage.getButtonNewNote().text

    @pytest.mark.xfail(reason="UNSTABLE")
    def test_check_grievance_tickets_details_page_normal_program(
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
        pageGrievanceTickets.selectGlobalProgramFilter("Test Programm")
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
        assert "-" in pageGrievanceDetailsPage.getLabelPaymentPlan().text
        assert "-" in pageGrievanceDetailsPage.getLabelPaymentPlanVerification().text
        assert "Test Program" in pageGrievanceDetailsPage.getLabelProgramme().text
        assert "Shakardara" in pageGrievanceDetailsPage.getAdministrativeLevel().text
        assert "-" in pageGrievanceDetailsPage.getAreaVillage().text
        assert "English | English" in pageGrievanceDetailsPage.getLanguagesSpoken().text
        assert "-" in pageGrievanceDetailsPage.getDocumentation().text
        assert "Test 4" in pageGrievanceDetailsPage.getTicketDescription().text
        assert "" in pageGrievanceDetailsPage.getNewNoteField().text
        assert "ADD NEW NOTE" in pageGrievanceDetailsPage.getButtonNewNote().text

    def test_check_grievance_tickets_details_page_social_worker_program(
        self,
        household_social_worker: Household,
        create_grievance_tickets_social_program: GrievanceTicket,
        pageGrievanceTickets: GrievanceTickets,
        pageGrievanceDetailsPage: GrievanceDetailsPage,
    ) -> None:
        """
        Go to Grievance tickets details page
        Check if all elements on page exist
        """
        pageGrievanceTickets.selectGlobalProgramFilter("Social Program")
        # Go to Grievance Tickets
        pageGrievanceTickets.getNavGrievance().click()
        assert "Grievance Tickets" in pageGrievanceTickets.getGrievanceTitle().text
        pageGrievanceTickets.getTicketListRow()[0].click()
        pageGrievanceDetailsPage.getTicketStatus()
        assert "Ticket ID" in pageGrievanceDetailsPage.getTitle().text
        assert "EDIT" in pageGrievanceDetailsPage.getButtonEdit().text
        assert "ASSIGN TO ME" in pageGrievanceDetailsPage.getButtonAssignToMe().text
        assert "New" in pageGrievanceDetailsPage.getLabelStatus().text
        assert "High" in pageGrievanceDetailsPage.getLabelPriority().text
        assert "Very urgent" in pageGrievanceDetailsPage.getLabelUrgency().text
        assert "Referral" in pageGrievanceDetailsPage.getTicketCategory().text
        assert "Social Program" in pageGrievanceDetailsPage.getLabelProgramme().text
        assert "IND-00-0000.0011" in pageGrievanceDetailsPage.getTicketTargetID().text


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


@pytest.mark.night
@pytest.mark.usefixtures("login")
class TestGrievanceTickets:
    @pytest.mark.xfail(reason="UNSTABLE")
    @pytest.mark.parametrize(
        "test_data",
        [
            pytest.param(
                {"category": "Sensitive Grievance", "type": "Miscellaneous"}, id="Sensitive Grievance Miscellaneous"
            ),
            pytest.param(
                {"category": "Sensitive Grievance", "type": "Personal disputes"},
                id="Sensitive Grievance Personal disputes",
            ),
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
        pageGrievanceNewTicket.select_listbox_element(test_data["type"])
        assert test_data["category"] in pageGrievanceNewTicket.getSelectCategory().text
        assert test_data["type"] in pageGrievanceNewTicket.getIssueType().text
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
        assert "Test Program" in pageGrievanceDetailsPage.getLabelProgramme().text
        user = User.objects.get(email="test@example.com")
        assert f"{user.first_name} {user.last_name}" in pageGrievanceDetailsPage.getLabelCreatedBy().text
        assert test_data["category"] in pageGrievanceDetailsPage.getTicketCategory().text
        assert test_data["type"] in pageGrievanceDetailsPage.getLabelIssueType().text
        assert "New" in pageGrievanceDetailsPage.getTicketStatus().text
        assert "Not set" in pageGrievanceDetailsPage.getTicketPriority().text
        assert "Not set" in pageGrievanceDetailsPage.getTicketUrgency().text

    def test_grievance_tickets_create_new_tickets_social_program(
        self,
        pageGrievanceTickets: GrievanceTickets,
        pageGrievanceNewTicket: NewTicket,
        pageGrievanceDetailsPage: GrievanceDetailsPage,
        household_social_worker: Household,
    ) -> None:
        pageGrievanceTickets.selectGlobalProgramFilter("Social Program")
        pageGrievanceTickets.getNavGrievance().click()
        assert "Grievance Tickets" in pageGrievanceTickets.getGrievanceTitle().text
        pageGrievanceTickets.getButtonNewTicket().click()
        pageGrievanceNewTicket.getSelectCategory().click()
        pageGrievanceNewTicket.select_listbox_element("Data Change")
        pageGrievanceNewTicket.getIssueType().click()
        select_element = pageGrievanceNewTicket.wait_for('ul[role="listbox"]')
        items = select_element.find_elements("tag name", "li")

        check_list = {
            "Add Individual": "true",
            "Household Data Update": "true",
            "Individual Data Update": "None",
            "Withdraw Individual": "None",
            "Withdraw Household": "true",
        }

        for item in items:
            sleep(0.5)
            assert str(item.get_attribute("aria-disabled")) in check_list[item.text], f"{item.text} - not disabled"

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
        pageGrievanceNewTicket.select_listbox_element("Add Member")
        assert "Data Change" in pageGrievanceNewTicket.getSelectCategory().text
        assert "Add Member" in pageGrievanceNewTicket.getIssueType().text
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceNewTicket.getHouseholdTab()
        pageGrievanceNewTicket.getHouseholdTableRows(0).click()
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceNewTicket.getReceivedConsent().click()
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceNewTicket.getDescription().send_keys("Add Member - TEST")
        pageGrievanceNewTicket.getPhoneNoAlternative().send_keys("999 999 999")
        pageGrievanceNewTicket.getDatePickerFilter().click()
        pageGrievanceNewTicket.getDatePickerFilter().send_keys(FormatTime(1, 5, 1986).numerically_formatted_date)
        pageGrievanceNewTicket.getInputIndividualdataBlockchainname().send_keys("TEST")
        pageGrievanceNewTicket.getInputIndividualdataFamilyname().send_keys("Teria")
        pageGrievanceNewTicket.getInputIndividualdataFullname().send_keys("Krido")
        pageGrievanceNewTicket.getEstimatedBirthDate().click()
        pageGrievanceNewTicket.select_listbox_element("Yes")
        pageGrievanceNewTicket.getSelectIndividualdataSex().click()
        pageGrievanceNewTicket.select_listbox_element("Male")
        pageGrievanceNewTicket.getInputIndividualdataGivenname().send_keys("Krato")
        pageGrievanceNewTicket.getSelectIndividualdataCommsdisability().click()
        pageGrievanceNewTicket.select_listbox_element("A lot of difficulty")
        pageGrievanceNewTicket.getSelectIndividualdataHearingdisability().click()
        pageGrievanceNewTicket.select_listbox_element("A lot of difficulty")
        pageGrievanceNewTicket.getSelectIndividualdataMemorydisability().click()
        pageGrievanceNewTicket.select_listbox_element("Cannot do at all")
        pageGrievanceNewTicket.getSelectIndividualdataSeeingdisability().click()
        pageGrievanceNewTicket.select_listbox_element("Some difficulty")
        pageGrievanceNewTicket.getSelectIndividualdataPhysicaldisability().click()
        pageGrievanceNewTicket.select_listbox_element("None")
        pageGrievanceNewTicket.getInputIndividualdataEmail().send_keys("kridoteria@bukare.cz")
        pageGrievanceNewTicket.getSelectIndividualdataDisability().click()
        pageGrievanceNewTicket.select_listbox_element("disabled")
        pageGrievanceNewTicket.getSelectIndividualdataPregnant().click()
        pageGrievanceNewTicket.select_listbox_element("No")
        pageGrievanceNewTicket.getSelectIndividualdataMaritalstatus().click()
        pageGrievanceNewTicket.select_listbox_element("Married")
        pageGrievanceNewTicket.getInputIndividualdataMiddlename().send_keys("Batu")
        pageGrievanceNewTicket.getInputIndividualdataPhoneno().send_keys("098 765 432")
        pageGrievanceNewTicket.getSelectIndividualdataPreferredlanguage().click()
        pageGrievanceNewTicket.select_listbox_element("English")
        pageGrievanceNewTicket.getSelectIndividualdataRelationship().click()
        pageGrievanceNewTicket.select_listbox_element("Wife / Husband")
        pageGrievanceNewTicket.getSelectIndividualdataRole().click()
        pageGrievanceNewTicket.select_listbox_element("Alternate collector")
        pageGrievanceNewTicket.getInputIndividualdataWalletaddress().send_keys("Wordoki")
        pageGrievanceNewTicket.getInputIndividualdataWalletname().send_keys("123")
        pageGrievanceNewTicket.getInputIndividualdataWhoanswersaltphone().send_keys("000 000 000")
        pageGrievanceNewTicket.getInputIndividualdataWhoanswersphone().send_keys("111 11 11")

        pageGrievanceNewTicket.getButtonNext().click()
        assert "Add Member - TEST" in pageGrievanceDetailsPage.getTicketDescription().text
        assert "Data Change" in pageGrievanceDetailsPage.getTicketCategory().text
        assert "Add Member" in pageGrievanceDetailsPage.getLabelIssueType().text
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
        pageGrievanceNewTicket.select_listbox_element("Add Member")
        assert "Data Change" in pageGrievanceNewTicket.getSelectCategory().text
        assert "Add Member" in pageGrievanceNewTicket.getIssueType().text
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
        pageGrievanceNewTicket.select_listbox_element("Male")

        pageGrievanceNewTicket.getEstimatedBirthDate().click()
        pageGrievanceNewTicket.select_listbox_element("Yes")

        pageGrievanceNewTicket.getSelectIndividualdataRelationship().click()
        pageGrievanceNewTicket.select_listbox_element("Wife / Husband")
        pageGrievanceNewTicket.getSelectIndividualdataRole().click()
        pageGrievanceNewTicket.select_listbox_element("Alternate collector")
        pageGrievanceNewTicket.getButtonNext().click()
        assert "ASSIGN TO ME" in pageGrievanceDetailsPage.getButtonAssignToMe().text
        assert "New" in pageGrievanceDetailsPage.getTicketStatus().text
        assert "Not set" in pageGrievanceDetailsPage.getTicketPriority().text
        assert "Not set" in pageGrievanceDetailsPage.getTicketUrgency().text
        assert "-" in pageGrievanceDetailsPage.getTicketAssigment().text
        assert "Data Change" in pageGrievanceDetailsPage.getTicketCategory().text
        assert "Add Member" in pageGrievanceDetailsPage.getLabelIssueType().text
        assert household_without_disabilities.unicef_id in pageGrievanceDetailsPage.getTicketTargetID().text
        assert "Test Program" in pageGrievanceDetailsPage.getLabelProgramme().text
        assert datetime.now().strftime("%-d %b %Y") in pageGrievanceDetailsPage.getLabelDateCreation().text
        assert datetime.now().strftime("%-d %b %Y") in pageGrievanceDetailsPage.getLabelLastModifiedDate().text
        assert "-" in pageGrievanceDetailsPage.getLabelDocumentation().text
        assert "Add Individual - TEST" in pageGrievanceDetailsPage.getLabelDescription().text
        assert "Male" in pageGrievanceDetailsPage.getLabelGender().text
        assert "Alternate collector" in pageGrievanceDetailsPage.getLabelRole().text
        assert "Krido" in pageGrievanceDetailsPage.getLabelFullName().text
        assert "1986-05-01" in pageGrievanceDetailsPage.getLabelBirthDate().text
        assert "Wife / Husband" in pageGrievanceDetailsPage.getLabelRelationship().text
        assert "Yes" in pageGrievanceDetailsPage.getLabelEstimatedBirthDate().text

    @pytest.mark.parametrize(
        "test_data",
        [
            pytest.param({"category": "Data Change", "type": "Group Data Update"}, id="Data Change Group Data Update"),
        ],
    )
    def test_hh_grievance_tickets_create_new_ticket(
        self,
        pageGrievanceTickets: GrievanceTickets,
        pageGrievanceNewTicket: NewTicket,
        pageGrievanceDetailsPage: GrievanceDetailsPage,
        household_without_disabilities: Household,
        test_data: dict,
    ) -> None:
        pageGrievanceTickets.getNavGrievance().click()
        assert "Grievance Tickets" in pageGrievanceTickets.getGrievanceTitle().text
        pageGrievanceTickets.getButtonNewTicket().click()
        pageGrievanceNewTicket.getSelectCategory().click()
        pageGrievanceNewTicket.select_option_by_name(str(test_data["category"]))
        pageGrievanceNewTicket.getIssueType().click()
        pageGrievanceNewTicket.select_listbox_element(str(test_data["type"]))
        assert test_data["category"] in pageGrievanceNewTicket.getSelectCategory().text
        assert test_data["type"] in pageGrievanceNewTicket.getIssueType().text
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceNewTicket.getHouseholdTab()
        pageGrievanceNewTicket.getHouseholdTableRows(0).click()
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceNewTicket.getReceivedConsent().click()
        pageGrievanceNewTicket.getButtonNext().click()

        pageGrievanceNewTicket.getDescription().send_keys("Add Group - TEST")
        pageGrievanceNewTicket.getButtonAddNewField()
        pageGrievanceNewTicket.getSelectFieldName().click()
        pageGrievanceNewTicket.select_listbox_element("Females age 12 - 17 with disability")
        pageGrievanceNewTicket.getInputValue().send_keys("1")
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceDetailsPage.getCheckboxHouseholdData()
        assert "Female Age Group 12 17" in pageGrievanceDetailsPage.getRows()[0].text
        assert "- 1" in pageGrievanceDetailsPage.getRows()[0].text

    @pytest.mark.parametrize(
        "test_data",
        [
            pytest.param(
                {"category": "Data Change", "type": "Member Data Update"},
                id="Data Change Member Data Update",
            )
        ],
    )
    def test_grievance_tickets_create_new_ticket(
        self,
        pageGrievanceTickets: GrievanceTickets,
        pageGrievanceNewTicket: NewTicket,
        pageGrievanceDetailsPage: GrievanceDetailsPage,
        household_without_disabilities: Household,
        test_data: dict,
    ) -> None:
        pageGrievanceTickets.getNavGrievance().click()
        assert "Grievance Tickets" in pageGrievanceTickets.getGrievanceTitle().text
        pageGrievanceTickets.getButtonNewTicket().click()
        pageGrievanceNewTicket.getSelectCategory().click()
        pageGrievanceNewTicket.select_option_by_name(str(test_data["category"]))
        pageGrievanceNewTicket.getIssueType().click()
        pageGrievanceNewTicket.element_clickable(f'li[data-cy="select-option-{test_data["type"]}"]')
        pageGrievanceNewTicket.select_listbox_element(str(test_data["type"]))
        assert test_data["category"] in pageGrievanceNewTicket.getSelectCategory().text
        assert test_data["type"] in pageGrievanceNewTicket.getIssueType().text
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceNewTicket.getHouseholdTab()
        pageGrievanceNewTicket.getHouseholdTableRows(0).click()
        pageGrievanceNewTicket.getIndividualTab().click()
        pageGrievanceNewTicket.getIndividualTableRows(0).click()
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceNewTicket.getReceivedConsent().click()
        pageGrievanceNewTicket.getButtonNext().click()

        pageGrievanceNewTicket.getDescription().send_keys("Add Member Data Update - TEST")
        pageGrievanceNewTicket.getButtonAddNewField().click()
        pageGrievanceNewTicket.getIndividualFieldName(0).click()
        pageGrievanceNewTicket.select_listbox_element("Gender")
        pageGrievanceNewTicket.getInputIndividualData("Gender").click()
        pageGrievanceNewTicket.select_listbox_element("Female")
        pageGrievanceNewTicket.getIndividualFieldName(1).click()
        pageGrievanceNewTicket.select_listbox_element("Preferred language")
        pageGrievanceNewTicket.getInputIndividualData("Preferred language").click()
        pageGrievanceNewTicket.select_listbox_element("English | English")

        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceDetailsPage.getCheckboxIndividualData()
        row0 = pageGrievanceDetailsPage.getRows()[0].text.split(" ")
        assert "Gender" in row0[0]
        assert "Female" in row0[-1]

        row1 = pageGrievanceDetailsPage.getRows()[1].text.split(" ")
        assert "Preferred Language" in f"{row1[0]} {row1[1]}"
        assert "English" in row1[-1]

    def test_grievance_tickets_create_new_tickets_Grievance_Complaint_Partner_Related_Complaint(
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
        pageGrievanceNewTicket.select_option_by_name("Grievance Complaint")
        pageGrievanceNewTicket.getIssueType().click()
        pageGrievanceNewTicket.select_listbox_element("Partner Related Complaint")
        assert "Grievance Complaint" in pageGrievanceNewTicket.getSelectCategory().text
        assert "Partner Related Complaint" in pageGrievanceNewTicket.getIssueType().text
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceNewTicket.getHouseholdTab()
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceNewTicket.getReceivedConsent().click()
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceNewTicket.getPartner().click()
        pageGrievanceNewTicket.select_option_by_name("UNICEF")
        pageGrievanceNewTicket.getDescription().send_keys("Test !@#$ OK")
        pageGrievanceNewTicket.getButtonNext().click()
        assert "UNICEF" in pageGrievanceDetailsPage.getLabelPartner().text

    def test_grievance_tickets_create_new_tickets_Grievance_Complaint_Payment_Related_Complaint(
        self,
        pageGrievanceTickets: GrievanceTickets,
        pageGrievanceNewTicket: NewTicket,
        pageGrievanceDetailsPage: GrievanceDetailsPage,
        hh_with_payment_record: Payment,
    ) -> None:
        payment_id = Payment.objects.first().unicef_id
        pageGrievanceTickets.getNavGrievance().click()
        assert "Grievance Tickets" in pageGrievanceTickets.getGrievanceTitle().text
        pageGrievanceTickets.getButtonNewTicket().click()
        pageGrievanceNewTicket.getSelectCategory().click()
        pageGrievanceNewTicket.select_option_by_name("Grievance Complaint")
        pageGrievanceNewTicket.getIssueType().click()
        pageGrievanceNewTicket.select_listbox_element("Payment Related Complaint")
        assert "Grievance Complaint" in pageGrievanceNewTicket.getSelectCategory().text
        assert "Payment Related Complaint" in pageGrievanceNewTicket.getIssueType().text
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceNewTicket.getHouseholdTab()
        pageGrievanceNewTicket.getHouseholdTableRows(0).click()
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceNewTicket.getReceivedConsent().click()
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceNewTicket.getDescription().send_keys("TEST Payment Related Complaint")
        pageGrievanceNewTicket.getLookUpPaymentRecord().click()
        pageGrievanceNewTicket.getCheckboxSelectAll().click()
        pageGrievanceNewTicket.getButtonSubmit().click()
        assert hh_with_payment_record.unicef_id in pageGrievanceDetailsPage.getPaymentRecord().text
        pageGrievanceNewTicket.getButtonNext().click()
        assert payment_id in pageGrievanceDetailsPage.getTicketPaymentLabel().text

    def test_grievance_tickets_look_up_linked_ticket(
        self,
        pageGrievanceTickets: GrievanceTickets,
        pageGrievanceNewTicket: NewTicket,
        pageGrievanceDetailsPage: GrievanceDetailsPage,
        household_without_disabilities: Household,
        add_grievance_tickets: GrievanceTicket,
    ) -> None:
        linked_ticket = GrievanceTicket.objects.first().unicef_id
        pageGrievanceTickets.getNavGrievance().click()
        assert "Grievance Tickets" in pageGrievanceTickets.getGrievanceTitle().text
        pageGrievanceTickets.getButtonNewTicket().click()
        pageGrievanceNewTicket.getSelectCategory().click()
        pageGrievanceNewTicket.select_option_by_name("Referral")
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceNewTicket.getHouseholdTab()
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceNewTicket.getReceivedConsent().click()
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceNewTicket.getDescription().send_keys("TEST Linked Ticket")
        pageGrievanceNewTicket.getLookUpButton().click()
        pageGrievanceNewTicket.getCheckboxSelectAll().click()
        pageGrievanceNewTicket.getButtonSubmit().click()
        assert linked_ticket in pageGrievanceNewTicket.getLinkedTicketId().text
        pageGrievanceNewTicket.getButtonEdit().click()
        pageGrievanceNewTicket.getButtonSubmit().click()
        pageGrievanceNewTicket.getButtonDelete().click()
        with pytest.raises(Exception):
            pageGrievanceNewTicket.getLinkedTicketId()
        pageGrievanceNewTicket.getLookUpButton().click()
        pageGrievanceNewTicket.getCheckboxSelectAll().click()
        pageGrievanceNewTicket.getButtonSubmit().click()
        assert linked_ticket in pageGrievanceNewTicket.getLinkedTicketId().text
        pageGrievanceNewTicket.getButtonNext().click()
        assert linked_ticket in pageGrievanceDetailsPage.getLabelTickets().text

    def test_grievance_tickets_add_documentation(
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
        pageGrievanceNewTicket.select_option_by_name("Referral")
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceNewTicket.getHouseholdTab()
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceNewTicket.getReceivedConsent().click()
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceNewTicket.getDescription().send_keys("Happy path test 1234!")
        pageGrievanceNewTicket.getAddDocumentation().click()
        pageGrievanceNewTicket.getInputDocumentationName(0).send_keys("example")
        pageGrievanceNewTicket.upload_file(f"{pytest.SELENIUM_PATH}/helpers/document_example.png")
        pageGrievanceNewTicket.getButtonNext().click()
        assert "example" in pageGrievanceDetailsPage.getLinkShowPhoto().text
        pageGrievanceDetailsPage.getLinkShowPhoto().click()
        pageGrievanceDetailsPage.getButtonRotateImage().click()
        pageGrievanceDetailsPage.getButtonCancel().click()
        assert "example" in pageGrievanceDetailsPage.getLinkShowPhoto().text

    def test_grievance_tickets_check_identity_verification(
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
        pageGrievanceNewTicket.select_listbox_element("Member Data Update")
        assert "Data Change" in pageGrievanceNewTicket.getSelectCategory().text
        assert "Member Data Update" in pageGrievanceNewTicket.getIssueType().text
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceNewTicket.getHouseholdTab()
        pageGrievanceNewTicket.getIndividualTab().click()
        individual_unicef_id = pageGrievanceNewTicket.getIndividualTableRows(0).text.split(" ")[0]
        pageGrievanceNewTicket.getIndividualTableRows(0).click()
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceNewTicket.getInputQuestionnaire_size().click()
        assert "3" in pageGrievanceNewTicket.getLabelHouseholdSize().text
        pageGrievanceNewTicket.getInputQuestionnaire_malechildrencount().click()
        assert "-" in pageGrievanceNewTicket.getLabelNumberOfMaleChildren().text
        pageGrievanceNewTicket.getInputQuestionnaire_femalechildrencount().click()
        assert "-" in pageGrievanceNewTicket.getLabelNumberOfFemaleChildren().text
        pageGrievanceNewTicket.getInputQuestionnaire_childrendisabledcount().click()
        assert "-" in pageGrievanceNewTicket.getLabelNumberOfDisabledChildren().text
        pageGrievanceNewTicket.getInputQuestionnaire_headofhousehold().click()
        individual = Individual.objects.get(unicef_id=individual_unicef_id)
        household = individual.household
        assert individual.full_name in pageGrievanceNewTicket.getLabelHeadOfHousehold().text
        pageGrievanceNewTicket.getInputQuestionnaire_countryorigin().click()
        assert str(household.country_origin) in pageGrievanceNewTicket.getLabelCountryOfOrigin().text
        pageGrievanceNewTicket.getInputQuestionnaire_address().click()
        assert household.address.replace("\n", " ") in pageGrievanceNewTicket.getLabelAddress().text
        pageGrievanceNewTicket.getInputQuestionnaire_village().click()
        assert household.village in pageGrievanceNewTicket.getLabelVillage().text
        pageGrievanceNewTicket.getInputQuestionnaire_admin1().click()
        assert "-" in pageGrievanceNewTicket.getLabelAdministrativeLevel1().text
        pageGrievanceNewTicket.getInputQuestionnaire_admin2().click()
        assert "-" in pageGrievanceNewTicket.getLabelAdministrativeLevel2().text
        pageGrievanceNewTicket.getInputQuestionnaire_admin3().click()
        assert "-" in pageGrievanceNewTicket.getLabelAdministrativeLevel3().text
        pageGrievanceNewTicket.getInputQuestionnaire_admin4().click()
        assert "-" in pageGrievanceNewTicket.getLabelAdministrativeLevel4().text
        pageGrievanceNewTicket.getInputQuestionnaire_months_displaced_h_f().click()
        assert "-" in pageGrievanceNewTicket.getLabelLengthOfTimeSinceArrival().text
        pageGrievanceNewTicket.getInputQuestionnaire_fullname().click()
        assert individual.full_name in pageGrievanceNewTicket.getLabelIndividualFullName().text
        pageGrievanceNewTicket.getInputQuestionnaire_birthdate().click()
        assert "-" in pageGrievanceNewTicket.getLabelBirthDate().text
        pageGrievanceNewTicket.getInputQuestionnaire_sex().click()
        assert individual.sex in pageGrievanceNewTicket.getLabelGender().text
        pageGrievanceNewTicket.getInputQuestionnaire_phoneno().click()
        assert "-" in pageGrievanceNewTicket.getLabelPhoneNumber().text
        pageGrievanceNewTicket.getInputQuestionnaire_relationship().click()
        assert "HEAD" in pageGrievanceNewTicket.getLabelRelationshipToHoh().text
        pageGrievanceNewTicket.getReceivedConsent().click()
        pageGrievanceNewTicket.getButtonNext().click()

    def test_grievance_tickets_edit_tickets_from_main_grievance_page(
        self,
        pageGrievanceTickets: GrievanceTickets,
        pageHouseholds: Households,
        create_four_grievance_tickets: [GrievanceTicket],
    ) -> None:
        pageGrievanceTickets.getNavGrievance().click()
        assert "Grievance Tickets" in pageGrievanceTickets.getGrievanceTitle().text
        pageGrievanceTickets.getSelectAll().click()
        pageGrievanceTickets.getButtonAssign().click()
        pageGrievanceTickets.getDropdown().click()
        pageGrievanceTickets.select_listbox_element("test@example.com")
        for str_row in pageGrievanceTickets.getRows():
            list_row = str_row.text.replace("\n", " ").split(" ")
            assert list_row[0] in pageGrievanceTickets.getSelectedTickets().text
        pageGrievanceTickets.getButtonSave().click()
        pageGrievanceTickets.getStatusContainer()
        pageGrievanceTickets.checkIfTextExistInArow(0, "Assigned")

        for str_row in pageGrievanceTickets.getRows():
            list_row = str_row.text.replace("\n", " ").split(" ")
            assert list_row[1] in "Assigned"

        pageGrievanceTickets.getSelectAll().click()
        pageGrievanceTickets.getButtonSetPriority().click()
        pageGrievanceTickets.getDropdown().click()
        pageGrievanceTickets.select_listbox_element("Medium")
        pageGrievanceTickets.getButtonSave().click()
        pageGrievanceTickets.getStatusContainer()

        pageGrievanceTickets.checkIfTextExistInArow(0, "Medium")
        for str_row in pageGrievanceTickets.getRows():
            assert "Medium" in str_row.text.replace("\n", " ").split(" ")
        pageGrievanceTickets.getSelectAll().click()
        pageGrievanceTickets.getButtonSetUrgency().click()
        pageGrievanceTickets.getDropdown().click()
        pageGrievanceTickets.select_listbox_element("Urgent")
        pageGrievanceTickets.getButtonSave().click()
        pageGrievanceTickets.getStatusContainer()

        pageGrievanceTickets.checkIfTextExistInArow(0, "Urgent")
        for str_row in pageGrievanceTickets.getRows():
            assert "Urgent" in str_row.text.replace("\n", " ").split(" ")

    @pytest.mark.xfail(reason="UNSTABLE")
    def test_grievance_tickets_process_tickets(
        self,
        pageGrievanceTickets: GrievanceTickets,
        pageGrievanceNewTicket: NewTicket,
        pageGrievanceDetailsPage: GrievanceDetailsPage,
        household_without_disabilities: Household,
        pageHouseholdsDetails: HouseholdsDetails,
        pageHouseholds: Households,
    ) -> None:
        pageGrievanceTickets.getNavGrievance().click()
        assert "Grievance Tickets" in pageGrievanceTickets.getGrievanceTitle().text
        pageGrievanceTickets.getButtonNewTicket().click()
        pageGrievanceNewTicket.getSelectCategory().click()
        pageGrievanceNewTicket.select_option_by_name("Data Change")
        pageGrievanceNewTicket.getIssueType().click()
        pageGrievanceNewTicket.select_listbox_element("Household Data Update")
        assert "Data Change" in pageGrievanceNewTicket.getSelectCategory().text
        assert "Items Group Data Update" in pageGrievanceNewTicket.getIssueType().text
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceNewTicket.getHouseholdTab()
        pageGrievanceNewTicket.getHouseholdTableRows(0).click()
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceNewTicket.getReceivedConsent().click()
        pageGrievanceNewTicket.getButtonNext().click()

        pageGrievanceNewTicket.getDescription().send_keys("Add Individual - TEST")
        pageGrievanceNewTicket.getButtonAddNewField()
        pageGrievanceNewTicket.getSelectFieldName().click()
        pageGrievanceNewTicket.select_option_by_name("Males Age 0 - 5")
        pageGrievanceNewTicket.getInputValue().send_keys("5")
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceDetailsPage.getCheckboxHouseholdData()
        pageGrievanceDetailsPage.getButtonAssignToMe().click()
        pageGrievanceDetailsPage.getButtonSetInProgress().click()
        pageGrievanceDetailsPage.getButtonSendForApproval().click()
        pageGrievanceDetailsPage.getCheckboxHouseholdData().click()
        pageGrievanceDetailsPage.getButtonApproval().click()
        pageGrievanceDetailsPage.getButtonCloseTicket().click()
        pageGrievanceDetailsPage.getButtonConfirm().click()
        assert "Ticket ID" in pageGrievanceDetailsPage.getTitle().text
        pageGrievanceNewTicket.selectGlobalProgramFilter("Test Program")
        pageGrievanceNewTicket.getNavProgrammePopulation().click()
        pageHouseholds.getHouseholdsRows()[0].click()
        assert "5" in pageHouseholdsDetails.getRow05().text

    @pytest.mark.xfail(reason="UNSTABLE")
    def test_grievance_tickets_add_note(
        self,
        pageGrievanceTickets: GrievanceTickets,
        pageGrievanceNewTicket: NewTicket,
        pageGrievanceDetailsPage: GrievanceDetailsPage,
        household_without_disabilities: Household,
        add_grievance_tickets: GrievanceTicket,
    ) -> None:
        pageGrievanceTickets.getNavGrievance().click()
        assert "Grievance Tickets" in pageGrievanceTickets.getGrievanceTitle().text
        pageGrievanceTickets.getTicketListRow()[0].click()
        pageGrievanceDetailsPage.getInputNewnote().send_keys("Test adding new note.")
        pageGrievanceDetailsPage.getButtonNewNote().click()
        user = pageGrievanceDetailsPage.getNoteName().text
        assert 1 == len(pageGrievanceDetailsPage.getNoteRows())
        assert user in pageGrievanceDetailsPage.getNoteRows()[0].text
        assert datetime.now().strftime("%-d %b %Y") in pageGrievanceDetailsPage.getNoteRows()[0].text
        assert "Test adding new note." in pageGrievanceDetailsPage.getNoteRows()[0].text

    @pytest.mark.xfail(reason="UNSTABLE")
    def test_grievance_tickets_activity_log(
        self,
        pageGrievanceTickets: GrievanceTickets,
        pageGrievanceDetailsPage: GrievanceDetailsPage,
        household_without_disabilities: Household,
        add_grievance_tickets: GrievanceTicket,
    ) -> None:
        pageGrievanceTickets.getNavGrievance().click()
        assert "Grievance Tickets" in pageGrievanceTickets.getGrievanceTitle().text
        pageGrievanceTickets.getTicketListRow()[0].click()
        pageGrievanceDetailsPage.getButtonAssignToMe().click()
        pageGrievanceDetailsPage.getButtonSetInProgress().click()
        pageGrievanceDetailsPage.driver.refresh()
        pageGrievanceDetailsPage.getExpandCollapseButton().click()
        assert "Assigned" in pageGrievanceDetailsPage.getLogRow()[0].text
        assert "In Progress" in pageGrievanceDetailsPage.getLogRow()[0].text

    def test_grievance_tickets_go_to_admin_panel_button(
        self,
        pageGrievanceTickets: GrievanceTickets,
        pageGrievanceNewTicket: NewTicket,
        pageGrievanceDetailsPage: GrievanceDetailsPage,
        household_without_disabilities: Household,
        add_grievance_tickets: GrievanceTicket,
        pageAdminPanel: AdminPanel,
    ) -> None:
        pageGrievanceTickets.getNavGrievance().click()
        assert "Grievance Tickets" in pageGrievanceTickets.getGrievanceTitle().text
        pageGrievanceTickets.getTicketListRow()[0].click()
        pageGrievanceDetailsPage.getButtonAdmin().click()
        assert "grievance_ticket_1" in pageAdminPanel.getUnicefID().text
        assert GrievanceTicket.objects.first().unicef_id in pageAdminPanel.getUnicefID().text

    @pytest.mark.xfail(reason="UNSTABLE")
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
            for ii in pageGrievanceDetailsPage.getPossibleDuplicateRowByUnicefId("IND-00-0000.0011").find_elements(
                By.TAG_NAME, "svg"
            )
        ]
        assert "people-icon" not in [
            ii.get_attribute("data-cy")
            for ii in pageGrievanceDetailsPage.getPossibleDuplicateRowByUnicefId("IND-00-0000.0022").find_elements(
                By.TAG_NAME, "svg"
            )
        ]
        assert "person-icon" not in [
            ii.get_attribute("data-cy")
            for ii in pageGrievanceDetailsPage.getPossibleDuplicateRowByUnicefId("IND-00-0000.0022").find_elements(
                By.TAG_NAME, "svg"
            )
        ]
        assert "people-icon" not in [
            ii.get_attribute("data-cy")
            for ii in pageGrievanceDetailsPage.getPossibleDuplicateRowByUnicefId("IND-00-0000.0033").find_elements(
                By.TAG_NAME, "svg"
            )
        ]
        assert "person-icon" not in [
            ii.get_attribute("data-cy")
            for ii in pageGrievanceDetailsPage.getPossibleDuplicateRowByUnicefId("IND-00-0000.0033").find_elements(
                By.TAG_NAME, "svg"
            )
        ]
        pageGrievanceDetailsPage.getButtonClear().click()
        pageGrievanceDetailsPage.getButtonConfirm().click()
        pageGrievanceDetailsPage.disappearPersonIcon()
        pageGrievanceDetailsPage.disappearPeopleIcon()
        try:
            assert "person-icon" not in [
                ii.get_attribute("data-cy")
                for ii in pageGrievanceDetailsPage.getPossibleDuplicateRowByUnicefId("IND-00-0000.0011").find_elements(
                    By.TAG_NAME, "svg"
                )
            ]
        except BaseException:
            sleep(4)
            assert "person-icon" not in [
                ii.get_attribute("data-cy")
                for ii in pageGrievanceDetailsPage.getPossibleDuplicateRowByUnicefId("IND-00-0000.0011").find_elements(
                    By.TAG_NAME, "svg"
                )
            ]
        assert "person-icon" not in [
            ii.get_attribute("data-cy")
            for ii in pageGrievanceDetailsPage.getPossibleDuplicateRowByUnicefId("IND-00-0000.0011").find_elements(
                By.TAG_NAME, "svg"
            )
        ]
        assert "people-icon" not in [
            ii.get_attribute("data-cy")
            for ii in pageGrievanceDetailsPage.getPossibleDuplicateRowByUnicefId("IND-00-0000.0022").find_elements(
                By.TAG_NAME, "svg"
            )
        ]
        assert "person-icon" not in [
            ii.get_attribute("data-cy")
            for ii in pageGrievanceDetailsPage.getPossibleDuplicateRowByUnicefId("IND-00-0000.0022").find_elements(
                By.TAG_NAME, "svg"
            )
        ]
        assert "people-icon" not in [
            ii.get_attribute("data-cy")
            for ii in pageGrievanceDetailsPage.getPossibleDuplicateRowByUnicefId("IND-00-0000.0033").find_elements(
                By.TAG_NAME, "svg"
            )
        ]
        assert "person-icon" not in [
            ii.get_attribute("data-cy")
            for ii in pageGrievanceDetailsPage.getPossibleDuplicateRowByUnicefId("IND-00-0000.0033").find_elements(
                By.TAG_NAME, "svg"
            )
        ]
        pageGrievanceDetailsPage.getPossibleDuplicateRowByUnicefId("IND-00-0000.0033").find_element(
            By.CSS_SELECTOR, 'input[type="checkbox"]'
        ).click()
        pageGrievanceDetailsPage.getButtonMarkDistinct().click()
        pageGrievanceDetailsPage.getButtonConfirm().click()
        pageGrievanceDetailsPage.getPersonIcon()
        pageGrievanceDetailsPage.getPossibleDuplicateRowByUnicefId("IND-00-0000.0011").find_element(
            By.CSS_SELECTOR, 'input[type="checkbox"]'
        ).click()
        pageGrievanceDetailsPage.getPossibleDuplicateRowByUnicefId("IND-00-0000.0022").find_element(
            By.CSS_SELECTOR, 'input[type="checkbox"]'
        ).click()
        pageGrievanceDetailsPage.getButtonMarkDuplicate().click()
        pageGrievanceDetailsPage.getPeopleIcon()
        assert "people-icon" in [
            ii.get_attribute("data-cy")
            for ii in pageGrievanceDetailsPage.getPossibleDuplicateRowByUnicefId("IND-00-0000.0011").find_elements(
                By.TAG_NAME, "svg"
            )
        ]
        assert "person-icon" in [
            ii.get_attribute("data-cy")
            for ii in pageGrievanceDetailsPage.getPossibleDuplicateRowByUnicefId("IND-00-0000.0033").find_elements(
                By.TAG_NAME, "svg"
            )
        ]
        assert "people-icon" in [
            ii.get_attribute("data-cy")
            for ii in pageGrievanceDetailsPage.getPossibleDuplicateRowByUnicefId("IND-00-0000.0022").find_elements(
                By.TAG_NAME, "svg"
            )
        ]
        duplicated_individual_unicef_id = "IND-00-0000.0022"
        pageGrievanceDetailsPage.getButtonCloseTicket().click()
        pageGrievanceDetailsPage.getButtonConfirm().click()
        pageGrievanceDetailsPage.disappearButtonConfirm()
        pageGrievanceDetailsPage.disappearButtonCloseTicket()

        pageGrievanceDetailsPage.selectGlobalProgramFilter("Test Program")
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

    @pytest.mark.xfail(reason="Unskip after fix bug: 209087")
    def test_grievance_tickets_create_new_error(
        self,
        pageGrievanceTickets: GrievanceTickets,
        pageGrievanceNewTicket: NewTicket,
        pageGrievanceDetailsPage: GrievanceDetailsPage,
    ) -> None:
        pageGrievanceTickets.getNavGrievance().click()
        assert "Grievance Tickets" in pageGrievanceTickets.getGrievanceTitle().text
        pageGrievanceTickets.getButtonNewTicket().click()
        pageGrievanceNewTicket.getButtonNext().click()
        with pytest.raises(Exception):
            pageGrievanceNewTicket.getHouseholdTab()
