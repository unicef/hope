from dateutil.relativedelta import relativedelta
from django.utils import timezone
import pytest

from e2e.new_selenium.conftest import grant_permission
from extras.test_utils.selenium import HopeTestBrowser, ui_date
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, PaymentPlanPurpose, Program, User

from .conftest import (
    BA_PURPOSE_NAME,
    OTHER_BA_PURPOSE_NAME,
    TEN_PURPOSE_NAMES,
    add_time_series_field,
    choose_partner,
    fill_programme_create_required_fields,
    navigate_to_programme_management,
)

pytestmark = pytest.mark.django_db()


def test_create_programme_mandatory_fields_only(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    ba_purpose: PaymentPlanPurpose,
) -> None:
    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.PROGRAMME_CREATE,
        Permissions.USER_MANAGEMENT_VIEW_LIST,
        Permissions.GEO_VIEW_LIST,
        Permissions.PM_PAYMENT_PLAN_PURPOSE_VIEW_LIST,
    ):
        browser.login(username="noperm_user")
        navigate_to_programme_management(browser)

        browser.click('a[data-cy="button-new-program"]')

        fill_programme_create_required_fields(browser)
        browser.click('button[data-cy="button-next"]')

        browser.wait_for_element_visible('button[data-cy="button-add-time-series-field"]')
        browser.click('button[data-cy="button-next"]')

        browser.wait_for_element_visible('button[data-cy="button-save"]').click()

        browser.wait_for_text("Test Programme", 'h5[data-cy="page-header-title"]')
        browser.assert_text("DRAFT", 'div[data-cy="status-container"]')
        browser.assert_text("1 May 2023", 'div[data-cy="label-START DATE"]')
        browser.assert_text("12 Dec 2033", 'div[data-cy="label-END DATE"]')
        browser.assert_text("Child Protection", 'div[data-cy="label-Sector"]')
        browser.assert_text("Household", 'div[data-cy="label-Payee Type"]')
        browser.assert_text("7700410", 'div[data-cy="label-GL Code"]')
        browser.assert_text("Full", 'div[data-cy="label-Data Collecting Type"]')
        browser.assert_text("Main Menu", 'div[data-cy="label-Payee Label"]')
        browser.assert_text("Regular", 'div[data-cy="label-Frequency of Payment"]')
        browser.assert_text("-", 'div[data-cy="label-Administrative Areas of implementation"]')
        browser.assert_text("No", 'div[data-cy="label-CASH+"]')
        browser.assert_text("0", 'div[data-cy="label-Programme size"]')
        browser.assert_text(BA_PURPOSE_NAME, 'div[data-cy="label-Payment Plan Purposes"]')


def test_create_programme_all_fields(
    browser: HopeTestBrowser,
    purpose: PaymentPlanPurpose,
) -> None:
    browser.login()
    navigate_to_programme_management(browser)

    browser.click('a[data-cy="button-new-program"]')

    fill_programme_create_required_fields(
        browser,
        name="Full Programme",
        start_date="2022-01-01",
        end_date="2035-02-01",
        sector="Health",
        dct="Partial",
        beneficiary_group="People",
    )
    browser.js_click('input[name="frequencyOfPayments"][value="ONE_OFF"]')
    browser.click('[data-cy="input-cashPlus"]')
    description_text = "Detailed description of the test case covering every field"
    elem = browser.find_element('textarea[name="description"]')
    elem.click()
    for ch in description_text:
        elem.send_keys(ch)
    browser.clear('input[name="budget"]')
    browser.type('input[name="budget"]', "1500.50")
    browser.type('input[name="administrativeAreasOfImplementation"]', "Kabul Province")
    browser.clear('input[name="populationGoal"]')
    browser.type('input[name="populationGoal"]', "250")
    browser.click('button[data-cy="button-next"]')

    add_time_series_field(
        browser,
        index=0,
        label="Monthly Income",
        subtype="Number",
        num_rounds="2",
        round_names=["Jan", "Feb"],
    )
    browser.click('button[data-cy="button-next"]')

    browser.wait_for_element_visible('button[data-cy="button-save"]').click()

    browser.wait_for_text("Full Programme", 'h5[data-cy="page-header-title"]')
    browser.assert_text("DRAFT", 'div[data-cy="status-container"]')
    browser.assert_text("1 Jan 2022", 'div[data-cy="label-START DATE"]')
    browser.assert_text("1 Feb 2035", 'div[data-cy="label-END DATE"]')
    browser.assert_text("Health", 'div[data-cy="label-Sector"]')
    browser.assert_text("Partial", 'div[data-cy="label-Data Collecting Type"]')
    browser.assert_text("One-off", 'div[data-cy="label-Frequency of Payment"]')
    browser.assert_text("Kabul Province", 'div[data-cy="label-Administrative Areas of implementation"]')
    browser.assert_text("Yes", 'div[data-cy="label-CASH+"]')
    browser.assert_text("0", 'div[data-cy="label-Programme size"]')
    browser.assert_text(
        description_text,
        'div[data-cy="label-Description"]',
    )
    browser.assert_text("People", 'div[data-cy="label-Payee Label"]')
    browser.wait_for_element_visible('div[data-cy="label-Programme Code"]')

    # Navigate to edit form to verify Budget, Population Goal, and PDU field
    browser.click('button[data-cy="button-edit-program"]')
    browser.click('li[data-cy="menu-item-edit-details"]')
    browser.wait_for_element_visible('input[name="budget"]')
    budget_value = browser.get_value('input[name="budget"]')
    assert float(budget_value) == 1500.50, f"Expected budget 1500.50, got {budget_value}"
    browser.assert_value('input[name="populationGoal"]', "250")

    # Verify time-series field on step 2
    browser.click('button[data-cy="button-next"]')
    browser.wait_for_element_visible('input[name="pduFields.0.label"]')
    browser.assert_value('input[name="pduFields.0.label"]', "Monthly Income")
    browser.assert_text("Number", 'div[data-cy="select-pduFields.0.pdu_data.subtype"]')
    browser.assert_text("2", 'div[data-cy="select-pduFields.0.pdu_data.number_of_rounds"]')
    browser.assert_value('input[data-cy="input-pduFields.0.pdu_data.rounds_names.0"]', "Jan")
    browser.assert_value('input[data-cy="input-pduFields.0.pdu_data.rounds_names.1"]', "Feb")

    # The new programme can be found in the programmes list
    navigate_to_programme_management(browser)
    browser.type('[data-cy="filters-search"] input', "Full Programme\n")
    browser.assert_text("DRAFT", 'tr[data-cy="table-row-Full Programme"]')
    browser.assert_text("Health", 'tr[data-cy="table-row-Full Programme"]')


def test_create_programme_time_series_fields(
    browser: HopeTestBrowser,
    purpose: PaymentPlanPurpose,
) -> None:
    browser.login()
    navigate_to_programme_management(browser)

    browser.click('a[data-cy="button-new-program"]')

    fill_programme_create_required_fields(browser, name="TSF Programme")
    browser.click('button[data-cy="button-next"]')

    add_time_series_field(
        browser,
        index=0,
        label="Text Field",
        subtype="Text",
        num_rounds="1",
        round_names=["Round A"],
    )
    add_time_series_field(
        browser,
        index=1,
        label="Number Field",
        subtype="Number",
        num_rounds="2",
        round_names=["Qtr1", "Qtr2"],
    )
    add_time_series_field(
        browser,
        index=2,
        label="Date Field",
        subtype="Date",
        num_rounds="1",
        round_names=["Period 1"],
    )
    browser.scroll_main_content(600)
    add_time_series_field(
        browser,
        index=3,
        label="Bool Field",
        subtype="Boolean (true/false)",
        num_rounds="3",
        round_names=["Check 1", "Check 2", "Check 3"],
    )

    browser.scroll_main_content(600)
    browser.click('button[data-cy="button-next"]')

    browser.wait_for_element_visible('button[data-cy="button-save"]').click()

    browser.wait_for_text("TSF Programme", 'h5[data-cy="page-header-title"]')
    browser.assert_text("DRAFT", 'div[data-cy="status-container"]')
    browser.assert_text("1 May 2023", 'div[data-cy="label-START DATE"]')
    browser.assert_text("12 Dec 2033", 'div[data-cy="label-END DATE"]')
    browser.assert_text("Child Protection", 'div[data-cy="label-Sector"]')
    browser.assert_text("Full", 'div[data-cy="label-Data Collecting Type"]')
    browser.assert_text("Regular", 'div[data-cy="label-Frequency of Payment"]')
    browser.assert_text("-", 'div[data-cy="label-Administrative Areas of implementation"]')
    browser.assert_text("No", 'div[data-cy="label-CASH+"]')
    browser.assert_text("0", 'div[data-cy="label-Programme size"]')

    # Navigate to edit form to verify all 4 time-series fields
    browser.click('button[data-cy="button-edit-program"]')
    browser.click('li[data-cy="menu-item-edit-details"]')
    browser.wait_for_element_visible('input[name="name"]')
    browser.click('button[data-cy="button-next"]')
    browser.wait_for_ready_state_complete()
    browser.wait_for_element_visible('input[name="pduFields.0.label"]')

    browser.assert_value('input[name="pduFields.0.label"]', "Text Field")
    browser.assert_text("Text", 'div[data-cy="select-pduFields.0.pdu_data.subtype"]')
    browser.assert_text("1", 'div[data-cy="select-pduFields.0.pdu_data.number_of_rounds"]')
    browser.assert_value('input[data-cy="input-pduFields.0.pdu_data.rounds_names.0"]', "Round A")

    browser.assert_value('input[name="pduFields.1.label"]', "Number Field")
    browser.assert_text("Number", 'div[data-cy="select-pduFields.1.pdu_data.subtype"]')
    browser.assert_text("2", 'div[data-cy="select-pduFields.1.pdu_data.number_of_rounds"]')
    browser.assert_value('input[data-cy="input-pduFields.1.pdu_data.rounds_names.0"]', "Qtr1")
    browser.assert_value('input[data-cy="input-pduFields.1.pdu_data.rounds_names.1"]', "Qtr2")

    browser.assert_value('input[name="pduFields.2.label"]', "Date Field")
    browser.assert_text("Date", 'div[data-cy="select-pduFields.2.pdu_data.subtype"]')
    browser.assert_text("1", 'div[data-cy="select-pduFields.2.pdu_data.number_of_rounds"]')
    browser.assert_value('input[data-cy="input-pduFields.2.pdu_data.rounds_names.0"]', "Period 1")

    browser.scroll_main_content(600)
    browser.assert_value('input[name="pduFields.3.label"]', "Bool Field")
    browser.assert_text("Boolean (true/false)", 'div[data-cy="select-pduFields.3.pdu_data.subtype"]')
    browser.assert_text("3", 'div[data-cy="select-pduFields.3.pdu_data.number_of_rounds"]')
    browser.assert_value('input[data-cy="input-pduFields.3.pdu_data.rounds_names.0"]', "Check 1")
    browser.assert_value('input[data-cy="input-pduFields.3.pdu_data.rounds_names.1"]', "Check 2")
    browser.assert_value('input[data-cy="input-pduFields.3.pdu_data.rounds_names.2"]', "Check 3")


def test_create_programme_validation_empty_fields(browser: HopeTestBrowser) -> None:
    browser.login()
    navigate_to_programme_management(browser)

    browser.click('a[data-cy="button-new-program"]')

    browser.click('button[data-cy="button-next"]')

    browser.assert_text("Programme Name is required", 'div[data-cy="input-programme-name"]')
    browser.assert_text("Start Date is required", 'div[data-cy="date-picker-filter"]')
    browser.assert_text("Sector is required", 'div[data-cy="input-sector"]')
    browser.assert_text("Payee Type is required", 'div[data-cy="input-payee-type"]')
    browser.assert_text("Data Collecting Type is required", 'div[data-cy="input-data-collecting-type"]')


def test_create_programme_cancel(browser: HopeTestBrowser) -> None:
    browser.login()
    navigate_to_programme_management(browser)

    browser.click('a[data-cy="button-new-program"]')

    browser.type('input[name="name"]', "Programme To Cancel")

    browser.click('a[data-cy="button-cancel"]')

    browser.assert_text("Programme Management", 'h5[data-cy="page-header-title"]')


def test_create_programme_purposes_scoped_to_ba(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    ba_purpose: PaymentPlanPurpose,
    other_ba_purpose: PaymentPlanPurpose,
) -> None:
    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.PROGRAMME_CREATE,
        Permissions.USER_MANAGEMENT_VIEW_LIST,
        Permissions.GEO_VIEW_LIST,
        Permissions.PM_PAYMENT_PLAN_PURPOSE_VIEW_LIST,
    ):
        browser.login(username="noperm_user")
        navigate_to_programme_management(browser)

        browser.click('a[data-cy="button-new-program"]')

        browser.wait_for_element_visible('[data-cy="input-payment-plan-purposes"]')
        browser.click('[data-cy="input-payment-plan-purposes"]')
        browser.wait_for_text(BA_PURPOSE_NAME, 'ul[role="listbox"]')
        browser.assert_text_not_visible(OTHER_BA_PURPOSE_NAME, 'ul[role="listbox"]')


def test_create_programme_max_ten_purposes_enforced(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    ten_ba_purposes: list[PaymentPlanPurpose],
) -> None:
    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.PROGRAMME_CREATE,
        Permissions.USER_MANAGEMENT_VIEW_LIST,
        Permissions.GEO_VIEW_LIST,
        Permissions.PM_PAYMENT_PLAN_PURPOSE_VIEW_LIST,
    ):
        browser.login(username="noperm_user")
        navigate_to_programme_management(browser)

        browser.click('a[data-cy="button-new-program"]')

        browser.wait_for_element_visible('[data-cy="input-payment-plan-purposes"]')
        for purpose_name in TEN_PURPOSE_NAMES:
            browser.select_chip_option(purpose_name, '[data-cy="input-payment-plan-purposes"]')

        # With 10 purposes selected, the input is disabled — clicking it does not open the listbox
        browser.click('[data-cy="input-payment-plan-purposes"]')
        browser.assert_element_absent('ul[role="listbox"]')


def test_create_programme_keeps_values_when_going_back(
    browser: HopeTestBrowser,
    superuser_of_unhcr: User,
    purpose: PaymentPlanPurpose,
) -> None:
    browser.login()
    navigate_to_programme_management(browser)
    browser.click('a[data-cy="button-new-program"]')
    fill_programme_create_required_fields(
        browser,
        name="Test Name",
        start_date="2022-01-01",
        end_date="2032-02-01",
        sector="Health",
        dct="Partial",
        beneficiary_group="People",
    )
    browser.click('[data-cy="input-cashPlus"]')
    browser.click('button[data-cy="button-next"]')
    browser.wait_for_element_visible('button[data-cy="button-add-time-series-field"]')
    browser.click('button[data-cy="button-next"]')
    browser.select_dropdown_option("partnerAccess", "Only Selected Partners within the business area")
    choose_partner(browser, "UNHCR")

    browser.click('button[data-cy="button-back"]')
    browser.wait_for_element_visible('button[data-cy="button-add-time-series-field"]')
    browser.click('button[data-cy="button-back"]')

    browser.assert_value('input[name="name"]', "Test Name")
    browser.clear('input[name="name"]')
    browser.assert_text("Programme Name is required", 'div[data-cy="input-programme-name"]')
    browser.type('input[name="name"]', "New Programme")
    browser.click('button[data-cy="button-next"]')
    browser.wait_for_element_visible('button[data-cy="button-add-time-series-field"]')
    browser.click('button[data-cy="button-next"]')
    browser.assert_text("UNHCR", 'div[data-cy="select-partners[0].id"]')
    browser.click('button[data-cy="button-save"]')

    browser.wait_for_text("New Programme", 'h5[data-cy="page-header-title"]')
    browser.assert_text("DRAFT", 'div[data-cy="status-container"]')
    browser.assert_text("1 Jan 2022", 'div[data-cy="label-START DATE"]')
    browser.assert_text("1 Feb 2032", 'div[data-cy="label-END DATE"]')
    browser.assert_text("Health", 'div[data-cy="label-Sector"]')
    browser.assert_text("Partial", 'div[data-cy="label-Data Collecting Type"]')
    browser.assert_text("Regular", 'div[data-cy="label-Frequency of Payment"]')
    browser.assert_text("-", 'div[data-cy="label-Administrative Areas of implementation"]')
    browser.assert_text("Yes", 'div[data-cy="label-CASH+"]')
    browser.assert_text("0", 'div[data-cy="label-Programme size"]')
    # The details page always lists UNHCR, so check that it got access to the programme itself.
    program = Program.objects.get(name="New Programme")
    assert list(program.role_assignments.values_list("partner__name", flat=True)) == ["UNHCR"]


def test_create_programme_dates_chosen_in_calendar(browser: HopeTestBrowser, purpose: PaymentPlanPurpose) -> None:
    start_date = timezone.now().date().replace(day=15)
    end_date = start_date + relativedelta(months=1, day=25)
    browser.login()
    navigate_to_programme_management(browser)
    browser.click('a[data-cy="button-new-program"]')
    fill_programme_create_required_fields(
        browser, sector="Health", dct="Partial", beneficiary_group="People", fill_dates=False
    )

    browser.pick_calendar_day("startDate", start_date.day)
    browser.pick_calendar_day("endDate", end_date.day, next_month=True)
    browser.click('button[data-cy="button-next"]')
    browser.wait_for_element_visible('button[data-cy="button-add-time-series-field"]')
    browser.click('button[data-cy="button-next"]')
    browser.click('button[data-cy="button-save"]')

    browser.wait_for_text("Test Programme", 'h5[data-cy="page-header-title"]')
    browser.assert_text(ui_date(start_date), 'div[data-cy="label-START DATE"]')
    browser.assert_text(ui_date(end_date), 'div[data-cy="label-END DATE"]')
