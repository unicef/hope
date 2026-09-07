from datetime import UTC, date, datetime

import pytest

from hope.apps.core.api.fields import UTCDateField


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (date(2024, 1, 2), "2024-01-02"),
        (datetime(2024, 1, 2, 13, 30, tzinfo=UTC), "2024-01-02"),
        (datetime.fromisoformat("2024-01-02T00:30:00+02:00"), "2024-01-01"),
    ],
)
def test_utc_date_field_representation(value: date | datetime, expected: str) -> None:
    assert UTCDateField().to_representation(value) == expected


def test_utc_date_field_accepts_date_input() -> None:
    assert UTCDateField().to_internal_value("2024-01-02") == date(2024, 1, 2)
