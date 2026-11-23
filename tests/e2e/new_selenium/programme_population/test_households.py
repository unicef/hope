from datetime import UTC, datetime

import pytest

from e2e.new_selenium.programme_population.conftest import assert_texts, open_from_menu
from extras.test_utils.factories import (
    HouseholdFactory,
    IndividualFactory,
    RegistrationDataImportFactory,
    UserFactory,
)
from extras.test_utils.selenium import HopeTestBrowser
from hope.apps.household.const import REFUGEE
from hope.models import Area, BusinessArea, Country, Household, Program

pytestmark = pytest.mark.django_db()

TABLE_TITLE = 'h6[data-cy="table-title"]'
TABLE_PAGINATION = 'div[data-cy="table-pagination"]'
HOUSEHOLD_ROW = 'tr[data-cy="household-table-row"]'
LIST_COLUMNS = {
    'th[data-cy="household-id"]': "Items Group ID",
    'th[data-cy="status"]': "Status",
    'th[data-cy="household-head-name"]': "Head of Items Group",
    'th[data-cy="household-size"]': "Items Group Size",
    'th[data-cy="household-location"]': "Administrative Level 2",
    'th[data-cy="household-residence-status"]': "Residence Status",
    'th[data-cy="household-total-cash-received"]': "Total Cash Received",
    'th[data-cy="household-registration-date"]': "Registration Date",
}


def label(name: str) -> str:
    return f'div[data-cy="label-{name}"]'


DETAILS_LABELS = {
    "Items Group Size": "3",
    "Residence Status": "Displaced | Refugee / Asylum Seeker",
    "Head of Items Group": "Agata Kowalska",
    "Country": "Afghanistan",
    "Country of Origin": "Afghanistan",
    "Address": "938 Luna Cliffs Apt. 551 Jameschester, SC 24934",
    "Village": "Small One",
    "Zip code": "-",
    "Administrative Level 1": "Kabul",
    "Administrative Level 2": "-",
    "Administrative Level 3": "-",
    "Administrative Level 4": "-",
    "Geolocation": "-",
    "UNHCR CASE ID": "-",
    "LENGTH OF TIME SINCE ARRIVAL": "-",
    "NUMBER OF TIMES DISPLACED": "-",
    "Linked Grievances": "-",
    "Cash received": "USD 0.00",
    "Total Cash Received": "USD 0.00",
}
DETAILS = {label(name): value for name, value in DETAILS_LABELS.items()}
STATUS_CONTAINER = 'div[data-cy="status-container"]'
TABLE_ROW = 'tr[data-cy="table-row"]'
TABLE_LABEL = 'span[data-cy="table-label"]'
KNOWN_AFFECTED_BENEFICIARIES = '[data-cy="known-affected-beneficiaries"]'
ROW_0_5 = '[data-cy="row05"]'
KAB_SIZE = '[data-cy="kab-size"]'
KAB_INFO = '[data-cy="kab-info"]'


@pytest.fixture
def household(program: Program, business_area: BusinessArea) -> Household:
    rdi = RegistrationDataImportFactory(
        imported_by=UserFactory(email="importer@example.com"),
        business_area=business_area,
        program=program,
        import_date=datetime(2022, 1, 29, tzinfo=UTC),
    )
    afghanistan = Country.objects.get(name="Afghanistan")
    head = IndividualFactory(
        household=None,
        business_area=business_area,
        program=program,
        full_name="Agata Kowalska",
        registration_data_import=rdi,
    )
    return HouseholdFactory(
        unicef_id="HH-00-0000.1380",
        business_area=business_area,
        program=program,
        registration_data_import=rdi,
        head_of_household=head,
        admin1=Area.objects.get(name="Kabul", area_type__area_level=1),
        size=7,
        residence_status=REFUGEE,
        address="938 Luna Cliffs Apt. 551 Jameschester, SC 24934",
        village="Small One",
        country_origin=afghanistan,
        country=afghanistan,
        kab_female_age_group_0_5_count=2,
        kab_female_age_group_0_5_disabled_count=1,
        kab_male_age_group_0_5_count=0,
        kab_size=3,
    )


def test_households_list_shows_household(household: Household, program: Program, login: HopeTestBrowser) -> None:
    open_from_menu(login, program, "Main Menu", "Items Groups")

    login.assert_text("Items Groups", TABLE_TITLE)
    login.assert_text("1–1 of 1", TABLE_PAGINATION)
    login.assert_text(household.unicef_id, HOUSEHOLD_ROW)
    login.assert_text("Agata Kowalska", HOUSEHOLD_ROW)
    login.assert_text("7", HOUSEHOLD_ROW)
    login.assert_text("Displaced | Refugee / Asylum Seeker", HOUSEHOLD_ROW)
    assert_texts(login, LIST_COLUMNS)


def test_household_details_shows_household(household: Household, program: Program, login: HopeTestBrowser) -> None:
    rdi = household.registration_data_import
    open_from_menu(login, program, "Main Menu", "Items Groups")

    login.click(HOUSEHOLD_ROW)

    login.assert_text(household.unicef_id, 'h5[data-cy="page-header-title"]')
    assert_texts(login, DETAILS)
    login.assert_text("ACTIVE", STATUS_CONTAINER)
    login.assert_text("Items Group Members", TABLE_TITLE)
    login.assert_text("Item ID", TABLE_LABEL)
    login.assert_text("No results", TABLE_ROW)
    login.assert_text(rdi.data_source, label("Source"))
    login.assert_text(rdi.name, label("Import name"))
    login.assert_text(household.last_registration_date.strftime("%-d %b %Y"), label("Registration Date"))
    login.assert_text("importer@example.com", label("User name"))
    # The "Main Menu" beneficiary group labels members as "Items".
    login.assert_text("Items Reported by Data Subjects", KNOWN_AFFECTED_BENEFICIARIES)
    # age group, females, with disability, pregnant, (spacer), males, with disability;
    # both the unset male disabled counter and the zero male counter render as "-"
    assert login.get_text(ROW_0_5).split() == ["0", "-", "5", "2", "1", "-", "-", "-"]
    login.assert_text("3", KAB_SIZE)
    login.assert_element_visible(KAB_INFO)
