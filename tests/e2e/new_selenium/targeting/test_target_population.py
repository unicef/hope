import pytest

from e2e.new_selenium.conftest import grant_permission
from extras.test_utils.selenium import HopeTestBrowser
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, PaymentPlan, PaymentPlanGroup, PaymentPlanPurpose, ProgramCycle, User

from .conftest import (
    CYCLE_TITLE,
    GROUP_NAME,
    OTHER_PURPOSE_NAME,
    PURPOSE_NAME,
    SECOND_CYCLE_TITLE,
    SECOND_GROUP_NAME,
)

pytestmark = pytest.mark.django_db()


def test_tp_details_shows_group_and_purpose(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    targeting_tp: PaymentPlan,
) -> None:
    program = targeting_tp.program_cycle.program
    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.TARGETING_VIEW_DETAILS,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
    ):
        browser.login(username="noperm_user", password="testtest2")
        browser.open(f"/{business_area.slug}/programs/{program.code}/target-population/{targeting_tp.id}")
        browser.wait_for_element_visible('h5[data-cy="page-header-title"]')
        browser.assert_text(GROUP_NAME, 'div[data-cy="label-Payment Plan Group"]')
        browser.assert_text(PURPOSE_NAME, 'div[data-cy="label-Purposes"]')


def test_create_tp_with_group_and_purpose(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    targeting_group: PaymentPlanGroup,
    tp_purpose: PaymentPlanPurpose,
) -> None:
    program = targeting_group.cycle.program
    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.TARGETING_VIEW_LIST,
        Permissions.TARGETING_CREATE,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
    ):
        browser.login(username="noperm_user", password="testtest2")
        browser.open(f"/{business_area.slug}/programs/{program.code}/target-population/")
        browser.wait_for_element_clickable('a[data-cy="button-new-tp"]').click()
        browser.wait_for_element_visible('[data-cy="filters-program-cycle-autocomplete"]')

        browser.click('[data-cy="filters-program-cycle-autocomplete"]')
        browser.select_listbox_element(CYCLE_TITLE)

        browser.wait_for_element_clickable('[data-cy="filters-payment-plan-group-autocomplete"]')
        browser.click('[data-cy="filters-payment-plan-group-autocomplete"]')
        browser.select_listbox_element(GROUP_NAME)

        browser.wait_for_element_visible('input[data-cy="input-name"]')
        browser.type('input[data-cy="input-name"]', "E2E Create TP")

        browser.select_chip_option(PURPOSE_NAME, '[data-cy="input-payment-plan-purposes"]')

        # Add minimal criteria so the form can be submitted
        browser.wait_for_element_clickable('[data-cy="button-target-population-add-criteria"]').click()
        browser.wait_for_element_visible('textarea[data-cy="input-included-household-ids"]')
        browser.type('textarea[data-cy="input-included-household-ids"]', "HH-0001")
        browser.wait_for_element_clickable('[role="dialog"] [data-cy="button-target-population-add-criteria"]').click()
        browser.wait_for_element_absent('textarea[data-cy="input-included-household-ids"]')

        browser.wait_for_element_clickable('[data-cy="button-target-population-create"]').click()

        browser.wait_for_text("E2E Create TP", 'h5[data-cy="page-header-title"]')
        browser.assert_text(GROUP_NAME, 'div[data-cy="label-Payment Plan Group"]')
        browser.assert_text(PURPOSE_NAME, 'div[data-cy="label-Purposes"]')


def test_create_tp_dropdowns_show_only_relevant_options(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    targeting_group: PaymentPlanGroup,
    second_targeting_group: PaymentPlanGroup,
    other_purpose: PaymentPlanPurpose,
) -> None:
    program = targeting_group.cycle.program
    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.TARGETING_VIEW_LIST,
        Permissions.TARGETING_CREATE,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
    ):
        browser.login(username="noperm_user", password="testtest2")
        browser.open(f"/{business_area.slug}/programs/{program.code}/target-population/")
        browser.wait_for_element_clickable('a[data-cy="button-new-tp"]').click()

        browser.wait_for_element_visible('[data-cy="input-payment-plan-purposes"]')
        browser.click('[data-cy="input-payment-plan-purposes"]')
        browser.wait_for_text(PURPOSE_NAME, 'ul[role="listbox"]')
        browser.assert_text_not_visible(OTHER_PURPOSE_NAME, 'ul[role="listbox"]')
        browser.execute_script(
            "document.dispatchEvent(new KeyboardEvent('keydown', {key:'Escape', keyCode:27, bubbles:true}))"
        )
        browser.wait_for_element_absent('ul[role="listbox"]')

        browser.click('[data-cy="filters-program-cycle-autocomplete"]')
        browser.select_listbox_element(CYCLE_TITLE)
        browser.wait_for_element_clickable('[data-cy="filters-payment-plan-group-autocomplete"]')
        browser.click('[data-cy="filters-payment-plan-group-autocomplete"]')
        browser.wait_for_text(GROUP_NAME, 'ul[role="listbox"]')
        browser.assert_text_not_visible(SECOND_GROUP_NAME, 'ul[role="listbox"]')


def test_edit_tp_shows_group_and_purpose(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    targeting_tp: PaymentPlan,
    second_targeting_cycle: ProgramCycle,
    second_targeting_group: PaymentPlanGroup,
) -> None:
    program = targeting_tp.program_cycle.program
    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.TARGETING_VIEW_DETAILS,
        Permissions.TARGETING_UPDATE,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
    ):
        browser.login(username="noperm_user", password="testtest2")
        browser.open(f"/{business_area.slug}/programs/{program.code}/target-population/edit-tp/{targeting_tp.id}")
        browser.wait_for_element_visible('[data-cy="filters-program-cycle-autocomplete"]')

        # Purposes field is shown because targeting_tp is the latest plan in its cycle
        browser.wait_for_element_visible('[data-cy="input-payment-plan-purposes"]')

        # Change cycle — reveals Payment Plan Group selector
        browser.click('[data-cy="filters-program-cycle-autocomplete"]')
        browser.select_listbox_element(SECOND_CYCLE_TITLE)

        browser.wait_for_element_visible('[data-cy="filters-payment-plan-group-autocomplete"]')
        browser.click('[data-cy="filters-payment-plan-group-autocomplete"]')
        browser.select_listbox_element(SECOND_GROUP_NAME)

        browser.wait_for_element_clickable('[data-cy="button-save"]').click()

        browser.wait_for_element_visible('h5[data-cy="page-header-title"]')
        browser.assert_text(SECOND_GROUP_NAME, 'div[data-cy="label-Payment Plan Group"]')
        browser.assert_text(PURPOSE_NAME, 'div[data-cy="label-Purposes"]')


def test_duplicate_tp_with_group_and_purpose(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    targeting_tp: PaymentPlan,
    targeting_group: PaymentPlanGroup,
    tp_purpose: PaymentPlanPurpose,
) -> None:
    program = targeting_tp.program_cycle.program
    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.TARGETING_VIEW_DETAILS,
        Permissions.TARGETING_DUPLICATE,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
    ):
        browser.login(username="noperm_user", password="testtest2")
        browser.open(f"/{business_area.slug}/programs/{program.code}/target-population/{targeting_tp.id}")

        browser.wait_for_element_clickable('[data-cy="button-target-population-duplicate"]').click()
        browser.wait_for_element_visible('input[name="name"]')

        browser.type('input[name="name"]', "E2E Duplicate TP")

        browser.click('[data-cy="filters-program-cycle-autocomplete"]')
        browser.select_listbox_element(CYCLE_TITLE)

        browser.wait_for_element_clickable('[data-cy="filters-payment-plan-group-autocomplete"]')
        browser.click('[data-cy="filters-payment-plan-group-autocomplete"]')
        browser.select_listbox_element(GROUP_NAME)

        browser.select_chip_option(PURPOSE_NAME, '[data-cy="input-payment-plan-purposes"]')

        # Save the duplicate — same data-cy as the button that opened the dialog
        browser.wait_for_element_clickable('[role="dialog"] [data-cy="button-target-population-duplicate"]').click()

        browser.wait_for_text("E2E Duplicate TP", 'h5[data-cy="page-header-title"]')
        browser.assert_text(GROUP_NAME, 'div[data-cy="label-Payment Plan Group"]')
        browser.assert_text(PURPOSE_NAME, 'div[data-cy="label-Purposes"]')


def test_edit_latest_tp_purposes_are_editable(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    targeting_tp: PaymentPlan,
) -> None:
    program = targeting_tp.program_cycle.program
    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.TARGETING_VIEW_DETAILS,
        Permissions.TARGETING_UPDATE,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
    ):
        browser.login(username="noperm_user", password="testtest2")
        browser.open(f"/{business_area.slug}/programs/{program.code}/target-population/edit-tp/{targeting_tp.id}")
        browser.wait_for_element_visible('[data-cy="input-payment-plan-purposes"]')


def test_edit_non_latest_tp_purposes_not_editable(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    targeting_tp: PaymentPlan,
    later_tp: PaymentPlan,
) -> None:
    program = targeting_tp.program_cycle.program
    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.TARGETING_VIEW_DETAILS,
        Permissions.TARGETING_UPDATE,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
    ):
        browser.login(username="noperm_user", password="testtest2")
        browser.open(f"/{business_area.slug}/programs/{program.code}/target-population/edit-tp/{targeting_tp.id}")
        browser.wait_for_element_visible('[data-cy="filters-program-cycle-autocomplete"]')
        browser.assert_element_absent('[data-cy="input-payment-plan-purposes"]')
