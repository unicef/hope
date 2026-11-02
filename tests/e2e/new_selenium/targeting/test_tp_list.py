import pytest

from e2e.new_selenium.conftest import grant_permission
from extras.test_utils.factories.payment import PaymentPlanFactory
from extras.test_utils.selenium import HopeTestBrowser
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, PaymentPlan, Program, User

from .conftest import BUILT_TP_NAME

pytestmark = pytest.mark.django_db()

LOCKED_TP_NAME = "Locked Large TP"


@pytest.fixture
def locked_large_tp(built_tp: PaymentPlan) -> PaymentPlan:
    return PaymentPlanFactory(
        name=LOCKED_TP_NAME,
        program_cycle=built_tp.program_cycle,
        payment_plan_group=built_tp.payment_plan_group,
        status=PaymentPlan.Status.TP_LOCKED,
        business_area=built_tp.business_area,
        total_households_count=10,
    )


def tp_list_url(program: Program) -> str:
    return f"/{program.business_area.slug}/programs/{program.code}/target-population"


def apply_filters(browser: HopeTestBrowser) -> None:
    browser.click('button[data-cy="button-filters-apply"]')


def clear_filters(browser: HopeTestBrowser) -> None:
    browser.click('button[data-cy="button-filters-clear"]')
    browser.wait_for_text(BUILT_TP_NAME, "table")
    browser.wait_for_text(LOCKED_TP_NAME, "table")


def test_tp_list_filters_by_name_status_and_household_count(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    built_tp: PaymentPlan,
    locked_large_tp: PaymentPlan,
) -> None:
    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.TARGETING_VIEW_LIST,
    ):
        browser.login(username="noperm_user")
        browser.open(tp_list_url(built_tp.program_cycle.program))
        browser.wait_for_text(BUILT_TP_NAME, "table")
        browser.wait_for_text(LOCKED_TP_NAME, "table")

        browser.type('[data-cy="filters-search"] input', "Locked")
        apply_filters(browser)
        browser.wait_for_text_not_visible(BUILT_TP_NAME, "table")
        browser.assert_text(LOCKED_TP_NAME, "table")
        clear_filters(browser)

        browser.click('[data-cy="filters-status"]')
        browser.select_listbox_element("Open")
        apply_filters(browser)
        browser.wait_for_text_not_visible(LOCKED_TP_NAME, "table")
        browser.assert_text(BUILT_TP_NAME, "table")
        clear_filters(browser)

        browser.type('[data-cy="filters-total-households-count-min"] input', "5")
        apply_filters(browser)
        browser.wait_for_text_not_visible(BUILT_TP_NAME, "table")
        browser.assert_text(LOCKED_TP_NAME, "table")


def test_create_button_disabled_when_programme_not_active(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    built_tp: PaymentPlan,
) -> None:
    program = built_tp.program_cycle.program
    Program.objects.filter(id=program.id).update(status=Program.FINISHED)
    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.TARGETING_VIEW_LIST,
        Permissions.TARGETING_CREATE,
    ):
        browser.login(username="noperm_user")
        browser.open(tp_list_url(program))
        browser.wait_for_text(BUILT_TP_NAME, "table")
        browser.assert_element_absent('a[data-cy="button-new-tp"]')
        browser.hover('[data-cy="button-new-tp-disabled"]')
        browser.wait_for_text("Program has to be active to create a new Target Population", 'div[role="tooltip"]')
