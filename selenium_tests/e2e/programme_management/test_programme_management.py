import pytest
import random
from time import sleep

class TestTest():

    @pytest.mark.parametrize("test_data",[
    pytest.param(
    {"program_name": "New Programme - " + str(random.random()),
    "selector": "Child Protection",
    "startDate": "2023-05-01",
    "endDate": "2033-12-12",
    "dataCollectingType":"Full"
    }, id="Child Protection & Full"),
    pytest.param(
    {"program_name": "New Programme - " + str(random.random()),
    "selector": "Education",
    "startDate": "2023-05-01",
    "endDate": "2033-12-12",
    "dataCollectingType":"Size only"
    }, id="Education & Size only"),
    pytest.param(
    {"program_name": "New Programme - " + str(random.random()),
    "selector": "WASH",
    "startDate": "2023-05-01",
    "endDate": "2033-12-12",
    "dataCollectingType":"size/age/gender disaggregated"
    }, id="WASH & size/age/gender disaggregated"),
    ])
    def test_create_programme(self, pageProgrammeManagement, pageProgrammeDetails, test_data):
        #Go to Programme Management
        pageProgrammeManagement.getNavProgrammeManagement().click()
        #Create Programme
        pageProgrammeManagement.getButtonNewProgram().click()
        pageProgrammeManagement.getInputProgrammeName().send_keys(test_data["program_name"])
        pageProgrammeManagement.getInputStartDate().send_keys(test_data["startDate"])
        pageProgrammeManagement.getInputEndDate().send_keys(test_data["endDate"])
        pageProgrammeManagement.chooseOptionSelector(test_data["selector"])
        pageProgrammeManagement.chooseOptionDataCollectingType(test_data["dataCollectingType"])
        pageProgrammeManagement.getButtonNext().click()
        pageProgrammeManagement.getButtonSave().click()
        #Check Details page
        assert test_data["program_name"] in pageProgrammeDetails.getHeaderTitle().text
        assert "DRAFT" in pageProgrammeDetails.getProgramStatus().text
        assert "1 May 2023" in pageProgrammeDetails.getLabelStartDate().text
        assert "12 Dec 2033" in pageProgrammeDetails.getLabelEndDate().text
        assert test_data["selector"] in pageProgrammeDetails.getLabelSelector().text
        assert test_data["dataCollectingType"] in pageProgrammeDetails.getLabelDataCollectingType().text
        assert "Regular" in pageProgrammeDetails.getLabelFreqOfPayment().text
        assert "-" in pageProgrammeDetails.getLabelAdministrativeAreas().text
        assert "No" in pageProgrammeDetails.getLabelCashPlus().text
        assert "0" in pageProgrammeDetails.getLabelTotalNumberOfHouseholds().text

    @pytest.mark.parametrize("test_data",[
    pytest.param(
    {"program_name": "New Programme - " + str(random.random()),
    "selector": "Health",
    "startDate": "2023-05-01",
    "endDate": "2033-12-12",
    "dataCollectingType":"Partial",
    "description": f"Text with random {str(random.random())} text",
    "budget": 1000.99,
    "administrativeAreas": "Test pass",
    "populationGoals": "100",
    }, id="All"),
    ])
    def test_create_programme_optional_values(self, pageProgrammeManagement, pageProgrammeDetails, test_data):
        #Go to Programme Management
        pageProgrammeManagement.getNavProgrammeManagement().click()
        #Create Programme
        pageProgrammeManagement.getButtonNewProgram().click()
        pageProgrammeManagement.getInputProgrammeName().send_keys(test_data["program_name"])
        pageProgrammeManagement.getInputStartDate().send_keys(test_data["startDate"])
        pageProgrammeManagement.getInputEndDate().send_keys(test_data["endDate"])
        pageProgrammeManagement.chooseOptionSelector(test_data["selector"])
        pageProgrammeManagement.chooseOptionDataCollectingType(test_data["dataCollectingType"])
        pageProgrammeManagement.getInputFreqOfPaymentOneOff().click()
        pageProgrammeManagement.getInputCashPlus().click()
        pageProgrammeManagement.getInputDescription().send_keys(test_data["description"])
        pageProgrammeManagement.getInputBudget().clear()
        pageProgrammeManagement.getInputBudget().send_keys(test_data["budget"])
        pageProgrammeManagement.getInputAdministrativeAreasOfImplementation().send_keys(test_data["administrativeAreas"])
        pageProgrammeManagement.getInputPopulation().clear()
        pageProgrammeManagement.getInputPopulation().send_keys(test_data["populationGoals"])
        pageProgrammeManagement.getButtonNext().click()
        pageProgrammeManagement.getButtonSave().click()
        #Check Details page
        assert test_data["program_name"] in pageProgrammeDetails.getHeaderTitle().text
        assert "DRAFT" in pageProgrammeDetails.getProgramStatus().text
        assert "1 May 2023" in pageProgrammeDetails.getLabelStartDate().text
        assert "12 Dec 2033" in pageProgrammeDetails.getLabelEndDate().text
        assert test_data["selector"] in pageProgrammeDetails.getLabelSelector().text
        assert test_data["dataCollectingType"] in pageProgrammeDetails.getLabelDataCollectingType().text
        assert "One-off" in pageProgrammeDetails.getLabelFreqOfPayment().text
        assert test_data["administrativeAreas"] in pageProgrammeDetails.getLabelAdministrativeAreas().text
        assert "Yes" in pageProgrammeDetails.getLabelCashPlus().text
        assert "0" in pageProgrammeDetails.getLabelTotalNumberOfHouseholds().text

    @pytest.mark.parametrize("test_data",[
    pytest.param(
    {"program_name": "New Programme - " + str(random.random()),
    "selector": "Health",
    "startDate": "2023-05-01",
    "endDate": "2033-12-12",
    "dataCollectingType":"Partial"
    }, id="One-off"),
    ])
    def test_create_programme_Frequency_of_Payment(self, pageProgrammeManagement, pageProgrammeDetails, test_data):
        #Go to Programme Management
        pageProgrammeManagement.getNavProgrammeManagement().click()
        #Create Programme
        pageProgrammeManagement.getButtonNewProgram().click()
        pageProgrammeManagement.getInputProgrammeName().send_keys(test_data["program_name"])
        pageProgrammeManagement.getInputStartDate().send_keys(test_data["startDate"])
        pageProgrammeManagement.getInputEndDate().send_keys(test_data["endDate"])
        pageProgrammeManagement.chooseOptionSelector(test_data["selector"])
        pageProgrammeManagement.chooseOptionDataCollectingType(test_data["dataCollectingType"])
        pageProgrammeManagement.getInputFreqOfPaymentOneOff().click()
        pageProgrammeManagement.getButtonNext().click()
        pageProgrammeManagement.getButtonSave().click()
        #Check Details page
        assert test_data["program_name"] in pageProgrammeDetails.getHeaderTitle().text
        assert "DRAFT" in pageProgrammeDetails.getProgramStatus().text
        assert "1 May 2023" in pageProgrammeDetails.getLabelStartDate().text
        assert "12 Dec 2033" in pageProgrammeDetails.getLabelEndDate().text
        assert test_data["selector"] in pageProgrammeDetails.getLabelSelector().text
        assert test_data["dataCollectingType"] in pageProgrammeDetails.getLabelDataCollectingType().text
        assert "One-off" in pageProgrammeDetails.getLabelFreqOfPayment().text
        assert "-" in pageProgrammeDetails.getLabelAdministrativeAreas().text
        assert "No" in pageProgrammeDetails.getLabelCashPlus().text
        assert "0" in pageProgrammeDetails.getLabelTotalNumberOfHouseholds().text

    @pytest.mark.parametrize("test_data",[
    pytest.param(
    {"program_name": "New Programme - " + str(random.random()),
    "selector": "Health",
    "startDate": "2023-05-01",
    "endDate": "2033-12-12",
    "dataCollectingType":"Partial"
    }, id="Yes"),
    ])
    def test_create_programme_Cash_Plus(self, pageProgrammeManagement, pageProgrammeDetails, test_data):
        #Go to Programme Management
        pageProgrammeManagement.getNavProgrammeManagement().click()
        #Create Programme
        pageProgrammeManagement.getButtonNewProgram().click()
        pageProgrammeManagement.getInputProgrammeName().send_keys(test_data["program_name"])
        pageProgrammeManagement.getInputStartDate().send_keys(test_data["startDate"])
        pageProgrammeManagement.getInputEndDate().send_keys(test_data["endDate"])
        pageProgrammeManagement.chooseOptionSelector(test_data["selector"])
        pageProgrammeManagement.chooseOptionDataCollectingType(test_data["dataCollectingType"])
        pageProgrammeManagement.getInputCashPlus().click()
        pageProgrammeManagement.getButtonNext().click()
        pageProgrammeManagement.getButtonSave().click()
        #Check Details page
        assert test_data["program_name"] in pageProgrammeDetails.getHeaderTitle().text
        assert "DRAFT" in pageProgrammeDetails.getProgramStatus().text
        assert "1 May 2023" in pageProgrammeDetails.getLabelStartDate().text
        assert "12 Dec 2033" in pageProgrammeDetails.getLabelEndDate().text
        assert test_data["selector"] in pageProgrammeDetails.getLabelSelector().text
        assert test_data["dataCollectingType"] in pageProgrammeDetails.getLabelDataCollectingType().text
        assert "Regular" in pageProgrammeDetails.getLabelFreqOfPayment().text
        assert "-" in pageProgrammeDetails.getLabelAdministrativeAreas().text
        assert "Yes" in pageProgrammeDetails.getLabelCashPlus().text
        assert "0" in pageProgrammeDetails.getLabelTotalNumberOfHouseholds().text


    @pytest.mark.parametrize("test_data",[
    pytest.param(
    {"program_name": "CheckProgramme - " + str(random.random()),
    "selector": "Health",
    "startDate": "2023-05-01",
    "endDate": "2033-12-12",
    "dataCollectingType":"Partial"
    }, id="programme_management_page"),
    ])
    def test_create_programme_check(self, pageProgrammeManagement, pageProgrammeDetails, test_data):
        #Go to Programme Management
        pageProgrammeManagement.getNavProgrammeManagement().click()
        #Create Programme
        pageProgrammeManagement.getButtonNewProgram().click()
        pageProgrammeManagement.getInputProgrammeName().send_keys(test_data["program_name"])
        pageProgrammeManagement.getInputStartDate().send_keys(test_data["startDate"])
        pageProgrammeManagement.getInputEndDate().send_keys(test_data["endDate"])
        pageProgrammeManagement.chooseOptionSelector(test_data["selector"])
        pageProgrammeManagement.chooseOptionDataCollectingType(test_data["dataCollectingType"])
        pageProgrammeManagement.getInputCashPlus().click()
        pageProgrammeManagement.getButtonNext().click()
        pageProgrammeManagement.getButtonSave().click()
        #Check Details page
        assert test_data["program_name"] in pageProgrammeDetails.getHeaderTitle().text
        assert "DRAFT" in pageProgrammeDetails.getProgramStatus().text
        assert "1 May 2023" in pageProgrammeDetails.getLabelStartDate().text
        assert "12 Dec 2033" in pageProgrammeDetails.getLabelEndDate().text
        assert test_data["selector"] in pageProgrammeDetails.getLabelSelector().text
        assert test_data["dataCollectingType"] in pageProgrammeDetails.getLabelDataCollectingType().text
        assert "Regular" in pageProgrammeDetails.getLabelFreqOfPayment().text
        assert "-" in pageProgrammeDetails.getLabelAdministrativeAreas().text
        assert "Yes" in pageProgrammeDetails.getLabelCashPlus().text
        assert "0" in pageProgrammeDetails.getLabelTotalNumberOfHouseholds().text
        # Check Programme Management Page
        pageProgrammeManagement.getNavProgrammeManagement().click()
        pageProgrammeManagement.fillFiltersSearch(test_data["program_name"])
        elements = pageProgrammeManagement.getRowByProgramName(test_data["program_name"])
        assert "DRAFT" in elements[1]
        assert "Health" in elements[2]

    @pytest.mark.skip
    def test_create_programme_add_partners_Business_Area(self, pageProgrammeManagement, pageProgrammeDetails, test_data):
        pass

    @pytest.mark.skip
    def test_create_programme_add_partners_Admin_Area(self, pageProgrammeManagement, pageProgrammeDetails, test_data):
        pass

    @pytest.mark.skip
    def test_create_programme_check_empty_mandatory_fields(self, pageProgrammeManagement, pageProgrammeDetails, test_data):
        pass

    @pytest.mark.skip
    def test_create_programme_delete_partners(self, pageProgrammeManagement, pageProgrammeDetails, test_data):
        pass

    @pytest.mark.skip
    def test_create_programme_back_scenario(self, pageProgrammeManagement, pageProgrammeDetails, test_data):
        pass

    @pytest.mark.skip
    def test_create_programme_cancel_scenario(self, pageProgrammeManagement, pageProgrammeDetails, test_data):
        pass

    @pytest.mark.skip
    def test_create_programme_chose_dates_via_calendar(self, pageProgrammeManagement, pageProgrammeDetails, test_data):
        pass
