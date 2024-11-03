import json
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, patch

import pytest

from hct_mis_api.apps.dashboard.services import DashboardDataCache
from hct_mis_api.apps.household.models import Household


@pytest.mark.django_db(databases=["default", "read_only"])
def test_get_cache_key() -> None:
    """Test that get_cache_key returns the expected key."""
    business_area_slug: str = "test-area"
    expected_key: str = "dashboard_data_test-area"
    assert DashboardDataCache.get_cache_key(business_area_slug) == expected_key


@pytest.mark.django_db(databases=["default", "read_only"])
@patch("hct_mis_api.apps.dashboard.services.cache")
def test_get_data_cache_hit(mock_cache: MagicMock) -> None:
    """Test get_data when data is found in the cache."""
    business_area_slug: str = "test-area"
    mock_cache.get.return_value = json.dumps({"test": "data"})
    data: Optional[Dict[str, Any]] = DashboardDataCache.get_data(business_area_slug)
    assert data == {"test": "data"}
    mock_cache.get.assert_called_once_with("dashboard_data_test-area")


@pytest.mark.django_db(databases=["default", "read_only"])
@patch("hct_mis_api.apps.dashboard.services.cache")
def test_get_data_cache_miss(mock_cache: MagicMock) -> None:
    """Test get_data when data is not found in the cache."""
    business_area_slug: str = "test-area"
    mock_cache.get.return_value = None
    data: Optional[Dict[str, Any]] = DashboardDataCache.get_data(business_area_slug)
    assert data is None
    mock_cache.get.assert_called_once_with("dashboard_data_test-area")


@pytest.mark.django_db(databases=["default", "read_only"])
@patch("hct_mis_api.apps.dashboard.services.cache")
def test_store_data(mock_cache: MagicMock) -> None:
    """Test that store_data correctly stores data in the cache."""
    business_area_slug: str = "test-area"
    data: Dict[str, Any] = {"test": "data"}
    DashboardDataCache.store_data(business_area_slug, data)
    mock_cache.set.assert_called_once_with("dashboard_data_test-area", json.dumps(data), 60 * 60 * 24)


@pytest.mark.django_db(databases=["default", "read_only"])
@patch("hct_mis_api.apps.dashboard.services.DashboardHouseholdSerializer")
@patch("hct_mis_api.apps.household.models.Household.objects")
def test_refresh_data(mock_household_objects: MagicMock, mock_serializer: MagicMock) -> None:
    """Test that refresh_data generates and stores updated data."""
    business_area_slug: str = "test-area"
    mock_households: List[Household] = [Household(id=1), Household(id=2)]
    mock_household_objects.using.return_value.filter.return_value = mock_households
    mock_serializer.return_value.data = {"id": 1, "name": "test"}

    with patch.object(DashboardDataCache, "store_data") as mock_store_data:
        data: Dict[str, Any] = DashboardDataCache.refresh_data(business_area_slug)

    assert data == {"id": 1, "name": "test"}
    mock_serializer.assert_called_once_with(mock_households, many=True)
    mock_store_data.assert_called_once_with(business_area_slug, {"id": 1, "name": "test"})
