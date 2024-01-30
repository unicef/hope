import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By

from page_object.programme_management.programme_management import ProgrammeManagement
from page_object.programme_details.programme_details import ProgrammeDetails

pytest.path = "http://localhost:8082"


@pytest.fixture(scope='class')
def browser() -> webdriver:
    return webdriver.Firefox()


@pytest.fixture(scope="class", autouse=True)
def login(request, browser) -> webdriver:
    browser.get(f"{pytest.path}/api/unicorn/")
    assert "Log in" in browser.title
    browser.find_element(By.ID, "id_username").send_keys('cypress-username')
    browser.find_element(By.ID, "id_password").send_keys('cypress-password')
    browser.find_element(By.XPATH, '//*[@id="login-form"]/div[3]/input').click()
    browser.get(f"{pytest.path}")
    assert "HOPE" in browser.title
    yield browser
    browser.close()


@pytest.fixture
def pageProgrammeManagement(request, browser: webdriver) -> ProgrammeManagement:
    yield ProgrammeManagement(browser)


@pytest.fixture
def pageProgrammeDetails(request, browser: webdriver) -> ProgrammeDetails:
    yield ProgrammeDetails(browser)
