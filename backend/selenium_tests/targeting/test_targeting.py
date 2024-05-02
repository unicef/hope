from django.conf import settings
from django.core.management import call_command

import pytest
from page_object.targeting.create_new import CreateNew
from page_object.targeting.t_details_page import DetailsTargeting
from page_object.targeting.targeting import Targeting

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def create_programs() -> None:
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/core/fixtures/data-selenium.json")
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/program/fixtures/data-cypress.json")
    return


@pytest.fixture
def add_targeting() -> None:
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/household/fixtures/documenttype.json")
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/registration_data/fixtures/data-cypress.json")
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/household/fixtures/data-cypress.json")
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/targeting/fixtures/data-cypress.json")


@pytest.mark.usefixtures("login")
class TestSmokeTargeting:
    def test_smoke_targeting_page(self, create_programs: None, add_targeting: None, pageTargeting: Targeting) -> None:
        pageTargeting.selectGlobalProgramFilter("Test Programm").click()
        pageTargeting.getNavTargeting().click()
        assert "Targeting" in pageTargeting.getTitlePage().text
        assert "CREATE NEW" in pageTargeting.getButtonCreateNew().text
        expected_column_names = ["Name", "Status", "Num. of Households", "Date Created", "Last Edited", "Created by"]
        assert expected_column_names == [name.text for name in pageTargeting.getTabColumnLabel()]
        assert 2 == len(pageTargeting.getTargetPopulationsRows())
        pageTargeting.getButtonCreateNew().click()
        assert "Use Filters" in pageTargeting.getCreateUseFilters().text
        assert "Use IDs" in pageTargeting.getCreateUseIDs().text

    def test_smoke_targeting_create_use_filters(
        self, create_programs: None, add_targeting: None, pageTargeting: Targeting, pageCreateTargeting: CreateNew
    ) -> None:
        pageTargeting.selectGlobalProgramFilter("Test Programm").click()
        pageTargeting.getNavTargeting().click()
        pageTargeting.getButtonCreateNew().click()
        pageTargeting.getCreateUseFilters().click()
        assert "New Target Population" in pageCreateTargeting.getPageHeaderTitle().text
        assert "SAVE" in pageCreateTargeting.getButtonTargetPopulationCreate().text
        pageCreateTargeting.getInputName()
        pageCreateTargeting.getDivTargetPopulationAddCriteria().click()
        pageCreateTargeting.getButtonHouseholdRule().click()
        pageCreateTargeting.getButtonIndividualRule().click()
        pageCreateTargeting.getAutocompleteTargetCriteriaOption().click()

    def test_smoke_targeting_create_use_ids(
        self, create_programs: None, add_targeting: None, pageTargeting: Targeting, pageCreateTargeting: CreateNew
    ) -> None:
        pageTargeting.selectGlobalProgramFilter("Test Programm").click()
        pageTargeting.getNavTargeting().click()
        pageTargeting.getButtonCreateNew().click()
        pageTargeting.getCreateUseIDs().click()
        assert "New Target Population" in pageCreateTargeting.getPageHeaderTitle().text
        assert "SAVE" in pageCreateTargeting.getButtonTargetPopulationCreate().text
        pageCreateTargeting.getInputName()
        pageCreateTargeting.getInputIncludedHouseholdIds()
        pageCreateTargeting.getInputHouseholdids()
        pageCreateTargeting.getInputIncludedIndividualIds()
        pageCreateTargeting.getInputIndividualids()

    def test_smoke_targeting_details_page(
        self,
        create_programs: None,
        add_targeting: None,
        pageTargeting: Targeting,
        pageDetailsTargeting: DetailsTargeting,
    ) -> None:
        pageTargeting.selectGlobalProgramFilter("Test Programm").click()
        pageTargeting.getNavTargeting().click()
        pageTargeting.chooseTargetPopulations(0).click()
        assert "Copy TP" in pageDetailsTargeting.getPageHeaderTitle().text
        pageDetailsTargeting.getButtonTargetPopulationDuplicate()
        pageDetailsTargeting.getButtonDelete()
        assert "EDIT" in pageDetailsTargeting.getButtonEdit().text
        assert "REBUILD" in pageDetailsTargeting.getButtonRebuild().text
        assert "LOCK" in pageDetailsTargeting.getButtonTargetPopulationLock().text
        assert "Details" in pageDetailsTargeting.getDetailsTitle().text
        assert "OPEN" in pageDetailsTargeting.getLabelStatus().text
        assert "OPEN" in pageDetailsTargeting.getTargetPopulationStatus().text
        assert "CREATED BY" in pageDetailsTargeting.getLabelizedFieldContainerCreatedBy().text
        pageDetailsTargeting.getLabelCreatedBy()
        assert "PROGRAMME POPULATION CLOSE DATE" in pageDetailsTargeting.getLabelizedFieldContainerCloseDate().text
        assert "PROGRAMME" in pageDetailsTargeting.getLabelizedFieldContainerProgramName().text
        assert "Test Programm" in pageDetailsTargeting.getLabelProgramme().text
        assert "SEND BY" in pageDetailsTargeting.getLabelizedFieldContainerSendBy().text
        assert "-" in pageDetailsTargeting.getLabelSendBy().text
        assert "-" in pageDetailsTargeting.getLabelSendDate().text
        assert "-" in pageDetailsTargeting.getCriteriaContainer().text
        assert "0" in pageDetailsTargeting.getLabelFemaleChildren().text
        assert "0" in pageDetailsTargeting.getLabelMaleChildren().text
        assert "0" in pageDetailsTargeting.getLabelMaleAdults().text
        assert "2" in pageDetailsTargeting.getLabelTotalNumberOfHouseholds().text
        assert "8" in pageDetailsTargeting.getLabelTargetedIndividuals().text
        assert "Households" in pageDetailsTargeting.getTableTitle().text
        expected_menu_items = [
            "ID",
            "Head of Household",
            "Household Size",
            "Administrative Level 2",
            "Score",
        ]
        assert expected_menu_items == [i.text for i in pageDetailsTargeting.getTableLabel()]
