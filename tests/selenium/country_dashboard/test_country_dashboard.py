import pytest

from tests.selenium.page_object.country_dashboard.country_dashboard import (
    CountryDashboard,
)


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("login")
class TestSmokeCountryDashboard:
    def test_smoke_country_dashboard(self, pageCountryDashboard: CountryDashboard) -> None:
        pageCountryDashboard.getNavCountryDashboard().click()
        pageCountryDashboard.switch_to_dashboard_iframe()
        # assert pageCountryDashboard.get_total_amount_paid().text == "", "Expected total amount paid to be empty."
        # assert pageCountryDashboard.get_number_of_payments().text == "", "Expected number of payments to be empty."
        # assert pageCountryDashboard.get_outstanding_payments().text == "", "Expected outstanding payments to be empty."
        # assert pageCountryDashboard.get_households_reached().text == "", "Expected households reached to be empty."
        # assert pageCountryDashboard.get_pwd_reached().text == "", "Expected PWD reached to be empty."
        # assert pageCountryDashboard.get_children_reached().text == "", "Expected children reached to be empty."
        # assert pageCountryDashboard.get_individuals_reached().text == "", "Expected individuals reached to be empty."
        # assert pageCountryDashboard.driver.find_element(By.ID, "payments-by-fsp").is_displayed(), \
        #     "Payments by FSP chart should be displayed."
        # assert pageCountryDashboard.driver.find_element(By.ID, "payments-by-delivery").is_displayed(), \
        #     "Payments by Delivery chart should be displayed."
        # assert pageCountryDashboard.driver.find_element(By.ID, "payments-by-sector").is_displayed(), \
        #     "Payments by Sector chart should be displayed."
        # pageCountryDashboard.switch_to_default_content()
        # print("All checks in the Country Dashboard iframe passed successfully.")
