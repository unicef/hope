import base64
from datetime import datetime
from time import sleep
from typing import Optional

from dateutil.relativedelta import relativedelta
import pytest
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from e2e.drawer.test_drawer import get_program_with_dct_type_and_name
from e2e.filters.test_filters import create_grievance
from e2e.helpers.date_time_format import FormatTime
from e2e.page_object.admin_panel.admin_panel import AdminPanel
from e2e.page_object.grievance.details_grievance_page import GrievanceDetailsPage
from e2e.page_object.grievance.grievance_tickets import GrievanceTickets
from e2e.page_object.grievance.new_ticket import NewTicket
from e2e.page_object.programme_population.households import Households
from e2e.page_object.programme_population.households_details import HouseholdsDetails
from e2e.page_object.programme_population.individuals import Individuals
from extras.test_utils.factories.core import (
    DataCollectingTypeFactory,
    create_afghanistan,
)
from extras.test_utils.factories.household import (
    IndividualRoleInHouseholdFactory,
    create_household,
    create_household_and_individuals,
)
from extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory

from hope.models.user import User
from hope.models.business_area import BusinessArea
from hope.models.data_collecting_type import DataCollectingType
from hope.models.area import Area
from hope.apps.grievance.models import GrievanceTicket, TicketNeedsAdjudicationDetails
from hope.models.household import HOST, Household
from hope.models.individual import Individual
from hope.models.payment import Payment
from hope.models.program import Program
from hope.models.beneficiary_group import BeneficiaryGroup

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
            "admin2": Area.objects.order_by("?").first(),
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
    return create_custom_household(observed_disability=[])


@pytest.fixture
def household_social_worker() -> Household:
    return create_custom_household(
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
    return PaymentFactory(
        parent=payment_plan,
        household=household_without_disabilities,
        delivered_quantity_usd=None,
        business_area=household_without_disabilities.business_area,
    )


def find_text_of_label(element: WebElement) -> str:
    return element.find_element(By.XPATH, "..").find_element(By.XPATH, "..").text


@pytest.fixture
def social_worker_program() -> Program:
    return create_program(
        "Social Program",
        dct_type=DataCollectingType.Type.SOCIAL,
        beneficiary_group="People",
    )


def create_program(
    name: str,
    dct_type: str = DataCollectingType.Type.STANDARD,
    status: str = Program.ACTIVE,
    beneficiary_group: str = "Main Menu",
) -> Program:
    dct = DataCollectingTypeFactory(type=dct_type)
    beneficiary_group = BeneficiaryGroup.objects.filter(name=beneficiary_group).first()
    return ProgramFactory(
        name=name,
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
        data_collecting_type=dct,
        status=status,
        beneficiary_group=beneficiary_group,
    )


def create_custom_household(
    observed_disability: list[str],
    residence_status: str = HOST,
    program_name: str = "Test Program",
    dct_type: str = DataCollectingType.Type.STANDARD,
    beneficiary_group_name: str = "Main Menu",
) -> Household:
    program = get_program_with_dct_type_and_name(
        program_name,
        "1234",
        dct_type=dct_type,
        beneficiary_group_name=beneficiary_group_name,
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
        business_area=business_area,
        unicef_id=unicef_id,
        language="Polish",
        consent=True,
        description="grievance_ticket_1",
        category=category,
        status=status,
        created_by=created_by,
        assigned_to=assigned_to,
        created_at=created_at,
        updated_at=updated_at,
        household_unicef_id=household_unicef_id,
        priority=priority,
        urgency=urgency,
        issue_type=GrievanceTicket.ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY,
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
    return grievance


@pytest.fixture
def create_four_grievance_tickets() -> [GrievanceTicket]:
    afghanistan = BusinessArea.objects.filter(slug="afghanistan").first()
    program = ProgramFactory(
        business_area=afghanistan,
        status=Program.ACTIVE,
        name="Test Program",
    )

    GrievanceTicket._meta.get_field("created_at").auto_now_add = False
    GrievanceTicket._meta.get_field("updated_at").auto_now = False
    grievance = [
        create_grievance_referral(assigned_to="", business_area=afghanistan, program=program) for _ in range(4)
    ]
    GrievanceTicket._meta.get_field("created_at").auto_now_add = True
    GrievanceTicket._meta.get_field("updated_at").auto_now = True
    return grievance


@pytest.fixture
def create_grievance_tickets_social_program() -> GrievanceTicket:
    grievance = create_grievance_referral(assigned_to="", household_unicef_id="HH-20-0000.0001")
    grievance.programs.add(Program.objects.filter(name="Social Program").first())
    grievance.save()
    return grievance


def create_grievance_referral(
    unicef_id: str = "GRV-0000001",
    status: int = GrievanceTicket.STATUS_NEW,
    category: int = GrievanceTicket.CATEGORY_REFERRAL,
    created_by: User | None = None,
    assigned_to: User | None | str = None,
    business_area: BusinessArea | None = None,
    program: Program | None = None,
    priority: int = 1,
    urgency: int = 1,
    household_unicef_id: str = "HH-20-0000.0001",
    updated_at: str = "2023-09-27T11:26:33.846Z",
    created_at: str = "2022-04-30T09:54:07.827000",
) -> GrievanceTicket:
    created_by = User.objects.first() if created_by is None else created_by
    business_area = BusinessArea.objects.filter(slug="afghanistan").first() if business_area is None else business_area
    if not program:
        program = ProgramFactory(
            business_area=business_area,
            status=Program.ACTIVE,
            name="Test Program E2E",
        )

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

    from hope.apps.grievance.models import TicketReferralDetails

    TicketReferralDetails.objects.create(
        ticket=grievance_ticket,
        individual=Individual.objects.filter(unicef_id="IND-00-0000.0011").first(),
    )
    # assign Program
    grievance_ticket.programs.add(program)
    grievance_ticket.save()
    return grievance_ticket


@pytest.mark.usefixtures("login")
class TestSmokeGrievanceTickets:
    def test_check_grievance_tickets_user_generated_page(
        self,
        create_programs: None,
        add_households: None,
        add_grievance: None,
        page_grievance_tickets: GrievanceTickets,
    ) -> None:
        """
        Go to Grievance tickets user generated page
        Check if all elements on page exist
        """
        # Go to Grievance Tickets
        page_grievance_tickets.get_nav_grievance().click()
        assert "Grievance Tickets" in page_grievance_tickets.get_grievance_title().text
        page_grievance_tickets.get_select_all().click()
        assert "NEW TICKET" in page_grievance_tickets.get_button_new_ticket().text
        assert "ASSIGN" in page_grievance_tickets.get_button_assign().text
        assert "SET PRIORITY" in page_grievance_tickets.get_button_set_priority().text
        assert "SET URGENCY" in page_grievance_tickets.get_button_set_urgency().text
        assert "ADD NOTE" in page_grievance_tickets.get_button_add_note().text
        assert len(page_grievance_tickets.get_ticket_list_row()) == 2
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
        assert expected_labels == [i.text for i in page_grievance_tickets.get_table_label()]

    @pytest.mark.xfail(reason="UNSTABLE")
    def test_check_grievance_tickets_system_generated_page(
        self,
        create_programs: None,
        add_households: None,
        add_grievance: None,
        page_grievance_tickets: GrievanceTickets,
    ) -> None:
        """
        Go to Grievance tickets system generated page
        Check if all elements on page exist
        """
        # Go to Grievance Tickets
        page_grievance_tickets.get_nav_grievance().click()
        assert "Grievance Tickets" in page_grievance_tickets.get_grievance_title().text
        page_grievance_tickets.get_ticket_list_row()
        page_grievance_tickets.get_tab_system_generated().click()
        assert len(page_grievance_tickets.get_ticket_list_row()) == 1
        page_grievance_tickets.get_select_all().click()
        assert "ASSIGN" in page_grievance_tickets.get_button_assign().text
        assert "SET PRIORITY" in page_grievance_tickets.get_button_set_priority().text
        assert "SET URGENCY" in page_grievance_tickets.get_button_set_urgency().text
        assert "ADD NOTE" in page_grievance_tickets.get_button_add_note().text
        assert "NEW TICKET" in page_grievance_tickets.get_button_new_ticket().text

    @pytest.mark.xfail(reason="UNSTABLE")
    def test_check_grievance_tickets_details_page(
        self,
        create_programs: None,
        add_households: None,
        add_grievance: None,
        page_grievance_tickets: GrievanceTickets,
        page_grievance_details_page: GrievanceDetailsPage,
    ) -> None:
        """
        Go to Grievance tickets details page
        Check if all elements on page exist
        """
        # Go to Grievance Tickets
        page_grievance_tickets.get_nav_grievance().click()
        assert "Grievance Tickets" in page_grievance_tickets.get_grievance_title().text
        page_grievance_tickets.get_ticket_list_row()[0].click()
        page_grievance_details_page.get_ticket_status()
        assert "Ticket ID" in page_grievance_details_page.get_title().text
        assert "EDIT" in page_grievance_details_page.get_button_edit().text
        assert "SEND BACK" in page_grievance_details_page.get_button_send_back().text
        assert "CLOSE TICKET" in page_grievance_details_page.get_button_close_ticket().text
        assert "For Approval" in page_grievance_details_page.get_ticket_status().text
        assert "Medium" in page_grievance_details_page.get_ticket_priority().text
        assert "Urgent" in page_grievance_details_page.get_ticket_urgency().text
        assert "-" in page_grievance_details_page.get_ticket_assigment().text
        assert "Referral" in page_grievance_details_page.get_ticket_category().text
        assert "HH-20-0000.0002" in page_grievance_details_page.get_ticket_target_id().text
        assert "-" in page_grievance_details_page.get_ticket_payment_label().text
        assert "-" in page_grievance_details_page.get_label_payment_plan().text
        assert "-" in page_grievance_details_page.get_label_payment_plan_verification().text
        assert "Andarab" in page_grievance_details_page.get_administrative_level().text
        assert "English | English" in page_grievance_details_page.get_languages_spoken().text
        assert "-" in page_grievance_details_page.get_documentation().text
        assert "Test 4" in page_grievance_details_page.get_ticket_description().text
        assert "" in page_grievance_details_page.get_new_note_field().text
        assert "ADD NEW NOTE" in page_grievance_details_page.get_button_new_note().text

    @pytest.mark.xfail(reason="UNSTABLE")
    def test_check_grievance_tickets_details_page_normal_program(
        self,
        create_programs: None,
        add_households: None,
        add_grievance: None,
        page_grievance_tickets: GrievanceTickets,
        page_grievance_details_page: GrievanceDetailsPage,
    ) -> None:
        """
        Go to Grievance tickets details page
        Check if all elements on page exist
        """
        page_grievance_tickets.select_global_program_filter("Test Programm")
        # Go to Grievance Tickets
        page_grievance_tickets.get_nav_grievance().click()
        assert "Grievance Tickets" in page_grievance_tickets.get_grievance_title().text
        page_grievance_tickets.get_ticket_list_row()[0].click()
        page_grievance_details_page.get_ticket_status()
        assert "Ticket ID" in page_grievance_details_page.get_title().text
        assert "EDIT" in page_grievance_details_page.get_button_edit().text
        assert "SEND BACK" in page_grievance_details_page.get_button_send_back().text
        assert "CLOSE TICKET" in page_grievance_details_page.get_button_close_ticket().text
        assert "For Approval" in page_grievance_details_page.get_ticket_status().text
        assert "Medium" in page_grievance_details_page.get_ticket_priority().text
        assert "Urgent" in page_grievance_details_page.get_ticket_urgency().text
        assert "-" in page_grievance_details_page.get_ticket_assigment().text
        assert "Referral" in page_grievance_details_page.get_ticket_category().text
        assert "HH-20-0000.0002" in page_grievance_details_page.get_ticket_household_id().text
        assert "IND-74-0000.0001" in page_grievance_details_page.get_ticket_individual_id().text
        assert "-" in page_grievance_details_page.get_label_payment_plan().text
        assert "-" in page_grievance_details_page.get_label_payment_plan_verification().text
        assert "Test Program" in page_grievance_details_page.get_label_programme().text
        assert "Shakardara" in page_grievance_details_page.get_administrative_level().text
        assert "-" in page_grievance_details_page.get_area_village().text
        assert "English | English" in page_grievance_details_page.get_languages_spoken().text
        assert "-" in page_grievance_details_page.get_documentation().text
        assert "Test 4" in page_grievance_details_page.get_ticket_description().text
        assert "" in page_grievance_details_page.get_new_note_field().text
        assert "ADD NEW NOTE" in page_grievance_details_page.get_button_new_note().text

    def test_check_grievance_tickets_details_page_social_worker_program(
        self,
        household_social_worker: Household,
        create_grievance_tickets_social_program: GrievanceTicket,
        page_grievance_tickets: GrievanceTickets,
        page_grievance_details_page: GrievanceDetailsPage,
    ) -> None:
        """
        Go to Grievance tickets details page
        Check if all elements on page exist
        """
        page_grievance_tickets.select_global_program_filter("Social Program")
        # Go to Grievance Tickets
        page_grievance_tickets.get_nav_grievance().click()
        assert "Grievance Tickets" in page_grievance_tickets.get_grievance_title().text
        page_grievance_tickets.get_ticket_list_row()[0].click()
        page_grievance_details_page.get_ticket_status()
        assert "Ticket ID" in page_grievance_details_page.get_title().text
        assert "EDIT" in page_grievance_details_page.get_button_edit().text
        assert "ASSIGN TO ME" in page_grievance_details_page.get_button_assign_to_me().text
        assert "New" in page_grievance_details_page.get_label_status().text
        assert "High" in page_grievance_details_page.get_label_priority().text
        assert "Very urgent" in page_grievance_details_page.get_label_urgency().text
        assert "Referral" in page_grievance_details_page.get_ticket_category().text
        assert "Social Program" in page_grievance_details_page.get_label_programme().text
        assert "IND-00-0000.0011" in page_grievance_details_page.get_ticket_target_id().text


@pytest.mark.usefixtures("login")
class TestGrievanceTicketsHappyPath:
    def test_grievance_tickets_create_new_ticket_referral(
        self,
        page_grievance_tickets: GrievanceTickets,
        page_grievance_new_ticket: NewTicket,
        page_grievance_details_page: GrievanceDetailsPage,
        social_worker_program: Program,
    ) -> None:
        page_grievance_tickets.get_nav_grievance().click()
        assert "Grievance Tickets" in page_grievance_tickets.get_grievance_title().text
        page_grievance_tickets.get_button_new_ticket().click()
        page_grievance_new_ticket.get_select_category().click()
        page_grievance_new_ticket.select_option_by_name("Referral")
        page_grievance_new_ticket.get_button_next().click()
        page_grievance_new_ticket.get_household_tab()
        assert page_grievance_new_ticket.wait_for_no_results()
        page_grievance_new_ticket.get_button_next().click()
        page_grievance_new_ticket.get_received_consent().click()
        page_grievance_new_ticket.get_button_next().click()
        page_grievance_new_ticket.get_description().send_keys("Happy path test 1234!")
        page_grievance_new_ticket.get_button_next().click()
        assert "Happy path test 1234!" in page_grievance_details_page.get_ticket_description().text
        assert "Referral" in page_grievance_details_page.get_ticket_category().text
        assert "New" in page_grievance_details_page.get_ticket_status().text
        assert "Not set" in page_grievance_details_page.get_ticket_priority().text
        assert "Not set" in page_grievance_details_page.get_ticket_urgency().text


@pytest.mark.night
@pytest.mark.usefixtures("login")
class TestGrievanceTickets:
    @pytest.mark.xfail(reason="UNSTABLE")
    @pytest.mark.parametrize(
        "test_data",
        [
            pytest.param(
                {"category": "Sensitive Grievance", "type": "Miscellaneous"},
                id="Sensitive Grievance Miscellaneous",
            ),
            pytest.param(
                {"category": "Sensitive Grievance", "type": "Personal disputes"},
                id="Sensitive Grievance Personal disputes",
            ),
            pytest.param(
                {"category": "Grievance Complaint", "type": "Other Complaint"},
                id="Grievance Complaint Other Complaint",
            ),
            pytest.param(
                {
                    "category": "Grievance Complaint",
                    "type": "Registration Related Complaint",
                },
                id="Grievance Complaint Registration Related Complaint",
            ),
            pytest.param(
                {"category": "Grievance Complaint", "type": "FSP Related Complaint"},
                id="Grievance Complaint FSP Related Complaint",
            ),
            pytest.param(
                {"category": "Data Change", "type": "Withdraw Individual"},
                id="Data Change Withdraw Individual",
            ),
            pytest.param(
                {"category": "Data Change", "type": "Withdraw Household"},
                id="Data Change Withdraw Household",
            ),
        ],
    )
    def test_grievance_tickets_create_new_tickets(
        self,
        page_grievance_tickets: GrievanceTickets,
        page_grievance_new_ticket: NewTicket,
        page_grievance_details_page: GrievanceDetailsPage,
        test_data: dict,
        household_without_disabilities: Household,
    ) -> None:
        page_grievance_tickets.get_nav_grievance().click()
        assert "Grievance Tickets" in page_grievance_tickets.get_grievance_title().text
        page_grievance_tickets.get_button_new_ticket().click()
        page_grievance_new_ticket.get_select_category().click()
        page_grievance_new_ticket.select_option_by_name(test_data["category"])
        page_grievance_new_ticket.get_issue_type().click()
        page_grievance_new_ticket.select_listbox_element(test_data["type"])
        assert test_data["category"] in page_grievance_new_ticket.get_select_category().text
        assert test_data["type"] in page_grievance_new_ticket.get_issue_type().text
        page_grievance_new_ticket.get_button_next().click()
        page_grievance_new_ticket.get_household_tab()
        page_grievance_new_ticket.get_household_table_rows(0).click()
        if test_data["type"] not in [
            "Withdraw Household",
            "Household Data Update",
            "Add Individual",
        ]:
            page_grievance_new_ticket.get_individual_tab().click()
            page_grievance_new_ticket.get_individual_table_rows(0).click()
        page_grievance_new_ticket.get_button_next().click()
        page_grievance_new_ticket.get_received_consent().click()
        page_grievance_new_ticket.get_button_next().click()
        page_grievance_new_ticket.get_description().send_keys("Happy path test 1234!")
        page_grievance_new_ticket.get_button_next().click()
        assert "Happy path test 1234!" in page_grievance_details_page.get_ticket_description().text
        assert "Test Program" in page_grievance_details_page.get_label_programme().text
        user = User.objects.get(email="test@example.com")
        assert f"{user.first_name} {user.last_name}" in page_grievance_details_page.get_label_created_by().text
        assert test_data["category"] in page_grievance_details_page.get_ticket_category().text
        assert test_data["type"] in page_grievance_details_page.get_label_issue_type().text
        assert "New" in page_grievance_details_page.get_ticket_status().text
        assert "Not set" in page_grievance_details_page.get_ticket_priority().text
        assert "Not set" in page_grievance_details_page.get_ticket_urgency().text

    def test_grievance_tickets_create_new_tickets_social_program(
        self,
        page_grievance_tickets: GrievanceTickets,
        page_grievance_new_ticket: NewTicket,
        page_grievance_details_page: GrievanceDetailsPage,
        household_social_worker: Household,
    ) -> None:
        page_grievance_tickets.select_global_program_filter("Social Program")
        page_grievance_tickets.get_nav_grievance().click()
        assert "Grievance Tickets" in page_grievance_tickets.get_grievance_title().text
        page_grievance_tickets.get_button_new_ticket().click()
        page_grievance_new_ticket.get_select_category().click()
        page_grievance_new_ticket.select_listbox_element("Data Change")
        page_grievance_new_ticket.get_issue_type().click()
        select_element = page_grievance_new_ticket.wait_for('ul[role="listbox"]')
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

    def test_grievance_tickets_create_new_ticket_data_change_add_individual_all_fields(
        self,
        page_grievance_tickets: GrievanceTickets,
        page_grievance_new_ticket: NewTicket,
        page_grievance_details_page: GrievanceDetailsPage,
        household_without_disabilities: Household,
    ) -> None:
        page_grievance_tickets.get_nav_grievance().click()
        assert "Grievance Tickets" in page_grievance_tickets.get_grievance_title().text
        page_grievance_tickets.get_button_new_ticket().click()
        page_grievance_new_ticket.get_select_category().click()
        page_grievance_new_ticket.select_option_by_name("Data Change")
        page_grievance_new_ticket.get_issue_type().click()
        page_grievance_new_ticket.select_listbox_element("Add Member")
        assert "Data Change" in page_grievance_new_ticket.get_select_category().text
        assert "Add Member" in page_grievance_new_ticket.get_issue_type().text
        page_grievance_new_ticket.get_button_next().click()
        page_grievance_new_ticket.get_household_tab()
        page_grievance_new_ticket.get_household_table_rows(0).click()
        page_grievance_new_ticket.get_button_next().click()
        page_grievance_new_ticket.get_received_consent().click()
        page_grievance_new_ticket.get_button_next().click()
        page_grievance_new_ticket.get_description().send_keys("Add Member - TEST")
        page_grievance_new_ticket.get_phone_no_alternative().send_keys("999 999 999")
        page_grievance_new_ticket.get_date_picker_filter().click()
        page_grievance_new_ticket.get_date_picker_filter().send_keys(FormatTime(1, 5, 1986).numerically_formatted_date)
        page_grievance_new_ticket.get_input_individualdata_blockchainname().send_keys("TEST")
        page_grievance_new_ticket.get_input_individualdata_familyname().send_keys("Teria")
        page_grievance_new_ticket.get_input_individualdata_fullname().send_keys("Krido")
        page_grievance_new_ticket.get_estimated_birth_date().click()
        page_grievance_new_ticket.select_listbox_element("Yes")
        page_grievance_new_ticket.get_select_individualdata_sex().click()
        page_grievance_new_ticket.select_listbox_element("Male")
        page_grievance_new_ticket.get_input_individualdata_givenname().send_keys("Krato")
        page_grievance_new_ticket.get_select_individualdata_commsdisability().click()
        page_grievance_new_ticket.select_listbox_element("A lot of difficulty")
        page_grievance_new_ticket.get_select_individualdata_hearingdisability().click()
        page_grievance_new_ticket.select_listbox_element("A lot of difficulty")
        page_grievance_new_ticket.get_select_individualdata_memorydisability().click()
        page_grievance_new_ticket.select_listbox_element("Cannot do at all")
        page_grievance_new_ticket.get_select_individualdata_seeingdisability().click()
        page_grievance_new_ticket.select_listbox_element("Some difficulty")
        page_grievance_new_ticket.get_select_individualdata_physicaldisability().click()
        page_grievance_new_ticket.select_listbox_element("None")
        page_grievance_new_ticket.get_input_individualdata_email().send_keys("kridoteria@bukare.cz")
        page_grievance_new_ticket.get_select_individualdata_disability().click()
        page_grievance_new_ticket.select_listbox_element("disabled")
        page_grievance_new_ticket.get_select_individualdata_pregnant().click()
        page_grievance_new_ticket.select_listbox_element("No")
        page_grievance_new_ticket.get_select_individualdata_maritalstatus().click()
        page_grievance_new_ticket.select_listbox_element("Married")
        page_grievance_new_ticket.get_input_individualdata_middlename().send_keys("Batu")
        page_grievance_new_ticket.get_input_individualdata_phoneno().send_keys("098 765 432")
        page_grievance_new_ticket.get_select_individualdata_preferredlanguage().click()
        page_grievance_new_ticket.select_listbox_element("English")
        page_grievance_new_ticket.get_select_individualdata_relationship().click()
        page_grievance_new_ticket.select_listbox_element("Wife / Husband")
        # page_grievance_new_ticket.get_select_individualdata_role().click()
        # page_grievance_new_ticket.select_listbox_element("Alternate collector")
        page_grievance_new_ticket.get_input_individualdata_walletaddress().send_keys("Wordoki")
        page_grievance_new_ticket.get_input_individualdata_walletname().send_keys("123")
        page_grievance_new_ticket.get_input_individualdata_whoanswersaltphone().send_keys("000 000 000")
        page_grievance_new_ticket.get_input_individualdata_whoanswersphone().send_keys("111 11 11")

        page_grievance_new_ticket.get_button_next().click()
        assert "Add Member - TEST" in page_grievance_details_page.get_ticket_description().text
        assert "Data Change" in page_grievance_details_page.get_ticket_category().text
        assert "Add Member" in page_grievance_details_page.get_label_issue_type().text
        assert "New" in page_grievance_details_page.get_ticket_status().text
        assert "Not set" in page_grievance_details_page.get_ticket_priority().text
        assert "Not set" in page_grievance_details_page.get_ticket_urgency().text

    def test_grievance_tickets_create_new_ticket_data_change_add_individual_mandatory_fields(
        self,
        page_grievance_tickets: GrievanceTickets,
        page_grievance_new_ticket: NewTicket,
        page_grievance_details_page: GrievanceDetailsPage,
        household_without_disabilities: Household,
    ) -> None:
        page_grievance_tickets.get_nav_grievance().click()
        assert "Grievance Tickets" in page_grievance_tickets.get_grievance_title().text
        page_grievance_tickets.get_button_new_ticket().click()
        page_grievance_new_ticket.get_select_category().click()
        page_grievance_new_ticket.select_option_by_name("Data Change")
        page_grievance_new_ticket.get_issue_type().click()
        page_grievance_new_ticket.select_listbox_element("Add Member")
        assert "Data Change" in page_grievance_new_ticket.get_select_category().text
        assert "Add Member" in page_grievance_new_ticket.get_issue_type().text
        page_grievance_new_ticket.get_button_next().click()
        page_grievance_new_ticket.get_household_tab()
        page_grievance_new_ticket.get_household_table_rows(0).click()
        page_grievance_new_ticket.get_button_next().click()
        page_grievance_new_ticket.get_received_consent().click()
        page_grievance_new_ticket.get_button_next().click()

        page_grievance_new_ticket.get_description().send_keys("Add Individual - TEST")
        page_grievance_new_ticket.get_date_picker_filter().click()
        page_grievance_new_ticket.get_date_picker_filter().send_keys(FormatTime(1, 5, 1986).numerically_formatted_date)

        page_grievance_new_ticket.get_input_individualdata_fullname().send_keys("Krido")
        page_grievance_new_ticket.get_select_individualdata_sex().click()
        page_grievance_new_ticket.select_listbox_element("Male")

        page_grievance_new_ticket.get_estimated_birth_date().click()
        page_grievance_new_ticket.select_listbox_element("Yes")

        page_grievance_new_ticket.get_select_individualdata_relationship().click()
        page_grievance_new_ticket.select_listbox_element("Wife / Husband")
        # page_grievance_new_ticket.get_select_individualdata_role().click()
        # page_grievance_new_ticket.select_listbox_element("Alternate collector")
        page_grievance_new_ticket.get_button_next().click()
        assert "ASSIGN TO ME" in page_grievance_details_page.get_button_assign_to_me().text
        assert "New" in page_grievance_details_page.get_ticket_status().text
        assert "Not set" in page_grievance_details_page.get_ticket_priority().text
        assert "Not set" in page_grievance_details_page.get_ticket_urgency().text
        assert "-" in page_grievance_details_page.get_ticket_assigment().text
        assert "Data Change" in page_grievance_details_page.get_ticket_category().text
        assert "Add Member" in page_grievance_details_page.get_label_issue_type().text
        assert household_without_disabilities.unicef_id in page_grievance_details_page.get_ticket_target_id().text
        assert "Test Program" in page_grievance_details_page.get_label_programme().text
        assert datetime.now().strftime("%-d %b %Y") in page_grievance_details_page.get_label_date_creation().text
        assert datetime.now().strftime("%-d %b %Y") in page_grievance_details_page.get_label_last_modified_date().text
        assert "-" in page_grievance_details_page.get_label_documentation().text
        assert "Add Individual - TEST" in page_grievance_details_page.get_label_description().text
        assert "Male" in page_grievance_details_page.get_label_gender().text
        # assert "Alternate collector" in page_grievance_details_page.get_label_role().text
        assert "Krido" in page_grievance_details_page.get_label_full_name().text
        assert "1986-05-01" in page_grievance_details_page.get_label_birth_date().text
        assert "Wife / Husband" in page_grievance_details_page.get_label_relationship().text
        assert "Yes" in page_grievance_details_page.get_label_estimated_birth_date().text

    @pytest.mark.parametrize(
        "test_data",
        [
            pytest.param(
                {"category": "Data Change", "type": "Group Data Update"},
                id="Data Change Group Data Update",
            ),
        ],
    )
    def test_hh_grievance_tickets_create_new_ticket(
        self,
        page_grievance_tickets: GrievanceTickets,
        page_grievance_new_ticket: NewTicket,
        page_grievance_details_page: GrievanceDetailsPage,
        household_without_disabilities: Household,
        test_data: dict,
    ) -> None:
        page_grievance_tickets.get_nav_grievance().click()
        assert "Grievance Tickets" in page_grievance_tickets.get_grievance_title().text
        page_grievance_tickets.get_button_new_ticket().click()
        page_grievance_new_ticket.get_select_category().click()
        page_grievance_new_ticket.select_option_by_name(str(test_data["category"]))
        page_grievance_new_ticket.get_issue_type().click()
        page_grievance_new_ticket.select_listbox_element(str(test_data["type"]))
        assert test_data["category"] in page_grievance_new_ticket.get_select_category().text
        assert test_data["type"] in page_grievance_new_ticket.get_issue_type().text
        page_grievance_new_ticket.get_button_next().click()
        page_grievance_new_ticket.get_household_tab()
        page_grievance_new_ticket.get_household_table_rows(0).click()
        page_grievance_new_ticket.get_button_next().click()
        page_grievance_new_ticket.get_received_consent().click()
        page_grievance_new_ticket.get_button_next().click()

        page_grievance_new_ticket.get_description().send_keys("Add Group - TEST")
        page_grievance_new_ticket.get_button_add_new_field()
        page_grievance_new_ticket.get_select_field_name().click()
        page_grievance_new_ticket.select_listbox_element("Females age 12 - 17 with disability")
        page_grievance_new_ticket.get_input_value().send_keys("1")
        page_grievance_new_ticket.get_button_next().click()
        page_grievance_details_page.get_checkbox_household_data()
        assert "Female Age Group 12 17" in page_grievance_details_page.get_rows()[0].text
        assert "- 1" in page_grievance_details_page.get_rows()[0].text

    @pytest.mark.xfail(reason="UNSTABLE AFTER REST REFACTOR")
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
        page_grievance_tickets: GrievanceTickets,
        page_grievance_new_ticket: NewTicket,
        page_grievance_details_page: GrievanceDetailsPage,
        household_without_disabilities: Household,
        test_data: dict,
    ) -> None:
        page_grievance_tickets.get_nav_grievance().click()
        assert "Grievance Tickets" in page_grievance_tickets.get_grievance_title().text
        page_grievance_tickets.get_button_new_ticket().click()
        page_grievance_new_ticket.get_select_category().click()
        page_grievance_new_ticket.select_option_by_name(str(test_data["category"]))
        page_grievance_new_ticket.get_issue_type().click()
        page_grievance_new_ticket.element_clickable(f'li[data-cy="select-option-{test_data["type"]}"]')
        page_grievance_new_ticket.select_listbox_element(str(test_data["type"]))
        assert test_data["category"] in page_grievance_new_ticket.get_select_category().text
        assert test_data["type"] in page_grievance_new_ticket.get_issue_type().text
        page_grievance_new_ticket.get_button_next().click()
        page_grievance_new_ticket.get_household_tab()
        page_grievance_new_ticket.get_household_table_rows(0).click()
        page_grievance_new_ticket.get_individual_tab().click()
        page_grievance_new_ticket.get_individual_table_rows(0).click()
        page_grievance_new_ticket.get_button_next().click()
        page_grievance_new_ticket.get_received_consent().click()
        page_grievance_new_ticket.get_button_next().click()

        page_grievance_new_ticket.get_description().send_keys("Add Member Data Update - TEST")
        page_grievance_new_ticket.get_button_add_new_field().click()
        page_grievance_new_ticket.get_individual_field_name(0).click()
        page_grievance_new_ticket.select_listbox_element("Gender")
        page_grievance_new_ticket.get_input_individual_data("Gender").click()
        page_grievance_new_ticket.select_listbox_element("Female")
        page_grievance_new_ticket.get_individual_field_name(1).click()
        page_grievance_new_ticket.select_listbox_element("Preferred language")
        page_grievance_new_ticket.get_input_individual_data("Preferred language").click()
        page_grievance_new_ticket.select_listbox_element("English | English")

        page_grievance_new_ticket.get_button_next().click()
        page_grievance_details_page.get_checkbox_individual_data()
        row0 = page_grievance_details_page.get_rows()[0].text.split(" ")
        assert "Gender" in row0[0]
        assert "Female" in row0[-1]

        row1 = page_grievance_details_page.get_rows()[1].text.split(" ")
        assert "Preferred Language" in f"{row1[0]} {row1[1]}"
        assert "English" in row1[-1]

    def test_grievance_tickets_create_new_tickets_grievance_complaint_partner_related_complaint(
        self,
        page_grievance_tickets: GrievanceTickets,
        page_grievance_new_ticket: NewTicket,
        page_grievance_details_page: GrievanceDetailsPage,
        household_without_disabilities: Household,
    ) -> None:
        page_grievance_tickets.get_nav_grievance().click()
        assert "Grievance Tickets" in page_grievance_tickets.get_grievance_title().text
        page_grievance_tickets.get_button_new_ticket().click()
        page_grievance_new_ticket.get_select_category().click()
        page_grievance_new_ticket.select_option_by_name("Grievance Complaint")
        page_grievance_new_ticket.get_issue_type().click()
        page_grievance_new_ticket.select_listbox_element("Partner Related Complaint")
        assert "Grievance Complaint" in page_grievance_new_ticket.get_select_category().text
        assert "Partner Related Complaint" in page_grievance_new_ticket.get_issue_type().text
        page_grievance_new_ticket.get_button_next().click()
        page_grievance_new_ticket.get_household_tab()
        page_grievance_new_ticket.get_button_next().click()
        page_grievance_new_ticket.get_received_consent().click()
        page_grievance_new_ticket.get_button_next().click()
        page_grievance_new_ticket.get_partner().click()
        page_grievance_new_ticket.select_option_by_name("UNICEF HQ")
        page_grievance_new_ticket.get_description().send_keys("Test !@#$ OK")
        page_grievance_new_ticket.get_button_next().click()
        assert "UNICEF HQ" in page_grievance_details_page.get_label_partner().text

    def test_grievance_tickets_create_new_tickets_grievance_complaint_payment_related_complaint(
        self,
        page_grievance_tickets: GrievanceTickets,
        page_grievance_new_ticket: NewTicket,
        page_grievance_details_page: GrievanceDetailsPage,
        hh_with_payment_record: Payment,
    ) -> None:
        payment_id = Payment.objects.first().unicef_id
        page_grievance_tickets.get_nav_grievance().click()
        assert "Grievance Tickets" in page_grievance_tickets.get_grievance_title().text
        page_grievance_tickets.get_button_new_ticket().click()
        page_grievance_new_ticket.get_select_category().click()
        page_grievance_new_ticket.select_option_by_name("Grievance Complaint")
        page_grievance_new_ticket.get_issue_type().click()
        page_grievance_new_ticket.select_listbox_element("Payment Related Complaint")
        assert "Grievance Complaint" in page_grievance_new_ticket.get_select_category().text
        assert "Payment Related Complaint" in page_grievance_new_ticket.get_issue_type().text
        page_grievance_new_ticket.get_button_next().click()
        page_grievance_new_ticket.get_household_tab()
        page_grievance_new_ticket.get_household_table_rows(0).click()
        page_grievance_new_ticket.get_button_next().click()
        page_grievance_new_ticket.get_received_consent().click()
        page_grievance_new_ticket.get_button_next().click()
        page_grievance_new_ticket.get_description().send_keys("TEST Payment Related Complaint")
        page_grievance_new_ticket.get_look_up_payment_record().click()
        page_grievance_new_ticket.get_checkbox_select_all().click()
        page_grievance_new_ticket.get_button_submit().click()
        assert hh_with_payment_record.unicef_id in page_grievance_details_page.get_payment_record().text
        page_grievance_new_ticket.get_button_next().click()
        assert payment_id in page_grievance_details_page.get_ticket_payment_label().text

    def test_grievance_tickets_look_up_linked_ticket(
        self,
        page_grievance_tickets: GrievanceTickets,
        page_grievance_new_ticket: NewTicket,
        page_grievance_details_page: GrievanceDetailsPage,
        household_without_disabilities: Household,
        add_grievance_tickets: GrievanceTicket,
    ) -> None:
        linked_ticket = GrievanceTicket.objects.first().unicef_id
        page_grievance_tickets.get_nav_grievance().click()
        assert "Grievance Tickets" in page_grievance_tickets.get_grievance_title().text
        page_grievance_tickets.get_button_new_ticket().click()
        page_grievance_new_ticket.get_select_category().click()
        page_grievance_new_ticket.select_option_by_name("Referral")
        page_grievance_new_ticket.get_button_next().click()
        page_grievance_new_ticket.get_household_tab()
        page_grievance_new_ticket.get_button_next().click()
        page_grievance_new_ticket.get_received_consent().click()
        page_grievance_new_ticket.get_button_next().click()
        page_grievance_new_ticket.get_description().send_keys("TEST Linked Ticket")
        page_grievance_new_ticket.get_look_up_button().click()
        page_grievance_new_ticket.get_checkbox_select_all().click()
        page_grievance_new_ticket.get_button_submit().click()
        assert linked_ticket in page_grievance_new_ticket.get_linked_ticket_id().text
        page_grievance_new_ticket.get_button_edit().click()
        page_grievance_new_ticket.get_button_submit().click()
        page_grievance_new_ticket.get_button_delete().click()
        with pytest.raises(NoSuchElementException):
            page_grievance_new_ticket.get_linked_ticket_id()
        page_grievance_new_ticket.get_look_up_button().click()
        page_grievance_new_ticket.get_checkbox_select_all().click()
        page_grievance_new_ticket.get_button_submit().click()
        assert linked_ticket in page_grievance_new_ticket.get_linked_ticket_id().text
        page_grievance_new_ticket.get_button_next().click()
        assert linked_ticket in page_grievance_details_page.get_label_tickets().text

    def test_grievance_tickets_add_documentation(
        self,
        page_grievance_tickets: GrievanceTickets,
        page_grievance_new_ticket: NewTicket,
        page_grievance_details_page: GrievanceDetailsPage,
        household_without_disabilities: Household,
    ) -> None:
        page_grievance_tickets.get_nav_grievance().click()
        assert "Grievance Tickets" in page_grievance_tickets.get_grievance_title().text
        page_grievance_tickets.get_button_new_ticket().click()
        page_grievance_new_ticket.get_select_category().click()
        page_grievance_new_ticket.select_option_by_name("Referral")
        page_grievance_new_ticket.get_button_next().click()
        page_grievance_new_ticket.get_household_tab()
        page_grievance_new_ticket.get_button_next().click()
        page_grievance_new_ticket.get_received_consent().click()
        page_grievance_new_ticket.get_button_next().click()
        page_grievance_new_ticket.get_description().send_keys("Happy path test 1234!")
        page_grievance_new_ticket.get_add_documentation().click()
        page_grievance_new_ticket.get_input_documentation_name(0).send_keys("example")
        page_grievance_new_ticket.upload_file(f"{pytest.SELENIUM_PATH}/helpers/document_example.png")
        page_grievance_new_ticket.get_button_next().click()
        assert "example" in page_grievance_details_page.get_link_show_photo().text
        page_grievance_details_page.get_link_show_photo().click()
        page_grievance_details_page.get_button_rotate_image().click()
        page_grievance_details_page.get_button_cancel().click()
        assert "example" in page_grievance_details_page.get_link_show_photo().text

    def test_grievance_tickets_check_identity_verification(
        self,
        page_grievance_tickets: GrievanceTickets,
        page_grievance_new_ticket: NewTicket,
        page_grievance_details_page: GrievanceDetailsPage,
        household_without_disabilities: Household,
    ) -> None:
        page_grievance_tickets.get_nav_grievance().click()
        assert "Grievance Tickets" in page_grievance_tickets.get_grievance_title().text
        page_grievance_tickets.get_button_new_ticket().click()
        page_grievance_new_ticket.get_select_category().click()
        page_grievance_new_ticket.select_option_by_name("Data Change")
        page_grievance_new_ticket.get_issue_type().click()
        page_grievance_new_ticket.select_listbox_element("Member Data Update")
        assert "Data Change" in page_grievance_new_ticket.get_select_category().text
        assert "Member Data Update" in page_grievance_new_ticket.get_issue_type().text
        page_grievance_new_ticket.get_button_next().click()
        page_grievance_new_ticket.get_household_tab()
        page_grievance_new_ticket.get_individual_tab().click()
        individual_unicef_id = page_grievance_new_ticket.get_individual_table_rows(0).text.split(" ")[0]
        page_grievance_new_ticket.get_individual_table_rows(0).click()
        page_grievance_new_ticket.get_button_next().click()
        page_grievance_new_ticket.get_input_questionnaire_size().click()
        assert "3" in page_grievance_new_ticket.get_label_household_size().text
        page_grievance_new_ticket.get_input_questionnaire_malechildrencount().click()
        assert "-" in page_grievance_new_ticket.get_label_number_of_male_children().text
        page_grievance_new_ticket.get_input_questionnaire_femalechildrencount().click()
        assert "-" in page_grievance_new_ticket.get_label_number_of_female_children().text
        page_grievance_new_ticket.get_input_questionnaire_childrendisabledcount().click()
        assert "-" in page_grievance_new_ticket.get_label_number_of_disabled_children().text
        page_grievance_new_ticket.get_input_questionnaire_headofhousehold().click()
        individual = Individual.objects.get(unicef_id=individual_unicef_id)
        household = individual.household
        assert individual.full_name in page_grievance_new_ticket.get_label_head_of_household().text
        page_grievance_new_ticket.get_input_questionnaire_countryorigin().click()
        assert str(household.country_origin) in page_grievance_new_ticket.get_label_country_of_origin().text
        page_grievance_new_ticket.get_input_questionnaire_address().click()
        assert household.address.replace("\n", " ") in page_grievance_new_ticket.get_label_address().text
        page_grievance_new_ticket.get_input_questionnaire_village().click()
        assert household.village in page_grievance_new_ticket.get_label_village().text
        page_grievance_new_ticket.get_input_questionnaire_admin_1().click()
        assert "-" in page_grievance_new_ticket.get_label_administrative_level_1().text
        page_grievance_new_ticket.get_input_questionnaire_admin_2().click()
        assert "-" in page_grievance_new_ticket.get_label_administrative_level_2().text
        page_grievance_new_ticket.get_input_questionnaire_admin_3().click()
        assert "-" in page_grievance_new_ticket.get_label_administrative_level_3().text
        page_grievance_new_ticket.get_input_questionnaire_admin_4().click()
        assert "-" in page_grievance_new_ticket.get_label_administrative_level_4().text
        page_grievance_new_ticket.get_input_questionnaire_months_displaced_h_f().click()
        assert "-" in page_grievance_new_ticket.get_label_length_of_time_since_arrival().text
        page_grievance_new_ticket.get_input_questionnaire_fullname().click()
        assert individual.full_name in page_grievance_new_ticket.get_label_individual_full_name().text
        page_grievance_new_ticket.get_input_questionnaire_birthdate().click()
        assert "-" in page_grievance_new_ticket.get_label_birth_date().text
        page_grievance_new_ticket.get_input_questionnaire_sex().click()
        assert individual.sex in page_grievance_new_ticket.get_label_gender().text
        page_grievance_new_ticket.get_input_questionnaire_phoneno().click()
        assert "-" in page_grievance_new_ticket.get_label_phone_number().text
        page_grievance_new_ticket.get_input_questionnaire_relationship().click()
        assert "HEAD" in page_grievance_new_ticket.get_label_relationship_to_hoh().text
        page_grievance_new_ticket.get_received_consent().click()
        page_grievance_new_ticket.get_button_next().click()

    def test_grievance_tickets_edit_tickets_from_main_grievance_page(
        self,
        page_grievance_tickets: GrievanceTickets,
        page_households: Households,
        create_four_grievance_tickets: [GrievanceTicket],
    ) -> None:
        page_grievance_tickets.get_nav_grievance().click()
        assert "Grievance Tickets" in page_grievance_tickets.get_grievance_title().text
        page_grievance_tickets.get_select_all().click()
        page_grievance_tickets.get_button_assign().click()
        page_grievance_tickets.get_dropdown().click()
        page_grievance_tickets.select_listbox_element("test@example.com")
        for str_row in page_grievance_tickets.get_rows():
            list_row = str_row.text.replace("\n", " ").split(" ")
            assert list_row[0] in page_grievance_tickets.get_selected_tickets().text
        page_grievance_tickets.get_button_save().click()
        page_grievance_tickets.get_status_container()
        page_grievance_tickets.check_if_text_exist_in_a_row(0, "Assigned")

        for str_row in page_grievance_tickets.get_rows():
            list_row = str_row.text.replace("\n", " ").split(" ")
            assert list_row[1] in "Assigned"

        page_grievance_tickets.get_select_all().click()
        page_grievance_tickets.get_button_set_priority().click()
        page_grievance_tickets.get_dropdown().click()
        page_grievance_tickets.select_listbox_element("Medium")
        page_grievance_tickets.get_button_save().click()
        page_grievance_tickets.get_status_container()

        page_grievance_tickets.check_if_text_exist_in_a_row(0, "Medium")
        for str_row in page_grievance_tickets.get_rows():
            assert "Medium" in str_row.text.replace("\n", " ").split(" ")
        page_grievance_tickets.get_select_all().click()
        page_grievance_tickets.get_button_set_urgency().click()
        page_grievance_tickets.get_dropdown().click()
        page_grievance_tickets.select_listbox_element("Urgent")
        page_grievance_tickets.get_button_save().click()
        page_grievance_tickets.get_status_container()

        page_grievance_tickets.check_if_text_exist_in_a_row(0, "Urgent")
        for str_row in page_grievance_tickets.get_rows():
            assert "Urgent" in str_row.text.replace("\n", " ").split(" ")

    @pytest.mark.xfail(reason="UNSTABLE")
    def test_grievance_tickets_process_tickets(
        self,
        page_grievance_tickets: GrievanceTickets,
        page_grievance_new_ticket: NewTicket,
        page_grievance_details_page: GrievanceDetailsPage,
        household_without_disabilities: Household,
        page_households_details: HouseholdsDetails,
        page_households: Households,
    ) -> None:
        page_grievance_tickets.get_nav_grievance().click()
        assert "Grievance Tickets" in page_grievance_tickets.get_grievance_title().text
        page_grievance_tickets.get_button_new_ticket().click()
        page_grievance_new_ticket.get_select_category().click()
        page_grievance_new_ticket.select_option_by_name("Data Change")
        page_grievance_new_ticket.get_issue_type().click()
        page_grievance_new_ticket.select_listbox_element("Household Data Update")
        assert "Data Change" in page_grievance_new_ticket.get_select_category().text
        assert "Items Group Data Update" in page_grievance_new_ticket.get_issue_type().text
        page_grievance_new_ticket.get_button_next().click()
        page_grievance_new_ticket.get_household_tab()
        page_grievance_new_ticket.get_household_table_rows(0).click()
        page_grievance_new_ticket.get_button_next().click()
        page_grievance_new_ticket.get_received_consent().click()
        page_grievance_new_ticket.get_button_next().click()

        page_grievance_new_ticket.get_description().send_keys("Add Individual - TEST")
        page_grievance_new_ticket.get_button_add_new_field()
        page_grievance_new_ticket.get_select_field_name().click()
        page_grievance_new_ticket.select_option_by_name("Males Age 0 - 5")
        page_grievance_new_ticket.get_input_value().send_keys("5")
        page_grievance_new_ticket.get_button_next().click()
        page_grievance_details_page.get_checkbox_household_data()
        page_grievance_details_page.get_button_assign_to_me().click()
        page_grievance_details_page.get_button_set_in_progress().click()
        page_grievance_details_page.get_button_send_for_approval().click()
        page_grievance_details_page.get_checkbox_household_data().click()
        page_grievance_details_page.get_button_approval().click()
        page_grievance_details_page.get_button_close_ticket().click()
        page_grievance_details_page.get_button_confirm().click()
        assert "Ticket ID" in page_grievance_details_page.get_title().text
        page_grievance_new_ticket.select_global_program_filter("Test Program")
        page_grievance_new_ticket.get_nav_programme_population().click()
        page_households.get_households_rows()[0].click()
        assert "5" in page_households_details.get_row05().text

    @pytest.mark.xfail(reason="UNSTABLE")
    def test_grievance_tickets_add_note(
        self,
        page_grievance_tickets: GrievanceTickets,
        page_grievance_new_ticket: NewTicket,
        page_grievance_details_page: GrievanceDetailsPage,
        household_without_disabilities: Household,
        add_grievance_tickets: GrievanceTicket,
    ) -> None:
        page_grievance_tickets.get_nav_grievance().click()
        assert "Grievance Tickets" in page_grievance_tickets.get_grievance_title().text
        page_grievance_tickets.get_ticket_list_row()[0].click()
        page_grievance_details_page.get_input_newnote().send_keys("Test adding new note.")
        page_grievance_details_page.get_button_new_note().click()
        user = page_grievance_details_page.get_note_name().text
        assert len(page_grievance_details_page.get_note_rows()) == 1
        assert user in page_grievance_details_page.get_note_rows()[0].text
        assert datetime.now().strftime("%-d %b %Y") in page_grievance_details_page.get_note_rows()[0].text
        assert "Test adding new note." in page_grievance_details_page.get_note_rows()[0].text

    @pytest.mark.xfail(reason="UNSTABLE")
    def test_grievance_tickets_activity_log(
        self,
        page_grievance_tickets: GrievanceTickets,
        page_grievance_details_page: GrievanceDetailsPage,
        household_without_disabilities: Household,
        add_grievance_tickets: GrievanceTicket,
    ) -> None:
        page_grievance_tickets.get_nav_grievance().click()
        assert "Grievance Tickets" in page_grievance_tickets.get_grievance_title().text
        page_grievance_tickets.get_ticket_list_row()[0].click()
        page_grievance_details_page.get_button_assign_to_me().click()
        page_grievance_details_page.get_button_set_in_progress().click()
        page_grievance_details_page.driver.refresh()
        page_grievance_details_page.get_expand_collapse_button().click()
        assert "Assigned" in page_grievance_details_page.get_log_row()[0].text
        assert "In Progress" in page_grievance_details_page.get_log_row()[0].text

    def test_grievance_tickets_go_to_admin_panel_button(
        self,
        page_grievance_tickets: GrievanceTickets,
        page_grievance_new_ticket: NewTicket,
        page_grievance_details_page: GrievanceDetailsPage,
        household_without_disabilities: Household,
        add_grievance_tickets: GrievanceTicket,
        page_admin_panel: AdminPanel,
    ) -> None:
        page_grievance_tickets.get_nav_grievance().click()
        assert "Grievance Tickets" in page_grievance_tickets.get_grievance_title().text
        page_grievance_tickets.get_ticket_list_row()[0].click()
        page_grievance_details_page.get_button_admin().click()
        assert "grievance_ticket_1" in page_admin_panel.get_unicef_id().text
        assert GrievanceTicket.objects.first().unicef_id in page_admin_panel.get_unicef_id().text

    @pytest.mark.xfail(reason="UNSTABLE")
    def test_grievance_tickets_needs_adjudication(
        self,
        add_grievance_needs_adjudication: None,
        page_grievance_tickets: GrievanceTickets,
        page_grievance_details_page: GrievanceDetailsPage,
        page_individuals: Individuals,
    ) -> None:
        page_grievance_tickets.get_nav_grievance().click()
        assert "Grievance Tickets" in page_grievance_tickets.get_grievance_title().text
        page_grievance_tickets.get_tab_system_generated().click()
        page_grievance_tickets.get_ticket_list_row()[0].click()
        page_grievance_details_page.get_select_all_checkbox().click()
        page_grievance_details_page.get_person_icon()
        assert "person-icon" in [
            ii.get_attribute("data-cy")
            for ii in page_grievance_details_page.get_possible_duplicate_row_by_unicef_id(
                "IND-00-0000.0011"
            ).find_elements(By.TAG_NAME, "svg")
        ]
        assert "people-icon" not in [
            ii.get_attribute("data-cy")
            for ii in page_grievance_details_page.get_possible_duplicate_row_by_unicef_id(
                "IND-00-0000.0022"
            ).find_elements(By.TAG_NAME, "svg")
        ]
        assert "person-icon" not in [
            ii.get_attribute("data-cy")
            for ii in page_grievance_details_page.get_possible_duplicate_row_by_unicef_id(
                "IND-00-0000.0022"
            ).find_elements(By.TAG_NAME, "svg")
        ]
        assert "people-icon" not in [
            ii.get_attribute("data-cy")
            for ii in page_grievance_details_page.get_possible_duplicate_row_by_unicef_id(
                "IND-00-0000.0033"
            ).find_elements(By.TAG_NAME, "svg")
        ]
        assert "person-icon" not in [
            ii.get_attribute("data-cy")
            for ii in page_grievance_details_page.get_possible_duplicate_row_by_unicef_id(
                "IND-00-0000.0033"
            ).find_elements(By.TAG_NAME, "svg")
        ]
        page_grievance_details_page.get_button_clear().click()
        page_grievance_details_page.get_button_confirm().click()
        page_grievance_details_page.disappear_person_icon()
        page_grievance_details_page.disappear_people_icon()
        try:
            assert "person-icon" not in [
                ii.get_attribute("data-cy")
                for ii in page_grievance_details_page.get_possible_duplicate_row_by_unicef_id(
                    "IND-00-0000.0011"
                ).find_elements(By.TAG_NAME, "svg")
            ]
        except BaseException:
            sleep(4)
            assert "person-icon" not in [
                ii.get_attribute("data-cy")
                for ii in page_grievance_details_page.get_possible_duplicate_row_by_unicef_id(
                    "IND-00-0000.0011"
                ).find_elements(By.TAG_NAME, "svg")
            ]
        assert "person-icon" not in [
            ii.get_attribute("data-cy")
            for ii in page_grievance_details_page.get_possible_duplicate_row_by_unicef_id(
                "IND-00-0000.0011"
            ).find_elements(By.TAG_NAME, "svg")
        ]
        assert "people-icon" not in [
            ii.get_attribute("data-cy")
            for ii in page_grievance_details_page.get_possible_duplicate_row_by_unicef_id(
                "IND-00-0000.0022"
            ).find_elements(By.TAG_NAME, "svg")
        ]
        assert "person-icon" not in [
            ii.get_attribute("data-cy")
            for ii in page_grievance_details_page.get_possible_duplicate_row_by_unicef_id(
                "IND-00-0000.0022"
            ).find_elements(By.TAG_NAME, "svg")
        ]
        assert "people-icon" not in [
            ii.get_attribute("data-cy")
            for ii in page_grievance_details_page.get_possible_duplicate_row_by_unicef_id(
                "IND-00-0000.0033"
            ).find_elements(By.TAG_NAME, "svg")
        ]
        assert "person-icon" not in [
            ii.get_attribute("data-cy")
            for ii in page_grievance_details_page.get_possible_duplicate_row_by_unicef_id(
                "IND-00-0000.0033"
            ).find_elements(By.TAG_NAME, "svg")
        ]
        page_grievance_details_page.get_possible_duplicate_row_by_unicef_id("IND-00-0000.0033").find_element(
            By.CSS_SELECTOR, 'input[type="checkbox"]'
        ).click()
        page_grievance_details_page.get_button_mark_distinct().click()
        page_grievance_details_page.get_button_confirm().click()
        page_grievance_details_page.get_person_icon()
        page_grievance_details_page.get_possible_duplicate_row_by_unicef_id("IND-00-0000.0011").find_element(
            By.CSS_SELECTOR, 'input[type="checkbox"]'
        ).click()
        page_grievance_details_page.get_possible_duplicate_row_by_unicef_id("IND-00-0000.0022").find_element(
            By.CSS_SELECTOR, 'input[type="checkbox"]'
        ).click()
        page_grievance_details_page.get_button_mark_duplicate().click()
        page_grievance_details_page.get_people_icon()
        assert "people-icon" in [
            ii.get_attribute("data-cy")
            for ii in page_grievance_details_page.get_possible_duplicate_row_by_unicef_id(
                "IND-00-0000.0011"
            ).find_elements(By.TAG_NAME, "svg")
        ]
        assert "person-icon" in [
            ii.get_attribute("data-cy")
            for ii in page_grievance_details_page.get_possible_duplicate_row_by_unicef_id(
                "IND-00-0000.0033"
            ).find_elements(By.TAG_NAME, "svg")
        ]
        assert "people-icon" in [
            ii.get_attribute("data-cy")
            for ii in page_grievance_details_page.get_possible_duplicate_row_by_unicef_id(
                "IND-00-0000.0022"
            ).find_elements(By.TAG_NAME, "svg")
        ]
        duplicated_individual_unicef_id = "IND-00-0000.0022"
        page_grievance_details_page.get_button_close_ticket().click()
        page_grievance_details_page.get_button_confirm().click()
        page_grievance_details_page.disappear_button_confirm()
        page_grievance_details_page.disappear_button_close_ticket()

        page_grievance_details_page.select_global_program_filter("Test Program")
        page_grievance_details_page.get_nav_programme_population().click()
        page_individuals.get_nav_individuals().click()
        page_individuals.get_individual_table_row()
        assert len(page_individuals.get_individual_table_row()) == 3
        for icon in page_individuals.get_individual_table_row()[0].find_elements(By.TAG_NAME, "svg"):
            assert "Confirmed Duplicate" in icon.get_attribute("aria-label")
            break
        else:
            raise AssertionError(f"Icon for {page_individuals.get_individual_table_row()[0].text} does not appear")
        for individual_row in page_individuals.get_individual_table_row():
            if duplicated_individual_unicef_id in individual_row.text:
                for icon in individual_row.find_elements(By.TAG_NAME, "svg"):
                    assert "Confirmed Duplicate" in icon.get_attribute("aria-label")

    @pytest.mark.xfail(reason="Unskip after fix bug: 209087")
    def test_grievance_tickets_create_new_error(
        self,
        page_grievance_tickets: GrievanceTickets,
        page_grievance_new_ticket: NewTicket,
        page_grievance_details_page: GrievanceDetailsPage,
    ) -> None:
        page_grievance_tickets.get_nav_grievance().click()
        assert "Grievance Tickets" in page_grievance_tickets.get_grievance_title().text
        page_grievance_tickets.get_button_new_ticket().click()
        page_grievance_new_ticket.get_button_next().click()
        with pytest.raises(NoSuchElementException):
            page_grievance_new_ticket.get_household_tab()
