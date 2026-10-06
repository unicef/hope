from typing import Any

import pytest

from hope.apps.utils.external_urls import build_url, frontend_url, normalize_base_url


@pytest.mark.parametrize(
    ("base_url", "expected"),
    [
        pytest.param("https://kobo.example.org/", "https://kobo.example.org", id="trailing_slash"),
        pytest.param("https://kobo.example.org///", "https://kobo.example.org", id="repeated_trailing_slashes"),
        pytest.param("  https://kobo.example.org/  ", "https://kobo.example.org", id="surrounding_whitespace"),
        pytest.param("https://kobo.example.org", "https://kobo.example.org", id="no_trailing_slash"),
        pytest.param(None, "", id="none"),
    ],
)
def test_normalize_base_url_strips_whitespace_and_trailing_slashes(base_url: str | None, expected: str) -> None:
    assert normalize_base_url(base_url) == expected


@pytest.mark.parametrize(
    ("base_url", "path", "expected"),
    [
        pytest.param(
            "https://kobo.example.org",
            "api/v2/assets",
            "https://kobo.example.org/api/v2/assets",
            id="bare_base_and_bare_path",
        ),
        pytest.param(
            "https://kobo.example.org/",
            "api/v2/assets",
            "https://kobo.example.org/api/v2/assets",
            id="trailing_slash_base_and_bare_path",
        ),
        pytest.param(
            "https://kobo.example.org",
            "/api/v2/assets",
            "https://kobo.example.org/api/v2/assets",
            id="bare_base_and_leading_slash_path",
        ),
        pytest.param(
            "https://kobo.example.org/",
            "/api/v2/assets",
            "https://kobo.example.org/api/v2/assets",
            id="trailing_slash_base_and_leading_slash_path",
        ),
        pytest.param(
            "https://engine.example.org/",
            "deduplication_sets/",
            "https://engine.example.org/deduplication_sets/",
            id="trailing_slash_of_the_path_is_kept",
        ),
        pytest.param(
            "https://kobo.example.org/",
            "api/v2/assets/?format=json&limit=30000",
            "https://kobo.example.org/api/v2/assets/?format=json&limit=30000",
            id="query_string_stays_attached_to_the_path",
        ),
        pytest.param(
            "https://rapidpro.example.org/api/v2",
            "runs.json",
            "https://rapidpro.example.org/api/v2/runs.json",
            id="path_segments_already_on_the_base_are_kept",
        ),
        pytest.param("https://kobo.example.org/", "", "https://kobo.example.org", id="empty_path"),
        pytest.param("https://kobo.example.org/", "/", "https://kobo.example.org", id="path_is_only_a_slash"),
    ],
)
def test_build_url_joins_base_and_path_with_exactly_one_slash(base_url: str, path: str, expected: str) -> None:
    assert build_url(base_url, path) == expected


def test_build_url_returns_the_normalized_base_when_called_without_a_path() -> None:
    assert build_url("https://kobo.example.org/") == "https://kobo.example.org"


@pytest.mark.parametrize(
    ("frontend_host", "path", "expected"),
    [
        pytest.param(
            "hope.example.org",
            "/api/download-survey-sample/1/",
            "https://hope.example.org/api/download-survey-sample/1/",
            id="path_with_a_leading_slash",
        ),
        pytest.param(
            "hope.example.org",
            "afghanistan/programs/all/grievance/tickets/user-generated/7",
            "https://hope.example.org/afghanistan/programs/all/grievance/tickets/user-generated/7",
            id="path_without_a_leading_slash",
        ),
        pytest.param(
            "hope.example.org/",
            "/api/download-survey-sample/1/",
            "https://hope.example.org/api/download-survey-sample/1/",
            id="frontend_host_with_a_trailing_slash",
        ),
        pytest.param("hope.example.org", "", "https://hope.example.org", id="empty_path"),
    ],
)
def test_frontend_url_joins_the_frontend_host_and_path_with_exactly_one_slash(
    settings: Any, frontend_host: str, path: str, expected: str
) -> None:
    settings.FRONTEND_HOST = frontend_host
    settings.SOCIAL_AUTH_REDIRECT_IS_HTTPS = True

    assert frontend_url(path) == expected


@pytest.mark.parametrize(
    ("redirect_is_https", "expected"),
    [
        pytest.param(True, "https://hope.example.org/api/download-survey-sample/1/", id="https"),
        pytest.param(False, "http://hope.example.org/api/download-survey-sample/1/", id="http"),
    ],
)
def test_frontend_url_takes_the_scheme_from_social_auth_redirect_is_https(
    settings: Any, redirect_is_https: bool, expected: str
) -> None:
    settings.FRONTEND_HOST = "hope.example.org"
    settings.SOCIAL_AUTH_REDIRECT_IS_HTTPS = redirect_is_https

    assert frontend_url("/api/download-survey-sample/1/") == expected
