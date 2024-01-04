from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from page_object.programme_management import ProgrammeManagement
import pytest

from time import sleep

@pytest.fixture(scope="class")
def driver_init(request):
    ff_driver = webdriver.Firefox()
    request.cls.browser = ff_driver
    request.cls.programmeManagement = ProgrammeManagement()
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

@pytest.mark.usefixtures("driver_init", "log_in")
class TestProgrammeManagement:

    def get(self, element_type=By.ID, locator=""):
        return self.browser.find_element(element_type, locator)

    def wait_for(self, element_type=By.ID, locator=""):
        return WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located((element_type, locator)))

    def test_create_programme(self):
        self.wait_for(By.XPATH, '//*[@id="root"]/div/div[1]/div/div[2]/ul/div/a[2]/div[2]/span').click()
        self.wait_for(By.CSS_SELECTOR, 'a[data-cy="button-new-program"]').click()
        sleep(1)