import os
from datetime import datetime

from page_object.programme_management.programme_management import ProgrammeManagement
from page_object.programme_details.programme_details import ProgrammeDetails
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pytest_django.live_server_helper import LiveServer
import pytest
import requests
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.account.models import Partner, Role, User, UserRole
from hct_mis_api.apps.account.fixtures import UserFactory
from time import sleep


def take_screenshot(driver, node_id: str) -> None:
    sleep(1)
    if not os.path.exists('screenshot'):
        os.makedirs('screenshot')
    file_name = os.path.join('screenshot',
                             f'{node_id}_{datetime.today().strftime("%Y-%m-%d_%H:%M")}.png'.replace("/", "_").replace(
                                 "::", "__"))
    driver.get_screenshot_as_file(file_name)


def pytest_configure():
    pytest.CSRF = ""
    pytest.SESSION_ID = ""
    pytest.session = requests.Session()


def create_session(host, username, password, csrf=""):
    if (not pytest.SESSION_ID) and (not pytest.CSRF):
        pytest.session.get(f"{host}")
        pytest.CSRF = csrf if csrf else pytest.session.cookies.get_dict()["csrftoken"]
    headers = {
        'X-CSRFToken': pytest.CSRF,
        'Cookie': f'csrftoken={pytest.CSRF}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {"username": username,
            "password": password}
    pytest.session.post(f"{host}/api/unicorn/login/", data=data, headers=headers)
    pytest.SESSION_ID = pytest.session.cookies.get_dict()["sessionid"]
    return pytest.session


@pytest.fixture(scope="session")
def driver() -> webdriver:
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=chrome_options)


@pytest.fixture(autouse=True, scope="class")
def browser(driver):
    driver.live_server = LiveServer("localhost")
    driver.get(f"{driver.live_server.url}")
    return driver


@pytest.fixture
def login(browser):
    permission_list = ["RDI_VIEW_LIST", "RDI_VIEW_DETAILS", "RDI_IMPORT_DATA", "RDI_RERUN_DEDUPE", "RDI_MERGE_IMPORT", "RDI_REFUSE_IMPORT", "POPULATION_VIEW_HOUSEHOLDS_LIST", "POPULATION_VIEW_HOUSEHOLDS_DETAILS", "POPULATION_VIEW_INDIVIDUALS_LIST", "POPULATION_VIEW_INDIVIDUALS_DETAILS", "PROGRAMME_VIEW_LIST_AND_DETAILS", "PROGRAMME_MANAGEMENT_VIEW", "PROGRAMME_DUPLICATE", "PROGRAMME_VIEW_PAYMENT_RECORD_DETAILS", "PROGRAMME_CREATE", "PROGRAMME_UPDATE", "PROGRAMME_REMOVE", "PROGRAMME_ACTIVATE", "PROGRAMME_FINISH", "TARGETING_VIEW_LIST", "TARGETING_VIEW_DETAILS", "TARGETING_CREATE", "TARGETING_UPDATE", "TARGETING_DUPLICATE", "TARGETING_REMOVE", "TARGETING_LOCK", "TARGETING_UNLOCK", "TARGETING_SEND", "PAYMENT_VERIFICATION_VIEW_LIST", "PAYMENT_VERIFICATION_VIEW_DETAILS", "PAYMENT_VERIFICATION_CREATE", "PAYMENT_VERIFICATION_UPDATE", "PAYMENT_VERIFICATION_ACTIVATE", "PAYMENT_VERIFICATION_DISCARD", "PAYMENT_VERIFICATION_FINISH", "PAYMENT_VERIFICATION_EXPORT", "PAYMENT_VERIFICATION_IMPORT", "PAYMENT_VERIFICATION_VERIFY", "PAYMENT_VERIFICATION_VIEW_PAYMENT_RECORD_DETAILS", "PAYMENT_VERIFICATION_DELETE", "PAYMENT_VERIFICATION_MARK_AS_FAILED", "USER_MANAGEMENT_VIEW_LIST", "DASHBOARD_VIEW_COUNTRY", "DASHBOARD_EXPORT", "GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE", "GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR", "GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER", "GRIEVANCES_VIEW_LIST_SENSITIVE", "GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR", "GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER", "GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE", "GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_CREATOR", "GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_OWNER", "GRIEVANCES_VIEW_DETAILS_SENSITIVE", "GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_CREATOR", "GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_OWNER", "GRIEVANCES_VIEW_HOUSEHOLD_DETAILS", "GRIEVANCES_VIEW_HOUSEHOLD_DETAILS_AS_CREATOR", "GRIEVANCES_VIEW_HOUSEHOLD_DETAILS_AS_OWNER", "GRIEVANCES_VIEW_INDIVIDUALS_DETAILS", "GRIEVANCES_VIEW_INDIVIDUALS_DETAILS_AS_CREATOR", "GRIEVANCES_VIEW_INDIVIDUALS_DETAILS_AS_OWNER", "GRIEVANCES_CREATE", "GRIEVANCES_UPDATE", "GRIEVANCES_UPDATE_AS_CREATOR", "GRIEVANCES_UPDATE_AS_OWNER", "GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE", "GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE_AS_CREATOR", "GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE_AS_OWNER", "GRIEVANCES_ADD_NOTE", "GRIEVANCES_ADD_NOTE_AS_CREATOR", "GRIEVANCES_ADD_NOTE_AS_OWNER", "GRIEVANCES_SET_IN_PROGRESS", "GRIEVANCES_SET_IN_PROGRESS_AS_CREATOR", "GRIEVANCES_SET_IN_PROGRESS_AS_OWNER", "GRIEVANCES_SET_ON_HOLD", "GRIEVANCES_SET_ON_HOLD_AS_CREATOR", "GRIEVANCES_SET_ON_HOLD_AS_OWNER", "GRIEVANCES_SEND_FOR_APPROVAL", "GRIEVANCES_SEND_FOR_APPROVAL_AS_CREATOR", "GRIEVANCES_SEND_FOR_APPROVAL_AS_OWNER", "GRIEVANCES_SEND_BACK", "GRIEVANCES_SEND_BACK_AS_CREATOR", "GRIEVANCES_SEND_BACK_AS_OWNER", "GRIEVANCES_APPROVE_DATA_CHANGE", "GRIEVANCES_APPROVE_DATA_CHANGE_AS_CREATOR", "GRIEVANCES_APPROVE_DATA_CHANGE_AS_OWNER", "GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK", "GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_CREATOR", "GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_OWNER", "GRIEVANCES_CLOSE_TICKET_FEEDBACK", "GRIEVANCES_CLOSE_TICKET_FEEDBACK_AS_CREATOR", "GRIEVANCES_CLOSE_TICKET_FEEDBACK_AS_OWNER", "GRIEVANCES_APPROVE_FLAG_AND_DEDUPE", "GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_CREATOR", "GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_OWNER", "GRIEVANCE_ASSIGN", "REPORTING_EXPORT", "ALL_VIEW_PII_DATA_ON_LISTS", "ACTIVITY_LOG_VIEW", "ACTIVITY_LOG_DOWNLOAD",  "PM_CREATE", "PM_VIEW_DETAILS", "PM_VIEW_LIST", "PM_EXPORT_XLSX_FOR_FSP", "PM_DOWNLOAD_XLSX_FOR_FSP", "PM_SENDING_PAYMENT_PLAN_TO_FSP", "PM_MARK_PAYMENT_AS_FAILED", "PM_EXPORT_PDF_SUMMARY", "PAYMENT_VERIFICATION_INVALID", "GRIEVANCES_APPROVE_PAYMENT_VERIFICATION", "GRIEVANCES_APPROVE_PAYMENT_VERIFICATION_AS_CREATOR", "GRIEVANCES_APPROVE_PAYMENT_VERIFICATION_AS_OWNER", "GRIEVANCE_DOCUMENTS_UPLOAD", "PM_IMPORT_XLSX_WITH_ENTITLEMENTS", "PM_APPLY_RULE_ENGINE_FORMULA_WITH_ENTITLEMENTS", "PM_ADMIN_FINANCIAL_SERVICE_PROVIDER_UPDATE", "PM_LOCK_AND_UNLOCK", "PM_LOCK_AND_UNLOCK_FSP", "PM_EXCLUDE_BENEFICIARIES_FROM_FOLLOW_UP_PP", "PM_SEND_FOR_APPROVAL", "PM_ACCEPTANCE_PROCESS_APPROVE", "PM_ACCEPTANCE_PROCESS_AUTHORIZE", "PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW", "PM_IMPORT_XLSX_WITH_RECONCILIATION", "ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST", "ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_DETAILS", "ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_CREATE", "ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_DETAILS_AS_CREATOR", "GRIEVANCES_FEEDBACK_VIEW_CREATE", "GRIEVANCES_FEEDBACK_VIEW_LIST", "GRIEVANCES_FEEDBACK_VIEW_DETAILS", "GRIEVANCES_FEEDBACK_VIEW_UPDATE", "ACCOUNTABILITY_SURVEY_VIEW_CREATE", "ACCOUNTABILITY_SURVEY_VIEW_LIST", "ACCOUNTABILITY_SURVEY_VIEW_DETAILS", "GRIEVANCES_FEEDBACK_MESSAGE_VIEW_CREATE", "CAN_ADD_BUSINESS_AREA_TO_PARTNER", "GRIEVANCES_CROSS_AREA_FILTER"]

    Role.objects.update_or_create(
        name="Role", defaults={"permissions": permission_list}
    )
    BusinessArea.objects.create(
        **{
            "code": "0060",
            "name": "Afghanistan",
            "long_name": "THE ISLAMIC REPUBLIC OF AFGHANISTAN",
            "region_code": "64",
            "region_name": "SAR",
            "slug": "afghanistan",
            "has_data_sharing_agreement": True,
            "is_payment_plan_applicable": False,
            "kobo_token": "XXX",
        }, )
    user = UserFactory.create(is_superuser=True, is_staff=True, username="superuser", password="testtest2",
                              email="test@example.com")
    UserRole.objects.create(
        user=user,
        role=Role.objects.get(name="Role"),
        business_area=BusinessArea.objects.get(name="Afghanistan"),
    )
    assert User.objects.filter(email="test@example.com").first()
    assert user.is_superuser

    browser.get(f"{browser.live_server.url}/api/unicorn/")
    create_session(browser.live_server.url, "superuser", "testtest2", browser.get_cookies()[0]['value'])
    browser.add_cookie({"name": "csrftoken", "value": pytest.CSRF})
    browser.add_cookie({"name": "sessionid", "value": pytest.SESSION_ID})
    browser.get(f"{browser.live_server.url}")
    return browser


@pytest.fixture
def pageProgrammeManagement(request, browser: webdriver) -> ProgrammeManagement:
    yield ProgrammeManagement(browser)


@pytest.fixture
def pageProgrammeDetails(request, browser: webdriver) -> ProgrammeDetails:
    yield ProgrammeDetails(browser)


# set up a hook to be able to check if a test has failed
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call) -> None:
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


@pytest.fixture(scope="function", autouse=True)
def test_failed_check(request, browser: webdriver) -> None:
    yield
    if request.node.rep_setup.failed:
        print("setting up a test failed!", request.node.nodeid)
    elif request.node.rep_setup.passed:
        if request.node.rep_call.failed:
            take_screenshot(browser, request.node.nodeid)
            print("\nexecuting test failed", request.node.nodeid)


# make a screenshot with a name of the test, date and time
def take_screenshot(driver: webdriver, node_id: str) -> None:
    sleep(1)
    if not os.path.exists('screenshot'):
        os.makedirs('screenshot')
    file_name = os.path.join('screenshot',
                             f'{node_id}_{datetime.today().strftime("%Y-%m-%d_%H:%M")}.png'.replace("/", "_").replace(
                                 "::", "__"))
    driver.get_screenshot_as_file(file_name)
