from django.core.cache import cache
import pytest

from hope.apps.core.utils import save_data_in_cache

# === Fixtures ===


@pytest.fixture
def clear_cache():
    cache.clear()


# === Tests ===


def test_save_data_in_cache_stores_value(clear_cache):
    assert cache.get("FOO", "NOTHING") == "NOTHING"

    result = save_data_in_cache("FOO", lambda: "BAR")

    assert result == "BAR"
    assert cache.get("FOO", "NOTHING") == "BAR"


def test_save_data_in_cache_skips_caching_when_condition_false(clear_cache):
    assert cache.get("FOO", "NOTHING") == "NOTHING"

    result = save_data_in_cache("FOO", lambda: "BAR", cache_condition=lambda x: x != "BAR")

    assert result == "BAR"
    assert cache.get("FOO", "NOTHING") == "NOTHING"


def test_save_data_in_cache_stores_value_when_condition_true(clear_cache):
    assert cache.get("FOO", "NOTHING") == "NOTHING"

    result = save_data_in_cache("FOO", lambda: "BAR", cache_condition=lambda x: x == "BAR")

    assert result == "BAR"
    assert cache.get("FOO", "NOTHING") == "BAR"
