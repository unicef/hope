import pytest

from e2e.new_selenium.conftest import grant_permission
from extras.test_utils.selenium import HopeTestBrowser, ui_date
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, Program, User

from .conftest import details_url

pytestmark = pytest.mark.django_db()

STATUS = 'div[data-cy="status-container"]'
FINISH_DIALOG_BUTTON = 'div[role="dialog"] button[data-cy="button-finish-program"]'


def test_draft_programme_details(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    draft_programme: Program,
) -> None:
    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.PROGRAMME_UPDATE,
        Permissions.PROGRAMME_REMOVE,
        Permissions.PROGRAMME_ACTIVATE,
    ):
        browser.login(username="noperm_user")
        browser.open(details_url(draft_programme))

        browser.wait_for_text(draft_programme.name, 'h5[data-cy="page-header-title"]')
        browser.assert_text("DRAFT", STATUS)
        browser.assert_text(ui_date(draft_programme.start_date), 'div[data-cy="label-START DATE"]')
        browser.assert_text(ui_date(draft_programme.end_date), 'div[data-cy="label-END DATE"]')
        browser.assert_text(draft_programme.code, 'div[data-cy="label-Programme Code"]')
        browser.assert_text(draft_programme.data_collecting_type.label, 'div[data-cy="label-Data Collecting Type"]')
        browser.assert_text("One-off", 'div[data-cy="label-Frequency of Payment"]')
        browser.assert_text("No", 'div[data-cy="label-CASH+"]')
        browser.assert_text("0", 'div[data-cy="label-Programme size"]')
        browser.assert_text("Activate the Programme to create a Cycle")
        browser.wait_for_element_visible('button[data-cy="button-activate-program"]')
        browser.wait_for_element_visible('button[data-cy="button-edit-program"]')
        browser.wait_for_element_visible('button[data-cy="button-remove-program"]')


def test_activate_programme(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    draft_programme: Program,
) -> None:
    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.PROGRAMME_ACTIVATE,
        Permissions.PM_PROGRAMME_CYCLE_VIEW_LIST,
    ):
        browser.login(username="noperm_user")
        browser.open(details_url(draft_programme))
        browser.wait_for_text("DRAFT", STATUS)

        browser.click('button[data-cy="button-activate-program"]')
        browser.click('button[data-cy="button-activate-program-modal"]')
        browser.wait_for_text("ACTIVE", STATUS)
        browser.wait_for_text("Default Programme Cycle", 'td[data-cy="program-cycle-title"]')
        draft_programme.refresh_from_db()
        assert draft_programme.status == Program.ACTIVE


def test_finish_programme(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    active_programme_with_finished_cycle: Program,
) -> None:
    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.PROGRAMME_FINISH,
    ):
        browser.login(username="noperm_user")
        browser.open(details_url(active_programme_with_finished_cycle))
        browser.wait_for_text("ACTIVE", STATUS)

        browser.click('button[data-cy="button-finish-program"]')
        browser.click(FINISH_DIALOG_BUTTON)
        browser.wait_for_text("FINISHED", STATUS)
        # Without PM_PROGRAMME_CYCLE_VIEW_LIST the cycles table is hidden instead of the page.
        browser.assert_elements_absent("table", 'h1[data-cy="access-denied-title"]')
        active_programme_with_finished_cycle.refresh_from_db()
        assert active_programme_with_finished_cycle.status == Program.FINISHED


def test_finish_programme_with_active_cycle_fails(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    active_programme_with_active_cycle: Program,
) -> None:
    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.PROGRAMME_FINISH,
    ):
        browser.login(username="noperm_user")
        browser.open(details_url(active_programme_with_active_cycle))
        browser.wait_for_text("ACTIVE", STATUS)

        browser.click('button[data-cy="button-finish-program"]')
        browser.click(FINISH_DIALOG_BUTTON)
        browser.wait_for_text("Cannot finish Program with active cycles.")
        browser.assert_text("ACTIVE", STATUS)
        active_programme_with_active_cycle.refresh_from_db()
        assert active_programme_with_active_cycle.status == Program.ACTIVE
