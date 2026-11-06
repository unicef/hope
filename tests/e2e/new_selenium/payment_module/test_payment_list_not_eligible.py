import pytest
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

from extras.test_utils.factories import (
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    PaymentFactory,
    PaymentListFactory,
    ProgramFactory,
)
from extras.test_utils.selenium import HopeTestBrowser
from hope.models import BusinessArea, Payment, PaymentList, Program

pytestmark = pytest.mark.django_db()


@pytest.fixture
def payment_list_with_not_eligible_and_pending_breakdown(
    business_area: BusinessArea,
) -> tuple[PaymentList, Payment, Payment, Payment, Payment]:
    program = ProgramFactory(business_area=business_area, status=Program.ACTIVE)
    payment_list = PaymentListFactory(
        business_area=business_area,
        program_cycle=program.cycles.first(),
        status=PaymentList.Status.ACCEPTED,
        financial_service_provider=FinancialServiceProviderFactory(),
        delivery_mechanism=DeliveryMechanismFactory(),
    )
    pending_payment = PaymentFactory(
        parent=payment_list,
        program=program,
        status=Payment.STATUS_PENDING,
    )
    sent_to_gateway_payment = PaymentFactory(
        parent=payment_list,
        program=program,
        status=Payment.STATUS_SENT_TO_PG,
    )
    sent_to_fsp_payment = PaymentFactory(
        parent=payment_list,
        program=program,
        status=Payment.STATUS_SENT_TO_FSP,
    )
    not_eligible_payment = PaymentFactory(
        parent=payment_list,
        program=program,
        status=Payment.STATUS_NOT_ELIGIBLE,
        conflicted=True,
        excluded=True,
        has_valid_wallet=False,
    )
    return (
        payment_list,
        pending_payment,
        sent_to_gateway_payment,
        sent_to_fsp_payment,
        not_eligible_payment,
    )


def _open_payment_list(browser: HopeTestBrowser, payment_list: PaymentList) -> None:
    program = payment_list.program_cycle.program
    url = f"/{payment_list.business_area.slug}/programs/{program.code}/payment-module/payment-lists/{payment_list.id}"
    browser.open(url)
    browser.wait_for_element_visible('div[data-cy="status-container"]')


def test_not_eligible_table_status_filter_and_pending_breakdown(
    login: HopeTestBrowser,
    payment_list_with_not_eligible_and_pending_breakdown: tuple[PaymentList, Payment, Payment, Payment, Payment],
) -> None:
    payment_list, pending_payment, sent_to_gateway_payment, sent_to_fsp_payment, not_eligible_payment = (
        payment_list_with_not_eligible_and_pending_breakdown
    )
    _open_payment_list(login, payment_list)

    login.wait_for_text("Payee List", '[data-cy="table-title"]')
    login.wait_for_text(str(pending_payment.unicef_id))
    login.wait_for_text(str(sent_to_gateway_payment.unicef_id))
    login.wait_for_text(str(sent_to_fsp_payment.unicef_id))
    login.wait_for_text("Not Eligible Payee List")
    login.wait_for_text(str(not_eligible_payment.unicef_id))
    login.wait_for_text("Hard Conflict")
    login.wait_for_text("Manual Exclusion")
    login.wait_for_text("Invalid Wallet")

    not_eligible_table = login.wait_for_element_visible('[data-cy="not-eligible-payments-table"]')
    not_eligible_headers = not_eligible_table.find_element(By.TAG_NAME, "thead").text
    assert "Household Size" not in not_eligible_headers
    assert "Administrative Level 2" not in not_eligible_headers
    assert "FSP" not in not_eligible_headers
    assert "Delivered Quantity" not in not_eligible_headers
    assert "FSP Auth Code" not in not_eligible_headers
    assert "Reconciliation" not in not_eligible_headers

    login.wait_for_text("3", '[data-cy="label-Pending"]')
    pending_breakdown_icon = login.wait_for_element_visible('[data-cy="pending-breakdown-icon"]')
    ActionChains(login.driver).move_to_element(pending_breakdown_icon).perform()
    login.wait_for_text("Pending: 1", '[role="tooltip"]')
    login.wait_for_text("Sent to Payment Gateway: 1", '[role="tooltip"]')
    login.wait_for_text("Sent to FSP: 1", '[role="tooltip"]')

    status_filter = login.wait_for_element_present('[data-cy="filter-payment-status"] [role="combobox"]')
    login.execute_script("arguments[0].scrollIntoView({block: 'center'});", status_filter)
    login.wait_for_element_clickable('[data-cy="filter-payment-status"] [role="combobox"]').click()
    login.wait_for_element_visible('ul[role="listbox"]')
    login.assert_element_absent('li[data-value="Not Eligible"]')
    login.assert_element_absent('li[data-value="Transaction Successful"]')
    login.wait_for_element_visible('li[data-value="Distribution Successful"]')
    login.select_option_by_name("Pending", selector='li[data-value="Pending"]')
    login.find_elements('button[data-cy="button-filters-apply"]')[0].click()

    login.wait_for_element_absent(
        f'a[href$="/payment-module/payments/{sent_to_gateway_payment.id}"]',
        timeout=30,
    )
    login.wait_for_element_absent(
        f'a[href$="/payment-module/payments/{sent_to_fsp_payment.id}"]',
        timeout=30,
    )
    login.wait_for_text(str(pending_payment.unicef_id))
    login.wait_for_text(str(not_eligible_payment.unicef_id))
