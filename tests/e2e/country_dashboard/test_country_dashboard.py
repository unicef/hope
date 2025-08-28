from datetime import timedelta
from random import choice
from typing import Callable

from django.utils import timezone
from e2e.page_object.country_dashboard.country_dashboard import CountryDashboard
from extras.test_utils.factories.geo import AreaFactory
from extras.test_utils.factories.household import create_household
from extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory
from extras.test_utils.factories.program import ProgramFactory
import factory
import pytest
from selenium.webdriver.common.by import By

from hope.apps.dashboard.services import DashboardDataCache
from hope.apps.program.models import BeneficiaryGroup


class ModifiedPaymentFactory(PaymentFactory):
    """
    A specialized factory for creating Payments that match the filtering logic
    in DashboardDataCache.refresh_data.
    """

    parent = factory.SubFactory(PaymentPlanFactory, status=factory.Iterator(["ACCEPTED", "FINISHED"]))
    status = factory.Iterator(
        [
            "Transaction Successful",
            "Distribution Successful",
            "Partially Distributed",
            "Pending",
        ]
    )
    delivered_quantity = factory.Faker("random_int", min=100, max=500)
    delivered_quantity_usd = factory.Faker("random_int", min=100, max=200)
    delivery_date = factory.Faker("date_time_this_month", before_now=True)


@pytest.fixture
def setup_household_and_payments(business_area: Callable) -> tuple:
    """
    Fixture to create a household and associated payments within the same BusinessArea as the dashboard.
    """
    beneficiary_group = BeneficiaryGroup.objects.filter(name="Main Menu").first()
    household_args = {
        "business_area": business_area,
        "program": ProgramFactory(
            business_area=business_area,
            status="Active",
            beneficiary_group=beneficiary_group,
        ),
        "size": 5,
        "children_count": 2,
        "admin1": AreaFactory(name="Kabul", area_type__name="Province", area_type__area_level=1),
    }

    household, _ = create_household(household_args=household_args)
    payments = ModifiedPaymentFactory.create_batch(
        2,
        household=household,
        delivered_quantity_usd=100,
        delivered_quantity=230,
        delivery_date=timezone.now() - timedelta(days=30),
        status=choice(["Transaction Successful", "Distribution Successful"]),
    )

    return household, payments


@pytest.mark.xfail(reason="UNSTABLE")
@pytest.mark.django_db
@pytest.mark.usefixtures("login", "setup_household_and_payments")
class TestSmokeCountryDashboard:
    def test_smoke_country_dashboard(self, page_country_dashboard: CountryDashboard, business_area: Callable) -> None:
        DashboardDataCache.refresh_data(business_area.slug)
        page_country_dashboard.get_nav_country_dashboard().click()
        page_country_dashboard.switch_to_dashboard_iframe()

        from selenium.webdriver.support.ui import WebDriverWait

        wait = WebDriverWait(page_country_dashboard.driver, 20)
        wait.until(
            lambda driver: page_country_dashboard.get_total_amount_paid().text != ""
            and page_country_dashboard.get_total_amount_paid().text != "0.00 USD"
        )

        assert page_country_dashboard.get_total_amount_paid().text != "", "Expected total amount paid to be populated."
        assert page_country_dashboard.get_total_amount_paid_local().text != "", (
            "Expected total amount in local paid to be populated."
        )
        assert int(page_country_dashboard.get_number_of_payments().text) > 0, (
            "Expected number of payments to be greater than zero."
        )
        assert page_country_dashboard.get_outstanding_payments().text == "0.00 USD", (
            "Expected outstanding payments to be 0.00 USD"
        )
        assert int(page_country_dashboard.get_households_reached().text) > 0, (
            "Expected households reached to be greater than zero."
        )
        assert int(page_country_dashboard.get_pwd_reached().text) == 0, "Expected PWD reached to be zero."
        assert int(page_country_dashboard.get_children_reached().text) > 0, (
            "Expected children reached to be greater than zero."
        )
        assert int(page_country_dashboard.get_individuals_reached().text) > 0, (
            "Expected individuals reached to be greater than zero."
        )
        assert page_country_dashboard.driver.find_element(By.ID, "payments-by-fsp").is_displayed(), (
            "Payments by FSP chart should be displayed."
        )
        assert page_country_dashboard.driver.find_element(By.ID, "payments-by-delivery").is_displayed(), (
            "Payments by Delivery chart should be displayed."
        )
        assert page_country_dashboard.driver.find_element(By.ID, "payments-by-sector").is_displayed(), (
            "Payments by Sector chart should be displayed."
        )
        assert page_country_dashboard.driver.find_element(By.ID, "payments-by-admin1").is_displayed(), (
            "Payments by Admin 1 chart should be displayed."
        )

        page_country_dashboard.switch_to_default_content()
