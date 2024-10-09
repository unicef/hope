import logging
import os
from datetime import datetime

from django.conf import settings
from django.core.management import call_command

import pytest
from _pytest.fixtures import FixtureRequest
from _pytest.nodes import Item
from _pytest.runner import CallInfo
from environ import Env
from flags.models import FlagState
from pytest_django.live_server_helper import LiveServer
from pytest_html_reporter import attach
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

from hct_mis_api.apps.account.fixtures import RoleFactory, UserFactory
from hct_mis_api.apps.account.models import Partner, Role, User, UserRole
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.models import (
    BusinessArea,
    BusinessAreaPartnerThrough,
    DataCollectingType,
)
from hct_mis_api.apps.geo.models import Country
from hct_mis_api.apps.household.fixtures import DocumentTypeFactory
from hct_mis_api.apps.household.models import DocumentType
from tests.selenium.page_object.accountability.communication import (
    AccountabilityCommunication,
)
from tests.selenium.page_object.accountability.comunication_details import (
    AccountabilityCommunicationDetails,
)
from tests.selenium.page_object.accountability.surveys import AccountabilitySurveys
from tests.selenium.page_object.accountability.surveys_details import (
    AccountabilitySurveysDetails,
)
from tests.selenium.page_object.admin_panel.admin_panel import AdminPanel
from tests.selenium.page_object.country_dashboard.country_dashboard import (
    CountryDashboard,
)
from tests.selenium.page_object.filters import Filters
from tests.selenium.page_object.grievance.details_feedback_page import (
    FeedbackDetailsPage,
)
from tests.selenium.page_object.grievance.details_grievance_page import (
    GrievanceDetailsPage,
)
from tests.selenium.page_object.grievance.feedback import Feedback
from tests.selenium.page_object.grievance.grievance_dashboard import GrievanceDashboard
from tests.selenium.page_object.grievance.grievance_tickets import GrievanceTickets
from tests.selenium.page_object.grievance.new_feedback import NewFeedback
from tests.selenium.page_object.grievance.new_ticket import NewTicket
from tests.selenium.page_object.managerial_console.managerial_console import (
    ManagerialConsole,
)
from tests.selenium.page_object.payment_module.new_payment_plan import NewPaymentPlan
from tests.selenium.page_object.payment_module.payment_module import PaymentModule
from tests.selenium.page_object.payment_module.payment_module_details import (
    PaymentModuleDetails,
)
from tests.selenium.page_object.payment_module.program_cycle import (
    ProgramCycleDetailsPage,
    ProgramCyclePage,
)
from tests.selenium.page_object.payment_verification.payment_record import PaymentRecord
from tests.selenium.page_object.payment_verification.payment_verification import (
    PaymentVerification,
)
from tests.selenium.page_object.payment_verification.payment_verification_details import (
    PaymentVerificationDetails,
)
from tests.selenium.page_object.people.people import People
from tests.selenium.page_object.people.people_details import PeopleDetails
from tests.selenium.page_object.program_log.payment_log import ProgramLog
from tests.selenium.page_object.programme_details.programme_details import (
    ProgrammeDetails,
)
from tests.selenium.page_object.programme_management.programme_management import (
    ProgrammeManagement,
)
from tests.selenium.page_object.programme_population.households import Households
from tests.selenium.page_object.programme_population.households_details import (
    HouseholdsDetails,
)
from tests.selenium.page_object.programme_population.individuals import Individuals
from tests.selenium.page_object.programme_population.individuals_details import (
    IndividualsDetails,
)
from tests.selenium.page_object.programme_population.periodic_data_update_templates import (
    PeriodicDatUpdateTemplates,
    PeriodicDatUpdateTemplatesDetails,
)
from tests.selenium.page_object.programme_population.periodic_data_update_uploads import (
    PeriodicDataUpdateUploads,
)
from tests.selenium.page_object.programme_users.programme_users import ProgrammeUsers
from tests.selenium.page_object.registration_data_import.rdi_details_page import (
    RDIDetailsPage,
)
from tests.selenium.page_object.registration_data_import.registration_data_import import (
    RegistrationDataImport,
)
from tests.selenium.page_object.targeting.targeting import Targeting
from tests.selenium.page_object.targeting.targeting_create import TargetingCreate
from tests.selenium.page_object.targeting.targeting_details import TargetingDetails


def pytest_addoption(parser) -> None:  # type: ignore
    parser.addoption("--mapping", action="store_true", default=False, help="Enable mapping mode")


def pytest_configure(config) -> None:  # type: ignore
    env = Env()
    settings.OUTPUT_DATA_ROOT = env("OUTPUT_DATA_ROOT", default="/tests/selenium/output_data")
    config.addinivalue_line("markers", "night: This marker is intended for e2e tests conducted during the night on CI")
    # delete all old screenshots
    settings.REPORT_DIRECTORY = f"{settings.OUTPUT_DATA_ROOT}/report"
    settings.DOWNLOAD_DIRECTORY = f"{settings.OUTPUT_DATA_ROOT}/report/downloads"
    settings.SCREENSHOT_DIRECTORY = f"{settings.REPORT_DIRECTORY}/screenshot"
    if not os.path.exists(settings.SCREENSHOT_DIRECTORY):
        os.makedirs(settings.SCREENSHOT_DIRECTORY)

    for file in os.listdir(settings.SCREENSHOT_DIRECTORY):
        os.remove(os.path.join(settings.SCREENSHOT_DIRECTORY, file))

    settings.DEBUG = True
    settings.ALLOWED_HOSTS = ["localhost", "127.0.0.1", "10.0.2.2", os.getenv("DOMAIN", "")]
    settings.CELERY_TASK_ALWAYS_EAGER = True

    settings.ELASTICSEARCH_INDEX_PREFIX = "test_"
    settings.EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

    settings.EXCHANGE_RATE_CACHE_EXPIRY = 0
    settings.USE_DUMMY_EXCHANGE_RATES = True

    settings.SOCIAL_AUTH_REDIRECT_IS_HTTPS = False
    settings.CSRF_COOKIE_SECURE = False
    settings.CSRF_COOKIE_HTTPONLY = False
    settings.SESSION_COOKIE_SECURE = False
    settings.SESSION_COOKIE_HTTPONLY = True
    settings.SECURE_HSTS_SECONDS = False
    settings.SECURE_CONTENT_TYPE_NOSNIFF = True
    settings.SECURE_REFERRER_POLICY = "same-origin"
    settings.CACHE_ENABLED = False
    settings.CACHES = {
        "default": {
            "BACKEND": "hct_mis_api.apps.core.memcache.LocMemCache",
            "TIMEOUT": 1800,
        }
    }

    settings.LOGGING["loggers"].update(
        {
            "": {"handlers": ["default"], "level": "DEBUG", "propagate": True},
            "registration_datahub.tasks.deduplicate": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": True,
            },
            "sanction_list.tasks.check_against_sanction_list_pre_merge": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": True,
            },
            "graphql": {"handlers": ["default"], "level": "CRITICAL", "propagate": True},
            "elasticsearch": {
                "handlers": ["default"],
                "level": "CRITICAL",
                "propagate": True,
            },
            "elasticsearch-dsl-django": {
                "handlers": ["default"],
                "level": "CRITICAL",
                "propagate": True,
            },
            "hct_mis_api.apps.registration_datahub.tasks.deduplicate": {
                "handlers": ["default"],
                "level": "CRITICAL",
                "propagate": True,
            },
            "hct_mis_api.apps.core.tasks.upload_new_template_and_update_flex_fields": {
                "handlers": ["default"],
                "level": "CRITICAL",
                "propagate": True,
            },
        }
    )

    logging.disable(logging.CRITICAL)
    pytest.SELENIUM_PATH = os.path.dirname(__file__)


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
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-dev-shm-usage")
    if not os.path.exists(settings.DOWNLOAD_DIRECTORY):
        os.makedirs(settings.DOWNLOAD_DIRECTORY)
    prefs = {
        "download.default_directory": settings.DOWNLOAD_DIRECTORY,
    }
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=chrome_options)
    yield driver


@pytest.fixture(scope="session")
def live_server() -> LiveServer:
    yield LiveServer("localhost")


@pytest.fixture(autouse=True, scope="session")
def browser(driver: Chrome, live_server: LiveServer) -> Chrome:
    try:
        driver.live_server = live_server
        yield driver
    finally:
        driver.quit()


@pytest.fixture
def login(browser: Chrome) -> Chrome:
    browser.get(f"{browser.live_server.url}/api/unicorn/")
    browser.execute_script(
        """
    window.indexedDB.databases().then(dbs => dbs.forEach(db => {
        console.log('Deleting database:', db.name);
        indexedDB.deleteDatabase(db.name);
    }));
    window.localStorage.clear();
    window.sessionStorage.clear();
    """
    )
    login = "id_username"
    password = "id_password"
    loginButton = '//*[@id="login-form"]/div[3]/input'
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.wait import WebDriverWait

    WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, loginButton)))
    browser.find_element(By.XPATH, loginButton)
    browser.find_element(By.ID, login).send_keys("superuser")
    browser.find_element(By.ID, password).send_keys("testtest2")
    browser.find_element(By.XPATH, loginButton).click()
    browser.get(f"{browser.live_server.url}/")
    yield browser


@pytest.fixture
def filters(request: FixtureRequest, browser: Chrome) -> Filters:
    yield Filters(browser)


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
def pageGrievanceTickets(request: FixtureRequest, browser: Chrome) -> GrievanceTickets:
    yield GrievanceTickets(browser)


@pytest.fixture
def pageFeedbackDetails(request: FixtureRequest, browser: Chrome) -> FeedbackDetailsPage:
    yield FeedbackDetailsPage(browser)


@pytest.fixture
def pageNewFeedback(request: FixtureRequest, browser: Chrome) -> NewFeedback:
    yield NewFeedback(browser)


@pytest.fixture
def pageRegistrationDataImport(request: FixtureRequest, browser: Chrome) -> RegistrationDataImport:
    yield RegistrationDataImport(browser)


@pytest.fixture
def pageDetailsRegistrationDataImport(request: FixtureRequest, browser: Chrome) -> RDIDetailsPage:
    yield RDIDetailsPage(browser)


@pytest.fixture
def pageHouseholds(request: FixtureRequest, browser: Chrome) -> Households:
    yield Households(browser)


@pytest.fixture
def pagePeople(request: FixtureRequest, browser: Chrome) -> People:
    yield People(browser)


@pytest.fixture
def pagePeopleDetails(request: FixtureRequest, browser: Chrome) -> PeopleDetails:
    yield PeopleDetails(browser)


@pytest.fixture
def pageHouseholdsDetails(request: FixtureRequest, browser: Chrome) -> HouseholdsDetails:
    yield HouseholdsDetails(browser)


@pytest.fixture
def pageIndividuals(request: FixtureRequest, browser: Chrome) -> Individuals:
    yield Individuals(browser)


@pytest.fixture
def pageIndividualsDetails(request: FixtureRequest, browser: Chrome) -> IndividualsDetails:
    yield IndividualsDetails(browser)


@pytest.fixture
def pagePeriodicDataUpdateTemplates(request: FixtureRequest, browser: Chrome) -> PeriodicDatUpdateTemplates:
    yield PeriodicDatUpdateTemplates(browser)


@pytest.fixture
def pagePeriodicDataUpdateTemplatesDetails(
    request: FixtureRequest,
    browser: Chrome,
) -> PeriodicDatUpdateTemplatesDetails:
    yield PeriodicDatUpdateTemplatesDetails(browser)


@pytest.fixture
def pagePeriodicDataUploads(request: FixtureRequest, browser: Chrome) -> PeriodicDataUpdateUploads:
    yield PeriodicDataUpdateUploads(browser)


@pytest.fixture
def pageTargeting(request: FixtureRequest, browser: Chrome) -> Targeting:
    yield Targeting(browser)


@pytest.fixture
def pagePaymentModule(request: FixtureRequest, browser: Chrome) -> PaymentModule:
    yield PaymentModule(browser)


@pytest.fixture
def pagePaymentRecord(request: FixtureRequest, browser: Chrome) -> PaymentRecord:
    yield PaymentRecord(browser)


@pytest.fixture
def pagePaymentVerificationDetails(request: FixtureRequest, browser: Chrome) -> PaymentVerificationDetails:
    yield PaymentVerificationDetails(browser)


@pytest.fixture
def pagePaymentVerification(request: FixtureRequest, browser: Chrome) -> PaymentVerification:
    yield PaymentVerification(browser)


@pytest.fixture
def pageTargetingDetails(request: FixtureRequest, browser: Chrome) -> TargetingDetails:
    yield TargetingDetails(browser)


@pytest.fixture
def pageTargetingCreate(request: FixtureRequest, browser: Chrome) -> TargetingCreate:
    yield TargetingCreate(browser)


@pytest.fixture
def pageGrievanceDetailsPage(request: FixtureRequest, browser: Chrome) -> GrievanceDetailsPage:
    yield GrievanceDetailsPage(browser)


@pytest.fixture
def pageGrievanceNewTicket(request: FixtureRequest, browser: Chrome) -> NewTicket:
    yield NewTicket(browser)


@pytest.fixture
def pageGrievanceDashboard(request: FixtureRequest, browser: Chrome) -> GrievanceDashboard:
    yield GrievanceDashboard(browser)


@pytest.fixture
def pageManagerialConsole(request: FixtureRequest, browser: Chrome) -> ManagerialConsole:
    yield ManagerialConsole(browser)


@pytest.fixture
def pagePaymentModuleDetails(request: FixtureRequest, browser: Chrome) -> PaymentModuleDetails:
    yield PaymentModuleDetails(browser)


@pytest.fixture
def pageNewPaymentPlan(request: FixtureRequest, browser: Chrome) -> NewPaymentPlan:
    yield NewPaymentPlan(browser)


@pytest.fixture
def pageProgramCycle(request: FixtureRequest, browser: Chrome) -> ProgramCyclePage:
    yield ProgramCyclePage(browser)


@pytest.fixture
def pageProgramCycleDetails(request: FixtureRequest, browser: Chrome) -> ProgramCycleDetailsPage:
    yield ProgramCycleDetailsPage(browser)


@pytest.fixture
def pageAccountabilitySurveys(request: FixtureRequest, browser: Chrome) -> AccountabilitySurveys:
    yield AccountabilitySurveys(browser)


@pytest.fixture
def pageAccountabilitySurveysDetails(request: FixtureRequest, browser: Chrome) -> AccountabilitySurveysDetails:
    yield AccountabilitySurveysDetails(browser)


@pytest.fixture
def pageProgrammeUsers(request: FixtureRequest, browser: Chrome) -> ProgrammeUsers:
    yield ProgrammeUsers(browser)


@pytest.fixture
def pageAccountabilityCommunication(request: FixtureRequest, browser: Chrome) -> AccountabilityCommunication:
    yield AccountabilityCommunication(browser)


@pytest.fixture
def pageAccountabilityCommunicationDetails(
    request: FixtureRequest, browser: Chrome
) -> AccountabilityCommunicationDetails:
    yield AccountabilityCommunicationDetails(browser)


@pytest.fixture
def pageProgramLog(request: FixtureRequest, browser: Chrome) -> ProgramLog:
    yield ProgramLog(browser)


@pytest.fixture
def pageCountryDashboard(request: FixtureRequest, browser: Chrome) -> CountryDashboard:
    yield CountryDashboard(browser)


@pytest.fixture
def business_area() -> BusinessArea:
    business_area, _ = BusinessArea.objects.get_or_create(
        **{
            "pk": "c259b1a0-ae3a-494e-b343-f7c8eb060c68",
            "code": "0060",
            "name": "Afghanistan",
            "long_name": "THE ISLAMIC REPUBLIC OF AFGHANISTAN",
            "region_code": "64",
            "region_name": "SAR",
            "slug": "afghanistan",
            "screen_beneficiary": True,
            "has_data_sharing_agreement": True,
            "is_payment_plan_applicable": True,
            "is_accountability_applicable": True,
            "kobo_token": "XXX",
        },
    )
    FlagState.objects.get_or_create(
        **{"name": "ALLOW_ACCOUNTABILITY_MODULE", "condition": "boolean", "value": "True", "required": False}
    )
    yield business_area


@pytest.fixture
def change_super_user(business_area: BusinessArea) -> None:
    user = User.objects.filter(email="test@example.com").first()
    user.partner = Partner.objects.get(name="UNHCR")
    user.partner.allowed_business_areas.add(business_area)
    user.save()
    yield user


@pytest.fixture(autouse=True)
def create_super_user(business_area: BusinessArea) -> User:
    Partner.objects.get_or_create(name="TEST")
    Partner.objects.get_or_create(name="UNICEF")
    Partner.objects.get_or_create(name="UNHCR")

    partner = Partner.objects.get(name="UNICEF")

    permission_list = [role.value for role in Permissions]

    role, _ = Role.objects.update_or_create(name="Role", defaults={"permissions": permission_list})
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data_small.json", verbosity=0)
    country = Country.objects.get(name="Afghanistan")
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
    UserRole.objects.create(
        user=user,
        role=Role.objects.get(name="Role"),
        business_area=business_area,
    )

    for partner in Partner.objects.exclude(name="UNICEF"):
        partner.allowed_business_areas.add(business_area)
        role = RoleFactory(name=f"Role for {partner.name}")
        partner_through = BusinessAreaPartnerThrough.objects.create(
            business_area=business_area,
            partner=partner,
        )
        partner_through.roles.set([role])

    assert User.objects.filter(email="test@example.com").first()
    assert user.is_superuser

    dct_list = [
        {
            "label": "Full",
            "code": "full",
            "description": "Full individual collected",
            "active": True,
            "type": DataCollectingType.Type.STANDARD,
        },
        {
            "label": "Size only",
            "code": "size_only",
            "description": "Size only collected",
            "active": True,
            "type": DataCollectingType.Type.STANDARD,
        },
        {
            "label": "WASH",
            "code": "wash",
            "description": "WASH",
            "active": True,
            "type": DataCollectingType.Type.STANDARD,
        },
        {
            "label": "Partial",
            "code": "partial",
            "description": "Partial individuals collected",
            "active": True,
            "type": DataCollectingType.Type.STANDARD,
        },
        {
            "label": "size/age/gender disaggregated",
            "code": "size_age_gender_disaggregated",
            "description": "No individual data",
            "active": True,
            "type": DataCollectingType.Type.STANDARD,
        },
    ]

    for dct in dct_list:
        data_collecting_type = DataCollectingType.objects.create(
            label=dct["label"],
            code=dct["code"],
            description=dct["description"],
            active=dct["active"],
            type=dct["type"],
        )
        data_collecting_type.limit_to.add(business_area)
        data_collecting_type.save()
    ba_partner_through, _ = BusinessAreaPartnerThrough.objects.get_or_create(
        business_area=business_area, partner=partner
    )
    ba_partner_through.roles.set([role])

    # add document types
    doc_type_keys = (
        "birth_certificate",
        "drivers_license",
        "electoral_card",
        "tax_id",
        "residence_permit_no",
        "bank_statement",
        "disability_certificate",
        "other_id",
        "foster_child",
    )
    for key in doc_type_keys:
        DocumentTypeFactory(key=key)
    DocumentType.objects.update_or_create(key="national_id", pk="227fcbc0-297a-4d85-8390-7de189278321")
    DocumentType.objects.update_or_create(key="national_passport", pk="012a3ecb-0d6e-440f-9c68-83e5bf1ccddf")
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
    if not os.path.exists(settings.SCREENSHOT_DIRECTORY):
        os.makedirs(settings.SCREENSHOT_DIRECTORY)
    file_name = f'{node_id.split("::")[-1]}_{datetime.today().strftime("%Y-%m-%d_%H.%M")}.png'.replace(
        "/", "_"
    ).replace("::", "__")
    file_path = os.path.join(settings.SCREENSHOT_DIRECTORY, file_name)
    driver.get_screenshot_as_file(file_path)
    attach(data=driver.get_screenshot_as_png())
