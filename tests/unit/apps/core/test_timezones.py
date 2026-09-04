from datetime import UTC, date, datetime

from freezegun import freeze_time
import pytest

from hope.apps.core.timezones import (
    format_human_datetime,
    get_country_timezone_name,
    latest_local_schedule_time,
    local_date,
    localize_datetime,
    resolve_timezone,
    resolve_timezone_name,
    to_utc_midnight,
    utc_date,
)


@pytest.mark.parametrize(
    ("timezone_name", "at", "hour", "expected_date", "expected_schedule_time"),
    [
        (
            "Asia/Kolkata",
            datetime(2026, 8, 10, 0, 30, tzinfo=UTC),
            6,
            date(2026, 8, 10),
            datetime(2026, 8, 10, 0, 30, tzinfo=UTC),
        ),
        (
            "America/New_York",
            datetime(2026, 8, 10, 9, tzinfo=UTC),
            6,
            date(2026, 8, 9),
            datetime(2026, 8, 9, 10, tzinfo=UTC),
        ),
        (
            "UTC",
            datetime(2026, 8, 10, 7, 30, tzinfo=UTC),
            8,
            date(2026, 8, 9),
            datetime(2026, 8, 9, 8, tzinfo=UTC),
        ),
    ],
)
def test_latest_local_schedule_time(
    timezone_name: str,
    at: datetime,
    hour: int,
    expected_date: date,
    expected_schedule_time: datetime,
) -> None:
    schedule_date, schedule_time = latest_local_schedule_time(timezone_name, at, hour)

    assert schedule_date == expected_date
    assert schedule_time == expected_schedule_time


@pytest.mark.parametrize("hour", [-1, 24])
def test_latest_local_schedule_time_rejects_invalid_hour(hour: int) -> None:
    with pytest.raises(ValueError, match="hour must be between 0 and 23"):
        latest_local_schedule_time("UTC", datetime(2026, 8, 10, tzinfo=UTC), hour)


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
