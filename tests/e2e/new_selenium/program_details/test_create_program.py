import pytest

from extras.test_utils.selenium import HopeTestBrowser

pytestmark = pytest.mark.django_db()


def _navigate_to_programme_management(browser: HopeTestBrowser) -> None:
    browser.click('a[data-cy="nav-Programmes"]')
    browser.wait_for_text("Programme Management", 'h5[data-cy="page-header-title"]')


def _fill_programme_create_required_fields(
    browser: HopeTestBrowser,
    *,
    name: str = "Test Programme",
    start_date: str = "2023-05-01",
    end_date: str = "2033-12-12",
    sector: str = "Child Protection",
    dct: str = "Full",
    beneficiary_group: str = "Main Menu",
) -> None:
    browser.type('input[name="name"]', name)
    start_el = browser.find_element('input[name="startDate"]')
    start_el.click()
    start_el.send_keys(start_date)
    browser.click('input[name="name"]')
    end_el = browser.wait_for_element_clickable('input[name="endDate"]')
    end_el.click()
    end_el.send_keys(end_date)
    browser.click('input[name="name"]')
    browser.click('[data-cy="select-sector"]')
    browser.select_option_by_name(sector)
    browser.click('[data-cy="input-data-collecting-type"]')
    browser.select_option_by_name(dct)
    browser.click('[data-cy="input-beneficiary-group"]')
    browser.select_option_by_name(beneficiary_group)


def _add_time_series_field(
    browser: HopeTestBrowser,
    index: int,
    *,
    label: str,
    subtype: str = "Text",
    num_rounds: str = "1",
    round_names: list[str] = (),
) -> None:
    browser.click('button[data-cy="button-add-time-series-field"]')
    browser.type(f'input[name="pduFields.{index}.label"]', label)
    browser.click(f'[data-cy="select-pduFields.{index}.pduData.subtype"]')
    browser.select_option_by_name(subtype)
    browser.click(f'[data-cy="select-pduFields.{index}.pduData.numberOfRounds"]')
    browser.select_option_by_name(num_rounds)
    for ri, rname in enumerate(round_names):
        browser.type(f'input[name="pduFields.{index}.pduData.roundsNames.{ri}"]', rname)


def test_create_programme_mandatory_fields_only(browser: HopeTestBrowser, unhcr_partner: None) -> None:
    browser.login()
    _navigate_to_programme_management(browser)

    browser.click('a[data-cy="button-new-program"]')

    _fill_programme_create_required_fields(browser)
    browser.click('button[data-cy="button-next"]')

    browser.wait_for_element_visible('button[data-cy="button-add-time-series-field"]')
    browser.click('button[data-cy="button-next"]')

    browser.wait_for_element_visible('button[data-cy="button-save"]')
    browser.click('button[data-cy="button-save"]')

    browser.wait_for_text("Test Programme", 'h5[data-cy="page-header-title"]')
    browser.assert_text("DRAFT", 'div[data-cy="status-container"]')
    browser.assert_text("1 May 2023", 'div[data-cy="label-START DATE"]')
    browser.assert_text("12 Dec 2033", 'div[data-cy="label-END DATE"]')
    browser.assert_text("Child Protection", 'div[data-cy="label-Sector"]')
    browser.assert_text("Full", 'div[data-cy="label-Data Collecting Type"]')
    browser.assert_text("Regular", 'div[data-cy="label-Frequency of Payment"]')
    browser.assert_text("-", 'div[data-cy="label-Administrative Areas of implementation"]')
    browser.assert_text("No", 'div[data-cy="label-CASH+"]')
    browser.assert_text("0", 'div[data-cy="label-Programme size"]')


def test_create_programme_all_fields(browser: HopeTestBrowser, unhcr_partner: None) -> None:
    browser.login()
    _navigate_to_programme_management(browser)

    browser.click('a[data-cy="button-new-program"]')

    _fill_programme_create_required_fields(
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
    browser.type('textarea[name="description"]', "Comprehensive test programme with all fields")
    browser.clear('input[name="budget"]')
    browser.type('input[name="budget"]', "1500.50")
    browser.type('input[name="administrativeAreasOfImplementation"]', "Kabul Province")
    browser.clear('input[name="populationGoal"]')
    browser.type('input[name="populationGoal"]', "250")
    browser.click('button[data-cy="button-next"]')

    _add_time_series_field(
        browser,
        index=0,
        label="Monthly Income",
        subtype="Number",
        num_rounds="2",
        round_names=["Jan", "Feb"],
    )
    browser.click('button[data-cy="button-next"]')

    browser.wait_for_element_visible('button[data-cy="button-save"]')
    browser.click('button[data-cy="button-save"]')

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
    browser.assert_text("Comprehensive test programme with all fields", 'div[data-cy="label-Description"]')
    browser.assert_text("People", 'div[data-cy="label-Beneficiary Group"]')
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


def test_create_programme_time_series_fields(browser: HopeTestBrowser, unhcr_partner: None) -> None:
    browser.login()
    _navigate_to_programme_management(browser)

    browser.click('a[data-cy="button-new-program"]')

    _fill_programme_create_required_fields(browser, name="TSF Programme")
    browser.click('button[data-cy="button-next"]')

    _add_time_series_field(
        browser,
        index=0,
        label="Text Field",
        subtype="Text",
        num_rounds="1",
        round_names=["Round A"],
    )
    _add_time_series_field(
        browser,
        index=1,
        label="Number Field",
        subtype="Number",
        num_rounds="2",
        round_names=["Qtr1", "Qtr2"],
    )
    _add_time_series_field(
        browser,
        index=2,
        label="Date Field",
        subtype="Date",
        num_rounds="1",
        round_names=["Period 1"],
    )
    browser.scroll_main_content(600)
    _add_time_series_field(
        browser,
        index=3,
        label="Bool Field",
        subtype="Boolean (true/false)",
        num_rounds="3",
        round_names=["Check 1", "Check 2", "Check 3"],
    )

    browser.scroll_main_content(600)
    browser.click('button[data-cy="button-next"]')

    browser.wait_for_element_visible('button[data-cy="button-save"]')
    browser.click('button[data-cy="button-save"]')

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


def test_create_programme_validation_empty_fields(browser: HopeTestBrowser, unhcr_partner: None) -> None:
    browser.login()
    _navigate_to_programme_management(browser)

    browser.click('a[data-cy="button-new-program"]')

    browser.click('button[data-cy="button-next"]')

    browser.assert_text("Programme Name is required", 'div[data-cy="input-programme-name"]')
    browser.assert_text("Start Date is required", 'div[data-cy="date-picker-filter"]')
    browser.assert_text("Sector is required", 'div[data-cy="input-sector"]')
    browser.assert_text("Data Collecting Type is required", 'div[data-cy="input-data-collecting-type"]')


def test_create_programme_cancel(browser: HopeTestBrowser, unhcr_partner: None) -> None:
    browser.login()
    _navigate_to_programme_management(browser)

    browser.click('a[data-cy="button-new-program"]')

    browser.type('input[name="name"]', "Programme To Cancel")

    browser.click('a[data-cy="button-cancel"]')

    browser.assert_text("Programme Management", 'h5[data-cy="page-header-title"]')
