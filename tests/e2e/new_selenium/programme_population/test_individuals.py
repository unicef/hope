from datetime import date

from dateutil.relativedelta import relativedelta
import pytest

from e2e.new_selenium.programme_population.conftest import assert_exact_texts, open_from_menu
from extras.test_utils.factories import (
    HouseholdFactory,
    IndividualFactory,
    RegistrationDataImportFactory,
)
from extras.test_utils.selenium import HopeTestBrowser
from hope.apps.household.const import FEMALE, HEAD, MARRIED
from hope.models import BusinessArea, Household, Program

pytestmark = pytest.mark.django_db()

# Born a day past her 83rd birthday, so the age shown is 83 whatever day the test runs.
BIRTH_DATE = date.today() - relativedelta(years=83, days=1)

TABLE_TITLE = 'h6[data-cy="table-title"]'
TABLE_PAGINATION = 'div[data-cy="table-pagination"]'
INDIVIDUAL_ROW = 'tr[data-cy="individual-table-row"]'
ID_CELL = f"{INDIVIDUAL_ROW} td:nth-child(2)"
NAME_CELL = f"{INDIVIDUAL_ROW} td:nth-child(3)"
HOUSEHOLD_ID_CELL = f"{INDIVIDUAL_ROW} td:nth-child(4)"
RELATIONSHIP_CELL = f"{INDIVIDUAL_ROW} td:nth-child(5)"
GENDER_CELL = f"{INDIVIDUAL_ROW} td:nth-child(7)"
LIST_COLUMNS = {
    'th[data-cy="individual-id"]': "Item ID",
    'th[data-cy="individual-name"]': "Item",
    'th[data-cy="household-id"]': "Items Group ID",
    'th[data-cy="relationship"]': "Relationship to Head of Items Group",
    'th[data-cy="individual-age"]': "Age",
    'th[data-cy="individual-sex"]': "Gender",
    'th[data-cy="individual-location"]': "Administrative Level 2",
}


def label(name: str) -> str:
    return f'div[data-cy="label-{name}"]'


DETAILS_LABELS = {
    "Full Name": "Alicja Kowalska",
    "Given Name": "Alicja",
    "Middle Name": "-",
    "Family Name": "Kowalska",
    "Gender": "Female",
    "Age": "83",
    "Date of Birth": BIRTH_DATE.strftime("%-d %b %Y"),
    "Estimated Date of Birth": "No",
    "Marital Status": "Married",
    "Work Status": "Not provided",
    "Pregnant": "Yes",
    "Role": "Primary collector",
    "Relationship to Head Of Items Group": "Head of household (self)",
    "Preferred language": "-",
    "Observed disabilities": "None",
    "Seeing disability severity": "None",
    "Hearing disability severity": "None",
    "Physical disability severity": "None",
    "Remembering or concentrating disability severity": "None",
    "Communicating disability severity": "None",
    "Disability": "Not Disabled",
    "Email": "fake111test@email.com",
    "Phone Number": "Invalid Phone Number",
    "Alternative Phone Number": "-",
    "Date of last screening against sanctions list": "-",
}
DETAILS = {label(name): value for name, value in DETAILS_LABELS.items()}


@pytest.fixture
def household(program: Program, business_area: BusinessArea) -> Household:
    rdi = RegistrationDataImportFactory(business_area=business_area, program=program)
    head = IndividualFactory(
        household=None,
        business_area=business_area,
        program=program,
        registration_data_import=rdi,
        full_name="Alicja Kowalska",
        given_name="Alicja",
        middle_name="",
        family_name="Kowalska",
        sex=FEMALE,
        birth_date=BIRTH_DATE,
        marital_status=MARRIED,
        pregnant=True,
        email="fake111test@email.com",
        phone_no="0048503123555",
        relationship=HEAD,
    )
    return HouseholdFactory(
        unicef_id="HH-00-0000.1380",
        business_area=business_area,
        program=program,
        registration_data_import=rdi,
        head_of_household=head,
        size=1,
    )


def test_individuals_list_shows_individual(household: Household, program: Program, login: HopeTestBrowser) -> None:
    head = household.head_of_household
    open_from_menu(login, program, "Main Menu", "Items")

    login.assert_text("Items", TABLE_TITLE)
    login.assert_text("1–1 of 1", TABLE_PAGINATION)
    login.assert_exact_text(head.unicef_id, ID_CELL)
    login.assert_exact_text("Alicja Kowalska", NAME_CELL)
    login.assert_exact_text(household.unicef_id, HOUSEHOLD_ID_CELL)
    login.assert_exact_text("Head of household (self)", RELATIONSHIP_CELL)
    login.assert_exact_text("Female", GENDER_CELL)
    assert_exact_texts(login, LIST_COLUMNS)


def test_individual_details_shows_individual(household: Household, program: Program, login: HopeTestBrowser) -> None:
    head = household.head_of_household
    open_from_menu(login, program, "Main Menu", "Items")

    login.click(INDIVIDUAL_ROW)

    login.assert_exact_text(f"Item ID: {head.unicef_id}", 'h5[data-cy="page-header-title"]')
    assert_exact_texts(login, DETAILS)
    login.assert_exact_text(household.unicef_id, label("Items Group ID"))
    login.assert_exact_text(f"{household.unicef_id} -Primary collector", label("Linked Items Groups"))
