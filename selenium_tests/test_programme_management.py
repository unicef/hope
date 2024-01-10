import pytest
import random

class TestTest():

    @pytest.mark.parametrize("test_data",
    [
    {"program_name": "New Programme - " + str(random.random()),
    "selector": "Child Protection",
    "startDate": "2023-05-01",
    "endDate": "2033-12-12",
    "dataCollectingType":"Full"},
    {"program_name": "New Programme - " + str(random.random()),
    "selector": "Child Protection",
    "startDate": "2023-05-01",
    "endDate": "2033-12-12",
    "dataCollectingType":"Full"},
    ])
    def test_create_programme(self, pageProgrammeManagement, test_data):
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
        assert test_data["program_name"] in pageProgrammeDetails.headerTitle().text
        assert "DRAFT" in pageProgrammeDetails.programStatus().text
        assert "1 May 2023" in pageProgrammeDetails.labelStartDate().text
        assert "12 Dec 2033" in pageProgrammeDetails.labelEndDate().text
        assert test_data["selector"] in pageProgrammeDetails.labelSelector().text
        assert test_data["dataCollectingType"] in pageProgrammeDetails.labelDataCollectingType().text
        assert "Regular" in pageProgrammeDetails.labelFreqOfPayment().text
        assert "-" in pageProgrammeDetails.labelAdministrativeAreas().text
        assert "No" in pageProgrammeDetails.labelCashPlus().text
        assert "0" in pageProgrammeDetails.labelTotalNumberOfHouseholds().text
