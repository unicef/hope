import pytest

from extras.test_utils.selenium import HopeTestBrowser
from hope.models import PaymentPlan

pytestmark = pytest.mark.django_db()


def _open_payment_plan(browser: HopeTestBrowser, payment_plan: PaymentPlan) -> None:
    program = payment_plan.program_cycle.program
    url = f"/{payment_plan.business_area.slug}/programs/{program.code}/payment-module/payment-plans/{payment_plan.id}"
    browser.open(url)
    browser.wait_for_element_visible('div[data-cy="status-container"]')


def test_close_payment_plan_flow(
    login: HopeTestBrowser,
    finished_payment_plan: PaymentPlan,
) -> None:
    _open_payment_plan(login, finished_payment_plan)
    login.assert_text("FINISHED", 'div[data-cy="status-container"]')

    login.wait_for_element_clickable('button[data-cy="button-set-ready-for-closure"]').click()
    login.wait_for_text("READY FOR CLOSURE", 'div[data-cy="status-container"]')

    login.wait_for_element_clickable('button[data-cy="button-close"]').click()
    login.wait_for_element_visible('button[data-cy="button-close-payment-plan"]')

    # No payment verification was carried out, so a justification comment is mandatory.
    login.type('textarea[data-cy="input-comment"]', "Closed without verification for e2e test.")
    login.click('button[data-cy="button-close-payment-plan"]')

    login.wait_for_text("CLOSED", 'div[data-cy="status-container"]')


def test_send_back_to_finished(
    login: HopeTestBrowser,
    finished_payment_plan: PaymentPlan,
) -> None:
    _open_payment_plan(login, finished_payment_plan)
    login.assert_text("FINISHED", 'div[data-cy="status-container"]')

    login.wait_for_element_clickable('button[data-cy="button-set-ready-for-closure"]').click()
    login.wait_for_text("READY FOR CLOSURE", 'div[data-cy="status-container"]')

    login.wait_for_element_clickable('button[data-cy="button-send-back"]').click()
    login.wait_for_text("FINISHED", 'div[data-cy="status-container"]')
    login.wait_for_element_visible('button[data-cy="button-set-ready-for-closure"]')


def test_close_requires_comment_when_no_verification(
    login: HopeTestBrowser,
    ready_for_closure_payment_plan: PaymentPlan,
) -> None:
    _open_payment_plan(login, ready_for_closure_payment_plan)
    login.wait_for_element_clickable('button[data-cy="button-close"]').click()
    close_btn = login.wait_for_element_visible('button[data-cy="button-close-payment-plan"]')
    assert not close_btn.is_enabled()
    login.type('textarea[name="comment"]', "Verified manually")
    assert login.find_element('button[data-cy="button-close-payment-plan"]').is_enabled()


def test_finance_closure_card_shows_closed_by(
    login: HopeTestBrowser,
    closed_payment_plan: PaymentPlan,
) -> None:
    _open_payment_plan(login, closed_payment_plan)
    login.wait_for_text("CLOSED", 'div[data-cy="status-container"]')
    login.assert_text("Test Selenium", 'div[data-cy="finance-closure-card"]')
