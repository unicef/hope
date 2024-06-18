import pytest
from page_object.filters import Filters

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.mark.usefixtures("login")
class TestSmokeCountryDashboard:
    def test_smoke_country_dashboard(self, filters: Filters) -> None:
        filters.getNavCountryDashboard().click()
        from selenium_tests.tools.tag_name_finder import printing
        printing("Mapping", filters.driver)
        printing("Methods", filters.driver)
        printing("Mapping", filters.driver)
