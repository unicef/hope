import pytest

from e2e.new_selenium.people.conftest import BIRTH_DATE, people_url
from e2e.new_selenium.programme_population.conftest import assert_texts
from extras.test_utils.selenium import HopeTestBrowser, ui_date
from hope.apps.household.const import FEMALE
from hope.models import Individual, Payment, Program

pytestmark = pytest.mark.django_db()

PAGE_TITLE = 'h5[data-cy="page-header-title"]'
TABLE_TITLE = 'h6[data-cy="table-title"]'
TABLE_PAGINATION = 'div[data-cy="table-pagination"]'
PERSON_ROW = 'tr[data-cy="individual-table-row"]'
PAYMENT_ROW = 'tr[role="checkbox"]'
BUTTON_SUBMIT = 'button[data-cy="button-submit"]'
BUTTON_CONFIRM = 'button[data-cy="button-confirm"]'
REQUESTED_CHANGE = 'span[data-cy="checkbox-requested-data-change"]'
LIST_COLUMNS = {
    'th[data-cy="individual-id"]': "Individual ID",
    'th[data-cy="individual-name"]': "Individual",
    # the Type and Age columns share one data-cy
    'th[data-cy="individual-age"]:nth-child(5)': "Type",
    'th[data-cy="individual-age"]:nth-child(6)': "Age",
    'th[data-cy="individual-sex"]': "Gender",
    'th[data-cy="individual-location"]': "Administrative Level 2",
}


def label(name: str) -> str:
    return f'div[data-cy="label-{name}"]'


DETAILS_LABELS = {
    "Full Name": "Stacey Freeman",
    "Given Name": "Stacey",
    "Middle Name": "-",
    "Family Name": "Freeman",
    "Gender": "Male",
    "Age": "40",
    "Date of Birth": ui_date(BIRTH_DATE),
    "Estimated Date of Birth": "No",
    "Marital Status": "Married",
    "Work Status": "Not provided",
    "Pregnant": "No",
    "Role": "Primary collector",
    "Preferred language": "-",
    "Residence Status": "Non-displaced | Host",
    "Type": "Beneficiary",
    "Country": "-",
    "Country of Origin": "-",
    "Address": "-",
    "Vilage": "Test Village",
    "Zip Code": "-",
    "Administrative Level 1": "-",
    "Administrative Level 2": "-",
    "Administrative Level 3": "-",
    "Administrative Level 4": "-",
    "Geolocation": "-",
    "Observed disabilities": "Difficulty seeing (even if wearing glasses)",
    "Seeing disability severity": "None",
    "Hearing disability severity": "None",
    "Physical disability severity": "None",
    "Remembering or concentrating disability severity": "None",
    "Communicating disability severity": "None",
    "Disability": "Not Disabled",
    "issued": "-",
    "Email": "stacey@example.com",
    "Phone Number": "-",
    "Alternative Phone Number": "-",
    "Date of last screening against sanctions list": "-",
    "Linked Grievances": "-",
}
DETAILS = {label(name): value for name, value in DETAILS_LABELS.items()}


def js_click(browser: HopeTestBrowser, selector: str) -> None:
    # toolbar buttons sit under the sticky page header in headless Chrome
    browser.wait_for_element_clickable(selector)
    browser.js_click(selector)


def test_people_list_is_empty_without_people(program: Program, login: HopeTestBrowser) -> None:
    login.open(people_url(program))

    login.assert_text("People", TABLE_TITLE)
    login.assert_text("0–0 of 0", TABLE_PAGINATION)
    assert_texts(login, LIST_COLUMNS)


def test_person_details_shows_person(person: Individual, program: Program, login: HopeTestBrowser) -> None:
    login.open(people_url(program))
    login.assert_text("1–1 of 1", TABLE_PAGINATION)
    login.assert_text("Stacey Freeman", PERSON_ROW)

    login.click(PERSON_ROW)

    login.assert_text(f"Individual ID: {person.unicef_id}", PAGE_TITLE)
    assert_texts(login, DETAILS)
    rdi = person.registration_data_import
    login.assert_text(program.data_collecting_type.label, label("Data Collecting Type"))
    login.assert_text("0–0 of 0", TABLE_PAGINATION)
    login.assert_text(rdi.name, label("Import name"))
    login.assert_text(rdi.imported_by.email, label("User name"))
    login.assert_text(ui_date(person.household.last_registration_date), label("Registration Date"))
    login.wait_for_element_visible(label("Source"))


def test_person_details_shows_payment(payment: Payment, program: Program, login: HopeTestBrowser) -> None:
    login.open(people_url(program))

    login.click(PERSON_ROW)

    login.assert_text("21.36", label("Total Cash Received"))
    login.assert_text(payment.unicef_id, PAYMENT_ROW)
    login.assert_text("21.36", PAYMENT_ROW)
    login.assert_text("DELIVERED FULLY", PAYMENT_ROW)
    assert len(login.find_elements(PAYMENT_ROW)) == 1


@pytest.mark.parametrize(
    ("category", "issue_type"),
    [pytest.param("Data Change", "Member Data Update", id="data-change-member-data-update")],
)
def test_person_data_updated_after_grievance_ticket_processed(
    category: str, issue_type: str, person: Individual, program: Program, login: HopeTestBrowser
) -> None:
    login.open(f"/{program.business_area.slug}/programs/all/grievance/tickets/user-generated")
    login.click('a[data-cy="button-new-ticket"]')
    login.select_dropdown_option("category", category)
    login.select_dropdown_option("issueType", issue_type)
    login.click(BUTTON_SUBMIT)
    login.click('button[data-cy="look-up-individual"]')
    login.click(PERSON_ROW)
    login.click(BUTTON_SUBMIT)
    login.check_checkbox('[data-cy="input-consent"]')
    login.click(BUTTON_SUBMIT)

    login.type('textarea[name="description"]', "Update person - TEST")
    login.click('button[data-cy="button-add-new-field"]')
    login.click('div[data-cy="select-individualDataUpdateFields[0].fieldName"]')
    login.select_listbox_element("Gender")
    login.click('div[data-cy="input-individual-data-Gender"]')
    login.select_listbox_element("Female")
    login.click('div[data-cy="select-individualDataUpdateFields[1].fieldName"]')
    login.select_listbox_element("Preferred language")
    login.click('div[data-cy="input-individual-data-Preferred language"]')
    login.select_listbox_element("English | English")
    login.click(BUTTON_SUBMIT)

    login.wait_for_element_visible(REQUESTED_CHANGE, timeout=60)
    gender_row = 'tr[role="checkbox"]:nth-child(1)'
    language_row = 'tr[role="checkbox"]:nth-child(2)'
    assert_texts(login, {gender_row: "Gender", language_row: "Preferred Language"})
    assert_texts(login, {gender_row: "Female", language_row: "English"})

    js_click(login, 'button[data-cy="button-assign"]')
    js_click(login, 'button[data-cy="button-confirm-assign"]')
    js_click(login, 'button[data-cy="button-set-to-in-progress"]')
    js_click(login, 'button[data-cy="button-send-for-approval"]')
    login.wait_for_element_clickable('button[data-cy="button-close-ticket"]')
    login.check_checkbox(f"{gender_row} {REQUESTED_CHANGE}")
    login.check_checkbox(f"{language_row} {REQUESTED_CHANGE}")
    js_click(login, 'button[data-cy="button-approve"]')
    js_click(login, BUTTON_CONFIRM)
    login.wait_for_element_absent(BUTTON_CONFIRM)
    js_click(login, 'button[data-cy="button-close-ticket"]')
    js_click(login, BUTTON_CONFIRM)
    login.wait_for_text("Closed", label("Status"), timeout=60)

    login.open(people_url(program))
    login.click(PERSON_ROW)
    login.assert_text("Female", label("Gender"))
    login.assert_text("en-us", label("Preferred language"))
    person.refresh_from_db()
    assert person.sex == FEMALE
    assert person.preferred_language == "en-us"
