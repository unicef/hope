from datetime import timedelta

from django.utils import timezone
import pytest

from extras.test_utils.factories import (
    AreaFactory,
    CurrencyFactory,
    HouseholdFactory,
    IndividualFactory,
    PaymentFactory,
    ProgramFactory,
)
from extras.test_utils.selenium import HopeTestBrowser
from hope.apps.dashboard.services import DashboardDataCache
from hope.apps.household.const import DISABLED
from hope.models import BeneficiaryGroup, BusinessArea, Household, Payment, PaymentPlan, Program

pytestmark = pytest.mark.django_db(databases=["default", "read_only"])

NAV_COUNTRY_DASHBOARD = 'a[data-cy="nav-Country Dashboard"]'
DASHBOARD_IFRAME = 'iframe[title="Dashboard"]'
TOTAL_AMOUNT_PAID = "#total-amount-paid"
TOTAL_DISBURSED_PAYMENTS = "#total-disbursed-payments"
NUMBER_OF_PAYMENTS = "#number-of-payments"
OUTSTANDING_PAYMENTS = "#outstanding-payments"
HOUSEHOLDS_REACHED = "#households-reached"
PWD_REACHED = "#pwd-reached"
CHILDREN_REACHED = "#children-reached"
INDIVIDUALS_REACHED = "#individuals-reached"
CHARTS = ["#payments-by-fsp", "#payments-by-delivery", "#payments-by-sector", "#payments-by-admin1"]


@pytest.fixture
def program(business_area: BusinessArea) -> Program:
    return ProgramFactory(
        business_area=business_area,
        status=Program.ACTIVE,
        beneficiary_group=BeneficiaryGroup.objects.filter(name="Main Menu").first(),
    )


@pytest.fixture
def household(business_area: BusinessArea, program: Program) -> Household:
    household = HouseholdFactory(
        business_area=business_area,
        program=program,
        size=5,
        children_count=2,
        admin1=AreaFactory(name="Kabul", area_type__name="Province", area_type__area_level=1),
    )
    IndividualFactory(
        business_area=business_area,
        program=program,
        household=household,
        registration_data_import=household.registration_data_import,
        disability=DISABLED,
    )
    return household


@pytest.fixture
def pending_payment(business_area: BusinessArea, program: Program) -> Payment:
    # A household of its own: the dashboard sums households per payment status.
    household = HouseholdFactory(business_area=business_area, program=program, size=3, children_count=1)
    return PaymentFactory(
        parent__business_area=business_area,
        parent__program_cycle__program=program,
        parent__status=PaymentPlan.Status.ACCEPTED,
        business_area=business_area,
        program=program,
        household=household,
        status=Payment.STATUS_PENDING,
        currency=CurrencyFactory(code="PLN"),
        entitlement_quantity=140,
        entitlement_quantity_usd=70,
        entitlement_date=timezone.now() - timedelta(days=30),
    )


@pytest.fixture
def payments(
    business_area: BusinessArea, program: Program, household: Household, pending_payment: Payment
) -> list[Payment]:
    payments = PaymentFactory.create_batch(
        2,
        parent__business_area=business_area,
        parent__program_cycle__program=program,
        parent__status=PaymentPlan.Status.ACCEPTED,
        business_area=business_area,
        program=program,
        household=household,
        status=Payment.STATUS_SUCCESS,
        currency__code="PLN",
        delivered_quantity=230,
        delivered_quantity_usd=100,
        delivery_date=timezone.now() - timedelta(days=30),
    )
    DashboardDataCache.refresh_data(business_area.slug)
    return payments


def test_country_dashboard_shows_metrics_from_payments(payments: list[Payment], login: HopeTestBrowser) -> None:
    login.wait_for_element_clickable(NAV_COUNTRY_DASHBOARD).click()
    login.switch_to_frame(DASHBOARD_IFRAME)

    login.assert_exact_text("200.00 USD", TOTAL_AMOUNT_PAID)
    login.assert_exact_text("600.00 PLN", TOTAL_DISBURSED_PAYMENTS)
    login.assert_exact_text("3", NUMBER_OF_PAYMENTS)
    login.assert_exact_text("70.00 USD", OUTSTANDING_PAYMENTS)
    login.assert_exact_text("2", HOUSEHOLDS_REACHED)
    login.assert_exact_text("1", PWD_REACHED)
    login.assert_exact_text("3", CHILDREN_REACHED)
    login.assert_exact_text("8", INDIVIDUALS_REACHED)
    login.assert_elements_visible(*CHARTS)
