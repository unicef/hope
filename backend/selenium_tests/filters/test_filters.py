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

    def test_filters(self, login, create_programs, filters: Filters, pageProgrammeManagement):
        pageProgrammeManagement.selectGlobalProgramFilter("Test Program").click()
        pageProgrammeManagement.screenshot("1", delay_sec=0)
        actual_menu_items = pageProgrammeManagement.getDrawerItems().text.split("\n")

        for i in actual_menu_items:
            print(f"------------------------{i}--------------------------")
            pageProgrammeManagement.get(f'[data-cy="nav-{i}"]').click()
            sleep(2)

            def printing(what: str) -> None:
                for ii in ids:
                    data_cy_attribute = ii.get_attribute("data-cy")  # type: ignore
                    if "filter-" in data_cy_attribute:
                        var_name = [i.capitalize() for i in data_cy_attribute.lower().replace("-", " ").split(" ")]
                        method_name = "get" + "".join(var_name)
                        var_name[0] = var_name[0].lower()
                        var_name = "".join(var_name)  # type: ignore
                        if what == "Labels":
                            print(f"{var_name} = '{ii.tag_name}[data-cy=\"{data_cy_attribute}\"]'")
                        if what == "Methods":
                            print(f"def {method_name}(self) -> WebElement: \n\treturn self.wait_for(self.{var_name})\n")

            ids = filters.driver.find_elements(By.XPATH, f"//*[@data-cy]")
            printing("Labels")
            print("\n")
            printing("Methods")
