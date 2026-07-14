from typing import Any

from constance.test import override_config
from django.contrib.messages import get_messages
from django.test import Client
from django.urls import reverse
import pytest

from extras.test_utils.factories import UserFactory
from hope.apps.administration.admin_site import clean, get_bookmarks
from hope.models import User

pytestmark = pytest.mark.django_db


class FakeRedisCache:
    """Stands in for the django-redis backend, which exposes keys() and delete()."""

    def __init__(self, keys: list[str]) -> None:
        self._keys = list(keys)

    def keys(self, pattern: str) -> list[str]:
        return list(self._keys)

    def delete(self, key: str) -> None:
        self._keys.remove(key)


@pytest.fixture
def staff_user() -> User:
    return UserFactory(is_staff=True)


@pytest.fixture
def superuser() -> User:
    return UserFactory(is_staff=True, is_superuser=True)


@pytest.fixture
def staff_client(client: Client, staff_user: User) -> Client:
    client.force_login(staff_user, "django.contrib.auth.backends.ModelBackend")
    return client


@pytest.fixture
def superuser_client(client: Client, superuser: User) -> Client:
    client.force_login(superuser, "django.contrib.auth.backends.ModelBackend")
    return client


@pytest.fixture
def redis_like_cache(monkeypatch: pytest.MonkeyPatch) -> FakeRedisCache:
    fake = FakeRedisCache(
        [
            "resolve_chart_payment_afghanistan",
            "exchange_rates_usd",
            "1starts_with_digit",
        ]
    )
    monkeypatch.setattr("hope.apps.administration.admin_site.dj_cache", fake)
    return fake


def test_clean_removes_literal_backslash_n_and_surrounding_whitespace() -> None:
    assert clean(r"  Kobo,https://kobo.example.org\n ") == "Kobo,https://kobo.example.org"


@override_config(QUICK_LINKS="https://example.org")
def test_get_bookmarks_single_part_entry_uses_url_everywhere() -> None:
    assert get_bookmarks(None) == [
        '<li><a target="https://example.org" class="viewlink" href="https://example.org">https://example.org</a></li>'
    ]


@override_config(QUICK_LINKS="Kobo,https://kobo.example.org")
def test_get_bookmarks_two_part_entry_uses_label_and_url() -> None:
    assert get_bookmarks(None) == [
        '<li><a target="Kobo" class="viewlink" href="https://kobo.example.org">Kobo</a></li>'
    ]


@override_config(QUICK_LINKS="Kobo,https://kobo.example.org,extra")
def test_get_bookmarks_three_part_entry_ignores_third_part() -> None:
    assert get_bookmarks(None) == [
        '<li><a target="Kobo" class="viewlink" href="https://kobo.example.org">Kobo</a></li>'
    ]


@override_config(QUICK_LINKS="--")
def test_get_bookmarks_separator_entry_renders_divider() -> None:
    assert get_bookmarks(None) == ["<li><hr/></li>"]


@override_config(QUICK_LINKS="one,two,three,four")
def test_get_bookmarks_four_part_entry_is_skipped() -> None:
    assert get_bookmarks(None) == []


@override_config(QUICK_LINKS="one,two,three,four,five")
def test_get_bookmarks_entry_with_more_than_four_parts_is_skipped() -> None:
    assert get_bookmarks(None) == []


@override_config(QUICK_LINKS="   \n\n")
def test_get_bookmarks_blank_entries_are_skipped() -> None:
    assert get_bookmarks(None) == []


@override_config(QUICK_LINKS="Kobo,https://kobo.example.org")
def test_get_bookmarks_skips_entry_on_value_error(mocker: Any) -> None:
    mocker.patch(
        "hope.apps.administration.admin_site.format_html",
        side_effect=ValueError("error"),
    )

    assert get_bookmarks(None) == []


def test_clear_cache_view_with_test_cache_backend_shows_not_possible_error(staff_client: Client) -> None:
    response = staff_client.get(reverse("admin:clear_cache"))

    assert response.status_code == 200
    assert response.context["cache_keys"] == []
    assert response.context["is_root"] is False
    messages = [str(message) for message in get_messages(response.wsgi_request)]
    assert messages == ["Not Possible Clear Cache For Test Settings"]


def test_clear_cache_view_non_superuser_gets_access_error(
    staff_client: Client, redis_like_cache: FakeRedisCache
) -> None:
    response = staff_client.get(reverse("admin:clear_cache"))

    assert response.status_code == 200
    assert response.context["cache_keys"] == ["resolve_chart_payment_afghanistan", "exchange_rates_usd"]
    assert response.context["is_root"] is False
    messages = [str(message) for message in get_messages(response.wsgi_request)]
    assert messages == ["Access Not Allowed. Only superuser have access to clear cache"]


def test_clear_cache_view_superuser_lists_keys_starting_with_letter(
    superuser_client: Client, redis_like_cache: FakeRedisCache
) -> None:
    response = superuser_client.get(reverse("admin:clear_cache"))

    assert response.status_code == 200
    assert response.context["cache_keys"] == ["resolve_chart_payment_afghanistan", "exchange_rates_usd"]
    assert response.context["is_root"] is True
    assert list(get_messages(response.wsgi_request)) == []


def test_clear_cache_view_superuser_post_deletes_keys_with_selected_prefix(
    superuser_client: Client,
    redis_like_cache: FakeRedisCache,
    django_assert_num_queries: Any,
) -> None:
    with django_assert_num_queries(1):
        response = superuser_client.post(reverse("admin:clear_cache"), {"resolve_chart_payment": "on"})

    assert response.status_code == 200
    assert response.context["cache_keys"] == ["exchange_rates_usd"]
    assert "resolve_chart_payment_afghanistan" not in redis_like_cache._keys
    messages = [str(message) for message in get_messages(response.wsgi_request)]
    assert messages == ["Finished remove cache for: ['resolve_chart_payment']"]
