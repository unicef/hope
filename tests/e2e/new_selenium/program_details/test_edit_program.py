import pytest

from e2e.new_selenium.conftest import grant_permission
from extras.test_utils.selenium import HopeTestBrowser
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, PaymentPlanPurpose, Program, User

from .conftest import BA_PURPOSE_NAME, SECOND_BA_PURPOSE_NAME

pytestmark = pytest.mark.django_db()


def test_edit_programme_updates_details(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    program_with_purpose: Program,
) -> None:
    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.PROGRAMME_UPDATE,
        Permissions.USER_MANAGEMENT_VIEW_LIST,
        Permissions.GEO_VIEW_LIST,
    ):
        browser.login(username="noperm_user", password="testtest2")
        browser.open(f"/{business_area.slug}/programs/{program_with_purpose.code}/details/{program_with_purpose.code}")
        browser.wait_for_element_clickable('button[data-cy="button-edit-program"]').click()
        browser.wait_for_element_clickable('li[data-cy="menu-item-edit-details"]').click()

        browser.wait_for_element_visible('input[name="name"]')
        browser.clear('input[name="name"]')
        browser.type('input[name="name"]', "Updated Programme Name")

        start_el = browser.find_element('input[name="startDate"]')
        browser.triple_click('input[name="startDate"]')
        start_el.send_keys("2022-01-01")
        browser.click('input[name="name"]')

        end_el = browser.find_element('input[name="endDate"]')
        browser.triple_click('input[name="endDate"]')
        end_el.send_keys("2099-10-01")
        browser.click('input[name="name"]')

        browser.click('button[data-cy="button-next"]')
        browser.wait_for_element_visible('button[data-cy="button-add-time-series-field"]')
        browser.click('button[data-cy="button-next"]')
        browser.wait_for_element_visible('button[data-cy="button-save"]').click()

        browser.wait_for_text("Updated Programme Name", 'h5[data-cy="page-header-title"]')
        browser.assert_text("1 Jan 2022", 'div[data-cy="label-START DATE"]')
        browser.assert_text("1 Oct 2099", 'div[data-cy="label-END DATE"]')


def test_edit_programme_cannot_remove_existing_purpose(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    program_with_purpose: Program,
) -> None:
    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.PROGRAMME_UPDATE,
        Permissions.USER_MANAGEMENT_VIEW_LIST,
        Permissions.GEO_VIEW_LIST,
    ):
        browser.login(username="noperm_user", password="testtest2")
        browser.open(f"/{business_area.slug}/programs/{program_with_purpose.code}/details/{program_with_purpose.code}")
        browser.wait_for_element_clickable('button[data-cy="button-edit-program"]').click()
        browser.wait_for_element_clickable('li[data-cy="menu-item-edit-details"]').click()

        browser.wait_for_element_visible('[data-cy="input-payment-plan-purposes"]')
        browser.click('[data-cy="input-payment-plan-purposes"]')
        browser.wait_for_text(BA_PURPOSE_NAME, 'ul[role="listbox"]')

        # Existing purpose is locked — it appears as a disabled option in the dropdown
        browser.assert_text(BA_PURPOSE_NAME, 'li[role="option"][aria-disabled="true"]')


def test_edit_programme_adds_new_purpose(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    program_with_purpose: Program,
    second_ba_purpose: PaymentPlanPurpose,
) -> None:
    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.PROGRAMME_UPDATE,
        Permissions.USER_MANAGEMENT_VIEW_LIST,
        Permissions.GEO_VIEW_LIST,
    ):
        browser.login(username="noperm_user", password="testtest2")
        browser.open(f"/{business_area.slug}/programs/{program_with_purpose.code}/details/{program_with_purpose.code}")
        browser.wait_for_element_clickable('button[data-cy="button-edit-program"]').click()
        browser.wait_for_element_clickable('li[data-cy="menu-item-edit-details"]').click()

        browser.wait_for_element_visible('[data-cy="input-payment-plan-purposes"]')
        browser.select_chip_option(SECOND_BA_PURPOSE_NAME, '[data-cy="input-payment-plan-purposes"]')

        browser.click('button[data-cy="button-next"]')
        browser.wait_for_element_visible('button[data-cy="button-add-time-series-field"]')
        browser.click('button[data-cy="button-next"]')
        browser.wait_for_element_visible('button[data-cy="button-save"]').click()

        browser.wait_for_element_visible('div[data-cy="label-Payment Plan Purposes"]')
        browser.assert_text(BA_PURPOSE_NAME, 'div[data-cy="label-Payment Plan Purposes"]')
        browser.assert_text(SECOND_BA_PURPOSE_NAME, 'div[data-cy="label-Payment Plan Purposes"]')


def test_edit_programme_max_five_purposes_enforced(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    program_with_five_purposes: Program,
) -> None:
    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.PROGRAMME_UPDATE,
        Permissions.USER_MANAGEMENT_VIEW_LIST,
        Permissions.GEO_VIEW_LIST,
    ):
        browser.login(username="noperm_user", password="testtest2")
        browser.open(
            f"/{business_area.slug}/programs/{program_with_five_purposes.code}"
            f"/details/{program_with_five_purposes.code}"
        )
        browser.wait_for_element_clickable('button[data-cy="button-edit-program"]').click()
        browser.wait_for_element_clickable('li[data-cy="menu-item-edit-details"]').click()

        browser.wait_for_element_visible('[data-cy="input-payment-plan-purposes"]')

        # All 5 purposes are already selected — the input is disabled and cannot be opened
        browser.click('[data-cy="input-payment-plan-purposes"]')
        browser.assert_element_absent('ul[role="listbox"]')
