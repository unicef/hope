import pytest

from extras.test_utils.selenium import HopeTestBrowser
from hope.models import Program

pytestmark = pytest.mark.django_db()

NAV_GRIEVANCE = 'a[data-cy="nav-Grievance"]'
HEADER_TITLE = 'h5[data-cy="page-header-title"]'
BTN_NEW_TICKET = 'a[data-cy="button-new-ticket"]'

SELECT_CATEGORY = 'div[data-cy="select-category"]'
BTN_SUBMIT = 'button[data-cy="button-submit"]'
LOOK_UP_HOUSEHOLD_TAB = 'button[data-cy="look-up-household"]'
TABLE_ROW = '[data-cy="table-row"]'
INPUT_CONSENT = 'span[data-cy="input-consent"]'
INPUT_DESCRIPTION = 'textarea[data-cy="input-description"]'

LABEL_DESCRIPTION = 'div[data-cy="label-Description"]'
LABEL_CATEGORY = 'div[data-cy="label-Category"]'
LABEL_STATUS = 'div[data-cy="label-Status"]'
LABEL_PRIORITY = 'div[data-cy="label-Priority"]'
LABEL_URGENCY = 'div[data-cy="label-Urgency"]'


def test_create_new_ticket_referral(browser: HopeTestBrowser, social_worker_program: Program) -> None:
    browser.login()

    browser.click(NAV_GRIEVANCE)
    browser.wait_for_text("Grievance Tickets", HEADER_TITLE)

    browser.click(BTN_NEW_TICKET)
    browser.click(SELECT_CATEGORY)
    browser.select_option_by_name("Referral")
    browser.click(BTN_SUBMIT)

    browser.wait_for_ready_state_complete()
    browser.wait_for_element_visible(LOOK_UP_HOUSEHOLD_TAB)
    browser.click(LOOK_UP_HOUSEHOLD_TAB)
    browser.assert_text("No results", TABLE_ROW)

    browser.click(BTN_SUBMIT)
    browser.wait_for_ready_state_complete()
    browser.click(INPUT_CONSENT)
    browser.click(BTN_SUBMIT)
    browser.type(INPUT_DESCRIPTION, "Happy path test 1234!")
    browser.click(BTN_SUBMIT)

    browser.assert_text("Happy path test 1234!", LABEL_DESCRIPTION)
    browser.assert_text("Referral", LABEL_CATEGORY)
    browser.assert_text("New", LABEL_STATUS)
    browser.assert_text("Not set", LABEL_PRIORITY)
    browser.assert_text("Not set", LABEL_URGENCY)
