import pytest

from e2e.new_selenium.conftest import grant_permission
from extras.test_utils.selenium import HopeTestBrowser
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, PaymentList, User

pytestmark = pytest.mark.django_db()

PAYMENT_LIST_STATUS = 'div[data-cy="status-container"]'
DELETE = 'button[data-cy="button-delete-pp"]'
DELETE_SUBMIT = 'button[data-cy="button-submit"]'
PAYMENT_LIST_VIEW_PERMISSIONS = (
    Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
    Permissions.PM_VIEW_LIST,
    Permissions.PM_VIEW_DETAILS,
)


def open_payment_list_as(browser: HopeTestBrowser, payment_list: PaymentList, status: str) -> None:
    browser.login(username="noperm_user")
    browser.open(
        f"/{payment_list.business_area.slug}/programs/{payment_list.program.code}"
        f"/payment-module/payment-lists/{payment_list.id}"
    )
    browser.wait_for_text(status, PAYMENT_LIST_STATUS)


def test_delete_payment_list_from_open_payment_plan(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    open_payment_list: PaymentList,
) -> None:
    payment_list = open_payment_list
    with grant_permission(
        user_with_no_permissions, business_area, *PAYMENT_LIST_VIEW_PERMISSIONS, Permissions.PM_CREATE
    ):
        open_payment_list_as(browser, payment_list, "OPEN")
        browser.wait_for_element_clickable(DELETE).click()
        browser.wait_for_element_clickable(DELETE_SUBMIT).click()
        browser.wait_for_text("Payment List Deleted")

    payment_list.refresh_from_db()
    assert payment_list.status == PaymentList.Status.DRAFT
    assert payment_list.payment_items.count() == 3


def test_delete_payment_list_hidden_without_permission(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    open_payment_list: PaymentList,
) -> None:
    with grant_permission(user_with_no_permissions, business_area, *PAYMENT_LIST_VIEW_PERMISSIONS):
        open_payment_list_as(browser, open_payment_list, "OPEN")
        browser.assert_elements_absent(DELETE)
