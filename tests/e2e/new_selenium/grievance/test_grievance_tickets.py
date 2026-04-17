import pytest

from extras.test_utils.selenium import HopeTestBrowser
from hope.models import Program

pytestmark = pytest.mark.django_db()


def test_create_new_ticket_referral(browser: HopeTestBrowser, social_worker_program: Program) -> None:
    browser.login()

    browser.click('a[data-cy="nav-Grievance"]')
    browser.wait_for_text("Grievance Tickets", 'h5[data-cy="page-header-title"]')

    browser.click('a[data-cy="button-new-ticket"]')
    browser.click('[data-cy="select-category"]')
    browser.select_option_by_name("Referral")
    browser.click('button[data-cy="button-submit"]')

    browser.wait_for_ready_state_complete()
    browser.wait_for_element_visible('button[data-cy="look-up-household"]')
    browser.click('button[data-cy="look-up-household"]')
    browser.assert_text("No results", '[data-cy="table-row"]')

    browser.click('button[data-cy="button-submit"]')
    browser.wait_for_ready_state_complete()
    browser.click('input[name="consent"]')
    browser.click('button[data-cy="button-submit"]')
    browser.type('textarea[name="description"]', "Happy path test 1234!")
    browser.click('button[data-cy="button-submit"]')

    browser.assert_text("Happy path test 1234!", 'div[data-cy="label-Description"]')
    browser.assert_text("Referral", 'div[data-cy="label-Category"]')
    browser.assert_text("New", 'div[data-cy="label-Status"]')
    browser.assert_text("Not set", 'div[data-cy="label-Priority"]')
    browser.assert_text("Not set", 'div[data-cy="label-Urgency"]')
