import pytest

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from helpers.hope import HOPE

from page_object.programme_management.programme_management import ProgrammeManagement
from page_object.programme_details.programme_details import ProgrammeDetails
from page_object.base_components import BaseLocators
import pytest

from time import sleep
import random

@pytest.fixture(scope="class", autouse=True)
def driver_init(request):
    ff_driver = webdriver.Firefox()
    request.cls.browser = ff_driver
    yield
    ff_driver.close()

@pytest.fixture(scope="class")
def log_in(request):
    request.cls.browser.get("http://localhost:8082/api/unicorn/")
    assert "Log in" in request.cls.browser.title
    request.cls.browser.find_element(By.ID, "id_username").send_keys('cypress-username')
    request.cls.browser.find_element(By.ID, "id_password").send_keys('cypress-password')
    request.cls.browser.find_element(By.XPATH, '//*[@id="login-form"]/div[3]/input').click()
    request.cls.browser.get("http://localhost:8082/")
    assert "HOPE" in request.cls.browser.title
    yield

@pytest.mark.usefixtures("log_in")
class TestProgrammeManagement(HOPE):

    @pytest.mark.parametrize("program_name, selector, startDate, endDate, dataCollectingType",
    [
    ("New Programme - " + str(random.random()),
    "Child Protection",
    "2023-05-01",
    "2033-12-12",
    "Full"),
    ("New Programme - " + str(random.random()),
    "Child Protection",
    "2023-05-01",
    "2033-12-12",
    "Full"),
    ])
    def test_create_programme(self, program_name, selector, startDate, endDate, dataCollectingType):
        #Go to Programme Management
        self.wait_for(BaseLocators.navProgrammeManagement).click()
        #Create Programme
        self.wait_for(ProgrammeManagement.buttonNewProgram).click()
        self.wait_for(ProgrammeManagement.inputProgrammeName).send_keys(program_name)
        self.get(ProgrammeManagement.inputStartDate).send_keys("2023-05-01")
        self.get(ProgrammeManagement.inputEndDate).send_keys("2033-12-12")
        self.get(ProgrammeManagement.selectSelector).click()
        self.get(ProgrammeManagement.optionChildProtection(selector)).click()
        self.wait_for_disappear(ProgrammeManagement.optionChildProtection(selector))
        self.wait_for(ProgrammeManagement.inputDataCollectingType).click()
        self.get(ProgrammeManagement.optionFull).click()
        self.wait_for_disappear(ProgrammeManagement.optionFull)
        self.get(ProgrammeManagement.buttonNext).click()
        self.wait_for(ProgrammeManagement.buttonSave).click()
        #Check Details
        assert program_name in self.wait_for(ProgrammeDetails.headerTitle).text
        assert "DRAFT" in self.wait_for(ProgrammeDetails.programStatus).text
        assert "1 May 2023" in self.wait_for(ProgrammeDetails.labelStartDate).text
        assert "12 Dec 2033" in self.wait_for(ProgrammeDetails.labelEndDate).text
        assert "Child Protection" in self.wait_for(ProgrammeDetails.labelSelector).text
        assert "Full" in self.wait_for(ProgrammeDetails.labelDataCollectingType).text
        assert "Regular" in self.wait_for(ProgrammeDetails.labelFreqOfPayment).text
        assert "-" in self.wait_for(ProgrammeDetails.labelAdministrativeAreas).text
        assert "No" in self.wait_for(ProgrammeDetails.labelCashPlus).text
        assert "0" in self.wait_for(ProgrammeDetails.labelTotalNumberOfHouseholds).text
