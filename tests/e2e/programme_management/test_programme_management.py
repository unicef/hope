import random
from datetime import datetime
from time import sleep

import pytest
from dateutil.relativedelta import relativedelta
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
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By

from hct_mis_api.apps.account.models import Partner
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.program.models import BeneficiaryGroup, Program

pytestmark = pytest.mark.django_db()


@pytest.fixture
def create_programs() -> None:
    create_program("Test Programm")
    yield


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
    # TODO: below line can be removed after temporary solution is removed for partners. Only being allowed in BA is enough.
    RoleAssignmentFactory(
        partner=partner_unhcr,
        business_area=afghanistan,
        role=RoleFactory(name="Role for UNHCR"),
        program=None,
    )


def create_program(
    name: str, dct_type: str = DataCollectingType.Type.STANDARD, status: str = Program.ACTIVE
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
        self, pageProgrammeManagement: ProgrammeManagement, pageProgrammeDetails: ProgrammeDetails, test_data: dict
    ) -> None:
        # Go to Programme Management
        pageProgrammeManagement.getNavProgrammeManagement().click()
        # Create Programme
        # 1st step (Details)
        pageProgrammeManagement.getButtonNewProgram().click()
        pageProgrammeManagement.getInputProgrammeName().send_keys(test_data["program_name"])
        pageProgrammeManagement.getInputStartDate().click()
        pageProgrammeManagement.getInputStartDate().send_keys(test_data["startDate"].numerically_formatted_date)
        pageProgrammeManagement.getInputEndDate().click()
        pageProgrammeManagement.getInputEndDate().send_keys(test_data["endDate"].numerically_formatted_date)
        pageProgrammeManagement.chooseOptionSelector(test_data["selector"])
        pageProgrammeManagement.chooseOptionDataCollectingType(test_data["dataCollectingType"])
        pageProgrammeManagement.getInputBeneficiaryGroup().click()
        pageProgrammeManagement.select_listbox_element("Main Menu")
        pageProgrammeManagement.getButtonNext().click()
        # 2nd step (Time Series Fields)
        pageProgrammeManagement.getButtonAddTimeSeriesField().click()
        pageProgrammeManagement.getInputPduFieldsObjectLabel(0).send_keys("test series field name")
        pageProgrammeManagement.getSelectPduFieldsObjectPduDataSubtype(0).click()
        pageProgrammeManagement.select_listbox_element("Text")
        pageProgrammeManagement.getSelectPduFieldsObjectPduDataNumberOfRounds(0).click()
        pageProgrammeManagement.select_listbox_element("1")
        pageProgrammeManagement.getInputPduFieldsRoundsNames(0, 0).send_keys("Round 1")
        pageProgrammeManagement.getButtonNext().click()
        # 3rd step (Partners)
        pageProgrammeManagement.getButtonSave().click()
        # Check Details page
        pageProgrammeManagement.screenshot("test_create_programme", file_path="./")
        pageProgrammeDetails.wait_for_text("New Programme", pageProgrammeDetails.headerTitle)
        assert "DRAFT" in pageProgrammeDetails.getProgramStatus().text
        assert test_data["startDate"].date_in_text_format in pageProgrammeDetails.getLabelStartDate().text
        assert test_data["endDate"].date_in_text_format in pageProgrammeDetails.getLabelEndDate().text
        assert test_data["selector"] in pageProgrammeDetails.getLabelSelector().text
        assert test_data["dataCollectingType"] in pageProgrammeDetails.getLabelDataCollectingType().text
        assert "Regular" in pageProgrammeDetails.getLabelFreqOfPayment().text
        assert "-" in pageProgrammeDetails.getLabelAdministrativeAreas().text
        assert "No" in pageProgrammeDetails.getLabelCashPlus().text
        assert "0" in pageProgrammeDetails.getLabelProgramSize().text

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
        self, pageProgrammeManagement: ProgrammeManagement, pageProgrammeDetails: ProgrammeDetails, test_data: dict
    ) -> None:
        # Go to Programme Management
        pageProgrammeManagement.getNavProgrammeManagement().click()
        # Create Programme
        pageProgrammeManagement.getButtonNewProgram().click()
        # 1st step (Details)
        pageProgrammeManagement.getInputProgrammeName().send_keys(test_data["program_name"])
        pageProgrammeManagement.getInputStartDate().click()
        pageProgrammeManagement.getInputStartDate().send_keys(test_data["startDate"].numerically_formatted_date)
        pageProgrammeManagement.getInputEndDate().click()
        pageProgrammeManagement.getInputEndDate().send_keys(test_data["endDate"].numerically_formatted_date)
        pageProgrammeManagement.chooseOptionSelector(test_data["selector"])
        pageProgrammeManagement.chooseOptionDataCollectingType(test_data["dataCollectingType"])
        pageProgrammeManagement.getInputFreqOfPaymentOneOff().click()
        pageProgrammeManagement.getInputCashPlus().click()
        pageProgrammeManagement.getInputDescription().send_keys(test_data["description"])
        pageProgrammeManagement.getInputBudget().clear()
        pageProgrammeManagement.getInputBudget().send_keys(test_data["budget"])
        pageProgrammeManagement.getInputAdministrativeAreasOfImplementation().send_keys(
            test_data["administrativeAreas"]
        )
        pageProgrammeManagement.getInputPopulation().clear()
        pageProgrammeManagement.getInputPopulation().send_keys(test_data["populationGoals"])
        pageProgrammeManagement.getInputBeneficiaryGroup().click()
        pageProgrammeManagement.select_listbox_element("People")
        pageProgrammeManagement.getButtonNext().click()
        # 2nd step (Time Series Fields)
        pageProgrammeManagement.getButtonAddTimeSeriesField()
        pageProgrammeManagement.getButtonNext().click()
        # 3rd step (Partners)
        pageProgrammeManagement.getButtonSave().click()
        # Check Details page
        pageProgrammeDetails.wait_for_text("New Programme", pageProgrammeDetails.headerTitle)
        pageProgrammeDetails.screenshot("0", file_path="./")
        assert "DRAFT" in pageProgrammeDetails.getProgramStatus().text
        assert test_data["startDate"].date_in_text_format in pageProgrammeDetails.getLabelStartDate().text
        assert test_data["endDate"].date_in_text_format in pageProgrammeDetails.getLabelEndDate().text
        assert test_data["selector"] in pageProgrammeDetails.getLabelSelector().text
        assert test_data["dataCollectingType"] in pageProgrammeDetails.getLabelDataCollectingType().text
        assert "One-off" in pageProgrammeDetails.getLabelFreqOfPayment().text
        assert test_data["administrativeAreas"] in pageProgrammeDetails.getLabelAdministrativeAreas().text
        assert "Yes" in pageProgrammeDetails.getLabelCashPlus().text
        assert "0" in pageProgrammeDetails.getLabelProgramSize().text
        assert test_data["description"] in pageProgrammeDetails.getLabelDescription().text

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
    def test_create_programme_Frequency_of_Payment(
        self, pageProgrammeManagement: ProgrammeManagement, pageProgrammeDetails: ProgrammeDetails, test_data: dict
    ) -> None:
        # Go to Programme Management
        pageProgrammeManagement.getNavProgrammeManagement().click()
        # Create Programme
        pageProgrammeManagement.getButtonNewProgram().click()
        # 1st step (Details)
        pageProgrammeManagement.getInputProgrammeName().send_keys("New Programme")
        pageProgrammeManagement.getInputStartDate().click()
        pageProgrammeManagement.getInputStartDate().send_keys(test_data["startDate"].numerically_formatted_date)
        pageProgrammeManagement.getInputEndDate().click()
        pageProgrammeManagement.getInputEndDate().send_keys(test_data["endDate"].numerically_formatted_date)
        pageProgrammeManagement.chooseOptionSelector(test_data["selector"])
        pageProgrammeManagement.chooseOptionDataCollectingType(test_data["dataCollectingType"])
        pageProgrammeManagement.getInputFreqOfPaymentOneOff().click()
        pageProgrammeManagement.getInputBeneficiaryGroup().click()
        pageProgrammeManagement.select_listbox_element("People")
        pageProgrammeManagement.getButtonNext().click()
        # 2nd step (Time Series Fields)
        pageProgrammeManagement.getButtonAddTimeSeriesField()
        pageProgrammeManagement.getButtonNext().click()
        # 3rd step (Partners)
        pageProgrammeManagement.getButtonSave().click()
        # Check Details page
        pageProgrammeDetails.wait_for_text("New Programme", pageProgrammeDetails.headerTitle)
        pageProgrammeDetails.wait_for_text("DRAFT", pageProgrammeDetails.programStatus)
        assert test_data["startDate"].date_in_text_format in pageProgrammeDetails.getLabelStartDate().text
        assert test_data["endDate"].date_in_text_format in pageProgrammeDetails.getLabelEndDate().text
        assert test_data["selector"] in pageProgrammeDetails.getLabelSelector().text
        assert test_data["dataCollectingType"] in pageProgrammeDetails.getLabelDataCollectingType().text
        assert "One-off" in pageProgrammeDetails.getLabelFreqOfPayment().text
        assert "-" in pageProgrammeDetails.getLabelAdministrativeAreas().text
        assert "No" in pageProgrammeDetails.getLabelCashPlus().text
        assert "0" in pageProgrammeDetails.getLabelProgramSize().text

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
    def test_create_programme_Cash_Plus(
        self, pageProgrammeManagement: ProgrammeManagement, pageProgrammeDetails: ProgrammeDetails, test_data: dict
    ) -> None:
        # Go to Programme Management
        pageProgrammeManagement.getNavProgrammeManagement().click()
        # Create Programme
        pageProgrammeManagement.getButtonNewProgram().click()
        # 1st step (Details)
        pageProgrammeManagement.getInputProgrammeName().send_keys(test_data["program_name"])
        pageProgrammeManagement.getInputStartDate().click()
        pageProgrammeManagement.getInputStartDate().send_keys(test_data["startDate"].numerically_formatted_date)
        pageProgrammeManagement.getInputEndDate().click()
        pageProgrammeManagement.getInputEndDate().send_keys(test_data["endDate"].numerically_formatted_date)
        pageProgrammeManagement.chooseOptionSelector(test_data["selector"])
        pageProgrammeManagement.chooseOptionDataCollectingType(test_data["dataCollectingType"])
        pageProgrammeManagement.getInputCashPlus().click()
        pageProgrammeManagement.getInputBeneficiaryGroup().click()
        pageProgrammeManagement.select_listbox_element("People")
        pageProgrammeManagement.getButtonNext().click()
        # 2nd step (Time Series Fields)
        pageProgrammeManagement.getButtonAddTimeSeriesField()
        pageProgrammeManagement.getButtonNext().click()
        # 3rd step (Partners)
        pageProgrammeManagement.getButtonSave().click()
        # Check Details page
        pageProgrammeDetails.wait_for_text("New Programme", pageProgrammeDetails.headerTitle)
        assert "DRAFT" in pageProgrammeDetails.getProgramStatus().text
        assert test_data["startDate"].date_in_text_format in pageProgrammeDetails.getLabelStartDate().text
        assert test_data["endDate"].date_in_text_format in pageProgrammeDetails.getLabelEndDate().text
        assert test_data["selector"] in pageProgrammeDetails.getLabelSelector().text
        assert test_data["dataCollectingType"] in pageProgrammeDetails.getLabelDataCollectingType().text
        assert "Regular" in pageProgrammeDetails.getLabelFreqOfPayment().text
        assert "-" in pageProgrammeDetails.getLabelAdministrativeAreas().text
        assert "Yes" in pageProgrammeDetails.getLabelCashPlus().text
        assert "0" in pageProgrammeDetails.getLabelProgramSize().text

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
        self, pageProgrammeManagement: ProgrammeManagement, pageProgrammeDetails: ProgrammeDetails, test_data: dict
    ) -> None:
        # Go to Programme Management
        pageProgrammeManagement.getNavProgrammeManagement().click()
        # Create Programme
        pageProgrammeManagement.getButtonNewProgram().click()
        # 1st step (Details)
        pageProgrammeManagement.getInputProgrammeName().send_keys(test_data["program_name"])
        pageProgrammeManagement.getInputStartDate().click()
        pageProgrammeManagement.getInputStartDate().send_keys(test_data["startDate"].numerically_formatted_date)
        pageProgrammeManagement.getInputEndDate().click()
        pageProgrammeManagement.getInputEndDate().send_keys(test_data["endDate"].numerically_formatted_date)
        pageProgrammeManagement.chooseOptionSelector(test_data["selector"])
        pageProgrammeManagement.chooseOptionDataCollectingType(test_data["dataCollectingType"])
        pageProgrammeManagement.getInputCashPlus().click()
        pageProgrammeManagement.getInputBeneficiaryGroup().click()
        pageProgrammeManagement.select_listbox_element("People")
        pageProgrammeManagement.getButtonNext().click()
        # 2nd step (Time Series Fields)
        pageProgrammeManagement.getButtonAddTimeSeriesField()
        pageProgrammeManagement.getButtonNext().click()
        # 3rd step (Partners)
        pageProgrammeManagement.getButtonSave().click()
        # Check Details page
        pageProgrammeDetails.wait_for_text("DRAFT", pageProgrammeDetails.programStatus)
        assert test_data["startDate"].date_in_text_format in pageProgrammeDetails.getLabelStartDate().text
        assert test_data["endDate"].date_in_text_format in pageProgrammeDetails.getLabelEndDate().text
        assert test_data["selector"] in pageProgrammeDetails.getLabelSelector().text
        assert test_data["dataCollectingType"] in pageProgrammeDetails.getLabelDataCollectingType().text
        assert "Regular" in pageProgrammeDetails.getLabelFreqOfPayment().text
        assert "-" in pageProgrammeDetails.getLabelAdministrativeAreas().text
        assert "Yes" in pageProgrammeDetails.getLabelCashPlus().text
        assert "0" in pageProgrammeDetails.getLabelProgramSize().text
        # Check Programme Management Page
        pageProgrammeManagement.getNavProgrammeManagement().click()
        pageProgrammeManagement.fillFiltersSearch(test_data["program_name"])
        elements = pageProgrammeManagement.getRowByProgramName(test_data["program_name"])
        assert "DRAFT" in elements[1]
        assert "Health" in elements[2]

    def test_create_programme_check_empty_mandatory_fields(self, pageProgrammeManagement: ProgrammeManagement) -> None:
        # Go to Programme Management
        pageProgrammeManagement.getNavProgrammeManagement().click()
        # Create Programme
        pageProgrammeManagement.getButtonNewProgram().click()
        pageProgrammeManagement.getButtonNext().click()
        # Cehck Mandatory fields texts
        assert "Programme Name is required" in pageProgrammeManagement.getLabelProgrammeName().text.split("\n")
        assert "Start Date is required" in pageProgrammeManagement.getLabelStartDate().text
        assert "Sector is required" in pageProgrammeManagement.getLabelSelector().text
        assert "Data Collecting Type is required" in pageProgrammeManagement.getLabelDataCollectingType().text

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
        self, pageProgrammeManagement: ProgrammeManagement, pageProgrammeDetails: ProgrammeDetails, test_data: dict
    ) -> None:
        # Go to Programme Management
        pageProgrammeManagement.getNavProgrammeManagement().click()
        # Create Programme
        pageProgrammeManagement.getButtonNewProgram().click()
        # 1st step (Details)
        pageProgrammeManagement.getInputProgrammeName().send_keys(test_data["program_name"])
        pageProgrammeManagement.getInputStartDate().click()
        pageProgrammeManagement.getInputStartDate().send_keys(test_data["startDate"].numerically_formatted_date)
        pageProgrammeManagement.getInputEndDate().click()
        pageProgrammeManagement.getInputEndDate().send_keys(test_data["endDate"].numerically_formatted_date)
        pageProgrammeManagement.chooseOptionSelector(test_data["selector"])
        pageProgrammeManagement.chooseOptionDataCollectingType(test_data["dataCollectingType"])
        pageProgrammeManagement.getInputCashPlus().click()
        pageProgrammeManagement.getInputBeneficiaryGroup().click()
        pageProgrammeManagement.select_listbox_element("People")
        pageProgrammeManagement.getButtonNext().click()
        # 2nd step (Time Series Fields)
        pageProgrammeManagement.getButtonAddTimeSeriesField()
        pageProgrammeManagement.getButtonNext().click()
        # 3rd step (Partners)
        pageProgrammeManagement.getAccessToProgram().click()
        pageProgrammeManagement.selectWhoAccessToProgram("Only Selected Partners within the business area")
        pageProgrammeManagement.choosePartnerOption("UNHCR")
        pageProgrammeManagement.getButtonAddPartner().click()
        pageProgrammeManagement.getButtonDelete().click()
        pageProgrammeManagement.getButtonDeletePopup().click()
        pageProgrammeManagement.getButtonSave().click()
        # Check Details page
        with pytest.raises(Exception):
            assert "UNHCR" in pageProgrammeDetails.getLabelPartnerName().text

    def test_create_programme_cancel_scenario(
        self, pageProgrammeManagement: ProgrammeManagement, pageProgrammeDetails: ProgrammeDetails
    ) -> None:
        # Go to Programme Management
        pageProgrammeManagement.getNavProgrammeManagement().click()
        # Create Programme
        pageProgrammeManagement.getButtonNewProgram().click()
        pageProgrammeManagement.getButtonCancel().click()
        assert "Programme Management" in pageProgrammeManagement.getHeaderTitle().text


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
    def test_create_programme_add_partners_Business_Area(
        self,
        change_super_user: None,
        pageProgrammeManagement: ProgrammeManagement,
        pageProgrammeDetails: ProgrammeDetails,
        test_data: dict,
    ) -> None:
        # Go to Programme Management
        pageProgrammeManagement.getNavProgrammeManagement().click()
        # Create Programme
        pageProgrammeManagement.getButtonNewProgram().click()
        # 1st step (Details)
        pageProgrammeManagement.getInputProgrammeName().send_keys(test_data["program_name"])
        pageProgrammeManagement.getInputStartDate().click()
        pageProgrammeManagement.getInputStartDate().send_keys(test_data["startDate"].numerically_formatted_date)
        pageProgrammeManagement.getInputEndDate().click()
        pageProgrammeManagement.getInputEndDate().send_keys(test_data["endDate"].numerically_formatted_date)
        pageProgrammeManagement.chooseOptionSelector(test_data["selector"])
        pageProgrammeManagement.chooseOptionDataCollectingType(test_data["dataCollectingType"])
        pageProgrammeManagement.getInputCashPlus().click()
        pageProgrammeManagement.getInputBeneficiaryGroup().click()
        pageProgrammeManagement.select_listbox_element("People")
        pageProgrammeManagement.getButtonNext().click()
        # 2nd step (Time Series Fields)
        pageProgrammeManagement.getButtonAddTimeSeriesField()
        pageProgrammeManagement.getButtonNext().click()
        # 3rd step (Partners)
        pageProgrammeManagement.getAccessToProgram().click()
        pageProgrammeManagement.selectWhoAccessToProgram("Only Selected Partners within the business area")
        pageProgrammeManagement.choosePartnerOption("UNHCR")
        pageProgrammeManagement.getButtonSave().click()
        # Check Details page

        pageProgrammeDetails.wait_for_text_in_any_element("UNHCR", pageProgrammeDetails.labelPartnerName)
        pageProgrammeDetails.wait_for_text_in_any_element("TEST", pageProgrammeDetails.labelPartnerName)

        assert "Business Area" in pageProgrammeDetails.getLabelAreaAccess().text

    @pytest.mark.skip(reason="Unskip after REST refactoring is complete")
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
    def test_copy_programme(
        self,
        change_super_user: None,
        pageProgrammeManagement: ProgrammeManagement,
        pageProgrammeDetails: ProgrammeDetails,
        test_data: dict,
    ) -> None:
        # Go to Programme Management
        pageProgrammeManagement.getNavProgrammeManagement().click()
        # Create Programme
        pageProgrammeManagement.getButtonNewProgram().click()
        # 1st step (Details)
        pageProgrammeManagement.getInputProgrammeName().send_keys(test_data["program_name"])
        pageProgrammeManagement.getInputStartDate().click()
        pageProgrammeManagement.getInputStartDate().send_keys(test_data["startDate"].numerically_formatted_date)
        pageProgrammeManagement.getInputEndDate().click()
        pageProgrammeManagement.getInputEndDate().send_keys(test_data["endDate"].numerically_formatted_date)
        pageProgrammeManagement.chooseOptionSelector(test_data["selector"])
        pageProgrammeManagement.chooseOptionDataCollectingType(test_data["dataCollectingType"])
        pageProgrammeManagement.getInputCashPlus().click()
        pageProgrammeManagement.getInputBeneficiaryGroup().click()
        pageProgrammeManagement.select_listbox_element("People")
        pageProgrammeManagement.getButtonNext().click()
        # 2nd step (Time Series Fields)
        pageProgrammeManagement.getButtonAddTimeSeriesField().click()
        pageProgrammeManagement.getInputPduFieldsObjectLabel(0).send_keys("Time Series Field Name 1")
        pageProgrammeManagement.getSelectPduFieldsObjectPduDataSubtype(0).click()
        pageProgrammeManagement.select_listbox_element("Text")
        pageProgrammeManagement.getSelectPduFieldsObjectPduDataNumberOfRounds(0).click()
        pageProgrammeManagement.select_listbox_element("1")
        pageProgrammeManagement.getInputPduFieldsRoundsNames(0, 0).send_keys("Round 1")
        pageProgrammeManagement.getButtonNext().click()
        # 3rd step (Partners)
        pageProgrammeManagement.getAccessToProgram().click()
        pageProgrammeManagement.selectWhoAccessToProgram("None of the Partners should have access")
        pageProgrammeManagement.getButtonSave().click()

        # Copy Programme
        pageProgrammeDetails.getCopyProgram().click()
        # 1st step (Details)
        programme_name = pageProgrammeManagement.getInputProgrammeName()
        pageProgrammeManagement.clear_input(programme_name)
        programme_name.send_keys("New Programme")

        pageProgrammeManagement.getButtonNext().click()
        # 2nd step (Time Series Fields)
        pageProgrammeManagement.getButtonAddTimeSeriesField().click()
        pageProgrammeManagement.getInputPduFieldsObjectLabel(0).send_keys("Any name")
        pageProgrammeManagement.getSelectPduFieldsObjectPduDataSubtype(0).click()
        pageProgrammeManagement.select_listbox_element("Number")
        pageProgrammeManagement.getSelectPduFieldsObjectPduDataNumberOfRounds(0).click()
        pageProgrammeManagement.select_listbox_element("1")
        pageProgrammeManagement.getInputPduFieldsRoundsNames(0, 0).send_keys("Round 1")
        pageProgrammeManagement.getButtonNext().click()
        # 3rd step (Partners)
        pageProgrammeManagement.getButtonSave().click()
        pageProgrammeDetails.wait_for_text("New Programme", pageProgrammeDetails.headerTitle)
        assert "New Programme" in pageProgrammeDetails.getHeaderTitle().text


@pytest.mark.night
@pytest.mark.usefixtures("login")
class TestAdminAreas:
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
    def test_create_programme_add_partners_admin_Area(
        self,
        change_super_user: None,
        pageProgrammeManagement: ProgrammeManagement,
        pageProgrammeDetails: ProgrammeDetails,
        test_data: dict,
    ) -> None:
        # Go to Programme Management
        pageProgrammeManagement.getNavProgrammeManagement().click()
        # Create Programme
        pageProgrammeManagement.getButtonNewProgram().click()
        # 1st step (Details)
        pageProgrammeManagement.getInputProgrammeName().send_keys(test_data["program_name"])
        pageProgrammeManagement.getInputStartDate().click()
        pageProgrammeManagement.getInputStartDate().send_keys(test_data["startDate"].numerically_formatted_date)
        pageProgrammeManagement.getInputEndDate().click()
        pageProgrammeManagement.getInputEndDate().send_keys(test_data["endDate"].numerically_formatted_date)
        pageProgrammeManagement.chooseOptionSelector(test_data["selector"])
        pageProgrammeManagement.chooseOptionDataCollectingType(test_data["dataCollectingType"])
        pageProgrammeManagement.getInputCashPlus().click()
        pageProgrammeManagement.getInputBeneficiaryGroup().click()
        pageProgrammeManagement.select_listbox_element("People")
        pageProgrammeManagement.getButtonNext().click()
        # 2nd step (Time Series Fields)
        pageProgrammeManagement.getButtonAddTimeSeriesField()
        pageProgrammeManagement.getButtonNext().click()
        # 3rd step (Partners)
        pageProgrammeManagement.getAccessToProgram().click()
        pageProgrammeManagement.selectWhoAccessToProgram("Only Selected Partners within the business area")

        pageProgrammeManagement.choosePartnerOption("UNHCR")
        pageProgrammeManagement.getLabelAdminArea().click()
        pageProgrammeManagement.chooseAreaAdmin1ByName("Kabul").click()
        # ToDo: Create additional waiting mechanism
        from time import sleep

        sleep(1)
        pageProgrammeManagement.getButtonSave().click()
        # Check Details page
        pageProgrammeDetails.wait_for_text_in_any_element("UNHCR", pageProgrammeDetails.labelPartnerName)
        pageProgrammeDetails.wait_for_text_in_any_element("TEST", pageProgrammeDetails.labelPartnerName)

        assert "1" in pageProgrammeDetails.getLabelAdminArea1().text
        assert "15" in pageProgrammeDetails.getLabelAdminArea2().text


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
        pageProgrammeManagement: ProgrammeManagement,
        pageProgrammeDetails: ProgrammeDetails,
        test_data: dict,
    ) -> None:
        # Go to Programme Management
        pageProgrammeManagement.getNavProgrammeManagement().click()
        # Create Programme
        pageProgrammeManagement.getButtonNewProgram().click()
        # 1st step (Details)
        pageProgrammeManagement.getInputProgrammeName().send_keys("Test Name")
        pageProgrammeManagement.getInputStartDate().click()
        pageProgrammeManagement.getInputStartDate().send_keys(test_data["startDate"].numerically_formatted_date)
        pageProgrammeManagement.getInputEndDate().click()
        pageProgrammeManagement.getInputEndDate().send_keys(test_data["endDate"].numerically_formatted_date)
        pageProgrammeManagement.chooseOptionSelector(test_data["selector"])
        pageProgrammeManagement.chooseOptionDataCollectingType(test_data["dataCollectingType"])
        pageProgrammeManagement.getInputCashPlus().click()
        pageProgrammeManagement.getInputBeneficiaryGroup().click()
        pageProgrammeManagement.select_listbox_element("People Menu")
        pageProgrammeManagement.getButtonNext().click()
        # 2nd step (Time Series Fields)
        pageProgrammeManagement.getButtonAddTimeSeriesField()
        pageProgrammeManagement.getButtonNext().click()
        # 3rd step (Partners)
        pageProgrammeManagement.getAccessToProgram().click()
        pageProgrammeManagement.selectWhoAccessToProgram("Only Selected Partners within the business area")
        pageProgrammeManagement.choosePartnerOption("UNHCR")
        pageProgrammeManagement.getButtonBack().click()
        pageProgrammeManagement.getButtonBack().click()
        assert "Test Name" in pageProgrammeManagement.getInputProgrammeName().get_attribute("value")
        pageProgrammeManagement.clear_input(pageProgrammeManagement.getInputProgrammeName())
        for _ in range(len(pageProgrammeManagement.getInputProgrammeName().get_attribute("value"))):
            pageProgrammeManagement.getInputProgrammeName().send_keys(Keys.BACKSPACE)
        assert "Programme Name is required" in pageProgrammeManagement.getLabelProgrammeName().text.split("\n")
        pageProgrammeManagement.getInputProgrammeName().send_keys(test_data["program_name"])
        # 2nd step (Time Series Fields)
        pageProgrammeManagement.getButtonNext().click()
        pageProgrammeManagement.getButtonAddTimeSeriesField()
        pageProgrammeManagement.getButtonNext().click()
        # 3rd step (Partners)
        pageProgrammeManagement.getAccessToProgram().click()
        ActionChains(pageProgrammeManagement.driver).send_keys(Keys.ESCAPE).perform()
        pageProgrammeManagement.getButtonSave().click()
        # Check Details page
        pageProgrammeDetails.wait_for_text("New Programme", pageProgrammeDetails.headerTitle)
        assert "DRAFT" in pageProgrammeDetails.getProgramStatus().text
        assert test_data["startDate"].date_in_text_format in pageProgrammeDetails.getLabelStartDate().text
        assert test_data["endDate"].date_in_text_format in pageProgrammeDetails.getLabelEndDate().text
        assert test_data["selector"] in pageProgrammeDetails.getLabelSelector().text
        assert test_data["dataCollectingType"] in pageProgrammeDetails.getLabelDataCollectingType().text
        assert "Regular" in pageProgrammeDetails.getLabelFreqOfPayment().text
        assert "-" in pageProgrammeDetails.getLabelAdministrativeAreas().text
        assert "Yes" in pageProgrammeDetails.getLabelCashPlus().text
        assert "0" in pageProgrammeDetails.getLabelProgramSize().text
        assert "UNHCR" in pageProgrammeDetails.getLabelPartnerName().text


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
        self, pageProgrammeManagement: ProgrammeManagement, pageProgrammeDetails: ProgrammeDetails, test_data: dict
    ) -> None:
        # Go to Programme Management
        pageProgrammeManagement.getNavProgrammeManagement().click()
        # Create Programme
        pageProgrammeManagement.getButtonNewProgram().click()
        pageProgrammeManagement.getInputProgrammeName().send_keys(test_data["program_name"])
        pageProgrammeManagement.chooseInputStartDateViaCalendar(15)
        pageProgrammeManagement.chooseInputEndDateViaCalendar(25)
        pageProgrammeManagement.chooseOptionSelector(test_data["selector"])
        pageProgrammeManagement.chooseOptionDataCollectingType(test_data["dataCollectingType"])
        pageProgrammeManagement.getInputBeneficiaryGroup().click()
        pageProgrammeManagement.select_listbox_element("People Menu")
        pageProgrammeManagement.getButtonNext().click()
        # 2nd step (Time Series Fields)
        pageProgrammeManagement.getButtonAddTimeSeriesField()
        pageProgrammeManagement.getButtonNext().click()
        # 3rd step (Partners)
        pageProgrammeManagement.getButtonSave().click()
        # Check Details page
        pageProgrammeDetails.wait_for_text("New Programme", pageProgrammeDetails.headerTitle)
        assert str(datetime.now().strftime("15 %b %Y")) in pageProgrammeDetails.getLabelStartDate().text
        end_date = datetime.now() + relativedelta(months=1)
        assert str(end_date.strftime("25 %b %Y")) in pageProgrammeDetails.getLabelEndDate().text

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
        self, pageProgrammeManagement: ProgrammeManagement, pageProgrammeDetails: ProgrammeDetails, test_data: dict
    ) -> None:
        # Go to Programme Management
        pageProgrammeManagement.getNavProgrammeManagement().click()
        # Create Programme
        pageProgrammeManagement.getButtonNewProgram().click()
        # 1st step (Details)
        pageProgrammeManagement.getInputProgrammeName().send_keys(test_data["program_name"])
        pageProgrammeManagement.getInputStartDate().click()
        pageProgrammeManagement.getInputStartDate().send_keys(test_data["startDate"].numerically_formatted_date)
        pageProgrammeManagement.getInputEndDate().click()
        pageProgrammeManagement.getInputEndDate().send_keys(test_data["endDate"].numerically_formatted_date)
        pageProgrammeManagement.chooseOptionSelector(test_data["selector"])
        pageProgrammeManagement.chooseOptionDataCollectingType(test_data["dataCollectingType"])
        pageProgrammeManagement.getInputCashPlus().click()
        pageProgrammeManagement.getInputBeneficiaryGroup().click()
        pageProgrammeManagement.select_listbox_element("People Menu")
        pageProgrammeManagement.getButtonNext().click()
        # 2nd step (Time Series Fields)
        pageProgrammeManagement.getButtonAddTimeSeriesField()
        pageProgrammeManagement.getButtonNext().click()
        # 3rd step (Partners)
        pageProgrammeManagement.getAccessToProgram().click()
        pageProgrammeManagement.selectWhoAccessToProgram(test_data["partners_access"])
        # ToDo: Workaround: Save button is clickable but Selenium clicking it too fast
        sleep(5)
        pageProgrammeManagement.getButtonSave().click()
        assert test_data["partners_access"] in pageProgrammeDetails.getLabelPartnerAccess().text
        assert test_data["dataCollectingType"] in pageProgrammeDetails.getLabelDataCollectingType().text

    @pytest.mark.xfail(reason="UNSTABLE")
    def test_edit_programme(
        self,
        create_programs: None,
        pageProgrammeManagement: ProgrammeManagement,
        pageProgrammeDetails: ProgrammeDetails,
    ) -> None:
        pageProgrammeManagement.clickNavProgrammeManagement()
        pageProgrammeManagement.getTableRowByProgramName("Test Programm").click()

        pageProgrammeManagement.getButtonEditProgram().click()
        pageProgrammeManagement.getSelectEditProgramDetails().click()

        # 1st step (Details)
        pageProgrammeManagement.clear_input(pageProgrammeManagement.getInputProgrammeName())
        pageProgrammeManagement.getInputProgrammeName().send_keys("New name after Edit")
        pageProgrammeManagement.clear_input(pageProgrammeManagement.getInputProgrammeCode())
        pageProgrammeManagement.getInputProgrammeCode().send_keys("NEW1")
        pageProgrammeManagement.clear_input(pageProgrammeManagement.pageProgrammeManagement.getInputStartDate())
        pageProgrammeManagement.getInputStartDate().send_keys(str(FormatTime(1, 1, 2022).numerically_formatted_date))
        pageProgrammeManagement.clear_input(pageProgrammeManagement.getInputEndDate())
        pageProgrammeManagement.getInputEndDate().send_keys(FormatTime(1, 10, 2099).numerically_formatted_date)
        pageProgrammeManagement.getButtonNext().click()
        # 2nd step (Time Series Fields)
        pageProgrammeManagement.getButtonAddTimeSeriesField()
        pageProgrammeManagement.element_clickable(pageProgrammeManagement.buttonSave)
        # ToDo: Workaround: Save button is clickable but Selenium clicking it too fast
        sleep(5)
        pageProgrammeManagement.getButtonSave().click()
        # Check Details page
        pageProgrammeDetails.wait_for_text("New name after Edit", pageProgrammeDetails.headerTitle)
        assert FormatTime(1, 1, 2022).date_in_text_format in pageProgrammeDetails.getLabelStartDate().text
        assert FormatTime(1, 10, 2099).date_in_text_format in pageProgrammeDetails.getLabelEndDate().text

    @pytest.mark.xfail(reason="UNSTABLE")
    def test_programme_partners(
        self,
        create_programs: None,
        pageProgrammeManagement: ProgrammeManagement,
        pageProgrammeDetails: ProgrammeDetails,
    ) -> None:
        partner1 = Partner.objects.create(name="Test Partner 1")
        partner2 = Partner.objects.create(name="Test Partner 2")
        role = RoleFactory(name="Role in BA")
        RoleAssignmentFactory(role=role, partner=partner1, business_area=BusinessArea.objects.get(slug="afghanistan"))
        # Go to Programme Management
        pageProgrammeManagement.getNavProgrammeManagement().click()
        # Create Programme
        pageProgrammeManagement.getButtonNewProgram().click()
        # 1st step (Details)
        pageProgrammeManagement.getInputProgrammeName().send_keys("Test Program Partners")
        pageProgrammeManagement.getInputStartDate().click()
        pageProgrammeManagement.getInputStartDate().send_keys(str(FormatTime(1, 1, 2022).numerically_formatted_date))
        pageProgrammeManagement.getInputEndDate().click()
        pageProgrammeManagement.getInputEndDate().send_keys(FormatTime(1, 10, 2099).numerically_formatted_date)
        pageProgrammeManagement.chooseOptionSelector("Health")
        pageProgrammeManagement.chooseOptionDataCollectingType("Partial")
        pageProgrammeManagement.getInputCashPlus().click()
        pageProgrammeManagement.getInputBeneficiaryGroup().click()
        pageProgrammeManagement.select_listbox_element("People Menu")
        pageProgrammeManagement.getButtonNext().click()
        # 2nd step (Time Series Fields)
        pageProgrammeManagement.getButtonAddTimeSeriesField()
        pageProgrammeManagement.getButtonNext().click()
        # 3rd step (Partners)
        # only partners with role in business area can be selected

        assert partner1 in Partner.objects.filter(business_areas__slug="afghanistan").all()
        assert partner2 not in Partner.objects.filter(business_areas__slug="afghanistan").all()
        assert Partner.objects.get(name="UNHCR") in Partner.objects.filter(business_areas__slug="afghanistan").all()

        partner_access_selected = "Only Selected Partners within the business area"
        pageProgrammeManagement.getAccessToProgram().click()
        pageProgrammeManagement.selectWhoAccessToProgram(partner_access_selected)

        pageProgrammeManagement.wait_for(pageProgrammeManagement.inputPartner).click()
        select_options_container = pageProgrammeManagement.getSelectOptionsContainer()
        options = select_options_container.find_elements(By.TAG_NAME, "li")
        assert any("Test Partner 1" == li.text for li in options) is True
        assert any("Test Partner 2" == li.text for li in options) is False
        assert any("UNHCR" == li.text for li in options) is True
        assert any("TEST" == li.text for li in options) is True

        pageProgrammeManagement.driver.find_element(By.CSS_SELECTOR, "body").click()

        pageProgrammeManagement.choosePartnerOption("UNHCR")

        pageProgrammeManagement.getButtonSave().click()

        # Check Details page
        pageProgrammeDetails.wait_for_text("Test Program Partners", pageProgrammeDetails.headerTitle)
        assert partner_access_selected in pageProgrammeDetails.getLabelPartnerAccess().text

        partner_name_elements = pageProgrammeManagement.driver.find_elements(
            By.CSS_SELECTOR, "[data-cy='label-partner-name']"
        )
        assert len(partner_name_elements) == 1
        assert any("UNHCR" in partner.text.strip() for partner in partner_name_elements)

        # edit program
        pageProgrammeManagement.getButtonEditProgram().click()
        pageProgrammeManagement.getSelectEditProgramPartners().click()

        pageProgrammeManagement.getAccessToProgram().click()
        pageProgrammeManagement.selectWhoAccessToProgram("All Current Partners within the business area")

        programme_edit_url = pageProgrammeManagement.driver.current_url
        pageProgrammeManagement.getButtonSave().click()

        # Check Details page
        sleep(10)
        assert "details" in pageProgrammeDetails.wait_for_new_url(programme_edit_url, 20).split("/")

        partner_name_elements_new = pageProgrammeManagement.driver.find_elements(
            By.CSS_SELECTOR, "[data-cy='label-partner-name']"
        )
        assert len(partner_name_elements_new) == 3
        pageProgrammeDetails.screenshot("partner_name_elements_new.png")
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
        pageProgrammeManagement: ProgrammeManagement,
        pageProgrammeDetails: ProgrammeDetails,
        test_data: dict,
    ) -> None:
        # Go to Programme Management
        pageProgrammeManagement.getNavProgrammeManagement().click()
        # Create Programme
        pageProgrammeManagement.getButtonNewProgram().click()
        # 1st step (Details)
        pageProgrammeManagement.getInputProgrammeName().send_keys(test_data["program_name"])
        pageProgrammeManagement.getInputStartDate().click()
        pageProgrammeManagement.getInputStartDate().send_keys(test_data["startDate"].numerically_formatted_date)
        pageProgrammeManagement.getInputEndDate().click()
        pageProgrammeManagement.getInputEndDate().send_keys(test_data["endDate"].numerically_formatted_date)
        pageProgrammeManagement.chooseOptionSelector(test_data["selector"])
        pageProgrammeManagement.chooseOptionDataCollectingType(test_data["dataCollectingType"])
        pageProgrammeManagement.getInputCashPlus().click()
        pageProgrammeManagement.getButtonNext().click()
        # 2nd step (Time Series Fields)
        pageProgrammeManagement.getButtonAddTimeSeriesField().click()
        pageProgrammeManagement.getInputPduFieldsObjectLabel(0).send_keys("Time Series Field Name 1")
        pageProgrammeManagement.getSelectPduFieldsObjectPduDataSubtype(0).click()
        pageProgrammeManagement.select_listbox_element("Text")
        pageProgrammeManagement.getSelectPduFieldsObjectPduDataNumberOfRounds(0).click()
        pageProgrammeManagement.select_listbox_element("2")
        pageProgrammeManagement.getInputPduFieldsRoundsNames(0, 0).send_keys("Round 1")
        pageProgrammeManagement.getInputPduFieldsRoundsNames(0, 1).send_keys("Round 2")
        pageProgrammeManagement.getButtonNext().click()
        # 3rd step (Partners)
        pageProgrammeManagement.getAccessToProgram().click()
        pageProgrammeManagement.selectWhoAccessToProgram("All Current Partners within the business area")
        pageProgrammeManagement.getButtonSave().click()
        pageProgrammeManagement.getButtonEditProgram()
        program_name = pageProgrammeDetails.getHeaderTitle().text
        # Create Registration Data Import for the program
        RegistrationDataImportFactory(
            program=Program.objects.get(name=program_name),
        )
        # Edit Programme
        pageProgrammeManagement.getButtonEditProgram().click()
        pageProgrammeManagement.getSelectEditProgramDetails().click()

        # 1st step (Details)
        pageProgrammeManagement.clear_input(pageProgrammeManagement.getInputProgrammeName())
        pageProgrammeManagement.getInputProgrammeName().send_keys("New name after Edit")
        pageProgrammeManagement.getButtonNext().click()
        # 2nd step (Time Series Fields)
        is_disabled_add_time_series_field = pageProgrammeManagement.getButtonAddTimeSeriesField().get_attribute(
            "disabled"
        )
        assert is_disabled_add_time_series_field == "true"

        is_disabled_edit_time_series_field_name = pageProgrammeManagement.getInputPduFieldsObjectLabel(0).get_attribute(
            "disabled"
        )
        assert is_disabled_edit_time_series_field_name == "true"

        is_disabled_edit_time_series_field_subtype = pageProgrammeManagement.getSelectPduFieldsObjectPduDataSubtype(
            0
        ).get_attribute("aria-disabled")
        assert is_disabled_edit_time_series_field_subtype == "true"

        # only possible to increase number of rounds
        pageProgrammeManagement.getSelectPduFieldsObjectPduDataNumberOfRounds(0).click()
        is_disabled_decrease_round_number = pageProgrammeManagement.get_listbox_element("1").get_attribute(
            "aria-disabled"
        )
        assert is_disabled_decrease_round_number == "true"
        is_disabled_decrease_round_number = pageProgrammeManagement.get_listbox_element("2").get_attribute(
            "aria-disabled"
        )
        assert is_disabled_decrease_round_number is None
        is_disabled_decrease_round_number = pageProgrammeManagement.get_listbox_element("3").get_attribute(
            "aria-disabled"
        )
        assert is_disabled_decrease_round_number is None
        pageProgrammeManagement.select_listbox_element("3")

        is_disabled_edit_time_series_existing_round_name_1 = pageProgrammeManagement.getInputPduFieldsRoundsNames(
            0, 0
        ).get_attribute("disabled")
        assert is_disabled_edit_time_series_existing_round_name_1 == "true"
        is_disabled_edit_time_series_existing_round_name_2 = pageProgrammeManagement.getInputPduFieldsRoundsNames(
            0, 1
        ).get_attribute("disabled")
        assert is_disabled_edit_time_series_existing_round_name_2 == "true"

        pageProgrammeManagement.getInputPduFieldsRoundsNames(0, 2).send_keys("Round 3")

        pageProgrammeManagement.getButtonSave().click()
        assert program_name in pageProgrammeDetails.getHeaderTitle().text
