import pytest

from extras.test_utils.selenium import HopeTestBrowser
from hope.models import PaymentList

pytestmark = pytest.mark.django_db()

# Regression test for PR #6064 -- https://github.com/unicef/hope/pull/6064
# "Hotfix // Payments ordering by created_at". The Payment Plan Payee List rendered blank


def _open_payment_list(browser: HopeTestBrowser, payment_list: PaymentList) -> None:
    program = payment_list.program_cycle.program
    url = f"/{payment_list.business_area.slug}/programs/{program.code}/payment-module/payment-lists/{payment_list.id}"
    browser.open(url)
    browser.wait_for_element_visible('div[data-cy="status-container"]')


def test_payee_list_second_page_is_not_blank(
    login: HopeTestBrowser,
    payment_list_for_pagination: tuple[PaymentList, str, str],
) -> None:
    payment_list, page_one_unicef_id, page_two_unicef_id = payment_list_for_pagination
    _open_payment_list(login, payment_list)

    # Payee List loaded; the newest payment is shown on page 1.
    login.wait_for_text("Payee List", '[data-cy="table-title"]')
    login.wait_for_text(page_one_unicef_id)

    # Navigate to page 2.
    login.wait_for_element_clickable('[data-cy="table-pagination"] button[aria-label="next page"]').click()

    # Regression: page 2 must render the oldest payment, not a blank list (PR #6064).
    login.wait_for_text(page_two_unicef_id)
