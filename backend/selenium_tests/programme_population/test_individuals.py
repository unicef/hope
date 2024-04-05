from django.conf import settings
from django.core.management import call_command

import pytest
from page_object.programme_population.individuals import Individuals

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def create_programs() -> None:
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/core/fixtures/data-selenium.json")
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/program/fixtures/data-cypress.json")
    return


@pytest.fixture
def add_households() -> None:
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/registration_data/fixtures/data-cypress.json")
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/household/fixtures/data-cypress.json")
    return


@pytest.mark.usefixtures("login")
class TestSmokeIndividuals:
    def test_smoke_page_individuals(self, create_programs: None, pageIndividuals: Individuals) -> None:
        pageIndividuals.selectGlobalProgramFilter("Test Programm").click()
        pageIndividuals.getNavProgrammePopulation().click()
        pageIndividuals.getNavHouseholds().click()

    def test_smoke_page_individuals_details(self, create_programs: None, pageIndividuals: Individuals) -> None:
        pageIndividuals.selectGlobalProgramFilter("Test Programm").click()
        pageIndividuals.getNavProgrammePopulation().click()
        pageIndividuals.getNavHouseholds().click()
