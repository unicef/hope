from datetime import datetime
import random
from time import sleep

from dateutil.relativedelta import relativedelta
import pytest
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By

from e2e.helpers.date_time_format import FormatTime
from e2e.page_object.programme_details.programme_details import ProgrammeDetails
from e2e.page_object.programme_management.programme_management import (
    ProgrammeManagement,
)
from extras.test_utils.factories.account import (
    PartnerFactory,
    RoleAssignmentFactory,
    RoleFactory,
)
from extras.test_utils.factories.core import DataCollectingTypeFactory
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from hope.models.beneficiary_group import BeneficiaryGroup
from hope.models.business_area import BusinessArea
from hope.models.data_collecting_type import DataCollectingType
from hope.models.partner import Partner
from hope.models.program import Program

pytestmark = pytest.mark.django_db()


@pytest.fixture
def create_programs() -> None:
    create_program("Test Programm")


@pytest.fixture(autouse=True)
def create_unhcr_partner() -> None:
    """
    This factory is needed due to the temporary solution applied on program mutation -
    partner needs to already hold any role in the business area to get this role for the new program.
    This can be reverted after changing the temporary solution to receive role in the mutation input.
    """
    partner_unhcr = PartnerFactory(name="UNHCR")
    afghanistan = BusinessArea.objects.get(slug="afghanistan")
    partner_unhcr.role_assignments.all().delete()
    partner_unhcr.allowed_business_areas.add(afghanistan)
    # TODO: below line can be removed after temporary solution is removed for partners.
    # Only being allowed in BA is enough.
    RoleAssignmentFactory(
        partner=partner_unhcr,
        business_area=afghanistan,
        role=RoleFactory(name="Role for UNHCR"),
        program=None,
    )


def create_program(
    name: str,
    dct_type: str = DataCollectingType.Type.STANDARD,
    status: str = Program.ACTIVE,
) -> Program:
    dct = DataCollectingTypeFactory(type=dct_type)
    beneficiary_group = BeneficiaryGroup.objects.filter(name="Main Menu").first()
    program = ProgramFactory(
        name=name,
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
        data_collecting_type=dct,
        status=status,
        budget=100,
        beneficiary_group=beneficiary_group,
    )
    program.refresh_from_db()
    return program


@pytest.mark.usefixtures("login")
class TestProgrammeManagement:
    @pytest.mark.parametrize(
        "test_data",
        [
            pytest.param(
                {
                    "program_name": "New Programme - " + str(random.random()),
                    "selector": "Child Protection",
                    "startDate": FormatTime(1, 5, 2023),
                    "endDate": FormatTime(12, 12, 2033),
                    "dataCollectingType": "Full",
                },
                id="Child Protection & Full",
            ),
            pytest.param(
                {
                    "program_name": "New Programme - " + str(random.random()),
                    "selector": "Education",
                    "startDate": FormatTime(11, 12, 2002),
                    "endDate": FormatTime(1, 8, 2043),
                    "dataCollectingType": "Size only",
                },
                id="Education & Size only",
            ),
        ],
    )
    def test_create_programme(
        self,
        page_programme_management: ProgrammeManagement,
        page_programme_details: ProgrammeDetails,
        test_data: dict,
    ) -> None:
        # Go to Programme Management
        page_programme_management.get_nav_programme_management().click()
        # Create Programme
        # 1st step (Details)
        page_programme_management.get_button_new_program().click()
        page_programme_management.get_input_programme_name().send_keys(test_data["program_name"])
        page_programme_management.get_input_start_date().click()
        page_programme_management.get_input_start_date().send_keys(test_data["startDate"].numerically_formatted_date)
        page_programme_management.get_input_end_date().click()
        page_programme_management.get_input_end_date().send_keys(test_data["endDate"].numerically_formatted_date)
        page_programme_management.choose_option_selector(test_data["selector"])
        page_programme_management.choose_option_data_collecting_type(test_data["dataCollectingType"])
        page_programme_management.get_input_beneficiary_group().click()
        page_programme_management.select_listbox_element("Main Menu")
        page_programme_management.get_button_next().click()
        # 2nd step (Time Series Fields)
        page_programme_management.get_button_add_time_series_field().click()
        page_programme_management.get_input_pdu_fields_object_label(0).send_keys("test series field name")
        page_programme_management.get_select_pdu_fields_object_pdu_data_subtype(0).click()
        page_programme_management.select_listbox_element("Text")
        page_programme_management.get_select_pdu_fields_object_pdu_data_number_of_rounds(0).click()
        page_programme_management.select_listbox_element("1")
        page_programme_management.get_input_pdu_fields_rounds_names(0, 0).send_keys("Round 1")
        page_programme_management.get_button_next().click()
        # 3rd step (Partners)
        page_programme_management.get_button_save().click()
        # Check Details page
        page_programme_management.screenshot("test_create_programme", file_path="./")
        page_programme_details.wait_for_text("New Programme", page_programme_details.header_title)
        assert "DRAFT" in page_programme_details.get_program_status().text
        assert test_data["startDate"].date_in_text_format in page_programme_details.get_label_start_date().text
        assert test_data["endDate"].date_in_text_format in page_programme_details.get_label_end_date().text
        assert test_data["selector"] in page_programme_details.get_label_selector().text
        assert test_data["dataCollectingType"] in page_programme_details.get_label_data_collecting_type().text
        assert "Regular" in page_programme_details.get_label_freq_of_payment().text
        assert "-" in page_programme_details.get_label_administrative_areas().text
        assert "No" in page_programme_details.get_label_cash_plus().text
        assert "0" in page_programme_details.get_label_program_size().text

    @pytest.mark.parametrize(
        "test_data",
        [
            pytest.param(
                {
                    "program_name": "New Programme - " + str(random.random()),
                    "selector": "Health",
                    "startDate": FormatTime(1, 1, 2022),
                    "endDate": FormatTime(1, 2, 2035),
                    "dataCollectingType": "Partial",
                    "description": f"Text with random {str(random.random())} text",
                    "budget": 1000.99,
                    "administrativeAreas": "Test pass",
                    "populationGoals": "100",
                },
                id="All",
            ),
        ],
    )
    def test_create_programme_optional_values(
        self,
        page_programme_management: ProgrammeManagement,
        page_programme_details: ProgrammeDetails,
        test_data: dict,
    ) -> None:
        # Go to Programme Management
        page_programme_management.get_nav_programme_management().click()
        # Create Programme
        page_programme_management.get_button_new_program().click()
        # 1st step (Details)
        page_programme_management.get_input_programme_name().send_keys(test_data["program_name"])
        page_programme_management.get_input_start_date().click()
        page_programme_management.get_input_start_date().send_keys(test_data["startDate"].numerically_formatted_date)
        page_programme_management.get_input_end_date().click()
        page_programme_management.get_input_end_date().send_keys(test_data["endDate"].numerically_formatted_date)
        page_programme_management.choose_option_selector(test_data["selector"])
        page_programme_management.choose_option_data_collecting_type(test_data["dataCollectingType"])
        page_programme_management.get_input_freq_of_payment_one_off().click()
        page_programme_management.get_input_cash_plus().click()
        page_programme_management.get_input_description().send_keys(test_data["description"])
        page_programme_management.get_input_budget().clear()
        page_programme_management.get_input_budget().send_keys(test_data["budget"])
        page_programme_management.get_input_administrative_areas_of_implementation().send_keys(
            test_data["administrativeAreas"]
        )
        page_programme_management.get_input_population().clear()
        page_programme_management.get_input_population().send_keys(test_data["populationGoals"])
        page_programme_management.get_input_beneficiary_group().click()
        page_programme_management.select_listbox_element("People")
        page_programme_management.get_button_next().click()
        # 2nd step (Time Series Fields)
        page_programme_management.get_button_add_time_series_field()
        page_programme_management.get_button_next().click()
        # 3rd step (Partners)
        page_programme_management.get_button_save().click()
        # Check Details page
        page_programme_details.wait_for_text("New Programme", page_programme_details.header_title)
        page_programme_details.screenshot("0", file_path="./")
        assert "DRAFT" in page_programme_details.get_program_status().text
        assert test_data["startDate"].date_in_text_format in page_programme_details.get_label_start_date().text
        assert test_data["endDate"].date_in_text_format in page_programme_details.get_label_end_date().text
        assert test_data["selector"] in page_programme_details.get_label_selector().text
        assert test_data["dataCollectingType"] in page_programme_details.get_label_data_collecting_type().text
        assert "One-off" in page_programme_details.get_label_freq_of_payment().text
        assert test_data["administrativeAreas"] in page_programme_details.get_label_administrative_areas().text
        assert "Yes" in page_programme_details.get_label_cash_plus().text
        assert "0" in page_programme_details.get_label_program_size().text

    @pytest.mark.parametrize(
        "test_data",
        [
            pytest.param(
                {
                    "program_name": "New Programme - " + str(random.random()),
                    "selector": "Health",
                    "startDate": FormatTime(1, 1, 2022),
                    "endDate": FormatTime(1, 2, 2042),
                    "dataCollectingType": "Partial",
                },
                id="One-off",
            ),
        ],
    )
    def test_create_programme_frequency_of_payment(
        self,
        page_programme_management: ProgrammeManagement,
        page_programme_details: ProgrammeDetails,
        test_data: dict,
    ) -> None:
        # Go to Programme Management
        page_programme_management.get_nav_programme_management().click()
        # Create Programme
        page_programme_management.get_button_new_program().click()
        # 1st step (Details)
        page_programme_management.get_input_programme_name().send_keys("New Programme")
        page_programme_management.get_input_start_date().click()
        page_programme_management.get_input_start_date().send_keys(test_data["startDate"].numerically_formatted_date)
        page_programme_management.get_input_end_date().click()
        page_programme_management.get_input_end_date().send_keys(test_data["endDate"].numerically_formatted_date)
        page_programme_management.choose_option_selector(test_data["selector"])
        page_programme_management.choose_option_data_collecting_type(test_data["dataCollectingType"])
        page_programme_management.get_input_freq_of_payment_one_off().click()
        page_programme_management.get_input_beneficiary_group().click()
        page_programme_management.select_listbox_element("People")
        page_programme_management.get_button_next().click()
        # 2nd step (Time Series Fields)
        page_programme_management.get_button_add_time_series_field()
        page_programme_management.get_button_next().click()
        # 3rd step (Partners)
        page_programme_management.get_button_save().click()
        # Check Details page
        page_programme_details.wait_for_text("New Programme", page_programme_details.header_title)
        page_programme_details.wait_for_text("DRAFT", page_programme_details.program_status)
        assert test_data["startDate"].date_in_text_format in page_programme_details.get_label_start_date().text
        assert test_data["endDate"].date_in_text_format in page_programme_details.get_label_end_date().text
        assert test_data["selector"] in page_programme_details.get_label_selector().text
        assert test_data["dataCollectingType"] in page_programme_details.get_label_data_collecting_type().text
        assert "One-off" in page_programme_details.get_label_freq_of_payment().text
        assert "-" in page_programme_details.get_label_administrative_areas().text
        assert "No" in page_programme_details.get_label_cash_plus().text
        assert "0" in page_programme_details.get_label_program_size().text

    @pytest.mark.night
    @pytest.mark.parametrize(
        "test_data",
        [
            pytest.param(
                {
                    "program_name": "New Programme - " + str(random.random()),
                    "selector": "Health",
                    "startDate": FormatTime(1, 1, 2022),
                    "endDate": FormatTime(1, 2, 2032),
                    "dataCollectingType": "Partial",
                },
                id="Yes",
            ),
        ],
    )
    def test_create_programme_cash_plus(
        self,
        page_programme_management: ProgrammeManagement,
        page_programme_details: ProgrammeDetails,
        test_data: dict,
    ) -> None:
        # Go to Programme Management
        page_programme_management.get_nav_programme_management().click()
        # Create Programme
        page_programme_management.get_button_new_program().click()
        # 1st step (Details)
        page_programme_management.get_input_programme_name().send_keys(test_data["program_name"])
        page_programme_management.get_input_start_date().click()
        page_programme_management.get_input_start_date().send_keys(test_data["startDate"].numerically_formatted_date)
        page_programme_management.get_input_end_date().click()
        page_programme_management.get_input_end_date().send_keys(test_data["endDate"].numerically_formatted_date)
        page_programme_management.choose_option_selector(test_data["selector"])
        page_programme_management.choose_option_data_collecting_type(test_data["dataCollectingType"])
        page_programme_management.get_input_cash_plus().click()
        page_programme_management.get_input_beneficiary_group().click()
        page_programme_management.select_listbox_element("People")
        page_programme_management.get_button_next().click()
        # 2nd step (Time Series Fields)
        page_programme_management.get_button_add_time_series_field()
        page_programme_management.get_button_next().click()
        # 3rd step (Partners)
        page_programme_management.get_button_save().click()
        # Check Details page
        page_programme_details.wait_for_text("New Programme", page_programme_details.header_title)
        assert "DRAFT" in page_programme_details.get_program_status().text
        assert test_data["startDate"].date_in_text_format in page_programme_details.get_label_start_date().text
        assert test_data["endDate"].date_in_text_format in page_programme_details.get_label_end_date().text
        assert test_data["selector"] in page_programme_details.get_label_selector().text
        assert test_data["dataCollectingType"] in page_programme_details.get_label_data_collecting_type().text
        assert "Regular" in page_programme_details.get_label_freq_of_payment().text
        assert "-" in page_programme_details.get_label_administrative_areas().text
        assert "Yes" in page_programme_details.get_label_cash_plus().text
        assert "0" in page_programme_details.get_label_program_size().text

    @pytest.mark.night
    @pytest.mark.parametrize(
        "test_data",
        [
            pytest.param(
                {
                    "program_name": "CheckProgramme - " + str(random.random()),
                    "selector": "Health",
                    "startDate": FormatTime(1, 1, 2022),
                    "endDate": FormatTime(1, 2, 2032),
                    "dataCollectingType": "Partial",
                },
                id="programme_management_page",
            ),
        ],
    )
    def test_create_programme_check(
        self,
        page_programme_management: ProgrammeManagement,
        page_programme_details: ProgrammeDetails,
        test_data: dict,
    ) -> None:
        # Go to Programme Management
        page_programme_management.get_nav_programme_management().click()
        # Create Programme
        page_programme_management.get_button_new_program().click()
        # 1st step (Details)
        page_programme_management.get_input_programme_name().send_keys(test_data["program_name"])
        page_programme_management.get_input_start_date().click()
        page_programme_management.get_input_start_date().send_keys(test_data["startDate"].numerically_formatted_date)
        page_programme_management.get_input_end_date().click()
        page_programme_management.get_input_end_date().send_keys(test_data["endDate"].numerically_formatted_date)
        page_programme_management.choose_option_selector(test_data["selector"])
        page_programme_management.choose_option_data_collecting_type(test_data["dataCollectingType"])
        page_programme_management.get_input_cash_plus().click()
        page_programme_management.get_input_beneficiary_group().click()
        page_programme_management.select_listbox_element("People")
        page_programme_management.get_button_next().click()
        # 2nd step (Time Series Fields)
        page_programme_management.get_button_add_time_series_field()
        page_programme_management.get_button_next().click()
        # 3rd step (Partners)
        page_programme_management.get_button_save().click()
        # Check Details page
        page_programme_details.wait_for_text("DRAFT", page_programme_details.program_status)
        assert test_data["startDate"].date_in_text_format in page_programme_details.get_label_start_date().text
        assert test_data["endDate"].date_in_text_format in page_programme_details.get_label_end_date().text
        assert test_data["selector"] in page_programme_details.get_label_selector().text
        assert test_data["dataCollectingType"] in page_programme_details.get_label_data_collecting_type().text
        assert "Regular" in page_programme_details.get_label_freq_of_payment().text
        assert "-" in page_programme_details.get_label_administrative_areas().text
        assert "Yes" in page_programme_details.get_label_cash_plus().text
        assert "0" in page_programme_details.get_label_program_size().text
        # Check Programme Management Page
        page_programme_management.get_nav_programme_management().click()
        page_programme_management.fill_filters_search(test_data["program_name"])
        elements = page_programme_management.get_row_by_program_name(test_data["program_name"])
        assert "DRAFT" in elements[1]
        assert "Health" in elements[2]

    def test_create_programme_check_empty_mandatory_fields(
        self, page_programme_management: ProgrammeManagement
    ) -> None:
        # Go to Programme Management
        page_programme_management.get_nav_programme_management().click()
        # Create Programme
        page_programme_management.get_button_new_program().click()
        page_programme_management.get_button_next().click()
        # Cehck Mandatory fields texts
        assert "Programme Name is required" in page_programme_management.get_label_programme_name().text.split("\n")
        assert "Start Date is required" in page_programme_management.get_label_start_date().text
        assert "Sector is required" in page_programme_management.get_label_selector().text
        assert "Data Collecting Type is required" in page_programme_management.get_label_data_collecting_type().text

    @pytest.mark.parametrize(
        "test_data",
        [
            pytest.param(
                {
                    "program_name": "CheckParents - " + str(random.random()),
                    "selector": "Health",
                    "startDate": FormatTime(1, 1, 2022),
                    "endDate": FormatTime(1, 2, 2032),
                    "dataCollectingType": "Partial",
                },
                id="programme_management_page",
            ),
        ],
    )
    def test_create_programme_delete_partners(
        self,
        page_programme_management: ProgrammeManagement,
        page_programme_details: ProgrammeDetails,
        test_data: dict,
    ) -> None:
        # Go to Programme Management
        page_programme_management.get_nav_programme_management().click()
        # Create Programme
        page_programme_management.get_button_new_program().click()
        # 1st step (Details)
        page_programme_management.get_input_programme_name().send_keys(test_data["program_name"])
        page_programme_management.get_input_start_date().click()
        page_programme_management.get_input_start_date().send_keys(test_data["startDate"].numerically_formatted_date)
        page_programme_management.get_input_end_date().click()
        page_programme_management.get_input_end_date().send_keys(test_data["endDate"].numerically_formatted_date)
        page_programme_management.choose_option_selector(test_data["selector"])
        page_programme_management.choose_option_data_collecting_type(test_data["dataCollectingType"])
        page_programme_management.get_input_cash_plus().click()
        page_programme_management.get_input_beneficiary_group().click()
        page_programme_management.select_listbox_element("People")
        page_programme_management.get_button_next().click()
        # 2nd step (Time Series Fields)
        page_programme_management.get_button_add_time_series_field()
        page_programme_management.get_button_next().click()
        # 3rd step (Partners)
        page_programme_management.get_access_to_program().click()
        page_programme_management.select_who_access_to_program("Only Selected Partners within the business area")
        page_programme_management.choose_partner_option("UNHCR")
        page_programme_management.get_button_add_partner().click()
        page_programme_management.get_button_delete().click()
        page_programme_management.get_button_delete_popup().click()
        page_programme_management.get_button_save().click()
        # Check Details page
        with pytest.raises(NoSuchElementException):
            assert "UNHCR" in page_programme_details.get_label_partner_name().text

    def test_create_programme_cancel_scenario(
        self,
        page_programme_management: ProgrammeManagement,
        page_programme_details: ProgrammeDetails,
    ) -> None:
        # Go to Programme Management
        page_programme_management.get_nav_programme_management().click()
        # Create Programme
        page_programme_management.get_button_new_program().click()
        page_programme_management.get_button_cancel().click()
        assert "Programme Management" in page_programme_management.get_header_title().text


# ToDo: Check Unicef partner! and delete classes
@pytest.mark.night
@pytest.mark.usefixtures("login")
class TestBusinessAreas:
    @pytest.mark.parametrize(
        "test_data",
        [
            pytest.param(
                {
                    "program_name": "CheckParents - " + str(random.random()),
                    "selector": "Health",
                    "startDate": FormatTime(1, 1, 2022),
                    "endDate": FormatTime(1, 2, 2032),
                    "dataCollectingType": "Partial",
                },
                id="programme_management_page",
            ),
        ],
    )
    def test_create_programme_add_partners_business_area(
        self,
        change_super_user: None,
        page_programme_management: ProgrammeManagement,
        page_programme_details: ProgrammeDetails,
        test_data: dict,
    ) -> None:
        # Go to Programme Management
        page_programme_management.get_nav_programme_management().click()
        # Create Programme
        page_programme_management.get_button_new_program().click()
        # 1st step (Details)
        page_programme_management.get_input_programme_name().send_keys(test_data["program_name"])
        page_programme_management.get_input_start_date().click()
        page_programme_management.get_input_start_date().send_keys(test_data["startDate"].numerically_formatted_date)
        page_programme_management.get_input_end_date().click()
        page_programme_management.get_input_end_date().send_keys(test_data["endDate"].numerically_formatted_date)
        page_programme_management.choose_option_selector(test_data["selector"])
        page_programme_management.choose_option_data_collecting_type(test_data["dataCollectingType"])
        page_programme_management.get_input_cash_plus().click()
        page_programme_management.get_input_beneficiary_group().click()
        page_programme_management.select_listbox_element("People")
        page_programme_management.get_button_next().click()
        # 2nd step (Time Series Fields)
        page_programme_management.get_button_add_time_series_field()
        page_programme_management.get_button_next().click()
        # 3rd step (Partners)
        page_programme_management.get_access_to_program().click()
        page_programme_management.select_who_access_to_program("Only Selected Partners within the business area")

        page_programme_management.choose_partner_option("UNHCR")
        page_programme_management.get_label_admin_area().click()
        page_programme_management.choose_area_admin1_by_name("Kabul").click()
        # ToDo: Create additional waiting mechanism
        from time import sleep

        sleep(1)
        page_programme_management.get_button_save().click()
        # Check Details page
        page_programme_details.wait_for_text_in_any_element("UNHCR", page_programme_details.label_partner_name)
        page_programme_details.wait_for_text_in_any_element("TEST", page_programme_details.label_partner_name)

        assert "1" in page_programme_details.get_label_admin_area1().text
        assert "15" in page_programme_details.get_label_admin_area2().text


@pytest.mark.night
@pytest.mark.usefixtures("login")
class TestComeBackScenarios:
    @pytest.mark.xfail(reason="UNSTABLE")
    @pytest.mark.parametrize(
        "test_data",
        [
            pytest.param(
                {
                    "program_name": "New Programme - " + str(random.random()),
                    "selector": "Health",
                    "startDate": FormatTime(1, 1, 2022),
                    "endDate": FormatTime(1, 2, 2032),
                    "dataCollectingType": "Partial",
                },
                id="Name Change",
            ),
        ],
    )
    def test_create_programme_back_scenarios(
        self,
        change_super_user: None,
        page_programme_management: ProgrammeManagement,
        page_programme_details: ProgrammeDetails,
        test_data: dict,
    ) -> None:
        # Go to Programme Management
        page_programme_management.get_nav_programme_management().click()
        # Create Programme
        page_programme_management.get_button_new_program().click()
        # 1st step (Details)
        page_programme_management.get_input_programme_name().send_keys("Test Name")
        page_programme_management.get_input_start_date().click()
        page_programme_management.get_input_start_date().send_keys(test_data["startDate"].numerically_formatted_date)
        page_programme_management.get_input_end_date().click()
        page_programme_management.get_input_end_date().send_keys(test_data["endDate"].numerically_formatted_date)
        page_programme_management.choose_option_selector(test_data["selector"])
        page_programme_management.choose_option_data_collecting_type(test_data["dataCollectingType"])
        page_programme_management.get_input_cash_plus().click()
        page_programme_management.get_input_beneficiary_group().click()
        page_programme_management.select_listbox_element("People Menu")
        page_programme_management.get_button_next().click()
        # 2nd step (Time Series Fields)
        page_programme_management.get_button_add_time_series_field()
        page_programme_management.get_button_next().click()
        # 3rd step (Partners)
        page_programme_management.get_access_to_program().click()
        page_programme_management.select_who_access_to_program("Only Selected Partners within the business area")
        page_programme_management.choose_partner_option("UNHCR")
        page_programme_management.get_button_back().click()
        page_programme_management.get_button_back().click()
        assert "Test Name" in page_programme_management.get_input_programme_name().get_attribute("value")
        page_programme_management.clear_input(page_programme_management.get_input_programme_name())
        for _ in range(len(page_programme_management.get_input_programme_name().get_attribute("value"))):
            page_programme_management.get_input_programme_name().send_keys(Keys.BACKSPACE)
        assert "Programme Name is required" in page_programme_management.get_label_programme_name().text.split("\n")
        page_programme_management.get_input_programme_name().send_keys(test_data["program_name"])
        # 2nd step (Time Series Fields)
        page_programme_management.get_button_next().click()
        page_programme_management.get_button_add_time_series_field()
        page_programme_management.get_button_next().click()
        # 3rd step (Partners)
        page_programme_management.get_access_to_program().click()
        ActionChains(page_programme_management.driver).send_keys(Keys.ESCAPE).perform()
        page_programme_management.get_button_save().click()
        # Check Details page
        page_programme_details.wait_for_text("New Programme", page_programme_details.header_title)
        assert "DRAFT" in page_programme_details.get_program_status().text
        assert test_data["startDate"].date_in_text_format in page_programme_details.get_label_start_date().text
        assert test_data["endDate"].date_in_text_format in page_programme_details.get_label_end_date().text
        assert test_data["selector"] in page_programme_details.get_label_selector().text
        assert test_data["dataCollectingType"] in page_programme_details.get_label_data_collecting_type().text
        assert "Regular" in page_programme_details.get_label_freq_of_payment().text
        assert "-" in page_programme_details.get_label_administrative_areas().text
        assert "Yes" in page_programme_details.get_label_cash_plus().text
        assert "0" in page_programme_details.get_label_program_size().text
        assert "UNHCR" in page_programme_details.get_label_partner_name().text


@pytest.mark.night
@pytest.mark.xfail(reason="UNSTABLE")
@pytest.mark.usefixtures("login")
class TestManualCalendar:
    @pytest.mark.parametrize(
        "test_data",
        [
            pytest.param(
                {
                    "program_name": "New Programme - " + str(random.random()),
                    "selector": "Health",
                    "dataCollectingType": "Partial",
                },
                id="Change Date",
            ),
        ],
    )
    @pytest.mark.xfail(reason="UNSTABLE")
    def test_create_programme_chose_dates_via_calendar(
        self,
        page_programme_management: ProgrammeManagement,
        page_programme_details: ProgrammeDetails,
        test_data: dict,
    ) -> None:
        # Go to Programme Management
        page_programme_management.get_nav_programme_management().click()
        # Create Programme
        page_programme_management.get_button_new_program().click()
        page_programme_management.get_input_programme_name().send_keys(test_data["program_name"])
        page_programme_management.choose_input_start_date_via_calendar(15)
        page_programme_management.choose_input_end_date_via_calendar(25)
        page_programme_management.choose_option_selector(test_data["selector"])
        page_programme_management.choose_option_data_collecting_type(test_data["dataCollectingType"])
        page_programme_management.get_input_beneficiary_group().click()
        page_programme_management.select_listbox_element("People Menu")
        page_programme_management.get_button_next().click()
        # 2nd step (Time Series Fields)
        page_programme_management.get_button_add_time_series_field()
        page_programme_management.get_button_next().click()
        # 3rd step (Partners)
        page_programme_management.get_button_save().click()
        # Check Details page
        page_programme_details.wait_for_text("New Programme", page_programme_details.header_title)
        assert str(datetime.now().strftime("15 %b %Y")) in page_programme_details.get_label_start_date().text
        end_date = datetime.now() + relativedelta(months=1)
        assert str(end_date.strftime("25 %b %Y")) in page_programme_details.get_label_end_date().text

    @pytest.mark.parametrize(
        "test_data",
        [
            pytest.param(
                {
                    "program_name": "CheckParents - " + str(random.random()),
                    "selector": "Health",
                    "startDate": FormatTime(1, 1, 2022),
                    "endDate": FormatTime(1, 2, 2032),
                    "dataCollectingType": "Partial",
                    "partners_access": "None of the Partners should have access",
                },
                id="none_of_the_partners_should_have_access",
            ),
            pytest.param(
                {
                    "program_name": "CheckParents - " + str(random.random()),
                    "selector": "Health",
                    "startDate": FormatTime(1, 1, 2022),
                    "endDate": FormatTime(1, 2, 2032),
                    "dataCollectingType": "Partial",
                    "partners_access": "All Current Partners within the business area",
                },
                id="all_partners_within_the_business_area",
            ),
        ],
    )
    def test_create_programme_accesses(
        self,
        page_programme_management: ProgrammeManagement,
        page_programme_details: ProgrammeDetails,
        test_data: dict,
    ) -> None:
        # Go to Programme Management
        page_programme_management.get_nav_programme_management().click()
        # Create Programme
        page_programme_management.get_button_new_program().click()
        # 1st step (Details)
        page_programme_management.get_input_programme_name().send_keys(test_data["program_name"])
        page_programme_management.get_input_start_date().click()
        page_programme_management.get_input_start_date().send_keys(test_data["startDate"].numerically_formatted_date)
        page_programme_management.get_input_end_date().click()
        page_programme_management.get_input_end_date().send_keys(test_data["endDate"].numerically_formatted_date)
        page_programme_management.choose_option_selector(test_data["selector"])
        page_programme_management.choose_option_data_collecting_type(test_data["dataCollectingType"])
        page_programme_management.get_input_cash_plus().click()
        page_programme_management.get_input_beneficiary_group().click()
        page_programme_management.select_listbox_element("People Menu")
        page_programme_management.get_button_next().click()
        # 2nd step (Time Series Fields)
        page_programme_management.get_button_add_time_series_field()
        page_programme_management.get_button_next().click()
        # 3rd step (Partners)
        page_programme_management.get_access_to_program().click()
        page_programme_management.select_who_access_to_program(test_data["partners_access"])
        # ToDo: Workaround: Save button is clickable but Selenium clicking it too fast
        sleep(5)
        page_programme_management.get_button_save().click()
        assert test_data["partners_access"] in page_programme_details.get_label_partner_access().text
        assert test_data["dataCollectingType"] in page_programme_details.get_label_data_collecting_type().text

    @pytest.mark.xfail(reason="UNSTABLE")
    def test_edit_programme(
        self,
        create_programs: None,
        page_programme_management: ProgrammeManagement,
        page_programme_details: ProgrammeDetails,
    ) -> None:
        page_programme_management.click_nav_programme_management()
        page_programme_management.get_table_row_by_program_name("Test Programm").click()

        page_programme_management.get_button_edit_program().click()
        page_programme_management.get_select_edit_program_details().click()

        # 1st step (Details)
        page_programme_management.clear_input(page_programme_management.get_input_programme_name())
        page_programme_management.get_input_programme_name().send_keys("New name after Edit")
        page_programme_management.clear_input(page_programme_management.get_input_programme_code())
        page_programme_management.get_input_programme_code().send_keys("NEW1")
        page_programme_management.clear_input(
            page_programme_management.page_programme_management.get_input_start_date()
        )
        page_programme_management.get_input_start_date().send_keys(
            str(FormatTime(1, 1, 2022).numerically_formatted_date)
        )
        page_programme_management.clear_input(page_programme_management.get_input_end_date())
        page_programme_management.get_input_end_date().send_keys(FormatTime(1, 10, 2099).numerically_formatted_date)
        page_programme_management.get_button_next().click()
        # 2nd step (Time Series Fields)
        page_programme_management.get_button_add_time_series_field()
        page_programme_management.element_clickable(page_programme_management.button_save)
        # ToDo: Workaround: Save button is clickable but Selenium clicking it too fast
        sleep(5)
        page_programme_management.get_button_save().click()
        # Check Details page
        page_programme_details.wait_for_text("New name after Edit", page_programme_details.header_title)
        assert FormatTime(1, 1, 2022).date_in_text_format in page_programme_details.get_label_start_date().text
        assert FormatTime(1, 10, 2099).date_in_text_format in page_programme_details.get_label_end_date().text

    @pytest.mark.xfail(reason="UNSTABLE")
    def test_programme_partners(
        self,
        create_programs: None,
        page_programme_management: ProgrammeManagement,
        page_programme_details: ProgrammeDetails,
    ) -> None:
        partner1 = Partner.objects.create(name="Test Partner 1")
        partner2 = Partner.objects.create(name="Test Partner 2")
        role = RoleFactory(name="Role in BA")
        RoleAssignmentFactory(
            role=role,
            partner=partner1,
            business_area=BusinessArea.objects.get(slug="afghanistan"),
        )
        # Go to Programme Management
        page_programme_management.get_nav_programme_management().click()
        # Create Programme
        page_programme_management.get_button_new_program().click()
        # 1st step (Details)
        page_programme_management.get_input_programme_name().send_keys("Test Program Partners")
        page_programme_management.get_input_start_date().click()
        page_programme_management.get_input_start_date().send_keys(
            str(FormatTime(1, 1, 2022).numerically_formatted_date)
        )
        page_programme_management.get_input_end_date().click()
        page_programme_management.get_input_end_date().send_keys(FormatTime(1, 10, 2099).numerically_formatted_date)
        page_programme_management.choose_option_selector("Health")
        page_programme_management.choose_option_data_collecting_type("Partial")
        page_programme_management.get_input_cash_plus().click()
        page_programme_management.get_input_beneficiary_group().click()
        page_programme_management.select_listbox_element("People Menu")
        page_programme_management.get_button_next().click()
        # 2nd step (Time Series Fields)
        page_programme_management.get_button_add_time_series_field()
        page_programme_management.get_button_next().click()
        # 3rd step (Partners)
        # only partners with role in business area can be selected

        assert partner1 in Partner.objects.filter(business_areas__slug="afghanistan").all()
        assert partner2 not in Partner.objects.filter(business_areas__slug="afghanistan").all()
        assert Partner.objects.get(name="UNHCR") in Partner.objects.filter(business_areas__slug="afghanistan").all()

        partner_access_selected = "Only Selected Partners within the business area"
        page_programme_management.get_access_to_program().click()
        page_programme_management.select_who_access_to_program(partner_access_selected)

        page_programme_management.wait_for(page_programme_management.input_partner).click()
        select_options_container = page_programme_management.get_select_options_container()
        options = select_options_container.find_elements(By.TAG_NAME, "li")
        assert any(li.text == "Test Partner 1" for li in options)
        assert not any(li.text == "Test Partner 2" for li in options)
        assert any(li.text == "UNHCR" for li in options)
        assert not any(li.text == "TEST" for li in options)

        page_programme_management.driver.find_element(By.CSS_SELECTOR, "body").click()

        page_programme_management.choose_partner_option("UNHCR")

        page_programme_management.get_button_save().click()

        # Check Details page
        page_programme_details.wait_for_text("Test Program Partners", page_programme_details.header_title)
        assert partner_access_selected in page_programme_details.get_label_partner_access().text

        partner_name_elements = page_programme_management.driver.find_elements(
            By.CSS_SELECTOR, "[data-cy='label-partner-name']"
        )
        assert len(partner_name_elements) == 1
        assert any("UNHCR" in partner.text.strip() for partner in partner_name_elements)

        # edit program
        page_programme_management.get_button_edit_program().click()
        page_programme_management.get_select_edit_program_partners().click()

        page_programme_management.get_access_to_program().click()
        page_programme_management.select_who_access_to_program("All Current Partners within the business area")

        programme_edit_url = page_programme_management.driver.current_url
        page_programme_management.get_button_save().click()

        # Check Details page
        sleep(10)
        assert "details" in page_programme_details.wait_for_new_url(programme_edit_url, 20).split("/")

        partner_name_elements_new = page_programme_management.driver.find_elements(
            By.CSS_SELECTOR, "[data-cy='label-partner-name']"
        )
        assert len(partner_name_elements_new) == 3
        page_programme_details.screenshot("partner_name_elements_new.png")
        assert any("UNHCR" in partner.text.strip() for partner in partner_name_elements_new)
        assert any("Test Partner 1" in partner.text.strip() for partner in partner_name_elements_new)
        assert any("TEST" in partner.text.strip() for partner in partner_name_elements_new)

    @pytest.mark.parametrize(
        "test_data",
        [
            pytest.param(
                {
                    "program_name": "New Programme - " + str(random.random()),
                    "selector": "Health",
                    "startDate": FormatTime(1, 1, 2022),
                    "endDate": FormatTime(1, 2, 2032),
                    "dataCollectingType": "Partial",
                },
                id="programme_management_page",
            ),
        ],
    )
    def test_edit_programme_with_rdi(
        self,
        page_programme_management: ProgrammeManagement,
        page_programme_details: ProgrammeDetails,
        test_data: dict,
    ) -> None:
        # Go to Programme Management
        page_programme_management.get_nav_programme_management().click()
        # Create Programme
        page_programme_management.get_button_new_program().click()
        # 1st step (Details)
        page_programme_management.get_input_programme_name().send_keys(test_data["program_name"])
        page_programme_management.get_input_start_date().click()
        page_programme_management.get_input_start_date().send_keys(test_data["startDate"].numerically_formatted_date)
        page_programme_management.get_input_end_date().click()
        page_programme_management.get_input_end_date().send_keys(test_data["endDate"].numerically_formatted_date)
        page_programme_management.choose_option_selector(test_data["selector"])
        page_programme_management.choose_option_data_collecting_type(test_data["dataCollectingType"])
        page_programme_management.get_input_cash_plus().click()
        page_programme_management.get_button_next().click()
        # 2nd step (Time Series Fields)
        page_programme_management.get_button_add_time_series_field().click()
        page_programme_management.get_input_pdu_fields_object_label(0).send_keys("Time Series Field Name 1")
        page_programme_management.get_select_pdu_fields_object_pdu_data_subtype(0).click()
        page_programme_management.select_listbox_element("Text")
        page_programme_management.get_select_pdu_fields_object_pdu_data_number_of_rounds(0).click()
        page_programme_management.select_listbox_element("2")
        page_programme_management.get_input_pdu_fields_rounds_names(0, 0).send_keys("Round 1")
        page_programme_management.get_input_pdu_fields_rounds_names(0, 1).send_keys("Round 2")
        page_programme_management.get_button_next().click()
        # 3rd step (Partners)
        page_programme_management.get_access_to_program().click()
        page_programme_management.select_who_access_to_program("All Current Partners within the business area")
        page_programme_management.get_button_save().click()
        page_programme_management.get_button_edit_program()
        program_name = page_programme_details.get_header_title().text
        # Create Registration Data Import for the program
        RegistrationDataImportFactory(
            program=Program.objects.get(name=program_name),
        )
        # Edit Programme
        page_programme_management.get_button_edit_program().click()
        page_programme_management.get_select_edit_program_details().click()

        # 1st step (Details)
        page_programme_management.clear_input(page_programme_management.get_input_programme_name())
        page_programme_management.get_input_programme_name().send_keys("New name after Edit")
        page_programme_management.get_button_next().click()
        # 2nd step (Time Series Fields)
        is_disabled_add_time_series_field = page_programme_management.get_button_add_time_series_field().get_attribute(
            "disabled"
        )
        assert is_disabled_add_time_series_field == "true"

        is_disabled_edit_time_series_field_name = page_programme_management.get_input_pdu_fields_object_label(
            0
        ).get_attribute("disabled")
        assert is_disabled_edit_time_series_field_name == "true"

        is_disabled_edit_time_series_field_subtype = (
            page_programme_management.get_select_pdu_fields_object_pdu_data_subtype(0).get_attribute("aria-disabled")
        )
        assert is_disabled_edit_time_series_field_subtype == "true"

        # only possible to increase number of rounds
        page_programme_management.get_select_pdu_fields_object_pdu_data_number_of_rounds(0).click()
        is_disabled_decrease_round_number = page_programme_management.get_listbox_element("1").get_attribute(
            "aria-disabled"
        )
        assert is_disabled_decrease_round_number == "true"
        is_disabled_decrease_round_number = page_programme_management.get_listbox_element("2").get_attribute(
            "aria-disabled"
        )
        assert is_disabled_decrease_round_number is None
        is_disabled_decrease_round_number = page_programme_management.get_listbox_element("3").get_attribute(
            "aria-disabled"
        )
        assert is_disabled_decrease_round_number is None
        page_programme_management.select_listbox_element("3")

        is_disabled_edit_time_series_existing_round_name_1 = (
            page_programme_management.get_input_pdu_fields_rounds_names(0, 0).get_attribute("disabled")
        )
        assert is_disabled_edit_time_series_existing_round_name_1 == "true"
        is_disabled_edit_time_series_existing_round_name_2 = (
            page_programme_management.get_input_pdu_fields_rounds_names(0, 1).get_attribute("disabled")
        )
        assert is_disabled_edit_time_series_existing_round_name_2 == "true"

        page_programme_management.get_input_pdu_fields_rounds_names(0, 2).send_keys("Round 3")

        page_programme_management.get_button_save().click()
        assert program_name in page_programme_details.get_header_title().text
