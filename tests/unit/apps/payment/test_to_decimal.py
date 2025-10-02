from decimal import Decimal

from django.test import TestCase

from hope.apps.payment.utils import normalize_score, to_decimal


class TestToDecimal(TestCase):
    def test_to_decimal(self) -> None:
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

    def test_normalize_score(self) -> None:
        self.assertIsNone(normalize_score(None))
        self.assertEqual(normalize_score("123.444111"), Decimal("123.444"))
        self.assertEqual(normalize_score("222.111"), Decimal("222.111"))
        self.assertEqual(normalize_score("111.2"), Decimal("111.2"))
