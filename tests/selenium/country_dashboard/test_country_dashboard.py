from datetime import timedelta
from random import choice
from typing import Callable

from django.utils import timezone

import pytest
from selenium.webdriver.common.by import By

from hct_mis_api.apps.dashboard.services import DashboardDataCache
from hct_mis_api.apps.geo.fixtures import AreaFactory
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.payment.fixtures import PaymentFactory
from hct_mis_api.apps.program.fixtures import ProgramFactory
from tests.selenium.page_object.country_dashboard.country_dashboard import (
    CountryDashboard,
)


@pytest.fixture
def setup_household_and_payments(business_area: Callable) -> tuple:
    """
    Fixture to create a household and associated payments within the same BusinessArea as the dashboard.
    """
    household_args = {
        "business_area": business_area,
        "program": ProgramFactory(business_area=business_area, status="Active"),
        "size": 5,
        "children_count": 2,
        "admin1": AreaFactory(name="Kabul", area_type__name="Province", area_type__area_level=1),
        "admin2": AreaFactory(name="Ayeara", area_type__name="District", area_type__area_level=2),
    }

    household, _ = create_household(household_args=household_args)
    payments = PaymentFactory.create_batch(
        2,
        household=household,
        delivered_quantity_usd=100,
        delivered_quantity=230,
        delivery_date=timezone.now() - timedelta(days=30),
        status=choice(["Transaction Successful", "Distribution Successful"]),
    )

    return household, payments


@pytest.mark.django_db(transaction=True, databases=["default", "read_only"])
@pytest.mark.usefixtures("login", "setup_household_and_payments")
class TestSmokeCountryDashboard:
    def test_smoke_country_dashboard(self, pageCountryDashboard: CountryDashboard, business_area: Callable) -> None:
        DashboardDataCache.refresh_data(business_area.slug)
        pageCountryDashboard.getNavCountryDashboard().click()
        pageCountryDashboard.switch_to_dashboard_iframe()
        assert pageCountryDashboard.get_total_amount_paid().text != "", "Expected total amount paid to be populated."
        assert (
            int(pageCountryDashboard.get_number_of_payments().text) > 0
        ), "Expected number of payments to be greater than zero."
        assert (
            pageCountryDashboard.get_outstanding_payments().text == "0.00 USD"
        ), "Expected outstanding payments to be 0.00 USD"
        assert (
            int(pageCountryDashboard.get_households_reached().text) > 0
        ), "Expected households reached to be greater than zero."
        assert int(pageCountryDashboard.get_pwd_reached().text) == 0, "Expected PWD reached to be zero."
        assert (
            int(pageCountryDashboard.get_children_reached().text) > 0
        ), "Expected children reached to be greater than zero."
        assert (
            int(pageCountryDashboard.get_individuals_reached().text) > 0
        ), "Expected individuals reached to be greater than zero."
        assert pageCountryDashboard.driver.find_element(
            By.ID, "payments-by-fsp"
        ).is_displayed(), "Payments by FSP chart should be displayed."
        assert pageCountryDashboard.driver.find_element(
            By.ID, "payments-by-delivery"
        ).is_displayed(), "Payments by Delivery chart should be displayed."
        assert pageCountryDashboard.driver.find_element(
            By.ID, "payments-by-sector"
        ).is_displayed(), "Payments by Sector chart should be displayed."

        pageCountryDashboard.switch_to_default_content()
        print("All checks in the Country Dashboard iframe passed successfully.")
