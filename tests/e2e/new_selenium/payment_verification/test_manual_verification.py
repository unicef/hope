from collections.abc import Callable
from decimal import Decimal
from functools import partial

import pytest

from e2e.new_selenium.payment_verification.conftest import (
    BUTTON_SUBMIT,
    DELIVERED_QUANTITY,
    PLAN_STATUS,
    RECORD_STATUS,
    activate_plan,
    verification_url,
)
from extras.test_utils.selenium import HopeTestBrowser
from hope.apps.grievance.models import GrievanceTicket
from hope.models import PaymentVerification

pytestmark = pytest.mark.django_db()

PAGE_HEADER_TITLE = 'h5[data-cy="page-header-title"]'
BUTTON_VERIFY = 'button[data-cy="button-ed-plan"]'
LABEL_STATUS = 'div[data-cy="label-STATUS"]'
INPUT_RECEIVED_AMOUNT = 'input[data-cy="input-receivedAmount"]'
TICKET_STATUS = 'div[data-cy="label-Status"]'


def _js_click(browser: HopeTestBrowser, selector: str) -> None:
    # toolbar buttons sit under the sticky page header in headless Chrome
    browser.wait_for_element_visible(selector)
    browser.js_click(selector)


def open_payment(browser: HopeTestBrowser, verification: PaymentVerification) -> None:
    browser.click(f'tr[role="checkbox"] a:contains("{verification.payment.unicef_id}")')
    browser.assert_text(f"Payment ID {verification.payment.unicef_id}", PAGE_HEADER_TITLE)


def mark_received(browser: HopeTestBrowser, amount: Decimal) -> None:
    browser.type(INPUT_RECEIVED_AMOUNT, str(amount))


def mark_not_received(browser: HopeTestBrowser) -> None:
    browser.click('[data-cy="choice-not-received"]')


def verify_payment(browser: HopeTestBrowser, fill_form: Callable[[HopeTestBrowser], None]) -> None:
    _js_click(browser, BUTTON_VERIFY)
    fill_form(browser)
    browser.click(BUTTON_SUBMIT)
    browser.wait_for_text("Payment has been verified.")


def test_payment_details_shows_payment_and_verification(
    login: HopeTestBrowser,
    manual_verification: PaymentVerification,
) -> None:
    payment = manual_verification.payment
    activate_plan(login, payment.parent)

    open_payment(login, manual_verification)

    login.assert_text("VERIFY", BUTTON_VERIFY)
    payment_status, verification_status = login.find_elements(LABEL_STATUS)
    assert payment_status.text.endswith("DELIVERED FULLY")
    assert verification_status.text.endswith("PENDING")
    login.assert_text("DELIVERED FULLY", 'div[data-cy="status-container"]')
    login.assert_text(payment.household.unicef_id, 'div[data-cy="label-Items Group ID"]')
    login.assert_text(payment.parent.name, 'div[data-cy="label-TARGET POPULATION"]')
    login.assert_text("Cash", 'div[data-cy="label-DISTRIBUTION MODALITY"]')
    login.assert_exact_text("-", 'div[data-cy="label-AMOUNT RECEIVED"]')
    login.assert_text("21.36", 'div[data-cy="label-ENTITLEMENT QUANTITY"]')
    login.assert_text("21.36", 'div[data-cy="label-DELIVERED QUANTITY"]')
    login.assert_text("PLN", 'div[data-cy="label-CURRENCY"]')
    login.assert_text("Cash", 'div[data-cy="label-DELIVERY TYPE"]')
    login.assert_text(payment.financial_service_provider.name, 'div[data-cy="label-FSP"]')


@pytest.mark.parametrize(
    ("fill_form", "status", "received_amount"),
    [
        pytest.param(
            partial(mark_received, amount=DELIVERED_QUANTITY),
            "RECEIVED",
            DELIVERED_QUANTITY,
            id="received-full-amount",
        ),
        pytest.param(
            partial(mark_received, amount=Decimal(100)),
            "RECEIVED WITH ISSUES",
            Decimal(100),
            id="received-other-amount",
        ),
        pytest.param(mark_not_received, "NOT RECEIVED", Decimal(0), id="not-received"),
    ],
)
def test_manual_verification_sets_payment_status(
    login: HopeTestBrowser,
    manual_verification: PaymentVerification,
    fill_form: Callable[[HopeTestBrowser], None],
    status: str,
    received_amount: Decimal,
) -> None:
    payment_plan = manual_verification.payment.parent
    activate_plan(login, payment_plan)
    open_payment(login, manual_verification)

    verify_payment(login, fill_form)

    login.wait_for_text("EDIT", BUTTON_VERIFY)
    assert login.find_elements(LABEL_STATUS)[1].text.endswith(status)
    login.click('div[data-cy="arrow_back"]')
    login.wait_for_text(status, RECORD_STATUS)
    login.assert_exact_text(status, RECORD_STATUS)
    manual_verification.refresh_from_db()
    assert manual_verification.status == status.replace(" ", "_")
    assert manual_verification.received_amount == received_amount


def test_grievance_ticket_for_partially_received_payment_updates_verification(
    login: HopeTestBrowser,
    manual_verification: PaymentVerification,
) -> None:
    payment_plan = manual_verification.payment.parent
    activate_plan(login, payment_plan)
    open_payment(login, manual_verification)
    verify_payment(login, partial(mark_received, amount=DELIVERED_QUANTITY - 1))
    login.click('div[data-cy="arrow_back"]')
    login.wait_for_text("RECEIVED WITH ISSUES", RECORD_STATUS)

    _js_click(login, BUTTON_VERIFY)
    login.assert_text("Finish Verification Plan", 'div[role="dialog"]')
    login.click(BUTTON_SUBMIT)
    login.wait_for_text("FINISHED", PLAN_STATUS)

    login.open_nav_section("Grievance")
    login.click('a[data-cy="nav-Grievance Tickets"]')
    login.wait_for_element_clickable('button[data-cy="tab-SYSTEM-GENERATED"]').click()
    ticket = GrievanceTicket.objects.get(payment_verification_ticket_details__payment_verification=manual_verification)
    login.wait_for_text(ticket.unicef_id, 'tr[role="checkbox"]')
    assert len(login.find_elements('tr[role="checkbox"]')) == 1
    login.click('tr[role="checkbox"]')
    login.wait_for_text(ticket.unicef_id, PAGE_HEADER_TITLE)

    _js_click(login, 'button[data-cy="button-assign"]')
    _js_click(login, 'button[data-cy="button-confirm-assign"]')
    _js_click(login, 'button[data-cy="button-set-to-in-progress"]')
    login.wait_for_element_clickable('[data-cy="grievance-verify"]').click()
    login.type('[data-cy="input-newReceivedAmount"]', str(DELIVERED_QUANTITY))
    login.click(BUTTON_SUBMIT)
    login.wait_for_text("Payment has been verified.")
    _js_click(login, 'button[data-cy="button-send-for-approval"]')
    login.wait_for_element_clickable('[data-cy="grievance-approve"]').click()
    login.wait_for_element_clickable('button[data-cy="button-confirm"]').click()
    login.wait_for_text("Changes Approved")
    _js_click(login, 'button[data-cy="button-close-ticket"]')
    _js_click(login, 'button[data-cy="button-confirm"]')
    # Closing the ticket is what sets the verification to RECEIVED.
    login.wait_for_text("Closed", TICKET_STATUS, timeout=60)

    login.open(verification_url(payment_plan))
    login.wait_for_text("RECEIVED", RECORD_STATUS)
    login.assert_exact_text("RECEIVED", RECORD_STATUS)
    manual_verification.refresh_from_db()
    assert manual_verification.status == PaymentVerification.STATUS_RECEIVED
    assert manual_verification.received_amount == DELIVERED_QUANTITY
