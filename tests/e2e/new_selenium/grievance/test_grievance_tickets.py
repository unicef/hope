import time

import pytest
from selenium.common.exceptions import (
    NoSuchElementException as SeleniumNoSuchElement,
    StaleElementReferenceException,
)
from seleniumbase.common.exceptions import NoSuchElementException

from e2e.new_selenium.conftest import grant_permission
from extras.test_utils.selenium import HopeTestBrowser
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, Program, User

pytestmark = pytest.mark.django_db()


def _click_drawer_nav(browser: HopeTestBrowser, selector: str, deadline_s: float = 30.0) -> None:
    # The drawer remounts as the SPA hydrates user permissions/programs after login,
    # so the nav link can go stale between find and click. Retry through staleness.
    deadline = time.time() + deadline_s
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            browser.click(selector, timeout=5)
            return
        except (
            StaleElementReferenceException,
            SeleniumNoSuchElement,
            NoSuchElementException,
        ) as exc:
            last_error = exc
            time.sleep(0.3)
    raise AssertionError(f"Could not click {selector} within {deadline_s}s: {last_error}")


def test_create_new_ticket_referral(
    browser: HopeTestBrowser,
    social_worker_program: Program,
    user_with_no_permissions: User,
    business_area: BusinessArea,
) -> None:
    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
        Permissions.GRIEVANCES_CREATE,
        Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE,
        Permissions.GEO_VIEW_LIST,
        Permissions.RDI_VIEW_DETAILS,
        Permissions.POPULATION_VIEW_INDIVIDUALS_LIST,
        Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS,
    ):
        browser.login(username="noperm_user", password="testtest2")
        _click_drawer_nav(browser, 'a[data-cy="nav-Grievance"]')
        browser.wait_for_text("Grievance Tickets", 'h5[data-cy="page-header-title"]')

        browser.click('a[data-cy="button-new-ticket"]')
        browser.select_dropdown_option("category", "Referral")
        browser.click('button[data-cy="button-submit"]')

        browser.wait_for_ready_state_complete()
        browser.wait_for_element_visible('button[data-cy="look-up-household"]')
        browser.click('button[data-cy="look-up-household"]')
        browser.assert_text("No results", '[data-cy="table-row"]')

        browser.click('button[data-cy="button-submit"]')
        browser.wait_for_ready_state_complete()
        browser.click('[data-cy="input-consent"]')
        browser.click('button[data-cy="button-submit"]')
        browser.type('textarea[name="description"]', "Happy path test 1234!")
        browser.click('button[data-cy="button-submit"]')

        browser.assert_text("Happy path test 1234!", 'div[data-cy="label-Description"]')
        browser.assert_text("Referral", 'div[data-cy="label-Category"]')
        browser.assert_text("New", 'div[data-cy="label-Status"]')
        browser.assert_text("Not set", 'div[data-cy="label-Priority"]')
        browser.assert_text("Not set", 'div[data-cy="label-Urgency"]')
