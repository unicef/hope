import pytest
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from programme_management import ProgrammeManagement

@pytest.fixture(scope='class')
def browser():
    return webdriver.Firefox()

@pytest.fixture(scope="class", autouse=True)
def login(request, browser):
    browser.get("http://localhost:8082/api/unicorn/")
    assert "Log in" in browser.title
    browser.find_element(By.ID, "id_username").send_keys('cypress-username')
    browser.find_element(By.ID, "id_password").send_keys('cypress-password')
    browser.find_element(By.XPATH, '//*[@id="login-form"]/div[3]/input').click()
    browser.get("http://localhost:8082/")
    assert "HOPE" in browser.title
    yield browser
    browser.close()

@pytest.fixture
def pageProgrammeManagement(request, browser):
    yield ProgrammeManagement(browser)