from django.conf import settings
from django.core.management import call_command

import pytest

from tests.selenium.page_object.programme_population.households import Households
from tests.selenium.page_object.programme_population.households_details import (
    HouseholdsDetails,
)

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
class TestSmokeHouseholds:
    def test_smoke_page_households(
        self, create_programs: None, add_households: None, pageHouseholds: Households
    ) -> None:
        pageHouseholds.selectGlobalProgramFilter("Test Programm")
        pageHouseholds.getNavProgrammePopulation().click()
        pageHouseholds.getNavHouseholds().click()
        assert 2 == len(pageHouseholds.getHouseholdsRows())
        assert "Households" in pageHouseholds.getTableTitle().text
        assert "Household ID" in pageHouseholds.getHouseholdId().text
        assert "Status" in pageHouseholds.getStatus().text
        assert "Head of Household" in pageHouseholds.getHouseholdHeadName().text
        assert "Household Size" in pageHouseholds.getHouseholdSize().text
        assert "Administrative Level 2" in pageHouseholds.getHouseholdLocation().text
        assert "Residence Status" in pageHouseholds.getHouseholdResidenceStatus().text
        assert "Total Cash Received" in pageHouseholds.getHouseholdTotalCashReceived().text
        assert "Registration Date" in pageHouseholds.getHouseholdRegistrationDate().text

    def test_smoke_page_households_details(
        self,
        create_programs: None,
        add_households: None,
        pageHouseholds: Households,
        pageHouseholdsDetails: HouseholdsDetails,
    ) -> None:
        pageHouseholds.selectGlobalProgramFilter("Test Programm")
        pageHouseholds.getNavProgrammePopulation().click()
        pageHouseholds.getNavHouseholds().click()
        pageHouseholds.getHouseholdsRowByNumber(0).click()
        assert "4" in pageHouseholdsDetails.getLabelHouseholdSize().text
        assert "Displaced | Refugee / Asylum Seeker" in pageHouseholdsDetails.getLabelResidenceStatus().text
        assert "Agata Kowalska" in pageHouseholdsDetails.getLabelHeadOfHousehold().text
        assert "No" in pageHouseholdsDetails.getLabelFemaleChildHeadedHousehold().text
        assert "No" in pageHouseholdsDetails.getLabelChildHeadedHousehold().text
        assert "Afghanistan" in pageHouseholdsDetails.getLabelCountry().text
        assert "Afghanistan" in pageHouseholdsDetails.getLabelCountryOfOrigin().text
        assert "938 Luna Cliffs Apt. 551 Jameschester, SC 24934" in pageHouseholdsDetails.getLabelAddress().text
        assert "-" in pageHouseholdsDetails.getLabelVillage().text
        assert "-" in pageHouseholdsDetails.getLabelZipCode().text
        assert "-" in pageHouseholdsDetails.getLabelAdministrativeLevel1().text
        assert "-" in pageHouseholdsDetails.getLabelAdministrativeLevel2().text
        assert "-" in pageHouseholdsDetails.getLabelAdministrativeLevel3().text
        assert "-" in pageHouseholdsDetails.getLabelAdministrativeLevel4().text
        assert "70.210209, 172.085021" in pageHouseholdsDetails.getLabelGeolocation().text
        assert "-" in pageHouseholdsDetails.getLabelUnhcrCaseId().text
        assert "-" in pageHouseholdsDetails.getLabelLengthOfTimeSinceArrival().text
        assert "-" in pageHouseholdsDetails.getLabelNumberOfTimesDisplaced().text
        assert "No" in pageHouseholdsDetails.getLabelIsThisAReturneeHousehold().text
        assert "-" in pageHouseholdsDetails.getLabelLinkedGrievances().text
        assert "Full_TEST" in pageHouseholdsDetails.getLabelDataCollectingType().text
        assert "USD 0.00" in pageHouseholdsDetails.getLabelCashReceived().text
        assert "USD 0.00" in pageHouseholdsDetails.getLabelTotalCashReceived().text
        assert "Household Members" in pageHouseholdsDetails.getTableTitle().text
        assert "Individual ID" in pageHouseholdsDetails.getTableLabel().text
        assert "ACTIVE" in pageHouseholdsDetails.getStatusContainer().text
        assert "No results" in pageHouseholdsDetails.getTableRow().text
        assert "XLS" in pageHouseholdsDetails.getLabelSource().text
        assert "Test" in pageHouseholdsDetails.getLabelImportName().text
        assert "22 Aug 2020" in pageHouseholdsDetails.getLabelRegistrationDate().text
        assert "test@example.com" in pageHouseholdsDetails.getLabelUserName().text
