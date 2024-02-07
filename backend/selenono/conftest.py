# import sys

import pytest
import requests
# import os
from selenium import webdriver
# from selenium.webdriver.common.by import By
# from datetime import datetime
# from time import sleep
#
# from page_object.programme_management.programme_management import ProgrammeManagement
# from page_object.programme_details.programme_details import ProgrammeDetails
from selenium.webdriver.chrome.options import Options
def pytest_configure():
    pytest.CSRF = ""
    pytest.SESSION_ID = ""
    pytest.session = requests.Session()
    pytest.path = "http://backend:8000"
#
# @pytest.fixture(autouse=True, scope="class")
# def browser() -> webdriver:
#     chrome_options = Options()
#     chrome_options.add_argument("--headless")
#     chrome_options.add_argument("--no-sandbox")
#     return webdriver.Chrome(options=chrome_options)

#
# @pytest.fixture(scope="class", autouse=True)
# def login(request, browser) -> webdriver:
#     browser.implicitly_wait(2)
#     browser.get(f"{pytest.path}/api/unicorn/")
#     browser.implicitly_wait(2)
#     take_screenshot(browser, "123")
#     assert "Log in" in browser.title
#     browser.find_element(By.ID, "id_username").send_keys('cypress-username')
#     browser.find_element(By.ID, "id_password").send_keys('cypress-password')
#     browser.find_element(By.XPATH, '//*[@id="login-form"]/div[3]/input').click()
#     browser.get(f"{pytest.path}")
#     assert "HOPE" in browser.title
#     yield browser
#     browser.close()
#
#
# @pytest.fixture
# def pageProgrammeManagement(request, browser: webdriver) -> ProgrammeManagement:
#     yield ProgrammeManagement(browser)
#
#
# @pytest.fixture
# def pageProgrammeDetails(request, browser: webdriver) -> ProgrammeDetails:
#     yield ProgrammeDetails(browser)
#
#
# # set up a hook to be able to check if a test has failed
# @pytest.hookimpl(tryfirst=True, hookwrapper=True)
# def pytest_runtest_makereport(item, call) -> None:
#     outcome = yield
#     rep = outcome.get_result()
#     setattr(item, "rep_" + rep.when, rep)
#
#
# @pytest.fixture(scope="function", autouse=True)
# def test_failed_check(request, browser: webdriver) -> None:
#     yield
#     if request.node.rep_setup.failed:
#         print("setting up a test failed!", request.node.nodeid)
#     elif request.node.rep_setup.passed:
#         if request.node.rep_call.failed:
#             take_screenshot(browser, request.node.nodeid)
#             print("\nexecuting test failed", request.node.nodeid)
#
#
# # make a screenshot with a name of the test, date and time
# def take_screenshot(driver: webdriver, node_id: str) -> None:
#     sleep(1)
#     if not os.path.exists('screenshot'):
#         os.makedirs('screenshot')
#     file_name = os.path.join('screenshot',
#                              f'{node_id}_{datetime.today().strftime("%Y-%m-%d_%H:%M")}.png'.replace("/", "_").replace(
#                                  "::", "__"))
#     driver.get_screenshot_as_file(file_name)
