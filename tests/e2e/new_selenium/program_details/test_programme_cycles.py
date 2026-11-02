from datetime import date

import pytest

from e2e.new_selenium.conftest import grant_permission
from extras.test_utils.selenium import HopeTestBrowser
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, Program, User

from .conftest import days_from_today

pytestmark = pytest.mark.django_db()

ROW = 'tr[data-cy="program-cycle-row"]'
DIALOG = 'div[role="dialog"]'
ADD_CYCLE = 'button[data-cy="button-add-new-programme-cycle"]'
TITLE_INPUT = f'{DIALOG} input[data-cy="input-title"]'
START_DATE = 'div[data-cy="start-date-cycle"]'
END_DATE = 'div[data-cy="end-date-cycle"]'
START_DATE_INPUT = f'{START_DATE} input[name="startDate"]'
END_DATE_INPUT = f'{END_DATE} input[name="endDate"]'
CREATE_CYCLE = 'button[data-cy="button-create-program-cycle"]'
SAVE_CYCLE = f'{DIALOG} button[data-cy="button-save"]'

CYCLE_PERMISSIONS = (
    Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
    Permissions.PM_PROGRAMME_CYCLE_VIEW_LIST,
    Permissions.PM_PROGRAMME_CYCLE_CREATE,
    Permissions.PM_PROGRAMME_CYCLE_UPDATE,
    Permissions.PM_PROGRAMME_CYCLE_DELETE,
)


def details_url(program: Program) -> str:
    return f"/{program.business_area.slug}/programs/{program.code}/details/{program.code}"


def row_cell(index: int, cell: str) -> str:
    return f'{ROW}:nth-of-type({index}) td[data-cy="program-cycle-{cell}"]'


def shown(day: date) -> str:
    return day.strftime("%-d %b %Y")


def open_programme(browser: HopeTestBrowser, program: Program, rows: int) -> None:
    browser.login(username="noperm_user")
    browser.open(details_url(program))
    browser.wait_for_element_visible(f"{ROW}:nth-of-type({rows})")


def fill_new_cycle(browser: HopeTestBrowser, title: str, start: date) -> None:
    browser.wait_for_element_visible(TITLE_INPUT)
    browser.type(TITLE_INPUT, title)
    browser.fill_date(START_DATE_INPUT, start.isoformat())


def test_add_programme_cycle(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    active_programme_with_finished_cycle: Program,
) -> None:
    start = days_from_today(1)
    end = days_from_today(10)
    with grant_permission(user_with_no_permissions, business_area, *CYCLE_PERMISSIONS):
        open_programme(browser, active_programme_with_finished_cycle, rows=1)

        browser.click(ADD_CYCLE)
        fill_new_cycle(browser, "123", start)
        browser.fill_date(END_DATE_INPUT, end.isoformat())
        browser.click(CREATE_CYCLE)

        browser.wait_for_element_visible(f"{ROW}:nth-of-type(2)")
        browser.assert_text("123", row_cell(2, "title"))
        browser.assert_text("Draft", row_cell(2, "status"))
        browser.assert_text(shown(start), row_cell(2, "start-date"))
        browser.assert_text(shown(end), row_cell(2, "end-date"))
        cycle = active_programme_with_finished_cycle.cycles.get(title="123")
        assert (cycle.start_date, cycle.end_date) == (start, end)


def test_add_programme_cycle_without_end_date(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    active_programme_with_finished_cycle: Program,
) -> None:
    start = days_from_today(11)
    with grant_permission(user_with_no_permissions, business_area, *CYCLE_PERMISSIONS):
        open_programme(browser, active_programme_with_finished_cycle, rows=1)

        browser.click(ADD_CYCLE)
        fill_new_cycle(browser, "Test %$ What?", start)
        browser.click(CREATE_CYCLE)

        browser.wait_for_element_visible(f"{ROW}:nth-of-type(2)")
        browser.assert_text("Test %$ What?", row_cell(2, "title"))
        browser.assert_text("Draft", row_cell(2, "status"))
        browser.assert_text(shown(start), row_cell(2, "start-date"))
        browser.assert_exact_text("-", row_cell(2, "end-date"))
        cycle = active_programme_with_finished_cycle.cycles.get(title="Test %$ What?")
        assert (cycle.start_date, cycle.end_date) == (start, None)


def test_add_programme_cycle_sets_end_date_of_open_ended_cycle_first(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    programme_with_open_ended_cycle: Program,
) -> None:
    today = days_from_today(0)
    tomorrow = days_from_today(1)
    with grant_permission(user_with_no_permissions, business_area, *CYCLE_PERMISSIONS):
        open_programme(browser, programme_with_open_ended_cycle, rows=1)
        browser.assert_text("-", row_cell(1, "end-date"))

        browser.click(ADD_CYCLE)
        browser.fill_date(f'{DIALOG} input[name="endDate"]', today.isoformat())
        browser.click('button[data-cy="button-update-program-cycle-modal"]')
        fill_new_cycle(browser, "Test Title", tomorrow)
        browser.fill_date(END_DATE_INPUT, tomorrow.isoformat())
        browser.click(CREATE_CYCLE)

        browser.wait_for_element_visible(f"{ROW}:nth-of-type(2)")
        browser.assert_text(shown(today), row_cell(1, "end-date"))
        browser.assert_text("Test Title", row_cell(2, "title"))
        browser.assert_text(shown(tomorrow), row_cell(2, "start-date"))
        browser.assert_text(shown(tomorrow), row_cell(2, "end-date"))
        assert programme_with_open_ended_cycle.cycles.get(title="Default Programme Cycle").end_date == today


def test_cancel_after_setting_end_date_keeps_the_end_date(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    programme_with_open_ended_cycle: Program,
) -> None:
    today = days_from_today(0)
    with grant_permission(user_with_no_permissions, business_area, *CYCLE_PERMISSIONS):
        open_programme(browser, programme_with_open_ended_cycle, rows=1)

        browser.click(ADD_CYCLE)
        browser.fill_date(f'{DIALOG} input[name="endDate"]', today.isoformat())
        browser.click('button[data-cy="button-update-program-cycle-modal"]')
        browser.wait_for_element_visible(CREATE_CYCLE)
        browser.click(f'{DIALOG} button[data-cy="button-cancel"]')

        browser.wait_for_element_absent(DIALOG)
        browser.wait_for_text(shown(today), row_cell(1, "end-date"))
        browser.assert_element_absent(f"{ROW}:nth-of-type(2)")
        assert programme_with_open_ended_cycle.cycles.get().end_date == today


@pytest.mark.parametrize(
    ("start_days", "end_days", "field", "message"),
    [
        (-40, 1, START_DATE, "Start Date cannot be before Programme Start Date"),
        (1, 121, END_DATE, "End Date cannot be after Programme End Date"),
    ],
    ids=["start-before-programme", "end-after-programme"],
)
def test_add_programme_cycle_outside_programme_dates(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    active_programme_with_finished_cycle: Program,
    start_days: int,
    end_days: int,
    field: str,
    message: str,
) -> None:
    with grant_permission(user_with_no_permissions, business_area, *CYCLE_PERMISSIONS):
        open_programme(browser, active_programme_with_finished_cycle, rows=1)

        browser.click(ADD_CYCLE)
        fill_new_cycle(browser, "Wrong dates", days_from_today(start_days))
        browser.fill_date(END_DATE_INPUT, days_from_today(end_days).isoformat())
        browser.click(CREATE_CYCLE)

        browser.wait_for_text(message, field)
        assert active_programme_with_finished_cycle.cycles.count() == 1


def test_add_programme_cycle_starting_before_latest_cycle_end_fails(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    active_programme_with_finished_cycle: Program,
) -> None:
    with grant_permission(user_with_no_permissions, business_area, *CYCLE_PERMISSIONS):
        open_programme(browser, active_programme_with_finished_cycle, rows=1)

        browser.click(ADD_CYCLE)
        fill_new_cycle(browser, "Overlapping", days_from_today(-1))
        browser.fill_date(END_DATE_INPUT, days_from_today(1).isoformat())
        browser.click(CREATE_CYCLE)

        browser.wait_for_text("Start date must be after the latest cycle end date.")
        assert active_programme_with_finished_cycle.cycles.count() == 1


def test_edit_programme_cycle(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    programme_with_draft_cycle: Program,
) -> None:
    start = days_from_today(11)
    end = days_from_today(12)
    with grant_permission(user_with_no_permissions, business_area, *CYCLE_PERMISSIONS):
        open_programme(browser, programme_with_draft_cycle, rows=1)

        browser.click(f'{row_cell(1, "details-btn")} button[data-cy="button-edit-program-cycle"]')
        browser.wait_for_element_visible(TITLE_INPUT)
        browser.clear(TITLE_INPUT)
        browser.type(TITLE_INPUT, "Edited title check")
        browser.fill_date(START_DATE_INPUT, start.isoformat())
        browser.fill_date(END_DATE_INPUT, end.isoformat())
        browser.click(SAVE_CYCLE)

        browser.wait_for_text("Edited title check", row_cell(1, "title"))
        browser.assert_text(shown(start), row_cell(1, "start-date"))
        browser.assert_text(shown(end), row_cell(1, "end-date"))
        cycle = programme_with_draft_cycle.cycles.get()
        assert (cycle.title, cycle.start_date, cycle.end_date) == ("Edited title check", start, end)


@pytest.mark.parametrize(
    ("start_days", "end_days", "field", "message"),
    [
        (-40, 17, START_DATE, "Start Date cannot be before Programme Start Date"),
        (11, 121, END_DATE, "End Date cannot be after Programme End Date"),
    ],
    ids=["start-before-programme", "end-after-programme"],
)
def test_edit_programme_cycle_outside_programme_dates(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    programme_with_mixed_cycles: Program,
    start_days: int,
    end_days: int,
    field: str,
    message: str,
) -> None:
    with grant_permission(user_with_no_permissions, business_area, *CYCLE_PERMISSIONS):
        open_programme(browser, programme_with_mixed_cycles, rows=3)

        browser.click(f'{row_cell(2, "details-btn")} button[data-cy="button-edit-program-cycle"]')
        browser.wait_for_element_visible(TITLE_INPUT)
        browser.fill_date(START_DATE_INPUT, days_from_today(start_days).isoformat())
        browser.fill_date(END_DATE_INPUT, days_from_today(end_days).isoformat())
        browser.click(SAVE_CYCLE)

        browser.wait_for_text(message, field)
        cycle = programme_with_mixed_cycles.cycles.get(title="Active Cycle")
        assert (cycle.start_date, cycle.end_date) == (days_from_today(11), days_from_today(17))


def test_delete_programme_cycle(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    programme_with_three_draft_cycles: Program,
) -> None:
    with grant_permission(user_with_no_permissions, business_area, *CYCLE_PERMISSIONS):
        open_programme(browser, programme_with_three_draft_cycles, rows=3)

        browser.click(f'{row_cell(2, "details-btn")} button[data-cy="delete-programme-cycle"]')
        browser.click('button[data-cy="button-delete"]')

        browser.wait_for_element_absent(f"{ROW}:nth-of-type(3)")
        browser.assert_text("First Cycle", row_cell(1, "title"))
        browser.assert_text("Third Cycle", row_cell(2, "title"))
        assert not programme_with_three_draft_cycles.cycles.filter(title="Second Cycle").exists()


def test_cycle_actions_depend_on_cycle_status(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    programme_with_mixed_cycles: Program,
) -> None:
    with grant_permission(user_with_no_permissions, business_area, *CYCLE_PERMISSIONS):
        open_programme(browser, programme_with_mixed_cycles, rows=3)

        browser.assert_element(f'{row_cell(1, "details-btn")} button[data-cy="button-edit-program-cycle"]')
        browser.assert_element(f'{row_cell(1, "details-btn")} button[data-cy="delete-programme-cycle"]')
        browser.assert_element(f'{row_cell(2, "details-btn")} button[data-cy="button-edit-program-cycle"]')
        browser.assert_elements_absent(
            f'{row_cell(2, "details-btn")} button[data-cy="delete-programme-cycle"]',
            f'{row_cell(3, "details-btn")} button[data-cy="button-edit-program-cycle"]',
            f'{row_cell(3, "details-btn")} button[data-cy="delete-programme-cycle"]',
        )


def test_programme_cycle_shows_payment_totals(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    programme_with_open_ended_cycle: Program,
) -> None:
    with grant_permission(user_with_no_permissions, business_area, *CYCLE_PERMISSIONS):
        open_programme(browser, programme_with_open_ended_cycle, rows=1)

        browser.assert_text("1,234.99", row_cell(1, "total-entitled-quantity-usd"))
        browser.assert_text("1,184.98", row_cell(1, "total-undelivered-quantity-usd"))
        browser.assert_text("50.01", row_cell(1, "total-delivered-quantity-usd"))
