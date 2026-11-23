import pytest

from e2e.new_selenium.conftest import grant_permission
from extras.test_utils.factories import RegistrationDataImportFactory
from extras.test_utils.selenium import HopeTestBrowser
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, PaymentPlanPurpose, Program, User

from .conftest import (
    BA_PURPOSE_NAME,
    SECOND_BA_PURPOSE_NAME,
    add_time_series_field,
    days_from_today,
    details_url,
    fill_programme_create_required_fields,
    navigate_to_programme_management,
)

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
        Permissions.PM_PAYMENT_PLAN_PURPOSE_VIEW_LIST,
    ):
        browser.login(username="noperm_user")
        browser.open(f"/{business_area.slug}/programs/{program_with_purpose.code}/details/{program_with_purpose.code}")
        browser.wait_for_element_clickable('button[data-cy="button-edit-program"]').click()
        browser.wait_for_element_clickable('li[data-cy="menu-item-edit-details"]').click()

        browser.wait_for_element_visible('input[name="name"]')
        browser.clear('input[name="name"]')
        browser.type('input[name="name"]', "Updated Programme Name")

        browser.fill_date('input[name="startDate"]', "2022-01-01")
        browser.click('input[name="name"]')

        browser.fill_date('input[name="endDate"]', "2099-10-01")
        browser.click('input[name="name"]')

        browser.click('button[data-cy="button-next"]')
        browser.wait_for_element_visible('button[data-cy="button-add-time-series-field"]')
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
        Permissions.PM_PAYMENT_PLAN_PURPOSE_VIEW_LIST,
    ):
        browser.login(username="noperm_user")
        browser.open(f"/{business_area.slug}/programs/{program_with_purpose.code}/details/{program_with_purpose.code}")
        browser.wait_for_element_clickable('button[data-cy="button-edit-program"]').click()
        browser.wait_for_element_clickable('li[data-cy="menu-item-edit-details"]').click()

        browser.wait_for_element_visible('[data-cy="input-payment-plan-purposes"]')
        browser.click('[data-cy="input-payment-plan-purposes"] input')
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
        Permissions.PM_PAYMENT_PLAN_PURPOSE_VIEW_LIST,
    ):
        browser.login(username="noperm_user")
        browser.open(f"/{business_area.slug}/programs/{program_with_purpose.code}/details/{program_with_purpose.code}")
        browser.wait_for_element_clickable('button[data-cy="button-edit-program"]').click()
        browser.wait_for_element_clickable('li[data-cy="menu-item-edit-details"]').click()

        browser.wait_for_element_visible('[data-cy="input-payment-plan-purposes"]')
        browser.select_chip_option(SECOND_BA_PURPOSE_NAME, '[data-cy="input-payment-plan-purposes"]')

        browser.click('button[data-cy="button-next"]')
        browser.wait_for_element_visible('button[data-cy="button-add-time-series-field"]')
        browser.wait_for_element_visible('button[data-cy="button-save"]').click()

        browser.wait_for_element_visible('div[data-cy="label-Payment Plan Purposes"]')
        browser.assert_text(BA_PURPOSE_NAME, 'div[data-cy="label-Payment Plan Purposes"]')
        browser.assert_text(SECOND_BA_PURPOSE_NAME, 'div[data-cy="label-Payment Plan Purposes"]')


def test_edit_programme_max_ten_purposes_enforced(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    program_with_ten_purposes: Program,
) -> None:
    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.PROGRAMME_UPDATE,
        Permissions.USER_MANAGEMENT_VIEW_LIST,
        Permissions.GEO_VIEW_LIST,
        Permissions.PM_PAYMENT_PLAN_PURPOSE_VIEW_LIST,
    ):
        browser.login(username="noperm_user")
        browser.open(
            f"/{business_area.slug}/programs/{program_with_ten_purposes.code}/details/{program_with_ten_purposes.code}"
        )
        browser.wait_for_element_clickable('button[data-cy="button-edit-program"]').click()
        browser.wait_for_element_clickable('li[data-cy="menu-item-edit-details"]').click()

        browser.wait_for_element_visible('[data-cy="input-payment-plan-purposes"]')

        # All 10 purposes are already selected — the input is disabled and cannot be opened
        browser.click('[data-cy="input-payment-plan-purposes"]')
        browser.assert_element_absent('ul[role="listbox"]')


def test_edit_programme_end_date_before_latest_cycle_fails(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    programme_with_mixed_cycles: Program,
) -> None:
    program = programme_with_mixed_cycles
    end_date = program.end_date
    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.PROGRAMME_UPDATE,
        Permissions.USER_MANAGEMENT_VIEW_LIST,
        Permissions.GEO_VIEW_LIST,
        Permissions.PM_PAYMENT_PLAN_PURPOSE_VIEW_LIST,
    ):
        browser.login(username="noperm_user")
        browser.open(details_url(program))
        browser.wait_for_element_clickable('button[data-cy="button-edit-program"]').click()
        browser.wait_for_element_clickable('li[data-cy="menu-item-edit-details"]').click()

        browser.wait_for_element_visible('input[name="name"]')
        browser.fill_date('input[name="endDate"]', days_from_today(5).isoformat())
        browser.click('input[name="name"]')
        browser.click('button[data-cy="button-next"]')
        browser.wait_for_element_visible('button[data-cy="button-add-time-series-field"]')
        browser.wait_for_element_visible('button[data-cy="button-save"]').click()

        browser.wait_for_text("End date must be the same as or after the latest cycle.")
        browser.assert_element('button[data-cy="button-save"]')
        program.refresh_from_db()
        assert program.end_date == end_date


def test_edit_programme_with_rdi_locks_time_series_fields(
    browser: HopeTestBrowser, ba_purpose: PaymentPlanPurpose
) -> None:
    browser.login()
    navigate_to_programme_management(browser)
    browser.click('a[data-cy="button-new-program"]')
    fill_programme_create_required_fields(browser, sector="Health", dct="Partial", beneficiary_group="People")
    browser.click('[data-cy="input-cashPlus"]')
    browser.click('button[data-cy="button-next"]')
    add_time_series_field(
        browser, 0, label="Time Series Field Name 1", num_rounds="2", round_names=["Round 1", "Round 2"]
    )
    browser.click('button[data-cy="button-next"]')
    browser.select_dropdown_option("partnerAccess", "All Current Partners within the business area")
    browser.click('button[data-cy="button-save"]')
    browser.wait_for_element_visible('button[data-cy="button-edit-program"]')
    program = Program.objects.get(name="Test Programme")
    RegistrationDataImportFactory(program=program, business_area=program.business_area)
    # The RDI was created behind the app's back, so reload to drop the cached programme.
    browser.refresh()

    browser.wait_for_element_clickable('button[data-cy="button-edit-program"]').click()
    browser.wait_for_element_clickable('li[data-cy="menu-item-edit-details"]').click()
    browser.wait_for_element_visible('input[name="name"]')
    browser.clear('input[name="name"]')
    browser.type('input[name="name"]', "New name after Edit")
    browser.click('button[data-cy="button-next"]')

    browser.wait_for_element_visible('button[data-cy="button-add-time-series-field"]:disabled')
    browser.assert_element('input[data-cy="input-pduFields.0.label"]:disabled')
    browser.assert_element('div[data-cy="select-pduFields.0.pdu_data.subtype"][aria-disabled="true"]')
    browser.assert_element('input[data-cy="input-pduFields.0.pdu_data.rounds_names.0"]:disabled')
    browser.assert_element('input[data-cy="input-pduFields.0.pdu_data.rounds_names.1"]:disabled')

    # The number of rounds can only be increased.
    browser.click('div[data-cy="select-pduFields.0.pdu_data.number_of_rounds"]')
    browser.assert_element('ul[role="listbox"] li[data-value="1"][aria-disabled="true"]')
    browser.assert_element('ul[role="listbox"] li[data-value="2"]:not([aria-disabled="true"])')
    browser.assert_element('ul[role="listbox"] li[data-value="3"]:not([aria-disabled="true"])')
    browser.select_listbox_element("3")
    browser.assert_element('input[data-cy="input-pduFields.0.pdu_data.rounds_names.0"]:disabled')
    browser.assert_element('input[data-cy="input-pduFields.0.pdu_data.rounds_names.1"]:disabled')
    browser.type('input[data-cy="input-pduFields.0.pdu_data.rounds_names.2"]', "Round 3")
    browser.click('button[data-cy="button-save"]')

    browser.wait_for_text("New name after Edit", 'h5[data-cy="page-header-title"]')
    pdu_data = program.pdu_fields.get().pdu_data
    assert pdu_data.number_of_rounds == 3
    assert pdu_data.rounds_names == ["Round 1", "Round 2", "Round 3"]
