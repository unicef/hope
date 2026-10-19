import pytest

from e2e.new_selenium.conftest import grant_permission
from extras.test_utils.factories import TicketNeedsAdjudicationDetailsFactory
from extras.test_utils.selenium import HopeTestBrowser
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.models import GrievanceTicket
from hope.models import BusinessArea, Household, PaymentPlan, PaymentPlanGroup, User

from .conftest import CYCLE_TITLE, GROUP_NAME, PURPOSE_NAME

pytestmark = pytest.mark.django_db()

HOUSEHOLDS_COUNT = '[data-cy="total-number-of-households-count"]'
HOUSEHOLD_SIZE = "What is the Household size?"
CREATE_PERMISSIONS = (
    Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
    Permissions.TARGETING_VIEW_LIST,
    Permissions.TARGETING_VIEW_DETAILS,
    Permissions.TARGETING_CREATE,
    Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST,
    Permissions.PM_PROGRAMME_CYCLE_VIEW_LIST,
)


def open_new_tp_form(browser: HopeTestBrowser, group: PaymentPlanGroup, name: str) -> None:
    program = group.cycle.program
    browser.open(f"/{program.business_area.slug}/programs/{program.code}/target-population/create")
    browser.click('[data-cy="filters-program-cycle-autocomplete"]')
    browser.select_listbox_element(CYCLE_TITLE)
    browser.wait_for_element_clickable('[data-cy="filters-payment-plan-group-autocomplete"] input')
    browser.click('[data-cy="filters-payment-plan-group-autocomplete"]')
    browser.select_listbox_element(GROUP_NAME)
    browser.type('input[data-cy="input-name"]', name)
    browser.select_chip_option(PURPOSE_NAME, '[data-cy="input-payment-plan-purposes"]')


def add_household_size_criteria(browser: HopeTestBrowser, size_from: int, size_to: int) -> None:
    browser.click('[data-cy="button-target-population-add-criteria"]')
    browser.click('[role="dialog"] button[data-cy="button-household-rule"]')
    browser.click('input[data-cy="autocomplete-target-criteria-option-0"]')
    browser.select_listbox_element(HOUSEHOLD_SIZE)
    browser.type('input[data-cy="input-householdsFiltersBlocks[0].value.from"]', str(size_from))
    browser.type('input[data-cy="input-householdsFiltersBlocks[0].value.to"]', str(size_to))
    browser.click('[role="dialog"] button[data-cy="button-target-population-add-criteria"]')


def accept_missing_fsp_warning(browser: HopeTestBrowser) -> None:
    browser.click('button[data-cy="button-confirm"]')
    browser.wait_for_element_absent('[role="dialog"]')


def save_new_tp(browser: HopeTestBrowser, name: str) -> PaymentPlan:
    browser.click('button[data-cy="button-target-population-create"]')
    browser.wait_for_text(name, 'h5[data-cy="page-header-title"]', timeout=20)
    return PaymentPlan.objects.get(name=name)


def targeted_household_ids(tp: PaymentPlan) -> set[str]:
    return set(tp.payment_items.values_list("household__unicef_id", flat=True))


def test_household_size_rule_targets_only_matching_households(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    targeting_group: PaymentPlanGroup,
    sized_households: list[Household],
) -> None:
    with grant_permission(user_with_no_permissions, business_area, *CREATE_PERMISSIONS):
        browser.login(username="noperm_user")
        open_new_tp_form(browser, targeting_group, "Size 2 to 4")
        add_household_size_criteria(browser, 2, 4)
        accept_missing_fsp_warning(browser)
        browser.assert_text(f"{HOUSEHOLD_SIZE}: 2 - 4", '[data-cy="criteria-container"]')
        tp = save_new_tp(browser, "Size 2 to 4")

        browser.wait_for_text("1", HOUSEHOLDS_COUNT)
        browser.assert_text(sized_households[1].unicef_id, "table")
        assert targeted_household_ids(tp) == {sized_households[1].unicef_id}


def test_or_criteria_target_households_matching_either_rule(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    targeting_group: PaymentPlanGroup,
    sized_households: list[Household],
) -> None:
    smallest, middle, largest = sized_households
    with grant_permission(user_with_no_permissions, business_area, *CREATE_PERMISSIONS):
        browser.login(username="noperm_user")
        open_new_tp_form(browser, targeting_group, "Smallest or largest")
        add_household_size_criteria(browser, 1, 1)
        accept_missing_fsp_warning(browser)
        browser.assert_text("ADD 'OR' FILTER", 'button[data-cy="button-target-population-add-criteria"]')
        add_household_size_criteria(browser, 5, 5)
        browser.wait_for_element_absent('[role="dialog"]')
        tp = save_new_tp(browser, "Smallest or largest")

        browser.wait_for_text("2", HOUSEHOLDS_COUNT)
        browser.assert_text_not_visible(middle.unicef_id, "table")
        assert targeted_household_ids(tp) == {smallest.unicef_id, largest.unicef_id}


def test_exclude_active_adjudication_ticket_flag_drops_household(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    targeting_group: PaymentPlanGroup,
    sized_households: list[Household],
) -> None:
    flagged = sized_households[0]
    TicketNeedsAdjudicationDetailsFactory(
        ticket__business_area=business_area,
        ticket__status=GrievanceTicket.STATUS_IN_PROGRESS,
        golden_records_individual=flagged.head_of_household,
    )
    with grant_permission(user_with_no_permissions, business_area, *CREATE_PERMISSIONS):
        browser.login(username="noperm_user")
        open_new_tp_form(browser, targeting_group, "Without adjudication")
        add_household_size_criteria(browser, 1, 10)
        accept_missing_fsp_warning(browser)
        browser.click('[data-cy="input-flagExcludeIfActiveAdjudicationTicket"]')
        tp = save_new_tp(browser, "Without adjudication")

        browser.wait_for_text("2", HOUSEHOLDS_COUNT)
        browser.assert_text_not_visible(flagged.unicef_id, "table")
        assert targeted_household_ids(tp) == {household.unicef_id for household in sized_households[1:]}


def test_exclude_household_id_in_standard_programme(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    built_tp: PaymentPlan,
    sized_households: list[Household],
) -> None:
    excluded = sized_households[2]
    program = built_tp.program_cycle.program
    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.TARGETING_VIEW_DETAILS,
        Permissions.TARGETING_UPDATE,
        Permissions.PM_PROGRAMME_CYCLE_VIEW_LIST,
        Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST,
    ):
        browser.login(username="noperm_user")
        browser.open(f"/{business_area.slug}/programs/{program.code}/target-population/edit-tp/{built_tp.id}")
        browser.click('[data-cy="button-show-hide-exclusions"]')
        browser.type('[data-cy="input-excluded-ids"] input', excluded.unicef_id)
        browser.type('[data-cy="input-exclusion-reason"] textarea', "Moved away")
        browser.click('[data-cy="button-save"]')

        browser.wait_for_element_absent('[data-cy="edit-target-population-form"]', timeout=20)
        browser.wait_for_text("2", HOUSEHOLDS_COUNT, timeout=20)
        browser.assert_text_not_visible(excluded.unicef_id, "table")
        built_tp.refresh_from_db()
        assert built_tp.excluded_ids == excluded.unicef_id
        assert excluded.unicef_id not in targeted_household_ids(built_tp)
