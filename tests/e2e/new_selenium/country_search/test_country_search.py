import pytest

from extras.test_utils.factories import HouseholdFactory, IndividualFactory, ProgramFactory
from extras.test_utils.selenium import HopeTestBrowser
from hope.models import BusinessArea, Household, Individual, Program

pytestmark = pytest.mark.django_db()

NAV_COUNTRY_SEARCH = 'a[data-cy="nav-Country Search"]'
PAGE_HEADER_TITLE = 'h5[data-cy="page-header-title"]'
SEARCH_FOR = "#search-for"
LISTBOX = 'ul[role="listbox"]'
SEARCH_INPUT = 'div[data-cy="office-filters-search"] input'
BUTTON_APPLY = 'button[data-cy="button-filters-apply"]'
PAGE_DETAILS = 'div[data-cy="page-details-container"]'
RESULTS_TABLE = f"{PAGE_DETAILS} table"


@pytest.fixture
def program(business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def household(business_area: BusinessArea, program: Program) -> Household:
    return HouseholdFactory(business_area=business_area, program=program)


@pytest.fixture
def individual(business_area: BusinessArea, program: Program, household: Household) -> Individual:
    return IndividualFactory(business_area=business_area, program=program, household=household)


def search(browser: HopeTestBrowser, search_for: str, value: str) -> None:
    browser.wait_for_element_clickable(NAV_COUNTRY_SEARCH).click()
    browser.assert_text("Country Search", PAGE_HEADER_TITLE)
    browser.click(SEARCH_FOR)
    browser.wait_for_element_visible(f'{LISTBOX} li[data-value="{search_for}"]').click()
    browser.wait_for_element_absent(LISTBOX)
    browser.type(SEARCH_INPUT, value)
    browser.click(BUTTON_APPLY)


@pytest.mark.parametrize(
    ("beneficiary_fixture", "search_for"),
    [
        pytest.param("household", "HH", id="household"),
        pytest.param("individual", "IND", id="individual"),
    ],
)
def test_country_search_finds_beneficiary_by_id(
    request: pytest.FixtureRequest,
    program: Program,
    login: HopeTestBrowser,
    beneficiary_fixture: str,
    search_for: str,
) -> None:
    beneficiary = request.getfixturevalue(beneficiary_fixture)

    search(login, search_for, beneficiary.unicef_id)

    login.assert_text(beneficiary.unicef_id, RESULTS_TABLE)
    login.assert_text(program.name, RESULTS_TABLE)


def test_country_search_shows_no_results_for_unknown_id(household: Household, login: HopeTestBrowser) -> None:
    search(login, "HH", "HH-00-0000.0000")

    login.assert_text("No results found", PAGE_DETAILS)
