from django.conf import settings
from django.core.management import call_command

import pytest
from page_object.filters import Filters
from selenium.common.exceptions import TimeoutException

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def create_programs() -> None:
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/core/fixtures/data-selenium.json")
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/program/fixtures/data-cypress.json")
    return


class TestSmokeFilters:

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
            for locator in all_programs[nav_menu]:
                try:
                    filters.wait_for(locator, timeout=20)
                except BaseException:
                    raise Exception(f"Element {locator} not found on the {nav_menu} page.")

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
                filters.createdByInput,
                filters.filtersCreationDateFrom,
                filters.filtersCreationDateTo
            ],
            "Surveys": [
                filters.filtersSearch,
                filters.filtersTargetPopulationAutocomplete,
                filters.targetPopulationInput,
                filters.createdByInput,
                filters.filtersCreationDateFrom,
                filters.filtersCreationDateTo,
            ],
            "Programme Users": [],
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
            for locator in programs[nav_menu]:
                try:
                    filters.wait_for(locator, timeout=20)
                except BaseException:
                    raise Exception(f"Element {locator} not found on the {nav_menu} page.")

