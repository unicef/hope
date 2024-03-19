import os
from datetime import datetime

from django.conf import settings
from django.core.management import call_command

import pytest
from _pytest.fixtures import FixtureRequest
from _pytest.nodes import Item
from _pytest.runner import CallInfo
from page_object.admin_panel.admin_panel import AdminPanel
from page_object.grievance.details_feedback_page import FeedbackDetailsPage
from page_object.grievance.feedback import Feedback
from page_object.grievance.new_feedback import NewFeedback
from page_object.programme_details.programme_details import ProgrammeDetails
from page_object.programme_management.programme_management import ProgrammeManagement
from pytest_django.live_server_helper import LiveServer
from requests import Session
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.models import Partner, Role, User, UserRole
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.geo.models import Country


def pytest_configure() -> None:
    pytest.CSRF = ""
    pytest.SESSION_ID = ""
    pytest.session = Session()


def create_session(host: str, username: str, password: str, csrf: str = "") -> object:
    if (not pytest.SESSION_ID) and (not pytest.CSRF):
        pytest.session.get(f"{host}")
        pytest.CSRF = csrf if csrf else pytest.session.cookies.get_dict()["csrftoken"]
    headers = {
        "X-CSRFToken": pytest.CSRF,
        "Cookie": f"csrftoken={pytest.CSRF}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"username": username, "password": password}
    pytest.session.post(f"{host}/api/unicorn/login/", data=data, headers=headers)
    pytest.SESSION_ID = pytest.session.cookies.get_dict()["sessionid"]
    return pytest.session


@pytest.fixture
def driver() -> Chrome:
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=chrome_options)


@pytest.fixture(autouse=True)
def browser(driver: Chrome) -> Chrome:
    driver.live_server = LiveServer("localhost")
    yield driver
    driver.close()
    pytest.CSRF = ""
    pytest.SESSION_ID = ""


@pytest.fixture
def login(browser: Chrome) -> Chrome:
    browser.get(f"{browser.live_server.url}/api/unicorn/")
    get_cookies = browser.get_cookies()  # type: ignore
    create_session(browser.live_server.url, "superuser", "testtest2", get_cookies[0]["value"])
    browser.add_cookie({"name": "csrftoken", "value": pytest.CSRF})
    browser.add_cookie({"name": "sessionid", "value": pytest.SESSION_ID})
    browser.get(f"{browser.live_server.url}")
    return browser


@pytest.fixture
def pageProgrammeManagement(request: FixtureRequest, browser: Chrome) -> ProgrammeManagement:
    yield ProgrammeManagement(browser)


@pytest.fixture
def pageProgrammeDetails(request: FixtureRequest, browser: Chrome) -> ProgrammeDetails:
    yield ProgrammeDetails(browser)


@pytest.fixture
def pageAdminPanel(request: FixtureRequest, browser: Chrome) -> AdminPanel:
    yield AdminPanel(browser)


@pytest.fixture
def pageFeedback(request: FixtureRequest, browser: Chrome) -> Feedback:
    yield Feedback(browser)


@pytest.fixture
def pageFeedbackDetails(request: FixtureRequest, browser: Chrome) -> FeedbackDetailsPage:
    yield FeedbackDetailsPage(browser)


@pytest.fixture
def pageNewFeedback(request: FixtureRequest, browser: Chrome) -> NewFeedback:
    yield NewFeedback(browser)


@pytest.fixture
def change_super_user() -> None:
    user = User.objects.filter(email="test@example.com").first()
    user.partner = Partner.objects.get(name="UNHCR")
    user.save()


@pytest.fixture(autouse=True)
def create_super_user() -> User:
    Partner.objects.get_or_create(name="TEST")
    Partner.objects.get_or_create(name="UNICEF")
    Partner.objects.get_or_create(name="UNHCR")

    partner = Partner.objects.get(name="UNICEF")

    permission_list = [role.value for role in Permissions]

    role, _ = Role.objects.update_or_create(name="Role", defaults={"permissions": permission_list})

    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json")
    country = Country.objects.get(name="Afghanistan")
    business_area = BusinessArea.objects.create(
        **{
            "pk": "c259b1a0-ae3a-494e-b343-f7c8eb060c68",
            "code": "0060",
            "name": "Afghanistan",
            "long_name": "THE ISLAMIC REPUBLIC OF AFGHANISTAN",
            "region_code": "64",
            "region_name": "SAR",
            "slug": "afghanistan",
            "has_data_sharing_agreement": True,
            "is_payment_plan_applicable": False,
            "kobo_token": "XXX",
        },
    )
    business_area.countries.add(country)

    user = UserFactory.create(
        pk="4196c2c5-c2dd-48d2-887f-3a9d39e78916",
        is_superuser=True,
        is_staff=True,
        username="superuser",
        password="testtest2",
        email="test@example.com",
        partner=partner,
    )
    user_role = UserRole.objects.create(
        user=user,
        role=Role.objects.get(name="Role"),
        business_area=BusinessArea.objects.get(name="Afghanistan"),
    )
    assert User.objects.filter(email="test@example.com").first()
    assert user.is_superuser

    dct_list = [
        {"label": "Full", "code": "full", "description": "Full individual collected", "active": True},
        {"label": "Size only", "code": "size_only", "description": "Size only collected", "active": True},
        {"label": "WASH", "code": "wash", "description": "WASH", "active": True},
        {"label": "Partial", "code": "partial", "description": "Partial individuals collected", "active": True},
        {
            "label": "size/age/gender disaggregated",
            "code": "size_age_gender_disaggregated",
            "description": "No individual data",
            "active": True,
        },
    ]

    for dct in dct_list:
        data_collecting_type = DataCollectingType.objects.create(
            label=dct["label"], code=dct["code"], description=dct["description"], active=dct["active"]
        )
        data_collecting_type.limit_to.add(business_area)
        data_collecting_type.save()

    partner.permissions = {
        str(business_area.pk): {
            "programs": {},
            "roles": [str(user_role.id)],
        }
    }
    partner.save()
    return user


# set up a hook to be able to check if a test has failed
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: Item, call: CallInfo[None]) -> None:
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


@pytest.fixture(scope="function", autouse=True)
def test_failed_check(request: FixtureRequest, browser: Chrome) -> None:
    yield
    if request.node.rep_setup.failed:
        print("setting up a test failed!", request.node.nodeid)
    elif request.node.rep_setup.passed:
        if request.node.rep_call.failed:
            screenshot(browser, request.node.nodeid)
            print("\nExecuting test failed", request.node.nodeid)


# make a screenshot with a name of the test, date and time
def screenshot(driver: Chrome, node_id: str) -> None:
    # sleep(1)
    if not os.path.exists("screenshot"):
        os.makedirs("screenshot")
    file_name = f'{node_id}_{datetime.today().strftime("%Y-%m-%d_%H.%M")}.png'.replace("/", "_").replace("::", "__")
    file_path = os.path.join("screenshot", file_name)
    driver.get_screenshot_as_file(file_path)
