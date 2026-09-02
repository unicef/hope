import pytest

from extras.test_utils.selenium import HopeTestBrowser
from hope.models import Household, Individual, Program

pytestmark = pytest.mark.django_db()

CHECKBOX_TRANSLITERATE = '[data-cy="input-transliterateLatinNames"]'
BUTTON_SUBMIT = 'button[data-cy="button-submit"]'
FIRST_FIELD_NAME = "individualDataUpdateFields[0].fieldName"
FIRST_FIELD_VALUE = '[data-cy="input-individualDataUpdateFields[0].fieldValue"]'


@pytest.fixture
def cyrillic_head(household_for_update: Household) -> Individual:
    head = household_for_update.head_of_household
    head.given_name = "Олександр"
    head.family_name = "Шевченко"
    head.full_name = "Олександр Шевченко"
    head.set_names_latin()
    head.save()
    return head


def _open_new_data_change_ticket(browser: HopeTestBrowser, program: Program, issue_type: str) -> None:
    browser.open(f"/{program.business_area.slug}/programs/{program.code}/grievance/tickets/user-generated")
    browser.wait_for_text("Grievance Tickets", 'h5[data-cy="page-header-title"]', timeout=60)
    browser.click('a[data-cy="button-new-ticket"]')
    browser.select_dropdown_option("category", "Data Change")
    browser.select_dropdown_option("issueType", issue_type)
    browser.click(BUTTON_SUBMIT)
    browser.wait_for_ready_state_complete()


def _pick_first_individual_and_consent(browser: HopeTestBrowser) -> None:
    browser.wait_for_element_visible('button[data-cy="look-up-individual"]').click()
    browser.wait_for_element_visible('tr[data-cy="individual-table-row"]').click()
    browser.click(BUTTON_SUBMIT)
    browser.wait_for_ready_state_complete()
    browser.click('[data-cy="input-consent"]')
    browser.click(BUTTON_SUBMIT)
    browser.wait_for_element_visible(f'[data-cy="select-{FIRST_FIELD_NAME}"]')


def _select_listbox(browser: HopeTestBrowser, field_name: str, option: str) -> None:
    # choice options here carry codes (MALE, YES) in data-cy, so pick by visible text
    browser.click(f'[data-cy="select-{field_name}"]')
    browser.select_listbox_element(option)


def _js_click(browser: HopeTestBrowser, selector: str) -> None:
    # toolbar buttons sit under the sticky page header in headless Chrome
    browser.wait_for_element_visible(selector)
    browser.js_click(selector)


def _send_for_approval(browser: HopeTestBrowser) -> None:
    _js_click(browser, 'button[data-cy="button-assign-to-me"]')
    _js_click(browser, 'button[data-cy="button-set-to-in-progress"]')
    _js_click(browser, 'button[data-cy="button-send-for-approval"]')
    browser.wait_for_element_clickable('button[data-cy="button-approve"]')


def _approve_and_close(browser: HopeTestBrowser) -> None:
    _js_click(browser, 'button[data-cy="button-approve"]')
    _js_click(browser, 'button[data-cy="button-confirm"]')
    _js_click(browser, 'button[data-cy="button-close-ticket"]')
    _js_click(browser, 'button[data-cy="button-confirm"]')
    browser.wait_for_text("Closed", 'div[data-cy="label-Status"]', timeout=60)


@pytest.mark.usefixtures("cyrillic_head")
def test_transliteration_checkbox_hidden_until_a_name_field_is_selected(
    login: HopeTestBrowser,
    household_update_program: Program,
) -> None:
    _open_new_data_change_ticket(login, household_update_program, "Individual Data Update")
    _pick_first_individual_and_consent(login)

    login.select_dropdown_option(FIRST_FIELD_NAME, "Phone number")
    login.assert_element_absent(CHECKBOX_TRANSLITERATE)

    login.click('button[data-cy="button-add-new-field"]')
    login.select_dropdown_option("individualDataUpdateFields[1].fieldName", "Given name")
    login.assert_element_visible(CHECKBOX_TRANSLITERATE)


def test_name_change_without_latin_requires_transliteration(
    login: HopeTestBrowser,
    household_update_program: Program,
    cyrillic_head: Individual,
) -> None:
    _open_new_data_change_ticket(login, household_update_program, "Individual Data Update")
    _pick_first_individual_and_consent(login)
    login.type('textarea[name="description"]', "Latin names via transliteration")

    login.select_dropdown_option(FIRST_FIELD_NAME, "Given name")
    login.type(FIRST_FIELD_VALUE, "Петро")
    login.click(CHECKBOX_TRANSLITERATE)  # default is on - turn it off
    login.click(BUTTON_SUBMIT)
    login.assert_text("Provide given_name_latin or enable automatic transliteration")

    login.click(CHECKBOX_TRANSLITERATE)
    login.click(BUTTON_SUBMIT)
    login.wait_for_element_visible('[data-cy="table-cell-new-value"]', timeout=60)
    login.assert_text("Петро")

    _send_for_approval(login)
    login.click('span[data-cy="checkbox-requested-data-change"]')
    _approve_and_close(login)

    program = household_update_program
    login.open(f"/{program.business_area.slug}/programs/{program.code}/population/individuals/{cyrillic_head.pk}")
    login.assert_text("Петро", 'div[data-cy="label-Given Name"]')
    login.assert_text("Petro", 'div[data-cy="label-Given Name"]')


def test_add_individual_with_transliteration_shows_latin_name_after_close(
    login: HopeTestBrowser,
    household_update_program: Program,
    household_for_update: Household,
) -> None:
    _open_new_data_change_ticket(login, household_update_program, "Add Individual")
    login.wait_for_element_visible('[data-cy="input-radio-household"]').click()
    login.click(BUTTON_SUBMIT)
    login.wait_for_ready_state_complete()
    login.click('[data-cy="input-consent"]')
    login.click(BUTTON_SUBMIT)

    login.type('textarea[name="description"]', "Add member with Cyrillic name")
    login.type('input[data-cy="input-individualData.fullName"]', "Дмитро Коваль")
    login.fill_date('input[name="individualData.birthDate"]', "1986-05-01")
    _select_listbox(login, "individualData.sex", "Male")
    _select_listbox(login, "individualData.estimatedBirthDate", "Yes")
    _select_listbox(login, "individualData.relationship", "Wife / Husband")
    login.assert_element_visible(CHECKBOX_TRANSLITERATE)
    login.click(BUTTON_SUBMIT)

    login.wait_for_element_visible('[data-cy="transliterate-latin-names-info"]', timeout=60)
    login.assert_text("Дмитро Коваль", 'div[data-cy="label-full name"]')

    _send_for_approval(login)
    _approve_and_close(login)

    program = household_update_program
    login.open(f"/{program.business_area.slug}/programs/{program.code}/population/household/{household_for_update.pk}")
    added = Individual.objects.get(household=household_for_update, full_name="Дмитро Коваль")
    login.assert_text("Дмитро Коваль")
    login.assert_text(added.full_name_latin)
