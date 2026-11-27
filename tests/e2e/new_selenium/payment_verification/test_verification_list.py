from datetime import date, timedelta

import pytest

from e2e.new_selenium.payment_verification.conftest import PLAN_STATUS, PROGRAM_NAME
from extras.test_utils.selenium import HopeTestBrowser, ui_date
from hope.models import PaymentVerification

pytestmark = pytest.mark.django_db()

PAGE_HEADER_TITLE = 'h5[data-cy="page-header-title"]'
TABLE_PAGINATION = 'div[data-cy="table-pagination"]'
PLAN_ROW = 'tr[data-cy="cash-plan-table-row"]'
LIST_COLUMNS = [
    "Payment Plan ID",
    "Verification Status",
    "Total Amount",
    "Payment Disbursement Dates",
    "Programme Cycle Title",
    "Last Modified Date",
]


def open_verification_list(browser: HopeTestBrowser) -> None:
    browser.select_global_program(PROGRAM_NAME)
    browser.click('a[data-cy="nav-Payment Verification"]')
    browser.assert_text("Payment Verification", PAGE_HEADER_TITLE)


def test_verification_list_shows_payment_plan(
    login: HopeTestBrowser,
    manual_verification: PaymentVerification,
) -> None:
    payment_plan = manual_verification.payment.parent

    open_verification_list(login)

    login.assert_text("List of Payment Plans", 'h6[data-cy="table-title"]')
    header_texts = [header.text for header in login.find_elements("thead th")]
    assert header_texts == LIST_COLUMNS
    login.assert_text(payment_plan.unicef_id, PLAN_ROW)
    login.assert_text("PENDING", f'{PLAN_ROW} div[data-cy="status-container"]')
    login.assert_exact_text(payment_plan.program_cycle.title, 'td[data-cy="cycle-title"]')
    login.assert_text("Rows per page:", TABLE_PAGINATION)
    login.assert_exact_text("5", f"{TABLE_PAGINATION} .MuiTablePagination-select")
    login.assert_text("1–1 of 1", TABLE_PAGINATION)


def test_verification_details_shows_payment_plan_and_verification_plan(
    login: HopeTestBrowser,
    manual_verification: PaymentVerification,
) -> None:
    verification_plan = manual_verification.payment_verification_plan
    payment_plan = verification_plan.payment_plan

    open_verification_list(login)
    login.click(PLAN_ROW)

    login.assert_text(f"Payment Plan {payment_plan.unicef_id}", PAGE_HEADER_TITLE)
    login.assert_text("CREATE VERIFICATION PLAN", 'button[data-cy="button-new-plan"]')
    login.assert_text("Payment Plan Details", 'div[data-cy="div-payment-plan-details"]')
    login.assert_text(PROGRAM_NAME, 'div[data-cy="label-PROGRAMME NAME"]')
    login.assert_text("1", 'div[data-cy="label-PAYMENT RECORDS"]')
    login.assert_text(ui_date(date.today() - timedelta(days=30)), 'div[data-cy="label-START DATE"]')
    login.assert_text(ui_date(date.today() + timedelta(days=30)), 'div[data-cy="label-END DATE"]')
    login.assert_text("Reconciliation Summary", 'div[data-cy="grid-bank-reconciliation"] h6[data-cy="table-label"]')
    login.assert_text("0%", 'div[data-cy="label-SUCCESSFUL"]')
    login.assert_text("0%", 'div[data-cy="label-ERRONEOUS"]')

    login.assert_text("Verification Plans Summary", 'div[data-cy="grid-verification-plans-summary"]')
    login.assert_text("PENDING", 'div[data-cy="verification-plans-summary-status"]')
    login.assert_exact_text("-", 'div[data-cy="label-Completion Date"]')
    login.assert_exact_text("1", 'div[data-cy="label-Number of Verification Plans"]')

    login.assert_text(f"Verification Plan #{verification_plan.unicef_id}")
    login.assert_text("DELETE", 'button[data-cy="button-delete-plan"]')
    login.assert_text("EDIT", 'button[data-cy="button-edit-plan"]')
    login.assert_text("ACTIVATE", 'button[data-cy="button-activate-plan"]')
    login.assert_text("PENDING", PLAN_STATUS)
    login.assert_text("Full list", 'div[data-cy="label-SAMPLING"]')
    login.assert_text("MANUAL", 'div[data-cy="label-VERIFICATION CHANNEL"]')
    login.assert_exact_text("0", 'div[data-cy="label-RESPONDED"]')
    login.assert_exact_text("0", 'div[data-cy="label-RECEIVED WITH ISSUES"]')
    login.assert_exact_text("0", 'div[data-cy="label-SAMPLE SIZE"]')
    login.assert_exact_text("0", 'div[data-cy="label-RECEIVED"]')
    login.assert_exact_text("0", 'div[data-cy="label-NOT RECEIVED"]')
