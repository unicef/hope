import pytest

from e2e.new_selenium.conftest import grant_permission
from extras.test_utils.selenium import HopeTestBrowser
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, ProgramCycle, User

pytestmark = pytest.mark.django_db()

ROW = 'tr[data-cy="program-cycle-row"]'
STATUS = 'div[data-cy="status-container"]'


def row_cell(index: int, cell: str) -> str:
    return f'{ROW}:nth-of-type({index}) td[data-cy="program-cycle-{cell}"]'


def cycles_url(cycle: ProgramCycle) -> str:
    program = cycle.program
    return f"/{program.business_area.slug}/programs/{program.code}/payment-module/program-cycles"


def test_program_cycles_list_shows_status_and_totals(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    active_cycle_with_payment_plans: ProgramCycle,
) -> None:
    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.PM_PROGRAMME_CYCLE_VIEW_LIST,
    ):
        browser.login(username="noperm_user")
        browser.open(cycles_url(active_cycle_with_payment_plans))
        browser.wait_for_element_visible(f"{ROW}:nth-of-type(3)")

        browser.assert_text("Default Programme Cycle", row_cell(1, "title"))
        browser.assert_text("Finished", row_cell(1, "status"))
        browser.assert_exact_text("0", row_cell(1, "total-entitled-quantity-usd"))
        browser.assert_text("Test Programme Cycle 001", row_cell(2, "title"))
        browser.assert_text("Active", row_cell(2, "status"))
        browser.assert_text("1,833.99", row_cell(2, "total-entitled-quantity-usd"))
        browser.assert_text("Programme Cycle in Draft", row_cell(3, "title"))
        browser.assert_text("Draft", row_cell(3, "status"))
        browser.assert_exact_text("0", row_cell(3, "total-entitled-quantity-usd"))


def test_program_cycle_details_shows_status_and_dates(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    active_cycle: ProgramCycle,
) -> None:
    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.PM_PROGRAMME_CYCLE_VIEW_LIST,
        Permissions.PM_PROGRAMME_CYCLE_VIEW_DETAILS,
        Permissions.PM_VIEW_LIST,
    ):
        browser.login(username="noperm_user")
        browser.open(cycles_url(active_cycle))
        browser.click_link("Test Programme Cycle 001")

        browser.wait_for_text("Test Programme Cycle 001", 'h5[data-cy="page-header-title"]')
        browser.assert_text("Active", STATUS)
        browser.assert_text(active_cycle.start_date.strftime("%-d %b %Y"), 'div[data-cy="label-Start Date"]')
        browser.assert_text(active_cycle.end_date.strftime("%-d %b %Y"), 'div[data-cy="label-End Date"]')


def test_finish_and_reactivate_program_cycle(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    active_cycle: ProgramCycle,
) -> None:
    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.PM_PROGRAMME_CYCLE_VIEW_DETAILS,
        Permissions.PM_VIEW_LIST,
        Permissions.PM_PROGRAMME_CYCLE_UPDATE,
    ):
        browser.login(username="noperm_user")
        browser.open(f"{cycles_url(active_cycle)}/{active_cycle.id}")
        browser.wait_for_text("Active", STATUS)

        browser.click('button[data-cy="button-finish-programme-cycle"]')
        browser.wait_for_text("Finished", STATUS)
        active_cycle.refresh_from_db()
        assert active_cycle.status == ProgramCycle.FINISHED

        browser.click('button[data-cy="button-reactivate-programme-cycle"]')
        browser.wait_for_text("Active", STATUS)
        active_cycle.refresh_from_db()
        assert active_cycle.status == ProgramCycle.ACTIVE


def test_finish_program_cycle_with_unreconciled_payment_plans_fails(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    active_cycle_with_payment_plans: ProgramCycle,
) -> None:
    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.PM_PROGRAMME_CYCLE_VIEW_DETAILS,
        Permissions.PM_VIEW_LIST,
        Permissions.PM_PROGRAMME_CYCLE_UPDATE,
    ):
        browser.login(username="noperm_user")
        browser.open(f"{cycles_url(active_cycle_with_payment_plans)}/{active_cycle_with_payment_plans.id}")
        browser.wait_for_text("Active", STATUS)

        browser.click('button[data-cy="button-finish-programme-cycle"]')
        browser.wait_for_text("All Payment Plans and Follow-Up Payment Plans have to be Reconciled.")
        browser.assert_text("Active", STATUS)
        active_cycle_with_payment_plans.refresh_from_db()
        assert active_cycle_with_payment_plans.status == ProgramCycle.ACTIVE
