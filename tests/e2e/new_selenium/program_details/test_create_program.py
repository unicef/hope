import pytest

from extras.test_utils.selenium import HopeTestBrowser

pytestmark = pytest.mark.django_db()

# ---------------------------------------------------------------------------
# Selectors – Programme Management wizard (3-step)
# ---------------------------------------------------------------------------
# Navigation
NAV_PROGRAMMES = 'a[data-cy="nav-Programmes"]'
HEADER_TITLE = 'h5[data-cy="page-header-title"]'

# Step 1 – Details
BTN_NEW_PROGRAM = 'a[data-cy="button-new-program"]'
INPUT_NAME = 'input[data-cy="input-name"]'
INPUT_START_DATE = 'input[name="startDate"]'
INPUT_END_DATE = 'input[name="endDate"]'
SELECT_SECTOR = 'div[data-cy="select-sector"]'
INPUT_DCT = 'div[data-cy="input-data-collecting-type"]'
INPUT_BENEFICIARY_GROUP = 'div[data-cy="input-beneficiary-group"]'
INPUT_CASH_PLUS = 'span[data-cy="input-cashPlus"]'
INPUT_DESCRIPTION = 'textarea[data-cy="input-description"]'
INPUT_BUDGET = 'input[data-cy="input-budget"]'
INPUT_ADMIN_AREAS = 'input[data-cy="input-administrativeAreasOfImplementation"]'
INPUT_POPULATION = 'input[data-cy="input-populationGoal"]'
INPUT_PROGRAMME_CODE = 'input[data-cy="input-programme-code"]'
INPUT_FREQ_ONE_OFF = '[data-cy="input-frequency-of-payment"] > div:first-child span'

# Step 2 – Time Series Fields
BTN_ADD_TSF = 'button[data-cy="button-add-time-series-field"]'
INPUT_PDU_LABEL = 'input[data-cy="input-pduFields.{}.label"]'
SELECT_PDU_SUBTYPE = 'div[data-cy="select-pduFields.{}.pduData.subtype"]'
SELECT_PDU_ROUNDS = 'div[data-cy="select-pduFields.{}.pduData.numberOfRounds"]'
INPUT_PDU_ROUND_NAME = 'input[data-cy="input-pduFields.{}.pduData.roundsNames.{}"]'

# Wizard navigation
BTN_NEXT = 'button[data-cy="button-next"]'
BTN_BACK = 'button[data-cy="button-back"]'
BTN_CANCEL = 'a[data-cy="button-cancel"]'
BTN_SAVE = 'button[data-cy="button-save"]'

# Programme Details page (verification)
DETAIL_STATUS = 'div[data-cy="status-container"]'
LABEL_START_DATE = 'div[data-cy="label-START DATE"]'
LABEL_END_DATE = 'div[data-cy="label-END DATE"]'
LABEL_SECTOR = 'div[data-cy="label-Sector"]'
LABEL_DCT = 'div[data-cy="label-Data Collecting Type"]'
LABEL_FREQ = 'div[data-cy="label-Frequency of Payment"]'
LABEL_ADMIN_AREAS = 'div[data-cy="label-Administrative Areas of implementation"]'
LABEL_CASH_PLUS = 'div[data-cy="label-CASH+"]'
LABEL_SIZE = 'div[data-cy="label-Programme size"]'
LABEL_DESCRIPTION = 'div[data-cy="label-Description"]'

# Validation labels (Step 1)
LABEL_NAME_FIELD = 'div[data-cy="input-programme-name"]'
LABEL_START_DATE_FIELD = 'div[data-cy="date-picker-filter"]'
LABEL_SECTOR_FIELD = 'div[data-cy="input-sector"]'
LABEL_DCT_FIELD = 'div[data-cy="input-data-collecting-type"]'


def _navigate_to_programme_management(browser: HopeTestBrowser) -> None:
    browser.click(NAV_PROGRAMMES)
    browser.wait_for_text("Programme Management", HEADER_TITLE)


def _fill_required_fields(
    browser: HopeTestBrowser,
    *,
    name: str = "Test Programme",
    start_date: str = "2023-05-01",
    end_date: str = "2033-12-12",
    sector: str = "Child Protection",
    dct: str = "Full",
    beneficiary_group: str = "Main Menu",
) -> None:
    browser.type(INPUT_NAME, name)
    start_el = browser.find_element(INPUT_START_DATE)
    start_el.click()
    start_el.send_keys(start_date)
    browser.click(INPUT_NAME)
    end_el = browser.wait_for_element_clickable(INPUT_END_DATE)
    end_el.click()
    end_el.send_keys(end_date)
    browser.click(INPUT_NAME)
    browser.wait_for_element_clickable(SELECT_SECTOR)
    browser.click(SELECT_SECTOR)
    browser.select_option_by_name(sector)
    browser.click(INPUT_DCT)
    browser.select_option_by_name(dct)
    browser.click(INPUT_BENEFICIARY_GROUP)
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
    browser.click(BTN_ADD_TSF)
    browser.type(INPUT_PDU_LABEL.format(index), label)
    browser.click(SELECT_PDU_SUBTYPE.format(index))
    browser.select_option_by_name(subtype)
    browser.click(SELECT_PDU_ROUNDS.format(index))
    browser.select_option_by_name(num_rounds)
    for ri, rname in enumerate(round_names):
        browser.type(INPUT_PDU_ROUND_NAME.format(index, ri), rname)


def test_create_programme_mandatory_fields_only(browser: HopeTestBrowser, unhcr_partner: None) -> None:
    browser.login()
    _navigate_to_programme_management(browser)

    browser.click(BTN_NEW_PROGRAM)

    _fill_required_fields(browser)
    browser.click(BTN_NEXT)

    browser.wait_for_element_visible(BTN_ADD_TSF)
    browser.click(BTN_NEXT)

    browser.wait_for_element_visible(BTN_SAVE)
    browser.click(BTN_SAVE)

    browser.wait_for_text("Test Programme", HEADER_TITLE)
    browser.assert_text("DRAFT", DETAIL_STATUS)
    browser.assert_text("1 May 2023", LABEL_START_DATE)
    browser.assert_text("12 Dec 2033", LABEL_END_DATE)
    browser.assert_text("Child Protection", LABEL_SECTOR)
    browser.assert_text("Full", LABEL_DCT)
    browser.assert_text("Regular", LABEL_FREQ)
    browser.assert_text("-", LABEL_ADMIN_AREAS)
    browser.assert_text("No", LABEL_CASH_PLUS)
    browser.assert_text("0", LABEL_SIZE)


def test_create_programme_all_fields(browser: HopeTestBrowser, unhcr_partner: None) -> None:
    browser.login()
    _navigate_to_programme_management(browser)

    browser.click(BTN_NEW_PROGRAM)

    _fill_required_fields(
        browser,
        name="Full Programme",
        start_date="2022-01-01",
        end_date="2035-02-01",
        sector="Health",
        dct="Partial",
        beneficiary_group="People",
    )
    browser.click(INPUT_FREQ_ONE_OFF)
    browser.click(INPUT_CASH_PLUS)
    browser.type(INPUT_DESCRIPTION, "Comprehensive test programme with all fields")
    browser.clear(INPUT_BUDGET)
    browser.type(INPUT_BUDGET, "1500.50")
    browser.type(INPUT_ADMIN_AREAS, "Kabul Province")
    browser.clear(INPUT_POPULATION)
    browser.type(INPUT_POPULATION, "250")
    browser.click(BTN_NEXT)

    _add_time_series_field(
        browser,
        index=0,
        label="Monthly Income",
        subtype="Number",
        num_rounds="2",
        round_names=["Jan", "Feb"],
    )
    browser.click(BTN_NEXT)

    browser.wait_for_element_visible(BTN_SAVE)
    browser.click(BTN_SAVE)

    browser.wait_for_text("Full Programme", HEADER_TITLE)
    browser.assert_text("DRAFT", DETAIL_STATUS)
    browser.assert_text("1 Jan 2022", LABEL_START_DATE)
    browser.assert_text("1 Feb 2035", LABEL_END_DATE)
    browser.assert_text("Health", LABEL_SECTOR)
    browser.assert_text("Partial", LABEL_DCT)
    browser.assert_text("One-off", LABEL_FREQ)
    browser.assert_text("Kabul Province", LABEL_ADMIN_AREAS)
    browser.assert_text("Yes", LABEL_CASH_PLUS)
    browser.assert_text("0", LABEL_SIZE)


def test_create_programme_time_series_fields(browser: HopeTestBrowser, unhcr_partner: None) -> None:
    browser.login()
    _navigate_to_programme_management(browser)

    browser.click(BTN_NEW_PROGRAM)

    _fill_required_fields(browser, name="TSF Programme")
    browser.click(BTN_NEXT)

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
    _add_time_series_field(
        browser,
        index=3,
        label="Bool Field",
        subtype="Boolean",
        num_rounds="3",
        round_names=["Check 1", "Check 2", "Check 3"],
    )

    browser.scroll_main_content(600)
    browser.click(BTN_NEXT)

    browser.wait_for_element_visible(BTN_SAVE)
    browser.click(BTN_SAVE)

    browser.wait_for_text("TSF Programme", HEADER_TITLE)
    browser.assert_text("DRAFT", DETAIL_STATUS)


def test_create_programme_validation_empty_fields(browser: HopeTestBrowser, unhcr_partner: None) -> None:
    browser.login()
    _navigate_to_programme_management(browser)

    browser.click(BTN_NEW_PROGRAM)

    browser.click(BTN_NEXT)

    browser.assert_text("Programme Name is required", LABEL_NAME_FIELD)
    browser.assert_text("Start Date is required", LABEL_START_DATE_FIELD)
    browser.assert_text("Sector is required", LABEL_SECTOR_FIELD)
    browser.assert_text("Data Collecting Type is required", LABEL_DCT_FIELD)


def test_create_programme_cancel(browser: HopeTestBrowser, unhcr_partner: None) -> None:
    browser.login()
    _navigate_to_programme_management(browser)

    browser.click(BTN_NEW_PROGRAM)

    browser.type(INPUT_NAME, "Programme To Cancel")

    browser.click(BTN_CANCEL)

    browser.assert_text("Programme Management", HEADER_TITLE)
