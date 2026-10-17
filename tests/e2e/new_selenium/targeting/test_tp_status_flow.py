import pytest

from e2e.new_selenium.conftest import grant_permission
from extras.test_utils.factories import HouseholdFactory
from extras.test_utils.selenium import HopeTestBrowser
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, PaymentPlan, User

from .conftest import BUILT_TP_NAME, CYCLE_TITLE, GROUP_NAME, PURPOSE_NAME

pytestmark = pytest.mark.django_db()

STATUS = 'div[data-cy="target-population-status"]'
HOUSEHOLDS_COUNT = '[data-cy="total-number-of-households-count"]'


def tp_url(tp: PaymentPlan) -> str:
    return f"/{tp.business_area.slug}/programs/{tp.program_cycle.program.code}/target-population/{tp.id}"


def test_lock_hides_edit_actions_and_unlock_restores_them(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    built_tp: PaymentPlan,
) -> None:
    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.TARGETING_VIEW_DETAILS,
        Permissions.TARGETING_UPDATE,
        Permissions.TARGETING_REMOVE,
        Permissions.TARGETING_LOCK,
        Permissions.TARGETING_UNLOCK,
    ):
        browser.login(username="noperm_user")
        browser.open(tp_url(built_tp))
        browser.wait_for_text("OPEN", STATUS)

        browser.click('button[data-cy="button-target-population-lock"]')
        browser.click('button[data-cy="button-target-population-modal-lock"]')
        browser.wait_for_text("LOCKED", STATUS)
        browser.wait_for_element_visible('button[data-cy="button-target-population-unlocked"]')
        browser.assert_element_absent('[data-cy="button-edit"]')
        browser.assert_element_absent('button[data-cy="button-rebuild"]')
        browser.assert_element_absent('button[data-cy="button-delete"]')
        built_tp.refresh_from_db()
        assert built_tp.status == PaymentPlan.Status.TP_LOCKED

        browser.click('button[data-cy="button-target-population-unlocked"]')
        browser.wait_for_text("OPEN", STATUS)
        browser.wait_for_element_visible('[data-cy="button-edit"]')
        browser.assert_element_absent('button[data-cy="button-target-population-unlocked"]')
        built_tp.refresh_from_db()
        assert built_tp.status == PaymentPlan.Status.TP_OPEN


def test_mark_ready_turns_tp_into_draft_payment_plan(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    locked_tp: PaymentPlan,
) -> None:
    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.TARGETING_VIEW_DETAILS,
        Permissions.TARGETING_SEND,
    ):
        browser.login(username="noperm_user")
        browser.open(tp_url(locked_tp))
        browser.wait_for_text("LOCKED", STATUS)

        browser.click('button[data-cy="button-target-population-send-to-hope"]')
        browser.click('button[data-cy="button-target-population-modal-send-to-hope"]')
        browser.wait_for_text("READY FOR PAYMENT MODULE", STATUS)
        locked_tp.refresh_from_db()
        assert locked_tp.status == PaymentPlan.Status.DRAFT
        browser.assert_element_absent('button[data-cy="button-target-population-unlocked"]')


def test_rebuild_picks_up_newly_matching_households(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    built_tp: PaymentPlan,
) -> None:
    program = built_tp.program_cycle.program
    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.TARGETING_VIEW_DETAILS,
        Permissions.TARGETING_UPDATE,
        Permissions.TARGETING_LOCK,
    ):
        browser.login(username="noperm_user")
        browser.open(tp_url(built_tp))
        browser.wait_for_text("3", HOUSEHOLDS_COUNT)

        new_household = HouseholdFactory(size=2, business_area=business_area, program=program)
        browser.click('button[data-cy="button-rebuild"]')
        browser.wait_for_text("Payment Plan has been rebuilt.")
        browser.wait_for_text("4", HOUSEHOLDS_COUNT)
        browser.assert_text(new_household.unicef_id, "table")
        assert built_tp.payment_items.count() == 4


def test_delete_open_tp_removes_it_from_the_list(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    built_tp: PaymentPlan,
) -> None:
    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.TARGETING_VIEW_LIST,
        Permissions.TARGETING_VIEW_DETAILS,
        Permissions.TARGETING_REMOVE,
    ):
        browser.login(username="noperm_user")
        browser.open(tp_url(built_tp))
        browser.click('button[data-cy="button-delete"]')
        browser.click('[role="dialog"] button[data-cy="button-delete"]')

        browser.wait_for_text("Target Population Deleted")
        browser.wait_for_text("No results", "table")
        browser.assert_text_not_visible(BUILT_TP_NAME, "table")
        assert not PaymentPlan.objects.filter(id=built_tp.id).exists()


def test_duplicate_locked_tp_creates_open_copy(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    locked_tp: PaymentPlan,
) -> None:
    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.TARGETING_VIEW_DETAILS,
        Permissions.TARGETING_DUPLICATE,
        Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST,
        Permissions.PM_PROGRAMME_CYCLE_VIEW_LIST,
    ):
        browser.login(username="noperm_user")
        browser.open(tp_url(locked_tp))
        browser.wait_for_text("LOCKED", STATUS)

        browser.click('button[data-cy="button-target-population-duplicate"]')
        browser.type('input[name="name"]', "Copy of locked TP")
        browser.click('[data-cy="filters-program-cycle-autocomplete"]')
        browser.select_listbox_element(CYCLE_TITLE)
        browser.wait_for_element_clickable('[data-cy="filters-payment-plan-group-autocomplete"] input')
        browser.click('[data-cy="filters-payment-plan-group-autocomplete"]')
        browser.select_listbox_element(GROUP_NAME)
        browser.select_chip_option(PURPOSE_NAME, '[data-cy="input-payment-plan-purposes"]')
        browser.click('[role="dialog"] [data-cy="button-target-population-duplicate"]')

        browser.wait_for_text("Copy of locked TP", 'h5[data-cy="page-header-title"]')
        browser.wait_for_text("OPEN", STATUS)
        browser.wait_for_text("3", HOUSEHOLDS_COUNT)
        locked_tp.refresh_from_db()
        assert locked_tp.status == PaymentPlan.Status.TP_LOCKED
