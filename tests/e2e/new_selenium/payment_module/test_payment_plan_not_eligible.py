import pytest
from selenium.webdriver.common.action_chains import ActionChains

from extras.test_utils.factories import (
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    PaymentFactory,
    PaymentPlanFactory,
    ProgramFactory,
)
from extras.test_utils.selenium import HopeTestBrowser
from hope.models import BusinessArea, Payment, PaymentPlan, Program

pytestmark = pytest.mark.django_db()


@pytest.fixture
def payment_plan_with_not_eligible_and_pending_breakdown(
    business_area: BusinessArea,
) -> tuple[PaymentPlan, Payment, Payment, Payment, Payment]:
    program = ProgramFactory(business_area=business_area, status=Program.ACTIVE)
    payment_plan = PaymentPlanFactory(
        business_area=business_area,
        program_cycle=program.cycles.first(),
        status=PaymentPlan.Status.ACCEPTED,
        financial_service_provider=FinancialServiceProviderFactory(),
        delivery_mechanism=DeliveryMechanismFactory(),
    )
    pending_payment = PaymentFactory(
        parent=payment_plan,
        program=program,
        status=Payment.STATUS_PENDING,
    )
    sent_to_gateway_payment = PaymentFactory(
        parent=payment_plan,
        program=program,
        status=Payment.STATUS_SENT_TO_PG,
    )
    sent_to_fsp_payment = PaymentFactory(
        parent=payment_plan,
        program=program,
        status=Payment.STATUS_SENT_TO_FSP,
    )
    not_eligible_payment = PaymentFactory(
        parent=payment_plan,
        program=program,
        status=Payment.STATUS_NOT_ELIGIBLE,
        excluded=True,
    )
    return (
        payment_plan,
        pending_payment,
        sent_to_gateway_payment,
        sent_to_fsp_payment,
        not_eligible_payment,
    )


def _open_payment_plan(browser: HopeTestBrowser, payment_plan: PaymentPlan) -> None:
    program = payment_plan.program_cycle.program
    url = f"/{payment_plan.business_area.slug}/programs/{program.code}/payment-module/payment-plans/{payment_plan.id}"
    browser.open(url)
    browser.wait_for_element_visible('div[data-cy="status-container"]')


def test_not_eligible_table_status_filter_and_pending_breakdown(
    login: HopeTestBrowser,
    payment_plan_with_not_eligible_and_pending_breakdown: tuple[PaymentPlan, Payment, Payment, Payment, Payment],
) -> None:
    payment_plan, pending_payment, sent_to_gateway_payment, sent_to_fsp_payment, not_eligible_payment = (
        payment_plan_with_not_eligible_and_pending_breakdown
    )
    _open_payment_plan(login, payment_plan)

    login.wait_for_text("Payee List", '[data-cy="table-title"]')
    login.wait_for_text(str(pending_payment.unicef_id))
    login.wait_for_text(str(sent_to_gateway_payment.unicef_id))
    login.wait_for_text(str(sent_to_fsp_payment.unicef_id))
    login.wait_for_text("Not Eligible Payee List")
    login.wait_for_text(str(not_eligible_payment.unicef_id))
    login.wait_for_text("Manual Exclusion")

    login.wait_for_text("3", '[data-cy="label-Pending"]')
    pending_summary = login.wait_for_element_visible('[data-cy="label-Pending"]')
    ActionChains(login.driver).move_to_element(pending_summary).perform()
    login.wait_for_text("Pending: 1", '[role="tooltip"]')
    login.wait_for_text("Sent to Payment Gateway: 1", '[role="tooltip"]')
    login.wait_for_text("Sent to FSP: 1", '[role="tooltip"]')

    status_filter = login.wait_for_element_present('[data-cy="filter-payment-status"] [role="combobox"]')
    login.execute_script("arguments[0].scrollIntoView({block: 'center'});", status_filter)
    login.wait_for_element_clickable('[data-cy="filter-payment-status"] [role="combobox"]').click()
    login.wait_for_element_visible('ul[role="listbox"]')
    login.assert_element_absent('li[data-value="Not Eligible"]')
    login.wait_for_element_clickable('li[data-value="Pending"]').click()
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
