from contextlib import suppress
from datetime import datetime
import logging
import os
from pathlib import Path
import re
from typing import Any

from _pytest.fixtures import FixtureRequest
from _pytest.nodes import Item
from _pytest.runner import CallInfo
from django.conf import settings
from django.contrib.staticfiles.handlers import StaticFilesHandler
from flags.models import FlagState
import pytest
from pytest_html import extras
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

from e2e.page_object.accountability.communication import AccountabilityCommunication
from e2e.page_object.accountability.comunication_details import (
    AccountabilityCommunicationDetails,
)
from e2e.page_object.accountability.surveys import AccountabilitySurveys
from e2e.page_object.accountability.surveys_details import AccountabilitySurveysDetails
from e2e.page_object.admin_panel.admin_panel import AdminPanel
from e2e.page_object.country_dashboard.country_dashboard import CountryDashboard
from e2e.page_object.filters import Filters
from e2e.page_object.generic_import.generic_import import GenericImport
from e2e.page_object.grievance.details_feedback_page import FeedbackDetailsPage
from e2e.page_object.grievance.details_grievance_page import GrievanceDetailsPage
from e2e.page_object.grievance.feedback import Feedback
from e2e.page_object.grievance.grievance_dashboard import GrievanceDashboard
from e2e.page_object.grievance.grievance_tickets import GrievanceTickets
from e2e.page_object.grievance.new_feedback import NewFeedback
from e2e.page_object.grievance.new_ticket import NewTicket
from e2e.page_object.managerial_console.managerial_console import ManagerialConsole
from e2e.page_object.payment_module.new_payment_plan import NewPaymentPlan
from e2e.page_object.payment_module.payment_module import PaymentModule
from e2e.page_object.payment_module.payment_module_details import PaymentModuleDetails
from e2e.page_object.payment_module.program_cycle import ProgramCyclePage
from e2e.page_object.payment_module.program_cycle_details import ProgramCycleDetailsPage
from e2e.page_object.payment_verification.payment_record import PaymentRecord
from e2e.page_object.payment_verification.payment_verification import (
    PaymentVerification,
)
from e2e.page_object.payment_verification.payment_verification_details import (
    PaymentVerificationDetails,
)
from e2e.page_object.people.people import People
from e2e.page_object.people.people_details import PeopleDetails
from e2e.page_object.program_log.payment_log import ProgramLog
from e2e.page_object.programme_details.programme_details import ProgrammeDetails
from e2e.page_object.programme_management.programme_management import (
    ProgrammeManagement,
)
from e2e.page_object.programme_population.households import Households
from e2e.page_object.programme_population.households_details import HouseholdsDetails
from e2e.page_object.programme_population.individuals import Individuals
from e2e.page_object.programme_population.individuals_details import IndividualsDetails
from e2e.page_object.programme_population.periodic_data_update_templates import (
    PDUXlsxTemplates,
    PDUXlsxTemplatesDetails,
)
from e2e.page_object.programme_population.periodic_data_update_uploads import (
    PDUXlsxUploads,
)
from e2e.page_object.programme_users.programme_users import ProgrammeUsers
from e2e.page_object.registration_data_import.rdi_details_page import RDIDetailsPage
from e2e.page_object.registration_data_import.registration_data_import import (
    RegistrationDataImport,
)
from e2e.page_object.targeting.targeting import Targeting
from e2e.page_object.targeting.targeting_create import TargetingCreate
from e2e.page_object.targeting.targeting_details import TargetingDetails
from extras.test_utils.old_factories.account import RoleFactory, UserFactory
from extras.test_utils.old_factories.geo import (
    generate_small_areas_for_afghanistan_only,
)
from extras.test_utils.old_factories.household import DocumentTypeFactory
from extras.test_utils.old_factories.program import BeneficiaryGroupFactory
from hope.apps.account.permissions import Permissions
from hope.config.env import env
from hope.models import (
    BusinessArea,
    Country,
    DataCollectingType,
    DocumentType,
    Partner,
    Role,
    RoleAssignment,
    User,
)

HERE = Path(__file__).resolve().parent
E2E_ROOT = HERE.parent

# Local build directory in the project root
BUILD_ROOT = E2E_ROOT / "build"
BUILD_ROOT.mkdir(exist_ok=True)

REPORT_DIRECTORY = BUILD_ROOT / "report"
REPORT_DIRECTORY.mkdir(parents=True, exist_ok=True)

DOWNLOAD_DIRECTORY = BUILD_ROOT / "downloads"
DOWNLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)

SCREENSHOT_DIRECTORY = BUILD_ROOT / "screenshot"
SCREENSHOT_DIRECTORY.mkdir(parents=True, exist_ok=True)


def pytest_addoption(parser) -> None:  # type: ignore
    parser.addoption("--mapping", action="store_true", default=False, help="Enable mapping mode")


def get_redis_host() -> str:
    regex = "\\/\\/(.*):"
    return re.search(regex, env("CACHE_LOCATION")).group(1)


@pytest.fixture(autouse=True)
def create_unicef_partner() -> None:
    unicef, _ = Partner.objects.get_or_create(name="UNICEF")
    Partner.objects.get_or_create(name=settings.UNICEF_HQ_PARTNER, parent=unicef)


@pytest.fixture(autouse=True)
def create_role_with_all_permissions() -> None:
    Role.objects.get_or_create(name="Role with all permissions")


@pytest.fixture(autouse=True)
def clear_default_cache() -> None:
    from django.core.cache import cache

    cache.clear()


def _patch_sync_apps_for_no_migrations() -> None:
    """Patch Django's sync_apps to not skip apps without models_module.

    This is needed for --no-migrations to work correctly when models are
    defined in hope.models instead of hope.apps.*.models.

    Django's sync_apps() skips apps where models_module is None, but our
    models are in hope.models with app_label pointing to hope.apps.*.
    """
    from django.core.management.commands import migrate

    original_sync_apps = migrate.Command.sync_apps

    def patched_sync_apps(self, connection, app_labels):
        from django.apps import apps as django_apps

        import hope.models

        for app_config in django_apps.get_app_configs():
            if app_config.models_module is None and "hope" in app_config.name:
                app_config.models_module = hope.models

        return original_sync_apps(self, connection, app_labels)

    migrate.Command.sync_apps = patched_sync_apps


def pytest_configure(config) -> None:  # type: ignore
    _patch_sync_apps_for_no_migrations()

    config.addinivalue_line(
        "markers",
        "night: This marker is intended for e2e tests conducted during the night on CI",
    )

    SCREENSHOT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    for file in SCREENSHOT_DIRECTORY.iterdir():
        if file.is_file():
            file.unlink()

    from django.conf import settings  # noqa

    settings.DATABASES["read_only"]["TEST"] = {"MIRROR": "default"}
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
def download_path(worker_id: str) -> str:
    try:
        assert worker_id is not None
        path = DOWNLOAD_DIRECTORY / worker_id
    except (AssertionError, TimeoutException):
        path = DOWNLOAD_DIRECTORY
    return str(path)


@pytest.fixture(scope="session")
def screenshot_path(worker_id: str) -> str:
    try:
        assert worker_id is not None
        path = SCREENSHOT_DIRECTORY / worker_id
    except (AssertionError, TimeoutException):
        path = SCREENSHOT_DIRECTORY
    return str(path)


@pytest.fixture
def driver(download_path: str) -> Chrome:
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

    with suppress(FileExistsError):
        os.makedirs(download_path)

    prefs = {"download.default_directory": download_path}
    chrome_options.add_experimental_option("prefs", prefs)

    return Chrome(options=chrome_options)


@pytest.fixture
def live_server_with_static(live_server, settings):
    """
    Wrap the live_server with StaticFilesHandler for Selenium tests.
    Also override storages for testing.
    """
    settings.STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }

    # Wrap the existing live_server with static files handler
    live_server._static_handler = StaticFilesHandler(live_server._live_server_modified_settings)
    return live_server


@pytest.fixture(autouse=True)
def browser(driver: Chrome, live_server_with_static) -> Chrome:
    """
    Provide a Chrome driver bound to Django's static live server.
    """
    try:
        driver.live_server = live_server_with_static
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
    login_button = '//*[@id="login-form"]/div[3]/input'
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions
    from selenium.webdriver.support.wait import WebDriverWait

    WebDriverWait(browser, 10).until(expected_conditions.visibility_of_element_located((By.XPATH, login_button)))
    browser.find_element(By.XPATH, login_button)
    browser.find_element(By.ID, login).send_keys("superuser")
    browser.find_element(By.ID, password).send_keys("testtest2")
    browser.find_element(By.XPATH, login_button).click()
    from time import sleep

    sleep(0.3)  # TODO: added just for test in CI
    browser.get(f"{browser.live_server.url}/")

    from django.core.cache import cache

    cache.clear()
    return browser


@pytest.fixture
def filters(request: FixtureRequest, browser: Chrome) -> Filters:
    return Filters(browser)


@pytest.fixture
def page_programme_management(request: FixtureRequest, browser: Chrome) -> ProgrammeManagement:
    return ProgrammeManagement(browser)


@pytest.fixture
def page_programme_details(request: FixtureRequest, browser: Chrome) -> ProgrammeDetails:
    return ProgrammeDetails(browser)


@pytest.fixture
def page_admin_panel(request: FixtureRequest, browser: Chrome) -> AdminPanel:
    return AdminPanel(browser)


@pytest.fixture
def page_feedback(request: FixtureRequest, browser: Chrome) -> Feedback:
    return Feedback(browser)


@pytest.fixture
def page_grievance_tickets(request: FixtureRequest, browser: Chrome) -> GrievanceTickets:
    return GrievanceTickets(browser)


@pytest.fixture
def page_feedback_details(request: FixtureRequest, browser: Chrome) -> FeedbackDetailsPage:
    return FeedbackDetailsPage(browser)


@pytest.fixture
def page_new_feedback(request: FixtureRequest, browser: Chrome) -> NewFeedback:
    return NewFeedback(browser)


@pytest.fixture
def page_registration_data_import(request: FixtureRequest, browser: Chrome) -> RegistrationDataImport:
    return RegistrationDataImport(browser)


@pytest.fixture
def page_details_registration_data_import(request: FixtureRequest, browser: Chrome) -> RDIDetailsPage:
    return RDIDetailsPage(browser)


@pytest.fixture
def page_households(request: FixtureRequest, browser: Chrome) -> Households:
    return Households(browser)


@pytest.fixture
def page_people(request: FixtureRequest, browser: Chrome) -> People:
    return People(browser)


@pytest.fixture
def page_people_details(request: FixtureRequest, browser: Chrome) -> PeopleDetails:
    return PeopleDetails(browser)


@pytest.fixture
def page_households_details(request: FixtureRequest, browser: Chrome) -> HouseholdsDetails:
    return HouseholdsDetails(browser)


@pytest.fixture
def page_individuals(request: FixtureRequest, browser: Chrome) -> Individuals:
    return Individuals(browser)


@pytest.fixture
def page_individuals_details(request: FixtureRequest, browser: Chrome) -> IndividualsDetails:
    return IndividualsDetails(browser)


@pytest.fixture
def page_pdu_xlsx_templates(request: FixtureRequest, browser: Chrome) -> PDUXlsxTemplates:
    return PDUXlsxTemplates(browser)


@pytest.fixture
def page_pdu_xlsx_templates_details(
    request: FixtureRequest,
    browser: Chrome,
) -> PDUXlsxTemplatesDetails:
    return PDUXlsxTemplatesDetails(browser)


@pytest.fixture
def page_pdu_xlsx_uploads(request: FixtureRequest, browser: Chrome) -> PDUXlsxUploads:
    return PDUXlsxUploads(browser)


@pytest.fixture
def page_targeting(request: FixtureRequest, browser: Chrome) -> Targeting:
    return Targeting(browser)


@pytest.fixture
def page_payment_module(request: FixtureRequest, browser: Chrome) -> PaymentModule:
    return PaymentModule(browser)


@pytest.fixture
def page_payment_record(request: FixtureRequest, browser: Chrome) -> PaymentRecord:
    return PaymentRecord(browser)


@pytest.fixture
def page_payment_verification_details(request: FixtureRequest, browser: Chrome) -> PaymentVerificationDetails:
    return PaymentVerificationDetails(browser)


@pytest.fixture
def page_payment_verification(request: FixtureRequest, browser: Chrome) -> PaymentVerification:
    return PaymentVerification(browser)


@pytest.fixture
def page_targeting_details(request: FixtureRequest, browser: Chrome) -> TargetingDetails:
    return TargetingDetails(browser)


@pytest.fixture
def page_targeting_create(request: FixtureRequest, browser: Chrome) -> TargetingCreate:
    return TargetingCreate(browser)


@pytest.fixture
def page_grievance_details_page(request: FixtureRequest, browser: Chrome) -> GrievanceDetailsPage:
    return GrievanceDetailsPage(browser)


@pytest.fixture
def page_grievance_new_ticket(request: FixtureRequest, browser: Chrome) -> NewTicket:
    return NewTicket(browser)


@pytest.fixture
def page_grievance_dashboard(request: FixtureRequest, browser: Chrome) -> GrievanceDashboard:
    return GrievanceDashboard(browser)


@pytest.fixture
def page_managerial_console(request: FixtureRequest, browser: Chrome) -> ManagerialConsole:
    return ManagerialConsole(browser)


@pytest.fixture
def page_payment_module_details(request: FixtureRequest, browser: Chrome) -> PaymentModuleDetails:
    return PaymentModuleDetails(browser)


@pytest.fixture
def page_new_payment_plan(request: FixtureRequest, browser: Chrome) -> NewPaymentPlan:
    return NewPaymentPlan(browser)


@pytest.fixture
def page_program_cycle(request: FixtureRequest, browser: Chrome) -> ProgramCyclePage:
    return ProgramCyclePage(browser)


@pytest.fixture
def page_program_cycle_details(request: FixtureRequest, browser: Chrome) -> ProgramCycleDetailsPage:
    return ProgramCycleDetailsPage(browser)


@pytest.fixture
def page_accountability_surveys(request: FixtureRequest, browser: Chrome) -> AccountabilitySurveys:
    return AccountabilitySurveys(browser)


@pytest.fixture
def page_accountability_surveys_details(request: FixtureRequest, browser: Chrome) -> AccountabilitySurveysDetails:
    return AccountabilitySurveysDetails(browser)


@pytest.fixture
def page_programme_users(request: FixtureRequest, browser: Chrome) -> ProgrammeUsers:
    return ProgrammeUsers(browser)


@pytest.fixture
def page_accountability_communication(request: FixtureRequest, browser: Chrome) -> AccountabilityCommunication:
    return AccountabilityCommunication(browser)


@pytest.fixture
def page_accountability_communication_details(
    request: FixtureRequest, browser: Chrome
) -> AccountabilityCommunicationDetails:
    return AccountabilityCommunicationDetails(browser)


@pytest.fixture
def page_program_log(request: FixtureRequest, browser: Chrome) -> ProgramLog:
    return ProgramLog(browser)


@pytest.fixture
def page_country_dashboard(request: FixtureRequest, browser: Chrome) -> CountryDashboard:
    return CountryDashboard(browser)


@pytest.fixture
def page_generic_import(request: FixtureRequest, browser: Chrome) -> GenericImport:
    return GenericImport(browser)


@pytest.fixture
def business_area(create_unicef_partner: Any, create_role_with_all_permissions: Any) -> BusinessArea:
    business_area, _ = BusinessArea.objects.get_or_create(
        pk="c259b1a0-ae3a-494e-b343-f7c8eb060c68",
        code="0060",
        name="Afghanistan",
        long_name="THE ISLAMIC REPUBLIC OF AFGHANISTAN",
        region_code="64",
        region_name="SAR",
        slug="afghanistan",
        has_data_sharing_agreement=True,
        is_accountability_applicable=True,
        kobo_token="XXX",
        active=True,
    )
    FlagState.objects.get_or_create(
        name="ALLOW_ACCOUNTABILITY_MODULE",
        condition="boolean",
        value="True",
        required=False,
    )
    return business_area


@pytest.fixture
def clear_downloaded_files(download_path: str) -> None:
    for file in os.listdir(download_path):
        os.remove(os.path.join(download_path, file))
    yield
    for file in os.listdir(download_path):
        os.remove(os.path.join(download_path, file))


@pytest.fixture
def change_super_user(business_area: BusinessArea) -> None:
    user = User.objects.filter(email="test@example.com").first()
    user.partner = Partner.objects.get(name="UNHCR")
    user.partner.allowed_business_areas.add(business_area)
    user.save()
    return user


@pytest.fixture(autouse=True)
def create_super_user(business_area: BusinessArea) -> User:
    BeneficiaryGroupFactory(
        id="913700c0-3b8b-429a-b68f-0cd3d2bcd09a",
        name="Main Menu",
        group_label="Items Group",
        group_label_plural="Items Groups",
        member_label="Item",
        member_label_plural="Items",
        master_detail=True,
    )

    BeneficiaryGroupFactory(
        id="9cf21adb-74a9-4c3c-9057-6fb27feb4220",
        name="People",
        group_label="Household",
        group_label_plural="Households",
        member_label="Individual",
        member_label_plural="Individuals",
        master_detail=False,
    )

    Partner.objects.get_or_create(name="TEST")
    partner, _ = Partner.objects.get_or_create(name="UNICEF")
    unicef_hq, _ = Partner.objects.get_or_create(name="UNICEF HQ", parent=partner)
    Partner.objects.get_or_create(name="UNHCR")

    permission_list = [role.value for role in Permissions]

    role, _ = Role.objects.update_or_create(name="Role", defaults={"permissions": permission_list})
    generate_small_areas_for_afghanistan_only()
    country = Country.objects.get(name="Afghanistan")
    business_area.countries.add(country)

    if not (user := User.objects.filter(pk="4196c2c5-c2dd-48d2-887f-3a9d39e78916").first()):
        user = UserFactory(
            pk="4196c2c5-c2dd-48d2-887f-3a9d39e78916",
            is_superuser=True,
            is_staff=True,
            username="superuser",
            password="testtest2",
            email="test@example.com",
            first_name="Test",
            last_name="Selenium",
            partner=unicef_hq,
        )
    RoleAssignment.objects.get_or_create(
        user=user,
        role=Role.objects.get(name="Role"),
        business_area=business_area,
    )

    for partner in Partner.objects.exclude(name__in=["UNICEF", settings.DEFAULT_EMPTY_PARTNER]):
        partner.allowed_business_areas.add(business_area)
        role = RoleFactory(name=f"Role for {partner.name}")
        partner_role_assignmnet, _ = RoleAssignment.objects.get_or_create(
            business_area=business_area,
            partner=partner,
            role=role,
        )

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
            "type": DataCollectingType.Type.SOCIAL,
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
        data_collecting_type, _ = DataCollectingType.objects.get_or_create(
            label=dct["label"],
            code=dct["code"],
            description=dct["description"],
            active=dct["active"],
            type=dct["type"],
        )
        data_collecting_type.limit_to.add(business_area)
        data_collecting_type.save()
    partner_role_assignment, _ = RoleAssignment.objects.get_or_create(
        business_area=business_area, partner=partner, role=role
    )

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


# Global variable to track the current test item
_current_test_item = None


# set up a hook to be able to check if a test has failed
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: Item, call: CallInfo[None]) -> None:
    global _current_test_item
    _current_test_item = item

    outcome = yield
    report = outcome.get_result()
    setattr(item, "rep_" + report.when, report)

    if report.when == "call" and report.failed:
        extra = getattr(report, "extra", [])
        item._html_extra_list = extra
        report.extra = extra


@pytest.fixture(autouse=True)
def test_failed_check(request: FixtureRequest, browser: Chrome) -> None:
    yield
    if request.node.rep_setup.failed:
        pass
    elif request.node.rep_setup.passed and request.node.rep_call.failed:
        screenshot(browser, request.node.nodeid)


def attach(data=None, path=None, name="attachment", mime_type=None):
    """Drop-in replacement for pytest_html_reporter's attach()"""
    global _current_test_item
    item = _current_test_item
    if item is None or not hasattr(item, "_html_extra_list"):
        return

    extra_list = item._html_extra_list
    if path:
        extra_list.append(extras.file(path, name=name, mime_type=mime_type))
    elif isinstance(data, bytes):
        extra_list.append(extras.image(data, name=name))
    else:
        extra_list.append(extras.text(str(data), name=name))


# make a screenshot with a name of the test, date and time
def screenshot(driver: Chrome, node_id: str) -> None:
    SCREENSHOT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    file_name = f"{node_id.split('::')[-1]}_{datetime.today().strftime('%Y-%m-%d_%H.%M')}.png".replace(
        "/", "_"
    ).replace("::", "__")
    file_path = SCREENSHOT_DIRECTORY / file_name
    driver.get_screenshot_as_file(str(file_path))
    attach(data=driver.get_screenshot_as_png())


@pytest.fixture(scope="session", autouse=True)
def register_custom_sql_signal() -> None:
    from django.db import connections
    from django.db.migrations.loader import MigrationLoader
    from django.db.models.signals import post_migrate, pre_migrate

    orig = getattr(settings, "MIGRATION_MODULES", None)
    settings.MIGRATION_MODULES = {}

    loader = MigrationLoader(None, load=False)
    loader.load_disk()
    all_migrations = loader.disk_migrations
    if orig is not None:
        settings.MIGRATION_MODULES = orig
    apps = set()
    all_sqls = []
    for (app_label, _), migration in all_migrations.items():
        apps.add(app_label)

        for operation in migration.operations:
            from django.db.migrations.operations.special import RunSQL

            if isinstance(operation, RunSQL):
                sql_statements = operation.sql if isinstance(operation.sql, (list, tuple)) else [operation.sql]
                for stmt in sql_statements:
                    all_sqls.append(stmt)  # noqa

    def pre_migration_custom_sql(
        sender: Any,
        app_config: Any,
        verbosity: Any,
        interactive: Any,
        using: Any,
        **kwargs: Any,
    ) -> None:
        filename = settings.TESTS_ROOT + "/../../development_tools/db/premigrations.sql"
        with open(filename, "r") as file:
            pre_sql = file.read()
        conn = connections[using]
        conn.cursor().execute(pre_sql)

    def post_migration_custom_sql(
        sender: Any,
        app_config: Any,
        verbosity: Any,
        interactive: Any,
        using: Any,
        **kwargs: Any,
    ) -> None:
        app_label = app_config.label
        if app_label not in apps:
            return
        apps.remove(app_label)
        if apps:
            return
        conn = connections[using]
        for stmt in all_sqls:
            conn.cursor().execute(stmt)

    pre_migrate.connect(
        pre_migration_custom_sql,
        dispatch_uid="tests.pre_migrationc_custom_sql",
        weak=False,
    )
    post_migrate.connect(
        post_migration_custom_sql,
        dispatch_uid="tests.post_migration_custom_sql",
        weak=False,
    )
