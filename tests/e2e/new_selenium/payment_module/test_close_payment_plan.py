import pytest

from extras.test_utils.selenium import HopeTestBrowser
from hope.models import PaymentPlanGroup

pytestmark = pytest.mark.django_db()

STATUS = 'div[data-cy="group-status"]'


def _open_group(browser: HopeTestBrowser, group: PaymentPlanGroup) -> None:
    program = group.cycle.program
    browser.open(f"/{program.business_area.slug}/programs/{program.code}/payment-module/groups/{group.id}")
    browser.wait_for_element_visible(STATUS)


def test_close_payment_plan_group_flow(login: HopeTestBrowser, finished_group: PaymentPlanGroup) -> None:
    _open_group(login, finished_group)
    login.assert_text("FINISHED", STATUS)

    login.wait_for_element_clickable('button[data-cy="button-set-ready-for-closure"]').click()
    login.wait_for_text("READY FOR CLOSURE", STATUS)

    login.wait_for_element_clickable('button[data-cy="button-close"]').click()
    close_button = login.wait_for_element_visible('button[data-cy="button-close-payment-plan-group"]')
    assert not close_button.is_enabled()

    # No payment verification was carried out, so a justification comment is mandatory.
    login.type('textarea[name="comment"]', "Closed without verification for e2e test.")
    login.click('button[data-cy="button-close-payment-plan-group"]')

    login.wait_for_text("CLOSED", STATUS)
    assert finished_group.payment_plans.get().status == "CLOSED"


def test_send_group_back_to_finished(login: HopeTestBrowser, finished_group: PaymentPlanGroup) -> None:
    _open_group(login, finished_group)

    login.wait_for_element_clickable('button[data-cy="button-set-ready-for-closure"]').click()
    login.wait_for_text("READY FOR CLOSURE", STATUS)

    login.wait_for_element_clickable('button[data-cy="button-send-back"]').click()
    login.wait_for_text("FINISHED", STATUS)
    login.wait_for_element_visible('button[data-cy="button-set-ready-for-closure"]')


def test_abort_and_reactivate_group(login: HopeTestBrowser, locked_group: PaymentPlanGroup) -> None:
    _open_group(login, locked_group)

    login.wait_for_element_clickable('button[data-cy="button-abort"]').click()
    login.type('textarea[name="comment"]', "Wrong cycle")
    login.click('button[data-cy="button-submit-abort"]')
    login.wait_for_text("ABORTED", STATUS)

    login.wait_for_element_clickable('button[data-cy="button-reactivate-payment-plan-group"]').click()
    login.wait_for_text("OPEN", STATUS)


def test_finance_closure_card_shows_closed_by(login: HopeTestBrowser, closed_group: PaymentPlanGroup) -> None:
    _open_group(login, closed_group)
    login.assert_text("CLOSED", STATUS)
    login.assert_text("Test Selenium", 'div[data-cy="finance-closure-card"]')
