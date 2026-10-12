from decimal import Decimal

from hope.apps.payment.utils import from_received_to_status, normalize_score, to_decimal
from hope.models import PaymentVerification


def test_to_decimal() -> None:
    assert to_decimal(" ") is None
    assert to_decimal("") is None
    assert to_decimal(None) is None
    assert to_decimal(3) == Decimal(f"{round(3.00, 2):.2f}")
    assert to_decimal("3") == Decimal(f"{round(3.00, 2):.2f}")
    assert to_decimal(3.1) == Decimal(f"{round(3.10, 2):.2f}")
    assert to_decimal(3.14) == Decimal(f"{round(3.14, 2):.2f}")
    assert to_decimal("3.1") == Decimal(f"{round(3.10, 2):.2f}")
    assert to_decimal("3.14") == Decimal(f"{round(3.14, 2):.2f}")
    assert to_decimal(Decimal(3.14)) == Decimal(f"{round(3.14, 2):.2f}")


def test_to_decimal_preserves_ten_fractional_digits() -> None:
    assert to_decimal("123456789.1234567891") == Decimal("123456789.1234567891")


def test_received_status_compares_full_precision() -> None:
    status = from_received_to_status(True, "123.1234567891", Decimal("123.1234567891"))

    assert status == PaymentVerification.STATUS_RECEIVED


def test_received_status_flags_difference_after_two_places() -> None:
    status = from_received_to_status(True, "123.1234567890", Decimal("123.1234567891"))

    assert status == PaymentVerification.STATUS_RECEIVED_WITH_ISSUES


def test_received_status_flags_invalid_amount() -> None:
    status = from_received_to_status(True, "invalid", Decimal("123.1234567891"))

    assert status == PaymentVerification.STATUS_RECEIVED_WITH_ISSUES


def test_normalize_score() -> None:
    assert normalize_score(None) is None
    assert normalize_score("123.444111") == Decimal("123.444")
    assert normalize_score("222.111") == Decimal("222.111")
    assert normalize_score("111.2") == Decimal("111.2")
