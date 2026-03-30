from typing import Generator

import pytest
from seleniumbase import config as sb_config
from seleniumbase.core import session_helper

from e2e.helpers.selenium_base import HopeTestBrowser
from extras.test_utils.factories.account import (
    PartnerFactory,
    RoleAssignmentFactory,
    RoleFactory,
)
from hope.models import BusinessArea

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
INPUT_FREQ_ONE_OFF = '//*[@data-cy="input-frequency-of-payment"]/div[1]/div/span'

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
DETAIL_HEADER = 'h5[data-cy="page-header-title"]'
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


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def browser_sb(live_server_with_static, request) -> Generator[HopeTestBrowser, None, None]:
    sb = HopeTestBrowser("base_method")
    sb.live_server_url = str(live_server_with_static)
    sb.setUp()
    sb._needs_tearDown = True
    sb._using_sb_fixture = True
    sb._using_sb_fixture_no_class = True
    sb_config._sb_node[request.node.nodeid] = sb
    yield sb
    if sb._needs_tearDown:
        sb.tearDown()
        sb._needs_tearDown = False


@pytest.fixture
def login_sb(browser_sb: HopeTestBrowser) -> HopeTestBrowser:
    browser_sb.login()
    return browser_sb


@pytest.fixture
def unhcr_partner() -> None:
    """Create UNHCR partner with a role in Afghanistan."""
    partner_unhcr = PartnerFactory(name="UNHCR")
    afghanistan = BusinessArea.objects.get(slug="afghanistan")
    partner_unhcr.role_assignments.all().delete()
    partner_unhcr.allowed_business_areas.add(afghanistan)
    RoleAssignmentFactory(
        partner=partner_unhcr,
        business_area=afghanistan,
        role=RoleFactory(name="Role for UNHCR"),
        program=None,
    )


# ---------------------------------------------------------------------------
# Selenium page-interaction helpers (kept thin — no business logic)
# ---------------------------------------------------------------------------
def _navigate_to_programme_management(sb: HopeTestBrowser) -> None:
    sb.click(NAV_PROGRAMMES)
    sb.wait_for_text("Programme Management", HEADER_TITLE)


def _fill_required_fields(
    sb: HopeTestBrowser,
    *,
    name: str = "Test Programme",
    start_date: str = "2023-05-01",
    end_date: str = "2033-12-12",
    sector: str = "Child Protection",
    dct: str = "Full",
    beneficiary_group: str = "Main Menu",
) -> None:
    sb.type(INPUT_NAME, name)
    sb.click(INPUT_START_DATE)
    sb.send_keys(INPUT_START_DATE, start_date)
    sb.click(INPUT_NAME)
    sb.wait_for_element_clickable(INPUT_END_DATE)
    sb.click(INPUT_END_DATE)
    sb.send_keys(INPUT_END_DATE, end_date)
    sb.click(INPUT_NAME)
    sb.wait_for_element_clickable(SELECT_SECTOR)
    sb.click(SELECT_SECTOR)
    sb.select_option_by_name(sector)
    sb.click(INPUT_DCT)
    sb.select_option_by_name(dct)
    sb.click(INPUT_BENEFICIARY_GROUP)
    sb.select_listbox_element(beneficiary_group)


def _add_time_series_field(
    sb: HopeTestBrowser,
    index: int,
    *,
    label: str,
    subtype: str = "Text",
    num_rounds: str = "1",
    round_names: list[str] | None = None,
) -> None:
    sb.click(BTN_ADD_TSF)
    sb.type(INPUT_PDU_LABEL.format(index), label)
    sb.click(SELECT_PDU_SUBTYPE.format(index))
    sb.select_listbox_element(subtype)
    sb.click(SELECT_PDU_ROUNDS.format(index))
    sb.select_listbox_element(num_rounds)
    if round_names is None:
        round_names = [f"Round {i + 1}" for i in range(int(num_rounds))]
    for ri, rname in enumerate(round_names):
        sb.type(INPUT_PDU_ROUND_NAME.format(index, ri), rname)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def test_create_programme_mandatory_fields_only(login_sb: HopeTestBrowser, unhcr_partner: None) -> None:
    sb = login_sb
    _navigate_to_programme_management(sb)

    sb.scroll_main_content(-600)
    sb.click(BTN_NEW_PROGRAM)

    _fill_required_fields(sb)
    sb.click(BTN_NEXT)

    sb.wait_for_element_visible(BTN_ADD_TSF)
    sb.click(BTN_NEXT)

    sb.wait_for_element_visible(BTN_SAVE)
    sb.click(BTN_SAVE)

    sb.wait_for_text("Test Programme", DETAIL_HEADER)
    sb.assert_text("DRAFT", DETAIL_STATUS)
    sb.assert_text("1 May 2023", LABEL_START_DATE)
    sb.assert_text("12 Dec 2033", LABEL_END_DATE)
    sb.assert_text("Child Protection", LABEL_SECTOR)
    sb.assert_text("Full", LABEL_DCT)
    sb.assert_text("Regular", LABEL_FREQ)
    sb.assert_text("-", LABEL_ADMIN_AREAS)
    sb.assert_text("No", LABEL_CASH_PLUS)
    sb.assert_text("0", LABEL_SIZE)


def test_create_programme_all_fields(login_sb: HopeTestBrowser, unhcr_partner: None) -> None:
    sb = login_sb
    _navigate_to_programme_management(sb)

    sb.scroll_main_content(-600)
    sb.click(BTN_NEW_PROGRAM)

    _fill_required_fields(
        sb,
        name="Full Programme",
        start_date="2022-01-01",
        end_date="2035-02-01",
        sector="Health",
        dct="Partial",
        beneficiary_group="People",
    )
    sb.click(INPUT_FREQ_ONE_OFF, by="xpath")
    sb.click(INPUT_CASH_PLUS)
    sb.type(INPUT_DESCRIPTION, "Comprehensive test programme with all fields")
    sb.clear(INPUT_BUDGET)
    sb.type(INPUT_BUDGET, "1500.50")
    sb.type(INPUT_ADMIN_AREAS, "Kabul Province")
    sb.clear(INPUT_POPULATION)
    sb.type(INPUT_POPULATION, "250")
    sb.click(BTN_NEXT)

    _add_time_series_field(
        sb,
        index=0,
        label="Monthly Income",
        subtype="Number",
        num_rounds="2",
        round_names=["Jan", "Feb"],
    )
    sb.click(BTN_NEXT)

    sb.wait_for_element_visible(BTN_SAVE)
    sb.click(BTN_SAVE)

    sb.wait_for_text("Full Programme", DETAIL_HEADER)
    sb.assert_text("DRAFT", DETAIL_STATUS)
    sb.assert_text("1 Jan 2022", LABEL_START_DATE)
    sb.assert_text("1 Feb 2035", LABEL_END_DATE)
    sb.assert_text("Health", LABEL_SECTOR)
    sb.assert_text("Partial", LABEL_DCT)
    sb.assert_text("One-off", LABEL_FREQ)
    sb.assert_text("Kabul Province", LABEL_ADMIN_AREAS)
    sb.assert_text("Yes", LABEL_CASH_PLUS)
    sb.assert_text("0", LABEL_SIZE)


def test_create_programme_time_series_fields(login_sb: HopeTestBrowser, unhcr_partner: None) -> None:
    sb = login_sb
    _navigate_to_programme_management(sb)

    sb.scroll_main_content(-600)
    sb.click(BTN_NEW_PROGRAM)

    _fill_required_fields(sb, name="TSF Programme")
    sb.click(BTN_NEXT)

    _add_time_series_field(
        sb, index=0, label="Text Field", subtype="Text", num_rounds="1", round_names=["Round A"]
    )
    _add_time_series_field(
        sb, index=1, label="Number Field", subtype="Number", num_rounds="2", round_names=["Qtr1", "Qtr2"]
    )
    _add_time_series_field(
        sb, index=2, label="Date Field", subtype="Date", num_rounds="1", round_names=["Period 1"]
    )
    _add_time_series_field(
        sb,
        index=3,
        label="Bool Field",
        subtype="Boolean",
        num_rounds="3",
        round_names=["Check 1", "Check 2", "Check 3"],
    )

    sb.scroll_main_content(600)
    sb.click(BTN_NEXT)

    sb.wait_for_element_visible(BTN_SAVE)
    sb.click(BTN_SAVE)

    sb.wait_for_text("TSF Programme", DETAIL_HEADER)
    sb.assert_text("DRAFT", DETAIL_STATUS)


def test_create_programme_validation_empty_fields(login_sb: HopeTestBrowser, unhcr_partner: None) -> None:
    sb = login_sb
    _navigate_to_programme_management(sb)

    sb.scroll_main_content(-600)
    sb.click(BTN_NEW_PROGRAM)

    sb.click(BTN_NEXT)

    sb.assert_text("Programme Name is required", LABEL_NAME_FIELD)
    sb.assert_text("Start Date is required", LABEL_START_DATE_FIELD)
    sb.assert_text("Sector is required", LABEL_SECTOR_FIELD)
    sb.assert_text("Data Collecting Type is required", LABEL_DCT_FIELD)


def test_create_programme_cancel(login_sb: HopeTestBrowser, unhcr_partner: None) -> None:
    sb = login_sb
    _navigate_to_programme_management(sb)

    sb.scroll_main_content(-600)
    sb.click(BTN_NEW_PROGRAM)

    sb.type(INPUT_NAME, "Programme To Cancel")

    sb.click(BTN_CANCEL)

    sb.assert_text("Programme Management", HEADER_TITLE)
