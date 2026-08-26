from hope.apps.utils.external_urls import build_url, normalize_base_url


def test_normalize_base_url_strips_trailing_slash() -> None:
    assert normalize_base_url("https://kobo.example.org/") == "https://kobo.example.org"


def test_normalize_base_url_strips_repeated_trailing_slashes() -> None:
    assert normalize_base_url("https://kobo.example.org///") == "https://kobo.example.org"


def test_normalize_base_url_strips_surrounding_whitespace() -> None:
    assert normalize_base_url("  https://kobo.example.org/  ") == "https://kobo.example.org"


def test_normalize_base_url_keeps_base_that_has_no_trailing_slash() -> None:
    assert normalize_base_url("https://kobo.example.org") == "https://kobo.example.org"


def test_normalize_base_url_returns_empty_string_for_none() -> None:
    assert normalize_base_url(None) == ""


def test_build_url_joins_bare_base_and_bare_path() -> None:
    assert build_url("https://kobo.example.org", "api/v2/assets") == "https://kobo.example.org/api/v2/assets"


def test_build_url_joins_trailing_slash_base_and_bare_path() -> None:
    assert build_url("https://kobo.example.org/", "api/v2/assets") == "https://kobo.example.org/api/v2/assets"


def test_build_url_joins_bare_base_and_leading_slash_path() -> None:
    assert build_url("https://kobo.example.org", "/api/v2/assets") == "https://kobo.example.org/api/v2/assets"


def test_build_url_joins_trailing_slash_base_and_leading_slash_path() -> None:
    assert build_url("https://kobo.example.org/", "/api/v2/assets") == "https://kobo.example.org/api/v2/assets"


def test_build_url_keeps_trailing_slash_of_the_path() -> None:
    assert build_url("https://engine.example.org/", "deduplication_sets/") == (
        "https://engine.example.org/deduplication_sets/"
    )


def test_build_url_keeps_query_string_attached_to_the_path() -> None:
    assert build_url("https://kobo.example.org/", "api/v2/assets/?format=json&limit=30000") == (
        "https://kobo.example.org/api/v2/assets/?format=json&limit=30000"
    )


def test_build_url_keeps_path_segments_already_present_on_the_base() -> None:
    assert build_url("https://rapidpro.example.org/api/v2", "runs.json") == (
        "https://rapidpro.example.org/api/v2/runs.json"
    )


def test_build_url_returns_the_normalized_base_when_the_path_is_empty() -> None:
    assert build_url("https://kobo.example.org/") == "https://kobo.example.org"


def test_build_url_returns_the_normalized_base_when_the_path_is_only_a_slash() -> None:
    assert build_url("https://kobo.example.org/", "/") == "https://kobo.example.org"
