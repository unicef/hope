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
    def test_smoke_page_individuals(self,
                                    create_programs: None,
                                    add_households: None,
                                    pageIndividuals: Individuals
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

    def test_smoke_page_individuals_details(self,
                                            create_programs: None,
                                            add_households: None,
                                            pageIndividuals: Individuals,
                                            pageIndividualsDetails: IndividualsDetails
                                            ) -> None:
        pageIndividuals.selectGlobalProgramFilter("Test Programm").click()
        pageIndividuals.getNavProgrammePopulation().click()
        pageIndividuals.getNavIndividuals().click()
        pageIndividuals.getIndividualTableRow()[0].click()
        print(pageIndividualsDetails.getLabelFullName().text)
        print(pageIndividualsDetails.getLabelGivenName().text)
        print(pageIndividualsDetails.getLabelMiddleName().text)
        print(pageIndividualsDetails.getLabelFamilyName().text)
        print(pageIndividualsDetails.getLabelGender().text)
        print(pageIndividualsDetails.getLabelAge().text)
        print(pageIndividualsDetails.getLabelDateOfBirth().text)
        print(pageIndividualsDetails.getLabelEstimatedDateOfBirth().text)
        print(pageIndividualsDetails.getLabelMaritalStatus().text)
        print(pageIndividualsDetails.getLabelWorkStatus().text)
        print(pageIndividualsDetails.getLabelPregnant().text)
        print(pageIndividualsDetails.getLabelHouseholdId().text)
        print(pageIndividualsDetails.getLabelRole().text)
        print(pageIndividualsDetails.getLabelRelationshipToHoh().text)
        print(pageIndividualsDetails.getLabelPreferredLanguage().text)
        print(pageIndividualsDetails.getLabelLinkedHouseholds().text)
        print(pageIndividualsDetails.getLabelObservedDisabilities().text)
        print(pageIndividualsDetails.getLabelSeeingDisabilitySeverity().text)
        print(pageIndividualsDetails.getLabelHearingDisabilitySeverity().text)
        print(pageIndividualsDetails.getLabelPhysicalDisabilitySeverity().text)
        print(pageIndividualsDetails.getLabelRememberingOrConcentratingDisabilitySeverity().text)
        print(pageIndividualsDetails.getLabelCommunicatingDisabilitySeverity().text)
        print(pageIndividualsDetails.getLabelDisability().text)
        print(pageIndividualsDetails.getLabelBirth_certificate().text)
        print(pageIndividualsDetails.getLabelIssued().text)
        print(pageIndividualsDetails.getLabelDrivers_license().text)
        print(pageIndividualsDetails.getLabelElectoral_card().text)
        print(pageIndividualsDetails.getLabelNational_passport().text)
        print(pageIndividualsDetails.getLabelNational_id().text)
        print(pageIndividualsDetails.getLabelUnhcrId().text)
        print(pageIndividualsDetails.getLabelWfpId().text)
        print(pageIndividualsDetails.getLabelEmail().text)
        print(pageIndividualsDetails.getLabelPhoneNumber().text)
        print(pageIndividualsDetails.getLabelAlternativePhoneNumber().text)
        print(pageIndividualsDetails.getLabelDateOfLastScreeningAgainstSanctionsList().text)
        print(pageIndividualsDetails.getLabelLinkedGrievances().text)
        print(pageIndividualsDetails.getLabelSchoolEnrolled().text)
        print(pageIndividualsDetails.getLabelSchoolEnrolledBefore().text)
