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
    "selector": "WASH",
    "startDate": "2023-05-01",
    "endDate": "2033-12-12",
    "dataCollectingType":"size/age/gender disaggregated"
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
        assert "Regular" in pageProgrammeDetails.getLabelFreqOfPayment().text
        assert "-" in pageProgrammeDetails.getLabelAdministrativeAreas().text
        assert "No" in pageProgrammeDetails.getLabelCashPlus().text
        assert "0" in pageProgrammeDetails.getLabelTotalNumberOfHouseholds().text
