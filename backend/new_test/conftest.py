import os
from datetime import datetime
from time import sleep

from django.conf import settings
from django.core.management import call_command

import pytest
from _pytest.fixtures import FixtureRequest
from _pytest.runner import CallInfo
from page_object.programme_details.programme_details import ProgrammeDetails
from page_object.programme_management.programme_management import ProgrammeManagement
from pytest_django.live_server_helper import LiveServer
from requests import Session
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from tomlkit.items import Item

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.models import Partner, Role, User, UserRole
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


@pytest.fixture(scope="session")
def driver() -> Chrome:
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=chrome_options)


@pytest.fixture(autouse=True, scope="class")
def browser(driver: Chrome) -> Chrome:
    driver.live_server = LiveServer("localhost")
    driver.get(f"{driver.live_server.url}")
    yield driver
    driver.close()


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


@pytest.fixture(autouse=True)
def create_super_user() -> None:
    Partner.objects.get_or_create(name="TEST")
    Partner.objects.get_or_create(name="UNICEF")
    Partner.objects.get_or_create(name="UNHCR")

    partner = Partner.objects.get(name="UNICEF")

    permission_list = [
        "RDI_VIEW_LIST",
        "RDI_VIEW_DETAILS",
        "RDI_IMPORT_DATA",
        "RDI_RERUN_DEDUPE",
        "RDI_MERGE_IMPORT",
        "RDI_REFUSE_IMPORT",
        "POPULATION_VIEW_HOUSEHOLDS_LIST",
        "POPULATION_VIEW_HOUSEHOLDS_DETAILS",
        "POPULATION_VIEW_INDIVIDUALS_LIST",
        "POPULATION_VIEW_INDIVIDUALS_DETAILS",
        "PROGRAMME_VIEW_LIST_AND_DETAILS",
        "PROGRAMME_MANAGEMENT_VIEW",
        "PROGRAMME_DUPLICATE",
        "PROGRAMME_VIEW_PAYMENT_RECORD_DETAILS",
        "PROGRAMME_CREATE",
        "PROGRAMME_UPDATE",
        "PROGRAMME_REMOVE",
        "PROGRAMME_ACTIVATE",
        "PROGRAMME_FINISH",
        "TARGETING_VIEW_LIST",
        "TARGETING_VIEW_DETAILS",
        "TARGETING_CREATE",
        "TARGETING_UPDATE",
        "TARGETING_DUPLICATE",
        "TARGETING_REMOVE",
        "TARGETING_LOCK",
        "TARGETING_UNLOCK",
        "TARGETING_SEND",
        "PAYMENT_VERIFICATION_VIEW_LIST",
        "PAYMENT_VERIFICATION_VIEW_DETAILS",
        "PAYMENT_VERIFICATION_CREATE",
        "PAYMENT_VERIFICATION_UPDATE",
        "PAYMENT_VERIFICATION_ACTIVATE",
        "PAYMENT_VERIFICATION_DISCARD",
        "PAYMENT_VERIFICATION_FINISH",
        "PAYMENT_VERIFICATION_EXPORT",
        "PAYMENT_VERIFICATION_IMPORT",
        "PAYMENT_VERIFICATION_VERIFY",
        "PAYMENT_VERIFICATION_VIEW_PAYMENT_RECORD_DETAILS",
        "PAYMENT_VERIFICATION_DELETE",
        "PAYMENT_VERIFICATION_MARK_AS_FAILED",
        "USER_MANAGEMENT_VIEW_LIST",
        "DASHBOARD_VIEW_COUNTRY",
        "DASHBOARD_EXPORT",
        "GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE",
        "GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR",
        "GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER",
        "GRIEVANCES_VIEW_LIST_SENSITIVE",
        "GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR",
        "GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER",
        "GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE",
        "GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_CREATOR",
        "GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_OWNER",
        "GRIEVANCES_VIEW_DETAILS_SENSITIVE",
        "GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_CREATOR",
        "GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_OWNER",
        "GRIEVANCES_VIEW_HOUSEHOLD_DETAILS",
        "GRIEVANCES_VIEW_HOUSEHOLD_DETAILS_AS_CREATOR",
        "GRIEVANCES_VIEW_HOUSEHOLD_DETAILS_AS_OWNER",
        "GRIEVANCES_VIEW_INDIVIDUALS_DETAILS",
        "GRIEVANCES_VIEW_INDIVIDUALS_DETAILS_AS_CREATOR",
        "GRIEVANCES_VIEW_INDIVIDUALS_DETAILS_AS_OWNER",
        "GRIEVANCES_CREATE",
        "GRIEVANCES_UPDATE",
        "GRIEVANCES_UPDATE_AS_CREATOR",
        "GRIEVANCES_UPDATE_AS_OWNER",
        "GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE",
        "GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE_AS_CREATOR",
        "GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE_AS_OWNER",
        "GRIEVANCES_ADD_NOTE",
        "GRIEVANCES_ADD_NOTE_AS_CREATOR",
        "GRIEVANCES_ADD_NOTE_AS_OWNER",
        "GRIEVANCES_SET_IN_PROGRESS",
        "GRIEVANCES_SET_IN_PROGRESS_AS_CREATOR",
        "GRIEVANCES_SET_IN_PROGRESS_AS_OWNER",
        "GRIEVANCES_SET_ON_HOLD",
        "GRIEVANCES_SET_ON_HOLD_AS_CREATOR",
        "GRIEVANCES_SET_ON_HOLD_AS_OWNER",
        "GRIEVANCES_SEND_FOR_APPROVAL",
        "GRIEVANCES_SEND_FOR_APPROVAL_AS_CREATOR",
        "GRIEVANCES_SEND_FOR_APPROVAL_AS_OWNER",
        "GRIEVANCES_SEND_BACK",
        "GRIEVANCES_SEND_BACK_AS_CREATOR",
        "GRIEVANCES_SEND_BACK_AS_OWNER",
        "GRIEVANCES_APPROVE_DATA_CHANGE",
        "GRIEVANCES_APPROVE_DATA_CHANGE_AS_CREATOR",
        "GRIEVANCES_APPROVE_DATA_CHANGE_AS_OWNER",
        "GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK",
        "GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_CREATOR",
        "GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_OWNER",
        "GRIEVANCES_CLOSE_TICKET_FEEDBACK",
        "GRIEVANCES_CLOSE_TICKET_FEEDBACK_AS_CREATOR",
        "GRIEVANCES_CLOSE_TICKET_FEEDBACK_AS_OWNER",
        "GRIEVANCES_APPROVE_FLAG_AND_DEDUPE",
        "GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_CREATOR",
        "GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_OWNER",
        "GRIEVANCE_ASSIGN",
        "REPORTING_EXPORT",
        "ALL_VIEW_PII_DATA_ON_LISTS",
        "ACTIVITY_LOG_VIEW",
        "ACTIVITY_LOG_DOWNLOAD",
        "PM_CREATE",
        "PM_VIEW_DETAILS",
        "PM_VIEW_LIST",
        "PM_EXPORT_XLSX_FOR_FSP",
        "PM_DOWNLOAD_XLSX_FOR_FSP",
        "PM_SENDING_PAYMENT_PLAN_TO_FSP",
        "PM_MARK_PAYMENT_AS_FAILED",
        "PM_EXPORT_PDF_SUMMARY",
        "PAYMENT_VERIFICATION_INVALID",
        "GRIEVANCES_APPROVE_PAYMENT_VERIFICATION",
        "GRIEVANCES_APPROVE_PAYMENT_VERIFICATION_AS_CREATOR",
        "GRIEVANCES_APPROVE_PAYMENT_VERIFICATION_AS_OWNER",
        "GRIEVANCE_DOCUMENTS_UPLOAD",
        "PM_IMPORT_XLSX_WITH_ENTITLEMENTS",
        "PM_APPLY_RULE_ENGINE_FORMULA_WITH_ENTITLEMENTS",
        "PM_ADMIN_FINANCIAL_SERVICE_PROVIDER_UPDATE",
        "PM_LOCK_AND_UNLOCK",
        "PM_LOCK_AND_UNLOCK_FSP",
        "PM_EXCLUDE_BENEFICIARIES_FROM_FOLLOW_UP_PP",
        "PM_SEND_FOR_APPROVAL",
        "PM_ACCEPTANCE_PROCESS_APPROVE",
        "PM_ACCEPTANCE_PROCESS_AUTHORIZE",
        "PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW",
        "PM_IMPORT_XLSX_WITH_RECONCILIATION",
        "ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST",
        "ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_DETAILS",
        "ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_CREATE",
        "ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_DETAILS_AS_CREATOR",
        "GRIEVANCES_FEEDBACK_VIEW_CREATE",
        "GRIEVANCES_FEEDBACK_VIEW_LIST",
        "GRIEVANCES_FEEDBACK_VIEW_DETAILS",
        "GRIEVANCES_FEEDBACK_VIEW_UPDATE",
        "ACCOUNTABILITY_SURVEY_VIEW_CREATE",
        "ACCOUNTABILITY_SURVEY_VIEW_LIST",
        "ACCOUNTABILITY_SURVEY_VIEW_DETAILS",
        "GRIEVANCES_FEEDBACK_MESSAGE_VIEW_CREATE",
        "CAN_ADD_BUSINESS_AREA_TO_PARTNER",
        "GRIEVANCES_CROSS_AREA_FILTER",
    ]

    role, _ = Role.objects.update_or_create(name="Role", defaults={"permissions": permission_list})

    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json")
    country = Country.objects.get(name="Afghanistan")
    business_area = BusinessArea.objects.create(
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
        },
    )
    business_area.countries.add(country)

    user = UserFactory.create(
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
    sleep(1)
    if not os.path.exists("screenshot"):
        os.makedirs("screenshot")
    file_name = f'{node_id}_{datetime.today().strftime("%Y-%m-%d_%H:%M")}.png'.replace("/", "_").replace("::", "__")
    file_path = os.path.join("screenshot", file_name)
    driver.get_screenshot_as_file(file_path)
