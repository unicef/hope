import pytest
from page_object.programme_population.individuals import Individuals

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.mark.usefixtures("login")
class TestSmokeIndividuals:
    def test_smoke_page_individuals(self, pageIndividuals: Individuals) -> None:
        pageIndividuals.getNavProgrammePopulation().click()
        pageIndividuals.getNavHouseholds().click()

    def test_smoke_page_individuals_details(
        self, pageIndividuals: Individuals
    ) -> None:
        pageIndividuals.getNavProgrammePopulation().click()
        pageIndividuals.getNavHouseholds().click()
