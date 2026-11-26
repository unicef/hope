from pathlib import Path

import pytest
from selenium.webdriver.support.ui import Select

from e2e.new_selenium.conftest import grant_permission
from extras.test_utils.selenium import HopeTestBrowser
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, Household, Individual, Program, RegistrationDataImport, User

from .conftest import AFGHANISTAN_PROGRAM_NAME, GENERIC_IMPORT_URL, SOMALIA_PROGRAM_NAME

pytestmark = pytest.mark.django_db()

BUSINESS_AREA_SELECT = "#id_business_area"
PROGRAM_SELECT = "#id_program"
FILE_INPUT = "#id_file"
FILE_NAME_DISPLAY = "#file-name-display"
SUBMIT_BUTTON = "button.submit-button"
TITLE = "h1.generic-import-title"

SOMALIA_FILE_NAME = "e2e_generic_import_somalia.xlsx"
INVALID_FILE_NAME = "e2e_generic_import_invalid.xlsx"

# Selenium cannot drag a file in from the desktop, so the drop event is built in the page.
DROP_FILE_JS = """
const dataTransfer = new DataTransfer();
dataTransfer.items.add(new File(["content"], arguments[1]));
arguments[0].dispatchEvent(new DragEvent("drop", {dataTransfer, bubbles: true, cancelable: true}));
"""

# Keeps the upload request waiting until the test releases it, so the uploading state can be checked.
HOLD_FETCH_JS = """
const originalFetch = window.fetch;
const released = new Promise(resolve => { window.releaseFetch = resolve; });
window.fetch = async (...args) => { await released; return originalFetch(...args); };
"""


def helper_file(name: str) -> str:
    return f"{pytest.SELENIUM_PATH}/helpers/{name}"


def option_labels(browser: HopeTestBrowser, selector: str) -> list[str]:
    return [option.text for option in Select(browser.find_element(selector)).options]


def selected_label(browser: HopeTestBrowser, selector: str) -> str:
    return Select(browser.find_element(selector)).first_selected_option.text


def select_business_area_and_program(browser: HopeTestBrowser, business_area: str, program: str) -> None:
    browser.select_option_by_text(BUSINESS_AREA_SELECT, business_area)
    browser.wait_for_text(program, PROGRAM_SELECT)
    browser.select_option_by_text(PROGRAM_SELECT, program)


def submit(browser: HopeTestBrowser) -> None:
    # browser.click() runs scripts after the click, and they dismiss an alert that opens quickly.
    browser.wait_for_element_clickable(SUBMIT_BUTTON).click()


def test_business_area_is_required(login: HopeTestBrowser, somalia_business_area: BusinessArea) -> None:
    login.open(GENERIC_IMPORT_URL)

    login.assert_exact_text("Generic Import - Upload File", TITLE)
    login.assert_exact_text("Business Area *", 'label[for="id_business_area"]')
    assert option_labels(login, BUSINESS_AREA_SELECT)[0] == "Select Business Area"
    assert sorted(option_labels(login, BUSINESS_AREA_SELECT)[1:]) == ["Afghanistan", "Somalia"]
    assert login.get_attribute(BUSINESS_AREA_SELECT, "required") == "true"


def test_program_select_disabled_until_business_area_selected(
    login: HopeTestBrowser, somalia_business_area: BusinessArea, afghanistan_program: Program
) -> None:
    login.open(GENERIC_IMPORT_URL)

    assert selected_label(login, BUSINESS_AREA_SELECT) == "Select Business Area"
    assert not login.is_element_enabled(PROGRAM_SELECT)
    assert selected_label(login, PROGRAM_SELECT) == "First select a Business Area"

    login.select_option_by_text(BUSINESS_AREA_SELECT, "Afghanistan")
    login.wait_for_text(AFGHANISTAN_PROGRAM_NAME, PROGRAM_SELECT)
    assert login.is_element_enabled(PROGRAM_SELECT)


def test_file_upload_field(login: HopeTestBrowser) -> None:
    login.open(GENERIC_IMPORT_URL)

    login.assert_element_present(FILE_INPUT)
    assert login.get_attribute(FILE_INPUT, "accept") == ".xlsx,.xls"
    login.assert_element_visible(".file-upload-label")
    login.assert_exact_text("Click to upload or drag and drop", ".file-upload-text .main-text")
    login.assert_exact_text("Excel files (.xlsx, .xls) - Max 50 MB", ".file-upload-text .sub-text")
    login.assert_element_present(FILE_NAME_DISPLAY)
    login.assert_element_not_visible(FILE_NAME_DISPLAY)


def test_invalid_file_extension_is_rejected(
    login: HopeTestBrowser,
    somalia_business_area: BusinessArea,
    afghanistan_program: Program,
    invalid_csv_file: Path,
) -> None:
    login.open(GENERIC_IMPORT_URL)
    select_business_area_and_program(login, "Afghanistan", AFGHANISTAN_PROGRAM_NAME)
    login.choose_file(FILE_INPUT, str(invalid_csv_file))
    submit(login)

    alert_text = login.wait_for_and_accept_alert(timeout=30)
    assert alert_text == "Upload failed: Only Excel files (.xlsx, .xls) are allowed."
    assert not RegistrationDataImport.objects.filter(program=afghanistan_program).exists()


def test_programs_load_after_selecting_business_area(
    login: HopeTestBrowser, somalia_program: Program, afghanistan_program: Program
) -> None:
    login.open(GENERIC_IMPORT_URL)
    assert not login.is_element_enabled(PROGRAM_SELECT)

    login.select_option_by_text(BUSINESS_AREA_SELECT, "Afghanistan")
    login.wait_for_text(AFGHANISTAN_PROGRAM_NAME, PROGRAM_SELECT)

    assert login.is_element_enabled(PROGRAM_SELECT)
    assert option_labels(login, PROGRAM_SELECT) == ["Select Program", AFGHANISTAN_PROGRAM_NAME]


def test_business_area_change_resets_program(
    login: HopeTestBrowser, somalia_program: Program, afghanistan_program: Program
) -> None:
    login.open(GENERIC_IMPORT_URL)
    select_business_area_and_program(login, "Afghanistan", AFGHANISTAN_PROGRAM_NAME)
    assert selected_label(login, PROGRAM_SELECT) == AFGHANISTAN_PROGRAM_NAME

    login.select_option_by_text(BUSINESS_AREA_SELECT, "Somalia")
    login.wait_for_text(SOMALIA_PROGRAM_NAME, PROGRAM_SELECT)

    assert selected_label(login, PROGRAM_SELECT) == "Select Program"
    assert option_labels(login, PROGRAM_SELECT) == ["Select Program", SOMALIA_PROGRAM_NAME]


def test_drag_and_drop_file_upload(login: HopeTestBrowser) -> None:
    login.open(GENERIC_IMPORT_URL)

    login.execute_script(DROP_FILE_JS, login.find_element(".file-upload-label"), SOMALIA_FILE_NAME)

    login.wait_for_text(f"Selected file: {SOMALIA_FILE_NAME} (7 Bytes)", FILE_NAME_DISPLAY)
    assert login.execute_script(f"return document.querySelector('{FILE_INPUT}').files[0].name") == SOMALIA_FILE_NAME


@pytest.mark.parametrize(
    ("selector", "expected_options"),
    [
        pytest.param(BUSINESS_AREA_SELECT, ["Select Business Area", "Afghanistan"], id="business-area"),
        pytest.param(PROGRAM_SELECT, ["Select Program", AFGHANISTAN_PROGRAM_NAME], id="program"),
    ],
)
def test_single_option_is_preselected(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    afghanistan_program: Program,
    somalia_program: Program,
    selector: str,
    expected_options: list[str],
) -> None:
    with grant_permission(user_with_no_permissions, business_area, Permissions.GENERIC_IMPORT_DATA):
        browser.login(username="noperm_user", wait_for_drawer=False)
        browser.open(GENERIC_IMPORT_URL)

        assert option_labels(browser, selector) == expected_options
        assert selected_label(browser, selector) == expected_options[1]
        assert browser.is_element_enabled(selector)


def test_user_without_generic_import_permission_is_denied(
    browser: HopeTestBrowser, user_with_no_permissions: User, business_area: BusinessArea
) -> None:
    other_permissions = set(Permissions) - {Permissions.GENERIC_IMPORT_DATA}
    with grant_permission(user_with_no_permissions, business_area, *other_permissions):
        browser.login(username="noperm_user", wait_for_drawer=False)
        browser.open(GENERIC_IMPORT_URL)

        browser.wait_for_text("Permission denied", "body")
        browser.assert_text("Required permission: GENERIC_IMPORT_DATA", "body")
        assert "403" in browser.get_title()
        browser.assert_element_absent("#generic-import-form")


def test_import_with_missing_columns_imports_nothing(login: HopeTestBrowser, somalia_program: Program) -> None:
    login.open(GENERIC_IMPORT_URL)
    select_business_area_and_program(login, "Somalia", SOMALIA_PROGRAM_NAME)
    login.choose_file(FILE_INPUT, helper_file(INVALID_FILE_NAME))
    login.wait_for_text(INVALID_FILE_NAME, FILE_NAME_DISPLAY)
    submit(login)

    alert_text = login.wait_for_and_accept_alert(timeout=60)
    assert "Generic Import" in alert_text
    rdi = RegistrationDataImport.objects.get(program=somalia_program, name__contains="Generic Import")
    assert rdi.name in alert_text
    # The parser's missing column errors are not reported, so the empty import ends as IN_REVIEW.
    assert rdi.status == RegistrationDataImport.IN_REVIEW, rdi.error_message
    assert (rdi.number_of_households, rdi.number_of_individuals) == (0, 0)
    assert not Household.all_merge_status_objects.filter(registration_data_import=rdi).exists()
    assert not Individual.all_merge_status_objects.filter(registration_data_import=rdi).exists()


def test_file_size_is_displayed(login: HopeTestBrowser) -> None:
    login.open(GENERIC_IMPORT_URL)

    login.choose_file(FILE_INPUT, helper_file(SOMALIA_FILE_NAME))

    size_kb = round(Path(helper_file(SOMALIA_FILE_NAME)).stat().st_size / 1024, 2)
    login.wait_for_exact_text(f"Selected file: {SOMALIA_FILE_NAME} ({size_kb} KB)", FILE_NAME_DISPLAY)


def test_submit_button_state_during_upload(login: HopeTestBrowser, somalia_program: Program) -> None:
    login.open(GENERIC_IMPORT_URL)
    select_business_area_and_program(login, "Somalia", SOMALIA_PROGRAM_NAME)
    login.choose_file(FILE_INPUT, helper_file(SOMALIA_FILE_NAME))
    login.assert_exact_text("Upload and Process", SUBMIT_BUTTON)
    assert login.is_element_enabled(SUBMIT_BUTTON)

    login.execute_script(HOLD_FETCH_JS)
    login.click(SUBMIT_BUTTON)
    login.wait_for_exact_text("Uploading...", SUBMIT_BUTTON)
    assert not login.is_element_enabled(SUBMIT_BUTTON)

    login.execute_script("window.releaseFetch()")
    alert_text = login.wait_for_and_accept_alert(timeout=60)
    assert "File uploaded successfully!" in alert_text
    login.wait_for_exact_text("Upload and Process", SUBMIT_BUTTON)
    login.wait_for_element_clickable(SUBMIT_BUTTON)
