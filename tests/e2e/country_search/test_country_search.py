import pytest

from e2e.page_object.country_search.country_search import CountrySearch
from extras.test_utils.factories import HouseholdFactory, ProgramFactory
from hope.models import BeneficiaryGroup, BusinessArea, Household

pytestmark = pytest.mark.django_db()


@pytest.fixture
def household(business_area: BusinessArea) -> Household:
    beneficiary_group = BeneficiaryGroup.objects.filter(name="Main Menu").first()
    program = ProgramFactory(business_area=business_area, beneficiary_group=beneficiary_group)
    return HouseholdFactory(business_area=business_area, program=program)


@pytest.mark.usefixtures("login")
def test_country_search_finds_household_by_id(page_country_search: CountrySearch, household: Household) -> None:
    page_country_search.get_nav_country_search().click()
    assert "Country Search" in page_country_search.get_page_header_title().text

    page_country_search.select_search_for("HH")
    page_country_search.get_office_search_input().send_keys(household.unicef_id)
    page_country_search.get_button_filters_apply().click()

    page_country_search.wait_for_text(household.unicef_id, page_country_search.results_table)


@pytest.mark.usefixtures("login")
def test_country_search_shows_no_results_for_unknown_id(
    page_country_search: CountrySearch, household: Household
) -> None:
    page_country_search.get_nav_country_search().click()
    assert "Country Search" in page_country_search.get_page_header_title().text

    page_country_search.select_search_for("HH")
    page_country_search.get_office_search_input().send_keys("HH-00-0000.0000")
    page_country_search.get_button_filters_apply().click()

    page_country_search.wait_for_text("No results found", page_country_search.page_details_container)
