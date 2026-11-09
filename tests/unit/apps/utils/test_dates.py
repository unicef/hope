from datetime import date, datetime, timezone

from hope.apps.utils.dates import normalize_date


def test_normalize_date_returns_empty_string_for_none() -> None:
    assert normalize_date(None) == ""


def test_normalize_date_passes_strings_through() -> None:
    assert normalize_date("2026-11-09") == "2026-11-09"
    assert normalize_date("2026-11-09T10:30:00+00:00") == "2026-11-09T10:30:00+00:00"


def test_normalize_date_formats_date() -> None:
    assert normalize_date(date(2026, 11, 9)) == "2026-11-09"


def test_normalize_date_formats_datetime() -> None:
    value = datetime(2026, 11, 9, 10, 30, tzinfo=timezone.utc)
    assert normalize_date(value) == "2026-11-09T10:30:00+00:00"


def test_normalize_date_stringifies_other_values() -> None:
    assert normalize_date(20261109) == "20261109"  # type: ignore[arg-type]
