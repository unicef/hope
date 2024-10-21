import json
from typing import Any, Dict, List

from django.core.cache import cache
from django.utils import timezone

from hct_mis_api.apps.dashboard.serializers import DashboardHouseholdSerializer
from hct_mis_api.apps.household.models import Household

CACHE_TIMEOUT = 60 * 60 * 6  # 6 hours


class DashboardDataCache:
    """
    Utility class to manage dashboard data caching using Redis.
    """

    @staticmethod
    def get_cache_key(business_area_slug: str) -> str:
        return f"dashboard_data_{business_area_slug}"

    @classmethod
    def get_data(cls, business_area_slug: str):
        """
        Retrieve cached dashboard data for a given business area.
        """
        cache_key = cls.get_cache_key(business_area_slug)
        data = cache.get(cache_key)
        if data:
            return json.loads(data)
        return None

    @classmethod
    def store_data(cls, business_area_slug: str, data: dict):
        """
        Store data in Redis cache for a given business area.
        """
        cache_key = cls.get_cache_key(business_area_slug)
        cache.set(cache_key, json.dumps(data), CACHE_TIMEOUT)

    @classmethod
    def refresh_data(cls, business_area_slug: str):
        """
        Generate and store updated data for a given business area.
        """
        households = Household.objects.using("read_only").filter(business_area__slug=business_area_slug)
        serialized_data = DashboardHouseholdSerializer(households, many=True).data

        cls.store_data(business_area_slug, serialized_data)
        return serialized_data
