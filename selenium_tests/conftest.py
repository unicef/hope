import pytest
from selenium import webdriver
import requests

from page_object.programme_management.programme_management import ProgrammeManagement
from page_object.programme_details.programme_details import ProgrammeDetails
from page_object.admin_panel.admin_panel import AdminPanel


def pytest_configure():
    pytest.CSRF = ""
    pytest.SESSION_ID = ""
    pytest.session = requests.Session()


@pytest.fixture(scope='class')
def browser() -> webdriver:
    return webdriver.Firefox()


def create_session():
    if (not pytest.SESSION_ID) and (not pytest.CSRF):
        pytest.session.get("http://localhost:8082/api/unicorn")
        pytest.CSRF = pytest.session.cookies.get_dict()["csrftoken"]
        headers = {
            'X-CSRFToken': pytest.CSRF,
            'Cookie': f'csrftoken={pytest.CSRF}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {"username": "cypress-username",
                "password": "cypress-password"}
        pytest.session.post("http://localhost:8082/api/unicorn/login/", data=data, headers=headers)
        pytest.SESSION_ID = pytest.session.cookies.get_dict()["sessionid"]
    return pytest.session


@pytest.fixture(scope="class", autouse=True)
def login(request, browser):
    create_session()
    browser.get("http://localhost:8082")
    browser.add_cookie({"name": "csrftoken", "value": pytest.CSRF})
    browser.add_cookie({"name": "sessionid", "value": pytest.SESSION_ID})
    browser.get("http://localhost:8082")
    assert "HOPE" in browser.title
    yield browser
    browser.close()


@pytest.fixture
def logout(request, browser):
    browser.delete_all_cookies()
    yield
    browser.delete_all_cookies()
    browser.add_cookie({"name": "csrftoken", "value": pytest.CSRF})
    browser.add_cookie({"name": "sessionid", "value": pytest.SESSION_ID})
    browser.get("http://localhost:8082")


@pytest.fixture
def pageProgrammeManagement(request, browser) -> ProgrammeManagement:
    yield ProgrammeManagement(browser)


@pytest.fixture
def pageProgrammeDetails(request, browser) -> ProgrammeDetails:
    yield ProgrammeDetails(browser)


@pytest.fixture
def PageAdminPanel(request, browser) -> AdminPanel:
    yield AdminPanel(browser)
