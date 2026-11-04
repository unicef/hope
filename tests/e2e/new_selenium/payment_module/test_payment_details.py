from decimal import Decimal

from django.utils import timezone
import pytest

from e2e.new_selenium.conftest import grant_permission
from extras.test_utils.selenium import HopeTestBrowser
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, Payment, PaymentList, User

from .conftest import PM_VIEW_PERMISSIONS, _lifecycle_payment_list

pytestmark = pytest.mark.django_db()

PAYMENT_STATUS = 'div[data-cy="label-STATUS"]'
DELIVERED_QUANTITY = 'div[data-cy="label-DELIVERED QUANTITY"]'
MARK_AS_FAILED = 'button[data-cy="button-mark-as-failed"]'
MARK_AS_FAILED_SUBMIT = 'button[data-cy="button-mark-as-failed-submit"]'
REVERT = 'button[data-cy="button-revert-mark-as-failed"]'
REVERT_SUBMIT = 'button[data-cy="button-revert-mark-as-failed-submit"]'
DELIVERED_QUANTITY_INPUT = 'input[data-cy="input-deliveredQuantity"]'


def program_url(payment_list: PaymentList) -> str:
    return f"/{payment_list.business_area.slug}/programs/{payment_list.program.code}"


def open_payment_as(browser: HopeTestBrowser, payment: Payment, status: str) -> None:
    browser.login(username="noperm_user")
    browser.open(f"{program_url(payment.parent)}/payment-module/payments/{payment.id}")
    browser.wait_for_text(status, PAYMENT_STATUS)


def first_payment(payment_list: PaymentList) -> Payment:
    return payment_list.payment_items.order_by("unicef_id").first()


def _delivered_payment_list(business_area: BusinessArea, status: str, force_failed_count: int = 0) -> PaymentList:
    """Released plan with 3 fully delivered payments, the first `force_failed_count` of them marked failed."""
    payment_list = _lifecycle_payment_list(business_area, status, status)
    for index, payment in enumerate(payment_list.payment_items.order_by("unicef_id")):
        failed = index < force_failed_count
        payment.status = Payment.STATUS_FORCE_FAILED if failed else Payment.STATUS_DISTRIBUTION_SUCCESS
        payment.delivered_quantity = Decimal(0) if failed else payment.entitlement_quantity
        payment.delivered_quantity_usd = Decimal(0) if failed else payment.entitlement_quantity_usd
        payment.delivery_date = None if failed else timezone.now()
        payment.save()
        payment.household.total_cash_received = payment.delivered_quantity
        payment.household.total_cash_received_usd = payment.delivered_quantity_usd
        payment.household.save(update_fields=["total_cash_received", "total_cash_received_usd"])
    payment_list.update_money_fields()
    return payment_list


@pytest.fixture
def delivered_payment_list(business_area: BusinessArea) -> PaymentList:
    return _delivered_payment_list(business_area, PaymentList.Status.ACCEPTED)


@pytest.fixture
def finished_delivered_payment_list(business_area: BusinessArea) -> PaymentList:
    return _delivered_payment_list(business_area, PaymentList.Status.FINISHED)


@pytest.fixture
def payment_list_with_force_failed_payment(business_area: BusinessArea) -> PaymentList:
    return _delivered_payment_list(business_area, PaymentList.Status.ACCEPTED, force_failed_count=1)


def test_mark_payment_as_failed(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    delivered_payment_list: PaymentList,
) -> None:
    payment = first_payment(delivered_payment_list)
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
    payment_list_with_force_failed_payment: PaymentList,
) -> None:
    payment = first_payment(payment_list_with_force_failed_payment)
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


DELIVERED_PLAN_FIXTURES = pytest.mark.parametrize(
    "payment_list_fixture",
    [
        pytest.param("delivered_payment_list", id="accepted"),
        pytest.param("finished_delivered_payment_list", id="finished"),
    ],
)


@DELIVERED_PLAN_FIXTURES
def test_mark_as_failed_shown_with_permission(
    request: pytest.FixtureRequest,
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    payment_list_fixture: str,
) -> None:
    payment = first_payment(request.getfixturevalue(payment_list_fixture))
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
    payment_list_fixture: str,
) -> None:
    payment = first_payment(request.getfixturevalue(payment_list_fixture))
    with grant_permission(user_with_no_permissions, business_area, *PM_VIEW_PERMISSIONS):
        open_payment_as(browser, payment, "DELIVERED FULLY")
        browser.assert_element_absent(MARK_AS_FAILED)
