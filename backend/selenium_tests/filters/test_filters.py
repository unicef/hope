from time import sleep

from django.conf import settings
from django.core.management import call_command

import pytest
from page_object.filters import Filters
from selenium.webdriver.common.by import By

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def create_programs() -> None:
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/core/fixtures/data-selenium.json")
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/program/fixtures/data-cypress.json")
    return


class TestSmokeFilters:
    @pytest.mark.skip()
    def test_filters_all_programs(self, login, create_programs, filters: Filters):
        all_programs = {
            "Country Dashboard": [filters.globalProgramFilter, filters.globalProgramFilterContainer],
            "Programs": [
                filters.filtersDataCollectingType,
                filters.filtersBudgetMax,
                filters.filtersBudgetMin,
                filters.filtersNumberOfHouseholdsMin,
                filters.filtersNumberOfHouseholdsMax,
                filters.filtersSector,
                filters.filtersStartDate,
                filters.filtersEndDate,
                filters.filtersStatus,
                filters.filtersSearch,
            ],
            "Grievance": [
                filters.filtersSearch,
                filters.selectFilter,
                filters.filtersDocumentType,
                filters.filtersDocumentNumber,
                filters.filtersProgram,
                filters.programmeInput,
                filters.selectFilter,
                filters.filtersStatus,
                filters.filtersFsp,
                filters.filtersCreationDateFrom,
                filters.filtersCreationDateTo,
                filters.selectFilter,
                filters.filtersCategory,
                filters.filtersAdminLevel,
                filters.filtersAssignee,
                filters.assignedToInput,
                filters.filtersCreatedByAutocomplete,
                filters.filtersRegistrationDataImport,
                filters.filtersPreferredLanguage,
                filters.filtersPriority,
                filters.filtersUrgency,
                filters.filtersActiveTickets,
                filters.filtersProgramState,
            ],
            "Feedback": [
                filters.filtersSearch,
                filters.filtersProgram,
                filters.programmeInput,
                filters.selectFilter,
                filters.filtersIssueType,
                filters.filtersCreatedByAutocomplete,
                filters.filtersCreationDateFrom,
                filters.filtersCreationDateTo,
                filters.selectFilter,
                filters.filtersProgramState,
            ],
            "Reporting": [
                filters.reportOnlyMyFilter,
                filters.reportStatusFilter,
                filters.reportCreatedToFilter,
                filters.reportCreatedFromFilter,
                filters.reportTypeFilter,
            ],
            "Activity Log": [
                filters.filtersResidenceStatus,
                filters.filtersSearch,
                filters.userInput,
                filters.selectFilter,
            ],
        }

        for nav_menu in all_programs:
            if nav_menu == "Feedback":
                filters.wait_for(f'[data-cy="nav-Grievance"]').click()
            filters.wait_for(f'[data-cy="nav-{nav_menu}"]').click()
            filters.wait_for(all_programs[nav_menu][0])
            ids = filters.driver.find_elements(By.XPATH, f"//*[@data-cy]")
            list_locators = []
            for i in ids:
                if "button-filters-apply" == i.get_attribute("data-cy"):
                    break
                list_locators.append(f'{i.tag_name}[data-cy="{i.get_attribute("data-cy")}"]')
            for locator in all_programs[nav_menu]:
                assert locator in list_locators

    def test_filters_selected_program(self, login, create_programs, filters: Filters):
        filters.selectGlobalProgramFilter("Test Programm").click()

        programs = {
            "Registration Data Import": [
                filters.filterSearch,
                filters.importedByInput,
                filters.selectFilter,
                filters.filterStatus,
                filters.filterSizeMin,
                filters.filterSizeMax,
                filters.filterImportDateRangeMin,
                filters.filterImportDateRangeMax,
            ],
            "Program Population": [
                filters.selectFilter,
                filters.filtersDocumentType,
                filters.filtersDocumentNumber,
                filters.selectFilter,
                filters.hhFiltersResidenceStatus,
                filters.hhFiltersAdmin2,
                filters.hhFiltersHouseholdSizeFrom,
                filters.hhFiltersHouseholdSizeTo,
                filters.selectFilter,
                filters.hhFiltersOrderBy,
                filters.selectFilter,
                filters.hhFiltersStatus,
            ],
            "Individuals": [
                filters.indFiltersSearch,
                filters.selectFilter,
                filters.filtersDocumentType,
                filters.filtersDocumentNumber,
                filters.selectFilter,
                filters.indFiltersGender,
                filters.indFiltersAgeFrom,
                filters.indFiltersAgeTo,
                filters.selectFilter,
                filters.indFiltersFlags,
                filters.selectFilter,
                filters.indFiltersOrderBy,
                filters.selectFilter,
                filters.indFiltersStatus,
                filters.indFiltersRegDateFrom,
                filters.indFiltersRegDateTo,
            ],
            "Targeting": [
                filters.filtersSearch,
                filters.selectFilter,
                filters.filtersStatus,
                filters.filtersTotalHouseholdsCountMin,
                filters.filtersTotalHouseholdsCountMax,
                filters.datePickerFilterFrom,
                filters.datePickerFilterTo,
            ],
            "Payment Module": [
                filters.selectFilter,
                filters.filtersTotalEntitledQuantityFrom,
                filters.filtersTotalEntitledQuantityTo,
                filters.datePickerFilterFrom,
                filters.datePickerFilterTo,
            ],
            "Payment Verification": [
                filters.filterSearch,
                filters.selectFilter,
                filters.filterStatus,
                filters.filterFsp,
                filters.selectFilter,
                filters.filterModality,
                filters.filterStartDate,
                filters.filterEndDate,
            ],
            "Grievance": [
                filters.filtersSearch,
                filters.selectFilter,
                filters.filtersDocumentType,
                filters.filtersDocumentNumber,
                filters.selectFilter,
                filters.filtersStatus,
                filters.filtersFsp,
                filters.filtersCreationDateFrom,
                filters.filtersCreationDateTo,
                filters.selectFilter,
                filters.filtersCategory,
                filters.filtersAdminLevel,
                filters.filtersAssignee,
                filters.assignedToInput,
                filters.filtersCreatedByAutocomplete,
                filters.filtersRegistrationDataImport,
                filters.filtersPreferredLanguage,
                filters.filtersPriority,
                filters.filtersUrgency,
                filters.filtersActiveTickets,
            ],
            "Feedback": [
                filters.filtersSearch,
                filters.selectFilter,
                filters.filtersIssueType,
                filters.filtersCreatedByAutocomplete,
                filters.filtersCreationDateFrom,
                filters.filtersCreationDateTo,
            ],
            "Accountability": [
                filters.filtersTargetPopulationAutocomplete,
                filters.targetPopulationInput,
                filters.filtersCreatedByAutocomplete,
                filters.createdByInput,
                filters.filtersCreationDateFrom,
                filters.filtersCreationDateTo
            ],
            "Surveys": [
                filters.filtersSearch,
                filters.filtersTargetPopulationAutocomplete,
                filters.targetPopulationInput,
                filters.filtersCreatedByAutocomplete,
                filters.createdByInput,
                filters.filtersCreationDateFrom,
                filters.filtersCreationDateTo,
            ],
            # "Programme Users": [],
            "Program Log": [
                filters.filtersSearch,
                filters.selectFilter,
                filters.filtersResidenceStatus,
                filters.userInput,
            ],
        }

        for nav_menu in programs:
            if nav_menu == "Feedback":
                filters.wait_for(f'[data-cy="nav-Grievance"]').click()
            if nav_menu == "Individuals":
                filters.wait_for(f'[data-cy="nav-Program Population"]').click()
            if nav_menu == "Surveys":
                filters.wait_for(f'[data-cy="nav-Accountability"]').click()
            filters.wait_for(f'[data-cy="nav-{nav_menu}"]').click()
            # filters.wait_for(programs[nav_menu][0], timeout=20)
            sleep(10)
            ids = filters.driver.find_elements(By.XPATH, f"//*[@data-cy]")
            print(f"---------------{nav_menu}---------------")
            list_locators = []
            for i in ids:
                if "button-filters-clear" == i.get_attribute("data-cy"):
                    break
                data_cy_attribute = i.get_attribute("data-cy")  # type: ignore
                var_name = [i.capitalize() for i in data_cy_attribute.lower().replace("-", " ").split(" ")]
                var_name[0] = var_name[0].lower()
                var_name = "".join(var_name)  # type: ignore
                print(f"filters.{var_name}, ")
                list_locators.append(f'{i.tag_name}[data-cy="{i.get_attribute("data-cy")}"]')
            print(list_locators)
            for locator in programs[nav_menu]:
                assert locator in list_locators
