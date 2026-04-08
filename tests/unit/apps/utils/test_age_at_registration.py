from datetime import datetime

from hope.apps.utils.age_at_registration import calculate_age_at_registration


def test_calculate_age_at_registration() -> None:
    # ValueError
    result = calculate_age_at_registration(datetime(2026, 10, 10), "ValueErrorHere")
    assert result is None

    # birthdate in future
    result = calculate_age_at_registration(datetime(2026, 10, 10), "9999-10-10")
    assert result is None

    result = calculate_age_at_registration(datetime(2025, 10, 10), "2000-10-10")
    assert result == 25
