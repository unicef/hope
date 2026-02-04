from decimal import Decimal

from hope.apps.payment.utils import normalize_score, to_decimal


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


def test_normalize_score() -> None:
    assert normalize_score(None) is None
    assert normalize_score("123.444111") == Decimal("123.444")
    assert normalize_score("222.111") == Decimal("222.111")
    assert normalize_score("111.2") == Decimal("111.2")
