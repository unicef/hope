import pytest
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from hope.apps.core.api.pagination import NoCountLimitOffsetPagination

pytestmark = pytest.mark.django_db


@pytest.fixture
def paginator() -> NoCountLimitOffsetPagination:
    return NoCountLimitOffsetPagination()


def _drf_request(query: str = "") -> Request:
    return Request(APIRequestFactory().get(f"/items/{query}"))


def test_paginate_queryset_returns_requested_slice(paginator: NoCountLimitOffsetPagination) -> None:
    page = paginator.paginate_queryset(list(range(10)), _drf_request("?limit=2&offset=4"))

    assert page == [4, 5]
    assert paginator.display_page_controls is True


def test_paginate_queryset_returns_none_without_limit(paginator: NoCountLimitOffsetPagination) -> None:
    paginator.default_limit = None

    page = paginator.paginate_queryset(list(range(10)), _drf_request())

    assert page is None


def test_get_paginated_response_contains_no_count(paginator: NoCountLimitOffsetPagination) -> None:
    page = paginator.paginate_queryset(list(range(10)), _drf_request("?limit=2&offset=4"))

    response = paginator.get_paginated_response(page)

    assert list(response.data.keys()) == ["next", "previous", "results"]
    assert response.data["results"] == [4, 5]
    assert response.data["next"] == "http://testserver/items/?limit=2&offset=6"
    assert response.data["previous"] == "http://testserver/items/?limit=2&offset=2"


def test_get_previous_link_drops_offset_param_for_first_page(paginator: NoCountLimitOffsetPagination) -> None:
    paginator.paginate_queryset(list(range(10)), _drf_request("?limit=2&offset=2"))

    assert paginator.get_previous_link() == "http://testserver/items/?limit=2"


def test_get_next_link_is_returned_even_past_the_last_item(paginator: NoCountLimitOffsetPagination) -> None:
    paginator.paginate_queryset(list(range(10)), _drf_request("?limit=5&offset=8"))

    assert paginator.get_next_link() == "http://testserver/items/?limit=5&offset=13"


def test_get_paginated_response_schema_drops_count_property(paginator: NoCountLimitOffsetPagination) -> None:
    schema = paginator.get_paginated_response_schema({"type": "array", "items": {}})

    assert "count" not in schema["properties"]
    assert {"next", "previous", "results"} <= set(schema["properties"])


def test_get_html_context_builds_links_around_current_page(paginator: NoCountLimitOffsetPagination) -> None:
    paginator.paginate_queryset(list(range(10)), _drf_request("?limit=2&offset=2"))

    context = paginator.get_html_context()

    assert context["previous_url"] == "http://testserver/items/?limit=2"
    assert context["next_url"] == "http://testserver/items/?limit=2&offset=4"
    assert [link.number for link in context["page_links"]] == [1, 2, 3]
    assert [link.is_active for link in context["page_links"]] == [False, True, False]
    assert context["page_links"][0].url == "http://testserver/items/?limit=2"
    assert context["page_links"][2].url == "http://testserver/items/?limit=2&offset=4"


def test_get_html_context_with_zero_limit_shows_single_page(paginator: NoCountLimitOffsetPagination) -> None:
    paginator.request = _drf_request()
    paginator.limit = 0
    paginator.offset = 0

    context = paginator.get_html_context()

    assert context["previous_url"] is None
    assert [link.number for link in context["page_links"]] == [1]
    assert context["page_links"][0].is_active is True
    assert context["page_links"][0].url == "http://testserver/items/"


def test_get_count_always_returns_zero(paginator: NoCountLimitOffsetPagination) -> None:
    assert paginator.get_count(list(range(10))) == 0
