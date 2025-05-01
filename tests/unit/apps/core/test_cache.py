from django.core.cache import cache

from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.utils import save_data_in_cache


class TestCache(APITestCase):
    def test_simple_cache(self) -> None:
        cache.clear()
        assert cache.get("FOO", "NOTHING") == "NOTHING"
        result_from_function = save_data_in_cache("FOO", lambda: "BAR")
        assert result_from_function == "BAR"
        assert cache.get("FOO", "NOTHING") == "BAR"

    def test_conditional_false_cache(self) -> None:
        cache.clear()
        assert cache.get("FOO", "NOTHING") == "NOTHING"
        result_from_function = save_data_in_cache("FOO", lambda: "BAR", cache_condition=lambda x: x != "BAR")
        assert result_from_function == "BAR"
        assert cache.get("FOO", "NOTHING") == "NOTHING"

    def test_conditional_cache(self) -> None:
        cache.clear()
        assert cache.get("FOO", "NOTHING") == "NOTHING"
        result_from_function = save_data_in_cache("FOO", lambda: "BAR", cache_condition=lambda x: x == "BAR")
        assert result_from_function == "BAR"
        assert cache.get("FOO", "NOTHING") == "BAR"
