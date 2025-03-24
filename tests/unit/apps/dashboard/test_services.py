import json
from decimal import Decimal
from typing import Any, Callable, Dict, Optional

from django.core.cache import cache

import pytest

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory
from hct_mis_api.apps.dashboard.serializers import DashboardBaseSerializer
from hct_mis_api.apps.dashboard.services import (
    DashboardDataCache,
    DashboardGlobalDataCache,
)
from hct_mis_api.apps.payment.models import Payment


CACHE_CONFIG = [
    ("DashboardDataCache", DashboardDataCache, "test-area"),
    ("DashboardGlobalDataCache", DashboardGlobalDataCache, "global"),
]


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
            {"country", "currency"},
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

    household = populate_dashboard_cache(afghanistan)

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
