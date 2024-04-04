import pytest
from page_object.programme_population.households import Households
from page_object.programme_population.households_details import HouseholdsDetails

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.mark.usefixtures("login")
class TestSmokeHouseholds:
    def test_smoke_page_households(self, pageHouseholds: Households) -> None:
        pageHouseholds.selectGlobalProgramFilter("Test Programm").click()
        pageHouseholds.getNavProgrammePopulation().click()
        pageHouseholds.getNavHouseholds().click()

    def test_smoke_page_households_details(
        self, pageHouseholds: Households, pageHouseholdsDetails: HouseholdsDetails
    ) -> None:
        pageHouseholds.selectGlobalProgramFilter("Test Programm").click()
        pageHouseholds.getNavProgrammePopulation().click()
        pageHouseholds.getNavHouseholds().click()
