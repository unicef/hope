import json
import re
from typing import Any, Callable, Dict, Optional

from django.core.cache import cache

import pytest
from rest_framework.utils.serializer_helpers import ReturnDict

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory
from hct_mis_api.apps.dashboard.serializers import DashboardHouseholdSerializer
from hct_mis_api.apps.dashboard.services import DashboardDataCache


def test_get_cache_key() -> None:
    """Test that get_cache_key returns the expected key."""
    business_area_slug: str = "test-area"
    expected_key: str = "dashboard_data_test-area"
    assert DashboardDataCache.get_cache_key(business_area_slug) == expected_key


@pytest.mark.django_db(databases=["default", "read_only"])
def test_get_data_cache_hit() -> None:
    """Test get_data when data is found in the cache."""
    business_area_slug: str = "test-area"
    cache.set("dashboard_data_test-area", json.dumps({"test": "data"}), 60 * 60 * 24)  # Set cache directly
    data: Optional[Dict[str, Any]] = DashboardDataCache.get_data(business_area_slug)
    assert data == {"test": "data"}


@pytest.mark.django_db(databases=["default", "read_only"])
def test_get_data_cache_miss() -> None:
    """Test get_data when data is not found in the cache."""
    business_area_slug: str = "test-area"
    cache.delete("dashboard_data_test-area")
    data: Optional[Dict[str, Any]] = DashboardDataCache.get_data(business_area_slug)
    assert data is None


@pytest.mark.django_db(databases=["default", "read_only"])
def test_store_data() -> None:
    """Test that store_data correctly stores data in the cache."""
    business_area_slug: str = "test-area"
    data: Dict[str, Any] = {"test": "data"}
    DashboardDataCache.store_data(business_area_slug, data)
    cached_data = cache.get("dashboard_data_test-area")
    assert cached_data is not None
    assert json.loads(cached_data) == data


@pytest.mark.django_db(transaction=True, databases=["default", "read_only"])
def test_refresh_data(afghanistan: BusinessAreaFactory, populate_dashboard_cache: Callable) -> None:
    cache_key = DashboardDataCache.get_cache_key(afghanistan.slug)
    cache.delete(cache_key)
    _ = populate_dashboard_cache(afghanistan)
    data: ReturnDict = DashboardDataCache.refresh_data(afghanistan.slug)
    assert len(data) > 0
    assert all(re.match(r"^[A-Z]{3}$", item["currency"]) for item in data)
    assert sum(item["payments"] for item in data) == 5
    all_fields = DashboardHouseholdSerializer().get_fields().keys()
    assert data[0].keys() >= all_fields
    cache_key = DashboardDataCache.get_cache_key(afghanistan.slug)
    cached_data = cache.get(cache_key)
    assert cached_data is not None
