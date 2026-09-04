import pytest

from extras.test_utils.selenium import HopeTestBrowser
from hope.models import Household, Individual, Program

pytestmark = pytest.mark.django_db()

BUTTON_SUBMIT = 'button[data-cy="button-submit"]'
INPUT_FULL_NAME_LATIN = 'input[data-cy="input-individualData.fullNameLatin"]'


def _select_listbox(browser: HopeTestBrowser, field_name: str, option: str) -> None:
    # choice options here carry codes (MALE, YES) in data-cy, so pick by visible text
    browser.click(f'[data-cy="select-{field_name}"]')
    browser.select_listbox_element(option)


def _js_click(browser: HopeTestBrowser, selector: str) -> None:
    # toolbar buttons sit under the sticky page header in headless Chrome
    browser.wait_for_element_visible(selector)
    browser.js_click(selector)


def test_add_individual_stores_latin_name_as_provided(
    login: HopeTestBrowser,
    household_update_program: Program,
    household_for_update: Household,
) -> None:
    program = household_update_program
    login.open(f"/{program.business_area.slug}/programs/{program.code}/grievance/tickets/user-generated")
    login.wait_for_text("Grievance Tickets", 'h5[data-cy="page-header-title"]', timeout=60)
    login.click('a[data-cy="button-new-ticket"]')
    login.select_dropdown_option("category", "Data Change")
    login.select_dropdown_option("issueType", "Add Individual")
    login.click(BUTTON_SUBMIT)
    login.wait_for_ready_state_complete()
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

    login.type(INPUT_FULL_NAME_LATIN, "Дмитро")
    login.click(BUTTON_SUBMIT)
    login.assert_text("Only ASCII letters, spaces, hyphens and apostrophes are allowed")

    login.set_value(INPUT_FULL_NAME_LATIN, "Dmytro Koval")
    login.click(BUTTON_SUBMIT)
    login.wait_for_element_visible('button[data-cy="button-assign-to-me"]', timeout=60)
    login.assert_text("Дмитро Коваль", 'div[data-cy="label-full name"]')

    _js_click(login, 'button[data-cy="button-assign-to-me"]')
    _js_click(login, 'button[data-cy="button-set-to-in-progress"]')
    _js_click(login, 'button[data-cy="button-send-for-approval"]')
    login.wait_for_element_clickable('button[data-cy="button-approve"]')
    _js_click(login, 'button[data-cy="button-approve"]')
    _js_click(login, 'button[data-cy="button-confirm"]')
    _js_click(login, 'button[data-cy="button-close-ticket"]')
    _js_click(login, 'button[data-cy="button-confirm"]')
    login.wait_for_text("Closed", 'div[data-cy="label-Status"]', timeout=60)

    added = Individual.objects.get(household=household_for_update, full_name="Дмитро Коваль")
    assert added.full_name_latin == "Dmytro Koval"
    login.open(f"/{program.business_area.slug}/programs/{program.code}/population/household/{household_for_update.pk}")
    login.assert_text("Дмитро Коваль")
    login.assert_text("Dmytro Koval")
