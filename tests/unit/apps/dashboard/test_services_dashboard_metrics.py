import calendar
from datetime import timezone as dt_timezone
from decimal import Decimal
from typing import Any, Dict
from unittest.mock import patch

from django.core.cache import cache
from django.utils import timezone
import pytest

from extras.test_utils.factories import (
    AreaFactory,
    AreaTypeFactory,
    BusinessAreaFactory,
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    HouseholdFactory,
    PaymentFactory,
    ProgramFactory,
)
from hope.apps.dashboard.services import (
    GLOBAL_SLUG,
    DashboardDataCache,
    DashboardGlobalDataCache,
)
from hope.models import Payment, PaymentPlan


@pytest.fixture
def use_default_db_for_dashboard():
    with (
        patch("hope.apps.dashboard.services.settings.DASHBOARD_DB", "default"),
        patch("hope.apps.dashboard.celery_tasks.settings.DASHBOARD_DB", "default"),
    ):
        yield


pytestmark = pytest.mark.usefixtures("use_default_db_for_dashboard")

CURRENT_YEAR = timezone.now().year
TEST_COUNTRY_SLUG = "afghanistan"
TEST_DATE = timezone.datetime(CURRENT_YEAR, 7, 15, tzinfo=dt_timezone.utc)


# ============================================================================
# Local Fixtures
# ============================================================================


@pytest.fixture
def afghanistan(db):
    return BusinessAreaFactory(
        code="0060",
        name="Afghanistan",
        long_name="THE ISLAMIC REPUBLIC OF AFGHANISTAN",
        region_code="64",
        region_name="SAR",
        slug="afghanistan",
        has_data_sharing_agreement=True,
        kobo_token="XXX",
        active=True,
    )


@pytest.fixture
def area_kabul(db):
    area_type = AreaTypeFactory(name="Province", area_level=1)
    return AreaFactory(name="Kabul", area_type=area_type)


@pytest.fixture
def populate_dashboard_cache(area_kabul):
    def _populate(ba, household_extra_args=None):
        program = ProgramFactory(business_area=ba)
        household = HouseholdFactory(
            business_area=ba,
            program=program,
            size=5,
            children_count=2,
            female_age_group_0_5_disabled_count=1,
            female_age_group_6_11_disabled_count=1,
            male_age_group_60_disabled_count=1,
            admin1=area_kabul,
            **(household_extra_args or {}),
        )
        payment_statuses = [
            Payment.STATUS_SUCCESS,
            Payment.STATUS_DISTRIBUTION_SUCCESS,
            Payment.STATUS_DISTRIBUTION_PARTIAL,
            Payment.STATUS_PENDING,
            Payment.STATUS_SUCCESS,
        ]
        for status in payment_statuses:
            PaymentFactory(
                household=household,
                program=program,
                business_area=ba,
                parent__status=PaymentPlan.Status.ACCEPTED,
                status=status,
            )
        return household

    return _populate


@pytest.fixture
def business_area_test(db):
    return BusinessAreaFactory(slug="test-area")


@pytest.fixture
def fsp_common(db):
    return FinancialServiceProviderFactory()


@pytest.fixture
def delivery_mechanism_common(db):
    return DeliveryMechanismFactory()


# ============================================================================
# Dashboard Data Cache Tests
# ============================================================================


@pytest.fixture
def dashboard_cache_test_data(populate_dashboard_cache, business_area_test):
    def _create(payment_updates):
        household = populate_dashboard_cache(business_area_test)
        Payment.objects.filter(household=household).update(**payment_updates)
        return business_area_test, household

    return _create


@pytest.mark.parametrize(
    ("test_name", "payment_updates", "expected_total"),
    [
        (
            "delivered_quantity_usd prioritized",
            {
                "delivered_quantity_usd": Decimal("100.0"),
                "entitlement_quantity_usd": Decimal("50.0"),
            },
            Decimal("500.0"),
        ),
        (
            "entitlement_quantity_usd used when delivered_quantity_usd is null",
            {"delivered_quantity_usd": None, "entitlement_quantity_usd": Decimal("50.0")},
            Decimal("250.0"),
        ),
        (
            "both fields null",
            {"delivered_quantity_usd": None, "entitlement_quantity_usd": None},
            Decimal("0.0"),
        ),
        (
            "Pending status with null delivered_quantity_usd",
            {
                "status": "Pending",
                "delivered_quantity_usd": None,
                "entitlement_quantity_usd": Decimal("50.0"),
            },
            Decimal("250.0"),
        ),
    ],
    ids=[
        "delivered_quantity_usd prioritized",
        "entitlement_quantity_usd used when delivered_quantity_usd is null",
        "both fields null",
        "Pending status with null delivered_quantity_usd",
    ],
)
@pytest.mark.django_db
def test_dashboard_data_cache_ba(
    test_name: str,
    payment_updates: Dict[str, Any],
    expected_total: Decimal,
    dashboard_cache_test_data,
) -> None:
    business_area, _ = dashboard_cache_test_data(payment_updates)

    result = DashboardDataCache.refresh_data(business_area.slug)

    total_usd = sum(Decimal(item["total_delivered_quantity_usd"]) for item in result)
    assert len(result) > 0
    assert total_usd == expected_total


@pytest.mark.django_db
def test_dashboard_global_data_cache_prioritizes_delivered_quantity_usd(
    dashboard_cache_test_data,
) -> None:
    payment_updates = {
        "delivered_quantity_usd": Decimal("100.0"),
        "entitlement_quantity_usd": Decimal("50.0"),
    }
    expected_total = Decimal("500.0")

    dashboard_cache_test_data(payment_updates)

    result = DashboardGlobalDataCache.refresh_data(identifier=GLOBAL_SLUG)

    total_usd = sum(Decimal(item["total_delivered_quantity_usd"]) for item in result)
    assert len(result) > 0
    assert total_usd == expected_total


# ============================================================================
# Unique Household Metrics Tests
# ============================================================================


@pytest.fixture
def country_dashboard_metrics_data(afghanistan, populate_dashboard_cache, fsp_common, delivery_mechanism_common):
    cache.delete(f"dashboard_data_{afghanistan.slug}")
    household = populate_dashboard_cache(afghanistan)
    common_status = "Transaction Successful"
    common_currency = "USD"

    Payment.objects.filter(household=household).update(
        delivery_date=TEST_DATE,
        financial_service_provider=fsp_common,
        delivery_type=delivery_mechanism_common,
        status=common_status,
        currency=common_currency,
        program=household.program,
    )
    return {
        "household": household,
        "afghanistan": afghanistan,
        "fsp": fsp_common,
        "delivery_type": delivery_mechanism_common,
        "status": common_status,
        "currency": common_currency,
    }


@pytest.mark.django_db
def test_country_dashboard_unique_household_metrics(country_dashboard_metrics_data) -> None:
    data = country_dashboard_metrics_data
    expected_household_count = 1
    expected_individuals = 5
    expected_children = 2
    expected_pwd = 3
    expected_payment_count = 5

    result = DashboardDataCache.refresh_data(TEST_COUNTRY_SLUG)
    assert result is not None, "Result should not be None"
    assert len(result) == 1, f"Expected 1 aggregation group, got {len(result)}"

    agg_data = result[0]

    assert agg_data["households"] == expected_household_count, "Household count mismatch"
    assert agg_data["individuals"] == expected_individuals, "Individuals count mismatch"
    assert agg_data["children_counts"] == expected_children, "Children count mismatch"
    assert agg_data["pwd_counts"] == expected_pwd, "PWD count mismatch"
    assert agg_data["payments"] == expected_payment_count, "Payment count mismatch"
    assert agg_data["year"] == CURRENT_YEAR
    assert agg_data["month"] == calendar.month_name[TEST_DATE.month]
    assert agg_data["admin1"] == "Kabul"
    assert agg_data["program"] == data["household"].program.name
    assert agg_data["sector"] == data["household"].program.sector
    assert agg_data["fsp"] == data["fsp"].name
    assert agg_data["delivery_types"] == data["delivery_type"].name
    assert agg_data["status"] == data["status"]
    assert agg_data["currency"] == data["currency"]


@pytest.fixture
def global_dashboard_metrics_data(afghanistan, populate_dashboard_cache, delivery_mechanism_common):
    cache.delete(f"dashboard_data_{afghanistan.slug}")
    household = populate_dashboard_cache(afghanistan)
    common_status = "Transaction Successful"

    Payment.objects.filter(household=household).update(
        delivery_date=TEST_DATE,
        delivery_type=delivery_mechanism_common,
        status=common_status,
        program=household.program,
    )
    return {
        "household": household,
        "afghanistan": afghanistan,
        "delivery_type": delivery_mechanism_common,
        "status": common_status,
    }


@pytest.mark.django_db
def test_global_dashboard_unique_household_metrics(global_dashboard_metrics_data) -> None:
    data = global_dashboard_metrics_data
    expected_household_count = 1
    expected_individuals = 5
    expected_children = 2
    expected_pwd = 3
    expected_payment_count = 5

    result = DashboardGlobalDataCache.refresh_data(identifier=GLOBAL_SLUG)
    assert result is not None, "Result should not be None"

    target_group_data = next(
        (
            item
            for item in result
            if (
                item["year"] == CURRENT_YEAR
                and item["country"] == data["afghanistan"].name
                and item["sector"] == data["household"].program.sector
                and item["delivery_types"] == data["delivery_type"].name
                and item["status"] == data["status"]
            )
        ),
        None,
    )

    assert target_group_data is not None, f"Expected aggregation group not found in global result: {result}"
    assert target_group_data["households"] == expected_household_count, "Household count mismatch"
    assert target_group_data["individuals"] == expected_individuals, "Individuals count mismatch"
    assert target_group_data["children_counts"] == expected_children, "Children count mismatch"
    assert target_group_data["pwd_counts"] == expected_pwd, "PWD count mismatch"
    assert target_group_data["payments"] == expected_payment_count, "Payment count mismatch"


@pytest.mark.django_db
def test_dashboard_households_counted_once_per_year(afghanistan, populate_dashboard_cache):
    """
    Ensure that a household is only counted once in the 'households' metric for a given year,
    even if it has payments in different months or programs.
    """
    cache.delete(f"dashboard_data_{afghanistan.slug}")
    household = populate_dashboard_cache(afghanistan)
    Payment.objects.filter(household=household).update(
        delivery_date=timezone.datetime(CURRENT_YEAR, 1, 1, tzinfo=dt_timezone.utc)
    )
    payment = Payment.objects.filter(household=household).first()
    payment.delivery_date = timezone.datetime(CURRENT_YEAR, 2, 1, tzinfo=dt_timezone.utc)
    payment.save()
    result = DashboardDataCache.refresh_data(afghanistan.slug)
    total_households_count = sum(item["households"] for item in result if item["year"] == CURRENT_YEAR)
    total_individuals_count = sum(item["individuals"] for item in result if item["year"] == CURRENT_YEAR)

    assert total_households_count == 1, "Household was double counted across months"
    assert total_individuals_count == household.size, "Individuals were double counted across months"


# ============================================================================
# Reconciliation Tests
# ============================================================================


@pytest.fixture
def reconciliation_test_data(afghanistan, populate_dashboard_cache):
    country_slug = afghanistan.slug
    country_name = afghanistan.name

    cache.delete(DashboardDataCache.get_cache_key(country_slug))
    cache.delete(DashboardGlobalDataCache.get_cache_key("global"))

    household = populate_dashboard_cache(afghanistan)
    Payment.objects.filter(household=household).update(delivery_date=TEST_DATE)

    return {
        "afghanistan": afghanistan,
        "country_slug": country_slug,
        "country_name": country_name,
    }


@pytest.mark.django_db
def test_dashboard_reconciliation_verification_consistency(reconciliation_test_data) -> None:
    data = reconciliation_test_data
    country_slug = data["country_slug"]
    country_name = data["country_name"]

    country_data = DashboardDataCache.refresh_data(country_slug)
    assert country_data, "Country dashboard data should not be empty"

    global_data_all = DashboardGlobalDataCache.refresh_data(identifier=GLOBAL_SLUG)
    assert global_data_all, "Global dashboard data should not be empty"

    global_data_filtered_for_country = [
        item for item in global_data_all if item.get("country") == country_name and item.get("year") == CURRENT_YEAR
    ]
    assert global_data_filtered_for_country, f"No global data found for {country_name} in {CURRENT_YEAR}"

    sum_reconciled_country = sum(item.get("reconciled", 0) for item in country_data if item.get("year") == CURRENT_YEAR)
    sum_reconciled_global = sum(item.get("reconciled", 0) for item in global_data_filtered_for_country)

    assert sum_reconciled_country == sum_reconciled_global, (
        "Sum of 'reconciled' counts should be consistent between country and filtered global dashboards "
        f"(Country: {sum_reconciled_country}, Global: {sum_reconciled_global})"
    )

    country_data_current_year = [item for item in country_data if item.get("year") == CURRENT_YEAR]
    assert country_data_current_year, f"No country-specific dashboard data found for {country_name} in {CURRENT_YEAR}"

    sum_finished_plans_country = sum(item.get("finished_payment_plans", 0) for item in country_data_current_year)
    sum_total_plans_country = sum(item.get("total_payment_plans", 0) for item in country_data_current_year)
    sum_finished_plans_global = sum(item.get("finished_payment_plans", 0) for item in global_data_filtered_for_country)
    sum_total_plans_global = sum(item.get("total_payment_plans", 0) for item in global_data_filtered_for_country)

    assert sum_finished_plans_country == sum_finished_plans_global, (
        "Sum of 'finished_payment_plans' should be consistent between country and filtered global dashboards "
        f"(Country: {sum_finished_plans_country}, Global: {sum_finished_plans_global})"
    )
    assert sum_total_plans_country == sum_total_plans_global, (
        "Sum of 'total_payment_plans' should be consistent between country and filtered global dashboards "
        f"(Country: {sum_total_plans_country}, Global: {sum_total_plans_global})"
    )
