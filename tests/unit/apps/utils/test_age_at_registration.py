from datetime import datetime

from hope.apps.utils.age_at_registration import calculate_age_at_registration


def test_calculate_age_at_registration_value_error() -> None:
    result = calculate_age_at_registration(datetime(2026, 10, 10), "ValueErrorHere")
    assert result is None


def test_calculate_age_at_registration_future_birthday() -> None:
    # birthdate in future
    result = calculate_age_at_registration(datetime(2026, 10, 10), "9999-10-10")
    assert result is None


def test_calculate_age_at_registration_zero() -> None:
    result = calculate_age_at_registration(datetime(2023, 12, 12), "2023-12-12")
    assert result == 0


def test_calculate_age_at_registration() -> None:
    result = calculate_age_at_registration(datetime(2025, 10, 10), "2000-10-10")
    assert result == 25
