import datetime
from decimal import Decimal

import pytest

from e2e.new_selenium.conftest import grant_permission
from extras.test_utils.selenium import HopeTestBrowser
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, Payment, PaymentPlan, User

from .conftest import PM_VIEW_PERMISSIONS, payment_plan_url

pytestmark = pytest.mark.django_db()

PAYMENT_STATUS = 'div[data-cy="label-STATUS"]'
DELIVERED_QUANTITY = 'div[data-cy="label-DELIVERED QUANTITY"]'
MARK_AS_FAILED = 'button[data-cy="button-mark-as-failed"]'
MARK_AS_FAILED_SUBMIT = 'button[data-cy="button-mark-as-failed-submit"]'
REVERT = 'button[data-cy="button-revert-mark-as-failed"]'
REVERT_SUBMIT = 'button[data-cy="button-revert-mark-as-failed-submit"]'
DELIVERED_QUANTITY_INPUT = 'input[data-cy="input-deliveredQuantity"]'
CREATE_FOLLOW_UP = 'button[data-cy="button-create-followup"]'
CHILD_PLAN_SUBMIT = 'button[data-cy="button-submit"]'


def program_url(payment_plan: PaymentPlan) -> str:
    return f"/{payment_plan.business_area.slug}/programs/{payment_plan.program.code}"


def open_payment_as(browser: HopeTestBrowser, payment: Payment, status: str) -> None:
    browser.login(username="noperm_user")
    browser.open(f"{program_url(payment.parent)}/payment-module/payments/{payment.id}")
    browser.wait_for_text(status, PAYMENT_STATUS)


def first_payment(payment_plan: PaymentPlan) -> Payment:
    return payment_plan.payment_items.order_by("unicef_id").first()


def test_mark_payment_as_failed(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    delivered_payment_plan: PaymentPlan,
) -> None:
    payment = first_payment(delivered_payment_plan)
    with grant_permission(
        user_with_no_permissions, business_area, *PM_VIEW_PERMISSIONS, Permissions.PM_MARK_PAYMENT_AS_FAILED
    ):
        open_payment_as(browser, payment, "DELIVERED FULLY")
        browser.wait_for_element_clickable(MARK_AS_FAILED).click()
        browser.wait_for_element_clickable(MARK_AS_FAILED_SUBMIT).click()
        browser.wait_for_text("Payment has been marked as failed successfully.")
        browser.wait_for_text("FORCE FAILED", PAYMENT_STATUS)
        browser.wait_for_element_clickable(REVERT)
        browser.assert_element_absent(MARK_AS_FAILED)

    payment.refresh_from_db()
    assert payment.status == Payment.STATUS_FORCE_FAILED
    assert payment.delivered_quantity == 0
    assert payment.delivery_date is None
    payment.household.refresh_from_db()
    assert payment.household.total_cash_received == 0


def test_revert_mark_as_failed(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    payment_plan_with_force_failed_payment: PaymentPlan,
) -> None:
    payment = first_payment(payment_plan_with_force_failed_payment)
    with grant_permission(
        user_with_no_permissions, business_area, *PM_VIEW_PERMISSIONS, Permissions.PM_MARK_PAYMENT_AS_FAILED
    ):
        open_payment_as(browser, payment, "FORCE FAILED")
        browser.wait_for_element_clickable(REVERT).click()
        browser.set_value(DELIVERED_QUANTITY_INPUT, "4")
        browser.fill_date('input[name="deliveryDate"]', "2026-01-15")
        browser.wait_for_element_clickable(REVERT_SUBMIT).click()
        browser.wait_for_text("Force failed has been reverted.")
        browser.wait_for_text("DELIVERED PARTIALLY", PAYMENT_STATUS)
        browser.wait_for_text("4", DELIVERED_QUANTITY)
        browser.wait_for_element_clickable(MARK_AS_FAILED)

    payment.refresh_from_db()
    assert payment.status == Payment.STATUS_DISTRIBUTION_PARTIAL
    assert payment.delivered_quantity == Decimal("4.00")
    assert payment.delivery_date.date().isoformat() == "2026-01-15"
    payment.household.refresh_from_db()
    assert payment.household.total_cash_received == Decimal("4.00")


def test_create_follow_up_from_force_failed_payment(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    payment_plan_with_force_failed_payment: PaymentPlan,
) -> None:
    source = payment_plan_with_force_failed_payment
    failed_payment = first_payment(source)
    start_date = datetime.date.today() + datetime.timedelta(days=10)
    end_date = start_date + datetime.timedelta(days=20)
    with grant_permission(user_with_no_permissions, business_area, *PM_VIEW_PERMISSIONS, Permissions.PM_CREATE):
        browser.login(username="noperm_user")
        browser.open(payment_plan_url(source))
        browser.wait_for_text(source.unicef_id, '[data-cy="pp-unicef-id"]')
        browser.wait_for_element_clickable(CREATE_FOLLOW_UP).click()
        browser.fill_date('input[name="dispersionStartDate"]', start_date.isoformat())
        browser.wait_for_element_clickable('input[name="dispersionEndDate"]')
        browser.fill_date('input[name="dispersionEndDate"]', end_date.isoformat())
        browser.wait_for_element_clickable(CHILD_PLAN_SUBMIT).click()
        browser.wait_for_text("Payment Plan Created")

        follow_up = PaymentPlan.objects.get(source_payment_plan=source, plan_type=PaymentPlan.PlanType.FOLLOW_UP)
        browser.wait_for_text(follow_up.unicef_id)
        assert f"followup-payment-plans/{follow_up.id}" in browser.get_current_url()

    assert list(follow_up.payment_items.values_list("household_id", "is_follow_up", "entitlement_quantity")) == [
        (failed_payment.household_id, True, failed_payment.entitlement_quantity)
    ]


DELIVERED_PLAN_FIXTURES = pytest.mark.parametrize(
    "payment_plan_fixture",
    [
        pytest.param("delivered_payment_plan", id="accepted"),
        pytest.param("finished_delivered_payment_plan", id="finished"),
    ],
)


@DELIVERED_PLAN_FIXTURES
def test_mark_as_failed_shown_with_permission(
    request: pytest.FixtureRequest,
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    payment_plan_fixture: str,
) -> None:
    payment = first_payment(request.getfixturevalue(payment_plan_fixture))
    with grant_permission(
        user_with_no_permissions, business_area, *PM_VIEW_PERMISSIONS, Permissions.PM_MARK_PAYMENT_AS_FAILED
    ):
        open_payment_as(browser, payment, "DELIVERED FULLY")
        browser.wait_for_element_clickable(MARK_AS_FAILED)


@DELIVERED_PLAN_FIXTURES
def test_mark_as_failed_hidden_without_permission(
    request: pytest.FixtureRequest,
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    payment_plan_fixture: str,
) -> None:
    payment = first_payment(request.getfixturevalue(payment_plan_fixture))
    with grant_permission(user_with_no_permissions, business_area, *PM_VIEW_PERMISSIONS):
        open_payment_as(browser, payment, "DELIVERED FULLY")
        browser.assert_element_absent(MARK_AS_FAILED)


def test_create_follow_up_needs_pm_create(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    payment_plan_with_force_failed_payment: PaymentPlan,
) -> None:
    source = payment_plan_with_force_failed_payment
    with grant_permission(user_with_no_permissions, business_area, *PM_VIEW_PERMISSIONS):
        browser.login(username="noperm_user")
        browser.open(payment_plan_url(source))
        browser.wait_for_text(source.unicef_id, '[data-cy="pp-unicef-id"]')
        assert not browser.wait_for_element_visible(CREATE_FOLLOW_UP).is_enabled()
