from datetime import UTC, date, datetime

import pytest

from hope.apps.core.timezones import to_utc_midnight


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
