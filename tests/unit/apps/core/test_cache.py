from django.core.cache import cache

from hope.apps.core.base_test_case import APITestCase
from hope.apps.core.utils import save_data_in_cache


class TestCache(APITestCase):
    def test_simple_cache(self) -> None:
        cache.clear()
        self.assertEqual(cache.get("FOO", "NOTHING"), "NOTHING")
        result_from_function = save_data_in_cache("FOO", lambda: "BAR")
        self.assertEqual(result_from_function, "BAR")
        self.assertEqual(cache.get("FOO", "NOTHING"), "BAR")

    def test_conditional_false_cache(self) -> None:
        cache.clear()
        self.assertEqual(cache.get("FOO", "NOTHING"), "NOTHING")
        result_from_function = save_data_in_cache("FOO", lambda: "BAR", cache_condition=lambda x: x != "BAR")
        self.assertEqual(result_from_function, "BAR")
        self.assertEqual(cache.get("FOO", "NOTHING"), "NOTHING")

    def test_conditional_cache(self) -> None:
        cache.clear()
        self.assertEqual(cache.get("FOO", "NOTHING"), "NOTHING")
        result_from_function = save_data_in_cache("FOO", lambda: "BAR", cache_condition=lambda x: x == "BAR")
        self.assertEqual(result_from_function, "BAR")
        self.assertEqual(cache.get("FOO", "NOTHING"), "BAR")
