import calendar
import json
from decimal import Decimal
from typing import Any, Callable, Dict, Optional

from django.core.cache import cache
from django.utils import timezone

import pytest

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory, UserFactory
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.dashboard.serializers import DashboardBaseSerializer
from hct_mis_api.apps.dashboard.services import (
    DashboardCacheBase,
    DashboardDataCache,
    DashboardGlobalDataCache,
    get_pwd_count_expression,
)
from hct_mis_api.apps.household.fixtures import HouseholdFactory
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.payment.fixtures import (
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    PaymentFactory,
    PaymentPlanFactory,
    create_payment_verification_plan_with_status,
)
from hct_mis_api.apps.payment.models import Payment
from hct_mis_api.apps.program.fixtures import ProgramFactory

CACHE_CONFIG = [
    ("DashboardDataCache", DashboardDataCache, "test-area"),
    ("DashboardGlobalDataCache", DashboardGlobalDataCache, "global"),
]
CURRENT_YEAR = timezone.now().year
TEST_COUNTRY_SLUG = "afghanistan"
TEST_DATE = timezone.datetime(CURRENT_YEAR, 7, 15, tzinfo=timezone.utc)


@pytest.mark.parametrize("cache_name, cache_class, slug", CACHE_CONFIG)
def test_get_cache_key(cache_name: str, cache_class: Any, slug: str) -> None:
    """Test that get_cache_key returns the expected key."""
    expected_key: str = f"dashboard_data_{slug}"
    assert cache_class.get_cache_key(slug) == expected_key


@pytest.mark.parametrize("cache_name, cache_class, slug", CACHE_CONFIG)
@pytest.mark.django_db(databases=["default", "read_only"])
def test_get_data_cache_hit(cache_name: str, cache_class: Any, slug: str) -> None:
    """Test get_data when data is found in the cache."""
    cache.set(
        f"dashboard_data_{slug}",
        json.dumps({"test": f"{cache_name}_data"}),
        60 * 60 * 24,
    )
    data: Optional[Dict[str, Any]] = cache_class.get_data(slug)
    assert data == {"test": f"{cache_name}_data"}


@pytest.mark.parametrize("cache_name, cache_class, slug", CACHE_CONFIG)
@pytest.mark.django_db(databases=["default", "read_only"])
def test_get_data_cache_miss(cache_name: str, cache_class: Any, slug: str) -> None:
    """Test get_data when data is not found in the cache."""
    cache.delete(f"dashboard_data_{slug}")
    data: Optional[Dict[str, Any]] = cache_class.get_data(slug)
    assert data is None


@pytest.mark.parametrize("cache_name, cache_class, slug", CACHE_CONFIG)
@pytest.mark.django_db(databases=["default", "read_only"])
def test_store_data(cache_name: str, cache_class: Any, slug: str) -> None:
    """Test that store_data correctly stores data in the cache."""
    data: Dict[str, Any] = {"test": f"{cache_name}_data"}
    cache_class.store_data(slug, data)
    cached_data = cache.get(f"dashboard_data_{slug}")
    assert cached_data is not None
    assert json.loads(cached_data) == data


@pytest.mark.parametrize(
    "cache_name, cache_class, slug, expected_optional_fields",
    [
        (
            "DashboardDataCache",
            DashboardDataCache,
            "afghanistan",
            {"month", "admin1", "currency", "total_delivered_quantity"},
        ),
        (
            "DashboardGlobalDataCache",
            DashboardGlobalDataCache,
            "global",
            {"country"},
        ),
    ],
)
@pytest.mark.django_db(transaction=True, databases=["default", "read_only"])
def test_refresh_data(
    cache_name: str,
    cache_class: Any,
    slug: str,
    expected_optional_fields: set,
    afghanistan: BusinessAreaFactory,
    populate_dashboard_cache: Callable,
) -> None:
    """Test refresh_data for specific and global dashboards."""
    cache_key = cache_class.get_cache_key(slug)
    cache.delete(cache_key)

    populate_dashboard_cache(afghanistan)

    refreshed_data = cache_class.refresh_data() if slug == "global" else cache_class.refresh_data(afghanistan.slug)
    assert refreshed_data is not None, "Refresh data returned None"
    assert len(refreshed_data) > 0, "No data returned by refresh"
    assert sum(item["payments"] for item in refreshed_data) > 0, "Payments data mismatch"
    serializer_fields = DashboardBaseSerializer().get_fields()
    required_fields = {key for key, field in serializer_fields.items() if field.required}

    for item in refreshed_data:
        assert item.keys() >= required_fields, f"Missing required fields in {cache_name}: {item.keys()}"
        assert (
            item.keys() & expected_optional_fields == expected_optional_fields
        ), f"Expected optional fields {expected_optional_fields} are missing in {cache_name}: {item.keys()}"
    cached_data = cache.get(cache_key)
    assert cached_data is not None, "Data not cached"


TEST_CASES = [
    (
        "delivered_quantity_usd prioritized",
        {"delivered_quantity_usd": Decimal("100.0"), "entitlement_quantity_usd": Decimal("50.0")},
        Decimal("500.0"),
        DashboardDataCache,
    ),
    (
        "entitlement_quantity_usd used when delivered_quantity_usd is null",
        {"delivered_quantity_usd": None, "entitlement_quantity_usd": Decimal("50.0")},
        Decimal("250.0"),
        DashboardDataCache,
    ),
    (
        "both fields null",
        {"delivered_quantity_usd": None, "entitlement_quantity_usd": None},
        Decimal("0.0"),
        DashboardDataCache,
    ),
    (
        "Pending status with null delivered_quantity_usd",
        {"status": "Pending", "delivered_quantity_usd": None, "entitlement_quantity_usd": Decimal("50.0")},
        Decimal("250.0"),
        DashboardDataCache,
    ),
    (
        "global cache prioritizes delivered_quantity_usd",
        {"delivered_quantity_usd": Decimal("100.0"), "entitlement_quantity_usd": Decimal("50.0")},
        Decimal("500.0"),
        DashboardGlobalDataCache,
    ),
]


@pytest.mark.parametrize(
    "test_name, payment_updates, expected_total, cache_service",
    TEST_CASES,
    ids=[case[0] for case in TEST_CASES],
)
@pytest.mark.django_db(transaction=True, databases=["default", "read_only"])
def test_dashboard_data_cache(
    test_name: str,
    payment_updates: Dict[str, Any],
    expected_total: Decimal,
    cache_service: Any,
    populate_dashboard_cache: Callable,
) -> None:
    """Test DashboardDataCache and DashboardGlobalDataCache behavior."""
    business_area = BusinessAreaFactory(slug="test-area")
    household = populate_dashboard_cache(business_area)

    Payment.objects.filter(household=household).update(**payment_updates)
    if cache_service == DashboardDataCache:
        result = cache_service.refresh_data(business_area.slug)
    else:
        result = cache_service.refresh_data()

    total_usd = sum(Decimal(item["total_delivered_quantity_usd"]) for item in result)
    assert len(result) > 0
    assert total_usd == expected_total


@pytest.mark.django_db(transaction=True, databases=["default", "read_only"])
def test_country_dashboard_unique_household_metrics(
    populate_dashboard_cache: Callable, afghanistan: BusinessAreaFactory
) -> None:
    """
    Verify country dashboard counts household metrics once for multiple payments
    within the same aggregation group.
    """
    cache.delete(f"dashboard_data_{afghanistan.slug}")
    household = populate_dashboard_cache(afghanistan)
    expected_household_count = 1
    expected_individuals = 5
    expected_children = 2
    expected_pwd = 3
    expected_payment_count = 5

    common_fsp = FinancialServiceProviderFactory()
    common_delivery_type = DeliveryMechanismFactory()
    common_status = "Transaction Successful"
    common_currency = "USD"

    Payment.objects.filter(household=household).update(
        delivery_date=TEST_DATE,
        financial_service_provider=common_fsp,
        delivery_type=common_delivery_type,
        status=common_status,
        currency=common_currency,
        program=household.program,
    )
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
    assert agg_data["program"] == household.program.name
    assert agg_data["sector"] == household.program.sector
    assert agg_data["fsp"] == common_fsp.name
    assert agg_data["delivery_types"] == common_delivery_type.name
    assert agg_data["status"] == common_status
    assert agg_data["currency"] == common_currency


@pytest.mark.django_db(transaction=True, databases=["default", "read_only"])
def test_global_dashboard_unique_household_metrics(
    populate_dashboard_cache: Callable, afghanistan: BusinessAreaFactory
) -> None:
    """
    Verify global dashboard counts household metrics once for multiple payments.
    """
    cache.delete(f"dashboard_data_{afghanistan.slug}")

    household = populate_dashboard_cache(afghanistan)
    expected_household_count = 1
    expected_individuals = 5
    expected_children = 2
    expected_pwd = 3
    expected_payment_count = 5
    common_delivery_type = DeliveryMechanismFactory()
    common_status = "Transaction Successful"
    Payment.objects.filter(household=household).update(
        delivery_date=TEST_DATE,
        delivery_type=common_delivery_type,
        status=common_status,
        program=household.program,
    )
    result = DashboardGlobalDataCache.refresh_data()
    assert result is not None, "Result should not be None"
    target_group_data = None
    for item in result:
        if (
            item["year"] == CURRENT_YEAR
            and item["country"] == afghanistan.name
            and item["sector"] == household.program.sector
            and item["delivery_types"] == common_delivery_type.name
            and item["status"] == common_status
        ):
            target_group_data = item
            break

    assert target_group_data is not None, f"Expected aggregation group not found in global result: {result}"
    assert target_group_data["households"] == expected_household_count, "Household count mismatch"
    assert target_group_data["individuals"] == expected_individuals, "Individuals count mismatch"
    assert target_group_data["children_counts"] == expected_children, "Children count mismatch"
    assert target_group_data["pwd_counts"] == expected_pwd, "PWD count mismatch"
    assert target_group_data["payments"] == expected_payment_count, "Payment count mismatch"


@pytest.mark.django_db(transaction=True, databases=["default", "read_only"])
def test_dashboard_reconciliation_verification_consistency(
    populate_dashboard_cache: Callable, afghanistan: BusinessAreaFactory
) -> None:
    country_slug = afghanistan.slug
    country_name = afghanistan.name

    cache.delete(DashboardDataCache.get_cache_key(country_slug))
    cache.delete(DashboardGlobalDataCache.get_cache_key("global"))

    household = populate_dashboard_cache(afghanistan)
    Payment.objects.filter(household=household).update(delivery_date=TEST_DATE)

    country_data = DashboardDataCache.refresh_data(country_slug)
    assert country_data, "Country dashboard data should not be empty"

    global_data_all = DashboardGlobalDataCache.refresh_data()
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


@pytest.mark.django_db(databases=["default", "read_only"])
def test_dashboard_data_cache_refresh_data_non_existent_business_area() -> None:
    """Test refresh_data for DashboardDataCache with a non-existent business area slug."""
    slug = "non-existent-slug"
    cache_key = DashboardDataCache.get_cache_key(slug)
    cache.delete(cache_key)

    BusinessArea.objects.filter(slug=slug).delete()

    result = DashboardDataCache.refresh_data(slug)
    assert result == []
    cached_data = cache.get(cache_key)
    assert cached_data is not None
    assert json.loads(cached_data) == []


@pytest.mark.django_db(databases=["default", "read_only"])
def test_get_pwd_count_expression_logic() -> None:
    """Test the get_pwd_count_expression for various PWD count scenarios."""
    ba = BusinessAreaFactory()
    hh1 = HouseholdFactory(
        business_area=ba,
        female_age_group_0_5_disabled_count=0,
        female_age_group_6_11_disabled_count=0,
        female_age_group_12_17_disabled_count=0,
        female_age_group_18_59_disabled_count=0,
        female_age_group_60_disabled_count=0,
        male_age_group_0_5_disabled_count=0,
        male_age_group_6_11_disabled_count=0,
        male_age_group_12_17_disabled_count=0,
        male_age_group_18_59_disabled_count=0,
        male_age_group_60_disabled_count=0,
    )

    hh2 = HouseholdFactory(
        business_area=ba,
        female_age_group_0_5_disabled_count=1,
        female_age_group_6_11_disabled_count=None,
        female_age_group_12_17_disabled_count=2,
        male_age_group_18_59_disabled_count=3,
        male_age_group_60_disabled_count=None,
    )

    hh3 = HouseholdFactory(
        business_area=ba,
        female_age_group_0_5_disabled_count=None,
        female_age_group_6_11_disabled_count=None,
        female_age_group_12_17_disabled_count=None,
        female_age_group_18_59_disabled_count=None,
        female_age_group_60_disabled_count=None,
        male_age_group_0_5_disabled_count=None,
        male_age_group_6_11_disabled_count=None,
        male_age_group_12_17_disabled_count=None,
        male_age_group_18_59_disabled_count=None,
        male_age_group_60_disabled_count=None,
    )

    households_with_pwd_counts = Household.objects.filter(id__in=[hh1.id, hh2.id, hh3.id]).annotate(
        calculated_pwd_count=get_pwd_count_expression()
    )

    for hh_annotated in households_with_pwd_counts:
        if hh_annotated.id == hh1.id:
            assert hh_annotated.calculated_pwd_count == 0, "PWD count mismatch for hh1 (zero PWDs)"
        elif hh_annotated.id == hh2.id:
            assert hh_annotated.calculated_pwd_count == 1 + 2 + 3, "PWD count mismatch for hh2 (some PWDs)"
        elif hh_annotated.id == hh3.id:
            assert hh_annotated.calculated_pwd_count == 0, "PWD count mismatch for hh3 (all PWD fields None)"


@pytest.mark.django_db(transaction=True, databases=["default", "read_only"])
def test_get_payment_plan_counts_logic() -> None:
    """Test _get_payment_plan_counts with different grouping criteria."""
    ba = BusinessAreaFactory()
    prog_a_sector_x = ProgramFactory(business_area=ba, sector="SectorX", name="ProgramA")
    prog_b_sector_y = ProgramFactory(business_area=ba, sector="SectorY", name="ProgramB")

    pp1 = PaymentPlanFactory(program_cycle__program=prog_a_sector_x)
    pp2 = PaymentPlanFactory(program_cycle__program=prog_a_sector_x)
    pp3 = PaymentPlanFactory(program_cycle__program=prog_b_sector_y)
    pp4 = PaymentPlanFactory(program_cycle__program=prog_a_sector_x)
    pp5 = PaymentPlanFactory(program_cycle__program=prog_a_sector_x)

    user = UserFactory()

    create_payment_verification_plan_with_status(
        payment_plan=pp2, user=user, business_area=ba, program=prog_a_sector_x, status="FINISHED"
    )
    create_payment_verification_plan_with_status(
        payment_plan=pp4, user=user, business_area=ba, program=prog_a_sector_x, status="FINISHED"
    )

    PaymentFactory(
        parent=pp1, program=prog_a_sector_x, delivery_date=timezone.datetime(2023, 1, 10, tzinfo=timezone.utc)
    )
    PaymentFactory(
        parent=pp3, program=prog_b_sector_y, delivery_date=timezone.datetime(2023, 3, 10, tzinfo=timezone.utc)
    )
    PaymentFactory(
        parent=pp5, program=prog_a_sector_x, delivery_date=timezone.datetime(2023, 1, 15, tzinfo=timezone.utc)
    )
    Payment.objects.filter(parent=pp1, business_area=ba).update(
        delivery_date=timezone.datetime(2023, 1, 10, tzinfo=timezone.utc)
    )
    Payment.objects.filter(parent=pp2, business_area=ba).update(
        delivery_date=timezone.datetime(2023, 6, 1, tzinfo=timezone.utc)
    )  # pp2 is FINISHED, expected in 2023
    Payment.objects.filter(parent=pp3, business_area=ba).update(
        delivery_date=timezone.datetime(2023, 3, 10, tzinfo=timezone.utc)
    )
    Payment.objects.filter(parent=pp4, business_area=ba).update(
        delivery_date=timezone.datetime(2024, 6, 1, tzinfo=timezone.utc)
    )  # pp4 is FINISHED, expected in 2024
    Payment.objects.filter(parent=pp5, business_area=ba).update(
        delivery_date=timezone.datetime(2023, 1, 15, tzinfo=timezone.utc)
    )

    base_payments_qs = Payment.objects.filter(business_area=ba)
    group_by_fields = ["year", "sector_name"]

    result = DashboardCacheBase._get_payment_plan_counts(base_payments_qs, group_by_fields)

    expected_total_counts = {
        (2023, "SectorX"): 3,
        (2023, "SectorY"): 1,
        (2024, "SectorX"): 1,
    }
    expected_finished_counts = {
        (2023, "SectorX"): 1,
        (2024, "SectorX"): 1,
    }

    assert result["total"] == expected_total_counts, "Total payment plan counts mismatch"
    assert result["finished"] == expected_finished_counts, "Finished payment plan counts mismatch"

    group_by_fields_program = ["year", "program_name"]
    result_program_grouping = DashboardCacheBase._get_payment_plan_counts(base_payments_qs, group_by_fields_program)

    expected_total_program = {
        (2023, "ProgramA"): 3,
        (2023, "ProgramB"): 1,
        (2024, "ProgramA"): 1,
    }
    expected_finished_program = {
        (2023, "ProgramA"): 1,
        (2024, "ProgramA"): 1,
    }
    assert result_program_grouping["total"] == expected_total_program, "Total plan counts mismatch (program grouping)"
    assert result_program_grouping["finished"] == expected_finished_program, "Finished plan counts (program grouping)"

    empty_plan_qs = Payment.objects.filter(pk__in=[])
    result_empty = DashboardCacheBase._get_payment_plan_counts(empty_plan_qs, group_by_fields)
    assert result_empty["total"] == {}, "Expected empty total counts for no plans"
    assert result_empty["finished"] == {}, "Expected empty finished counts for no plans"


@pytest.mark.django_db(databases=["default", "read_only"])
def test_dashboard_data_cache_refresh_data_no_payments(afghanistan: BusinessArea) -> None:
    """Test refresh_data for DashboardDataCache when a business area has no payments."""
    Payment.objects.filter(
        program__business_area=afghanistan,
        parent__status__in=["ACCEPTED", "FINISHED"],
        program__is_visible=True,
        parent__is_removed=False,
        is_removed=False,
        conflicted=False,
        excluded=False,
    ).exclude(status__in=["Transaction Erroneous", "Not Distributed", "Force failed", "Manually Cancelled"]).delete()

    cache_key = DashboardDataCache.get_cache_key(afghanistan.slug)
    cache.delete(cache_key)

    result = DashboardDataCache.refresh_data(afghanistan.slug)
    assert result == []
    cached_data = cache.get(cache_key)
    assert cached_data is not None
    assert json.loads(cached_data) == []


@pytest.mark.django_db(databases=["default", "read_only"])
def test_dashboard_global_data_cache_refresh_data_no_payments() -> None:
    """Test refresh_data for DashboardGlobalDataCache when there are no payments globally."""
    Payment.objects.filter(
        parent__status__in=["ACCEPTED", "FINISHED"],
        program__is_visible=True,
        parent__is_removed=False,
        is_removed=False,
        conflicted=False,
        excluded=False,
    ).exclude(status__in=["Transaction Erroneous", "Not Distributed", "Force failed", "Manually Cancelled"]).delete()

    cache_key = DashboardGlobalDataCache.get_cache_key("global")
    cache.delete(cache_key)

    result = DashboardGlobalDataCache.refresh_data()
    assert result == []
    cached_data = cache.get(cache_key)
    assert cached_data is not None
    assert json.loads(cached_data) == []
