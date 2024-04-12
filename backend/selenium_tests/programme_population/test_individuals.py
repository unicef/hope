from django.conf import settings
from django.core.management import call_command

import pytest
from page_object.programme_population.individuals import Individuals
from page_object.programme_population.individuals_details import IndividualsDetails

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def create_programs() -> None:
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/core/fixtures/data-selenium.json")
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/program/fixtures/data-cypress.json")
    return


@pytest.fixture
def add_households() -> None:
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/registration_data/fixtures/data-cypress.json")
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/household/fixtures/documenttype.json")
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/household/fixtures/data-cypress.json")
    return


@pytest.mark.usefixtures("login")
class TestSmokeIndividuals:
    def test_smoke_page_individuals(
        self, create_programs: None, add_households: None, pageIndividuals: Individuals
    ) -> None:
        pageIndividuals.selectGlobalProgramFilter("Test Programm").click()
        pageIndividuals.getNavProgrammePopulation().click()
        pageIndividuals.getNavIndividuals().click()
        assert "Individuals" in pageIndividuals.getTableTitle().text
        assert "Individual ID" in pageIndividuals.getIndividualId().text
        assert "Individual" in pageIndividuals.getIndividualName().text
        assert "Household ID" in pageIndividuals.getHouseholdId().text
        assert "Relationship to HoH" in pageIndividuals.getRelationship().text
        assert "Age" in pageIndividuals.getIndividualAge().text
        assert "Gender" in pageIndividuals.getIndividualSex().text
        assert "Administrative Level 2" in pageIndividuals.getIndividualLocation().text
        assert 6 == len(pageIndividuals.getIndividualTableRow())

    def test_smoke_page_individuals_details(
        self,
        create_programs: None,
        add_households: None,
        pageIndividuals: Individuals,
        pageIndividualsDetails: IndividualsDetails,
    ) -> None:
        pageIndividuals.selectGlobalProgramFilter("Test Programm").click()
        pageIndividuals.getNavProgrammePopulation().click()
        pageIndividuals.getNavIndividuals().click()
        pageIndividuals.getIndividualTableRow()[0].click()
        assert "Alicja Kowalska" in pageIndividualsDetails.getLabelFullName().text
        assert "Alicja" in pageIndividualsDetails.getLabelGivenName().text
        assert "-" in pageIndividualsDetails.getLabelMiddleName().text
        assert "Kowalska" in pageIndividualsDetails.getLabelFamilyName().text
        assert "Female" in pageIndividualsDetails.getLabelGender().text
        assert "82" in pageIndividualsDetails.getLabelAge().text
        assert "26 Aug 1941" in pageIndividualsDetails.getLabelDateOfBirth().text
        assert "No" in pageIndividualsDetails.getLabelEstimatedDateOfBirth().text
        assert "Married" in pageIndividualsDetails.getLabelMaritalStatus().text
        assert "Not provided" in pageIndividualsDetails.getLabelWorkStatus().text
        assert "Yes" in pageIndividualsDetails.getLabelPregnant().text
        assert "-" in pageIndividualsDetails.getLabelHouseholdId().text
        assert "Alternate collector" in pageIndividualsDetails.getLabelRole().text
        assert (
            "Not a Family Member. Can only act as a recipient."
            in pageIndividualsDetails.getLabelRelationshipToHoh().text
        )
        assert "-" in pageIndividualsDetails.getLabelPreferredLanguage().text
        assert "HH-20-0000.0001 -Alternate collector" in pageIndividualsDetails.getLabelLinkedHouseholds().text
        assert "-" in pageIndividualsDetails.getLabelObservedDisabilities().text
        assert "None" in pageIndividualsDetails.getLabelSeeingDisabilitySeverity().text
        assert "None" in pageIndividualsDetails.getLabelHearingDisabilitySeverity().text
        assert "None" in pageIndividualsDetails.getLabelPhysicalDisabilitySeverity().text
        assert "None" in pageIndividualsDetails.getLabelRememberingOrConcentratingDisabilitySeverity().text
        assert "None" in pageIndividualsDetails.getLabelCommunicatingDisabilitySeverity().text
        assert "Not Disabled" in pageIndividualsDetails.getLabelDisability().text
        assert "Poland" in pageIndividualsDetails.getLabelIssued().text
        assert "fake111test@email.com" in pageIndividualsDetails.getLabelEmail().text
        assert "0048503123555" in pageIndividualsDetails.getLabelPhoneNumber().text
        assert "-" in pageIndividualsDetails.getLabelAlternativePhoneNumber().text
        assert "-" in pageIndividualsDetails.getLabelDateOfLastScreeningAgainstSanctionsList().text
