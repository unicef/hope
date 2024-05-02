from django.conf import settings
from django.core.management import call_command

import pytest
from page_object.targeting.create_new import CreateNew
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
        pageTargeting.screenshot("UseFilters")

    def test_smoke_targeting_create_use_ids(
        self, create_programs: None, add_targeting: None, pageTargeting: Targeting, pageCreateTargeting: CreateNew
    ) -> None:
        pageTargeting.selectGlobalProgramFilter("Test Programm").click()
        pageTargeting.getNavTargeting().click()
        pageTargeting.getButtonCreateNew().click()
        pageTargeting.getCreateUseIDs().click()
        pageTargeting.screenshot("UseIDs")

    def test_smoke_targeting_details_page(
        self, create_programs: None, add_targeting: None, pageTargeting: Targeting
    ) -> None:
        pageTargeting.selectGlobalProgramFilter("Test Programm").click()
        pageTargeting.getNavTargeting().click()
        pageTargeting.getTargetPopulationsRows()[0].click()
        pageTargeting.screenshot("Details")
