from collections.abc import Callable

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


def filter_by_name(browser: HopeTestBrowser) -> None:
    browser.type('[data-cy="filters-search"] input', "Locked")


def filter_by_open_status(browser: HopeTestBrowser) -> None:
    browser.click('[data-cy="filters-status"]')
    browser.select_listbox_element("Open")


def filter_by_min_households(browser: HopeTestBrowser) -> None:
    browser.type('[data-cy="filters-total-households-count-min"] input', "5")


@pytest.fixture
def finished_programme_tp(built_tp: PaymentPlan) -> PaymentPlan:
    Program.objects.filter(id=built_tp.program_cycle.program_id).update(status=Program.FINISHED)
    return built_tp


@pytest.mark.parametrize(
    ("apply_filter", "shown", "hidden"),
    [
        pytest.param(filter_by_name, LOCKED_TP_NAME, BUILT_TP_NAME, id="name"),
        pytest.param(filter_by_open_status, BUILT_TP_NAME, LOCKED_TP_NAME, id="status"),
        pytest.param(filter_by_min_households, LOCKED_TP_NAME, BUILT_TP_NAME, id="household-count"),
    ],
)
def test_tp_list_filter(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    built_tp: PaymentPlan,
    locked_large_tp: PaymentPlan,
    apply_filter: Callable[[HopeTestBrowser], None],
    shown: str,
    hidden: str,
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

        apply_filter(browser)
        browser.click('button[data-cy="button-filters-apply"]')

        browser.wait_for_text_not_visible(hidden, "table")
        browser.assert_text(shown, "table")


def test_create_button_disabled_when_programme_not_active(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    finished_programme_tp: PaymentPlan,
) -> None:
    program = finished_programme_tp.program_cycle.program
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
