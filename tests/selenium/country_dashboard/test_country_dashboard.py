import pytest

from tests.selenium.page_object.country_dashboard.country_dashboard import (
    CountryDashboard,
)

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.mark.usefixtures("login")
class TestSmokeCountryDashboard:
    def test_smoke_country_dashboard_with_and_without_data(self, pageCountryDashboard: CountryDashboard) -> None:
        pageCountryDashboard.get_nav_resources_release_note().click()
        assert "Dashboard" in pageCountryDashboard.get_page_header_title().text
        assert pageCountryDashboard.get_main_content().is_displayed()
        assert pageCountryDashboard.get_page_header_container().is_displayed()
        pageCountryDashboard.switch_to_dashboard_iframe()
        assert pageCountryDashboard.get_total_amount_paid().text == ""
        assert pageCountryDashboard.get_number_of_payments().text == ""
        assert pageCountryDashboard.get_outstanding_payments().text == ""
        assert pageCountryDashboard.get_households_reached().text == ""
        assert pageCountryDashboard.get_pwd_reached().text == ""
        assert pageCountryDashboard.get_children_reached().text == ""
        assert pageCountryDashboard.get_individuals_reached().text == ""
        assert pageCountryDashboard.get_reconciliation_percentage().text == "%"
        assert pageCountryDashboard.get_pending_reconciliation_percentage().text == "%"
        spinners = pageCountryDashboard.get_spinner_elements()
        assert len(spinners) > 0, "Expected chart loading spinners to be present when no data is loaded."
        pageCountryDashboard.switch_to_default_content()
