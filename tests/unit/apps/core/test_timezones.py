from datetime import UTC, date, datetime

from freezegun import freeze_time
import pytest

from hope.apps.core.timezones import (
    format_human_datetime,
    get_country_timezone_name,
    local_date,
    localize_datetime,
    resolve_timezone,
    resolve_timezone_name,
    to_utc_midnight,
    utc_date,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (date(2024, 1, 2), date(2024, 1, 2)),
        (datetime(2024, 1, 2, 13, 30), date(2024, 1, 2)),
        (datetime.fromisoformat("2024-01-02T00:30:00+02:00"), date(2024, 1, 1)),
    ],
)
def test_utc_date(value: date | datetime, expected: date) -> None:
    assert utc_date(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (date(2024, 1, 2), datetime(2024, 1, 2, tzinfo=UTC)),
        (datetime(2024, 1, 2, 13, 30, tzinfo=UTC), datetime(2024, 1, 2, tzinfo=UTC)),
        (datetime.fromisoformat("2024-01-02T00:30:00+02:00"), datetime(2024, 1, 1, tzinfo=UTC)),
        ("2024-01-02", datetime(2024, 1, 2, tzinfo=UTC)),
    ],
)
def test_to_utc_midnight(value: date | datetime | str, expected: datetime) -> None:
    assert to_utc_midnight(value) == expected


@pytest.mark.parametrize(
    ("iso_code2", "expected"),
    [
        (None, "UTC"),
        ("", "UTC"),
        ("XX", "UTC"),
        ("pl", "Europe/Warsaw"),
    ],
)
def test_get_country_timezone_name(iso_code2: str | None, expected: str) -> None:
    assert get_country_timezone_name(iso_code2) == expected


def test_resolve_timezone_name_defaults_to_utc() -> None:
    assert resolve_timezone_name() == "UTC"


def test_resolve_timezone_defaults_to_utc() -> None:
    assert str(resolve_timezone()) == "UTC"


def test_localize_datetime_uses_explicit_timezone() -> None:
    value = datetime(2026, 8, 21, 12, 30, tzinfo=UTC)

    assert localize_datetime(value, timezone_name="Europe/Warsaw") == datetime.fromisoformat(
        "2026-08-21T14:30:00+02:00"
    )


def test_localize_datetime_uses_resolved_timezone() -> None:
    value = datetime(2026, 8, 21, 12, 30, tzinfo=UTC)

    assert localize_datetime(value) == value


def test_format_human_datetime_uses_resolved_timezone() -> None:
    value = datetime(2026, 8, 21, 12, 30, tzinfo=UTC)

    assert format_human_datetime(value) == "21 August 2026 12:30 PM (UTC)"


def test_format_human_datetime_rejects_naive_datetime() -> None:
    value = datetime(2026, 1, 21, 12, 30)

    with pytest.raises(ValueError, match=r"localtime\(\) cannot be applied to a naive datetime"):
        format_human_datetime(value, timezone_name="America/New_York")


def test_local_date_uses_provided_datetime() -> None:
    value = datetime(2026, 8, 21, 22, 30, tzinfo=UTC)

    assert local_date(at=value) == date(2026, 8, 21)


@freeze_time("2026-08-21 22:30:00")
def test_local_date_uses_current_datetime() -> None:
    assert local_date() == date(2026, 8, 21)
