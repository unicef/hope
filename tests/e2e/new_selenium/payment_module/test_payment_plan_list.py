import pytest

from extras.test_utils.selenium import HopeTestBrowser, ui_date
from hope.models import PaymentPlan

from .conftest import PAYMENT_PLANS_PROGRAM_NAME

pytestmark = pytest.mark.django_db()

PAGE_HEADER_TITLE = 'h5[data-cy="page-header-title"]'
TABLE_PAGINATION = 'div[data-cy="table-pagination"]'
TABLE_LABEL = 'span[data-cy="table-label"]'
LIST_COLUMNS = [
    "Payment Plan ID",
    "Status",
    "Target Population",
    "Num. of Items Groups",
    "Currency",
    "Total Entitled Quantity",
    "Total Delivered Quantity",
    "Total Undelivered Quantity",
    "Dispersion Start Date",
    "Dispersion End Date",
    "Export Batch",
    "Linked Payment Plans",
]
PAYEE_LIST_COLUMNS = [
    "Payment ID",
    "Items Group ID",
    "Items Group Size",
    "Administrative Level 2",
    "Collector",
    "FSP",
    "Entitlement",
    "Delivered Quantity",
    "Status",
    "FSP Auth Code",
    "Reconciliation",
]


def open_payment_plans(browser: HopeTestBrowser) -> None:
    browser.select_global_program(PAYMENT_PLANS_PROGRAM_NAME)
    browser.open_nav_section("Payment Module")
    browser.click('a[data-cy="nav-Payment Plans"]')
    browser.wait_for_text("Payment Module", PAGE_HEADER_TITLE)


def table_labels(browser: HopeTestBrowser) -> list[str]:
    return [label.text for label in browser.find_elements(TABLE_LABEL) if label.text]


def test_payment_plan_list_shows_payment_plan(
    login: HopeTestBrowser,
    accepted_payment_plan_without_payments: PaymentPlan,
) -> None:
    payment_plan = accepted_payment_plan_without_payments

    open_payment_plans(login)

    login.assert_text("Status", 'div[data-cy="select-filter"]')
    login.assert_element_visible('div[data-cy="filters-total-entitled-quantity-from"] input')
    login.assert_element_visible('div[data-cy="filters-total-entitled-quantity-to"] input')
    login.assert_element_visible('div[data-cy="date-picker-filter-From"]')
    login.assert_element_visible('div[data-cy="date-picker-filter-To"]')
    login.assert_text("CLEAR", 'button[data-cy="button-filters-clear"]')
    login.assert_text("APPLY", 'button[data-cy="button-filters-apply"]')
    login.assert_text("Payment Plans", 'h6[data-cy="table-title"]')
    login.wait_for_text(payment_plan.unicef_id, '[role="checkbox"]')
    assert table_labels(login) == LIST_COLUMNS
    login.assert_text("ACCEPTED", 'div[data-cy="status-container"]')
    login.assert_text("Rows per page:", TABLE_PAGINATION)
    login.assert_exact_text("5", f"{TABLE_PAGINATION} .MuiTablePagination-select")
    login.assert_text("1–1 of 1", TABLE_PAGINATION)


def test_payment_plan_details_shows_summary(
    login: HopeTestBrowser,
    accepted_payment_plan_without_payments: PaymentPlan,
) -> None:
    payment_plan = accepted_payment_plan_without_payments
    open_payment_plans(login)

    login.click(f'[role="checkbox"]:contains("{payment_plan.unicef_id}")')

    login.wait_for_text(payment_plan.unicef_id, PAGE_HEADER_TITLE)
    login.assert_text("ACCEPTED", 'div[data-cy="status-container"]')
    login.assert_text("EXPORT XLSX", 'button[data-cy="button-export-xlsx"]')
    login.assert_text("USD", 'div[data-cy="label-Currency"]')
    login.assert_text(ui_date(payment_plan.dispersion_start_date), 'div[data-cy="label-Dispersion Start Date"]')
    login.assert_text(ui_date(payment_plan.dispersion_end_date), 'div[data-cy="label-Dispersion End Date"]')
    login.assert_text("-", 'div[data-cy="label-Related Follow-Up Payment Plans"]')
    login.assert_text("CREATE", 'button[data-cy="button-create-exclusions"]')
    login.assert_text("Supporting Documents", 'h6[data-cy="supporting-documents-title"]')
    login.assert_text("No documents uploaded", 'div[data-cy="supporting-documents-empty"]')
    login.assert_text("0", 'div[data-cy="label-Female Children"]')
    login.assert_text("0", 'div[data-cy="label-Female Adults"]')
    login.assert_text("0", 'div[data-cy="label-Male Children"]')
    login.assert_text("0", 'div[data-cy="label-Male Adults"]')
    login.assert_element_present('div[data-cy="chart-container"]')
    login.assert_text("0", 'div[data-cy="label-Total Number of Items Groups"]')
    login.assert_text("0", 'div[data-cy="label-Targeted Items"]')
    login.assert_text("Payee List", 'h6[data-cy="table-title"]')
    login.assert_text("UPLOAD FILE", 'button[data-cy="button-import"]')
    assert table_labels(login) == PAYEE_LIST_COLUMNS
