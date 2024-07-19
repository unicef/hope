from time import sleep

from django.conf import settings
from django.core.management import call_command

import pytest
from page_object.programme_population.households import Households
from page_object.programme_population.households_details import HouseholdsDetails

from selenium_tests.page_object.programme_population.individuals import Individuals
from selenium_tests.tools.tag_name_finder import printing

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def create_programs() -> None:
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/core/fixtures/data-selenium.json")
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/program/fixtures/data-cypress.json")
    yield


@pytest.fixture
def add_households() -> None:
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/registration_data/fixtures/data-cypress.json")
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/household/fixtures/data-cypress.json")
    yield


@pytest.mark.usefixtures("login")
class TestPeriodicDataUpdateUpload:
    def test_periodic_data_update_upload(
        self,
        create_programs: None,
        add_households: None,
        pageIndividuals: Individuals,
    ) -> None:
        pageIndividuals.selectGlobalProgramFilter("Test Programm").click()
        pageIndividuals.getNavProgrammePopulation().click()
        pageIndividuals.getNavIndividuals().click()
        pageIndividuals.getTabPeriodicDataUpdates().click()
        sleep(2)
        printing("Mapping", pageIndividuals.driver)
        printing("Methods", pageIndividuals.driver)


