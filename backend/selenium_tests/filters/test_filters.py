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

    def test_filters_all_programs(self, login, create_programs, filters: Filters, pageProgrammeManagement):

        all_programs = {
            "Country Dashboard": [filters.globalProgramFilter, filters.globalProgramFilterContainer],
            "Programs": [filters.filtersDataCollectingType,
                         filters.filtersBudgetMax,
                         filters.filtersBudgetMin,
                         filters.filtersNumberOfHouseholdsMin,
                         filters.filtersNumberOfHouseholdsMax,
                         filters.filtersSector,
                         filters.filtersStartDate,
                         filters.filtersEndDate,
                         filters.filtersStatus,
                         filters.filtersSearch],
            "Grievance": [filters.filtersSearch,
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
                          filters.registrationDataImportInput,
                          filters.filtersPreferredLanguage,
                          filters.filtersPriority,
                          filters.filtersUrgency,
                          filters.filtersActiveTickets,
                          filters.filtersProgramState,
                          ],
            "Reporting": [filters.reportOnlyMyFilter,
                          filters.reportStatusFilter,
                          filters.reportCreatedToFilter,
                          filters.reportCreatedFromFilter,
                          filters.reportTypeFilter
                          ],
            "Activity Log": [filters.filtersResidenceStatus,
                             filters.filtersSearch,
                             filters.userInput,
                             filters.selectFilter],
        }

        for nav_menu in all_programs:
            if nav_menu == "Feedback":
                pageProgrammeManagement.wait_for(f'[data-cy="nav-Grievance"]').click()
            pageProgrammeManagement.wait_for(f'[data-cy="nav-{nav_menu}"]').click()
            sleep(5)
            ids = filters.driver.find_elements(By.XPATH, f"//*[@data-cy]")
            print(f"---------------{nav_menu}---------------")
            for locator in all_programs[nav_menu]:
                list_locators = []
                for i in ids:
                    if 'button-filters-apply' == i.get_attribute("data-cy"):
                        break
                    data_cy_attribute = i.get_attribute("data-cy")  # type: ignore
                    var_name = [i.capitalize() for i in data_cy_attribute.lower().replace("-", " ").split(" ")]
                    var_name[0] = var_name[0].lower()
                    var_name = "".join(var_name)  # type: ignore
                    print(f"filters.{var_name}, ")
                    list_locators.append(f'{i.tag_name}[data-cy=\"{i.get_attribute("data-cy")}\"]')
                assert locator in list_locators

    @pytest.mark.skip()
    def test_filters_selected_program(self, login, create_programs, filters: Filters, pageProgrammeManagement):
        pageProgrammeManagement.selectGlobalProgramFilter("Test Program").click()
        pageProgrammeManagement.screenshot("1", delay_sec=0)

        programs = {
            "Registration Data Import": [],
            "Program Population": [],
            "Program Details": [],
            "Targeting": [],
            "Payment Verification": [],
            "Grievance": [],
            "Programme Users": [],
            "Program Log": [],
        }

        for nav_menu in programs:
            pageProgrammeManagement.wait_for(f'[data-cy="nav-{nav_menu}"]').click()
            ids = filters.driver.find_elements(By.XPATH, f"//*[@data-cy]")
            for locator in programs[nav_menu]:
                assert locator in printing(ids)
