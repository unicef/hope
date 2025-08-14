from decimal import Decimal

from django.test import TestCase

from hope.apps.payment.utils import to_decimal


class TestToDecimal(TestCase):
    def test_to_decimal(self) -> None:
        self.assertEqual(to_decimal(" "), None)
        self.assertEqual(to_decimal(""), None)
        self.assertEqual(to_decimal(None), None)
        self.assertEqual(to_decimal(3), Decimal(f"{round(3.00, 2):.2f}"))
        self.assertEqual(to_decimal("3"), Decimal(f"{round(3.00, 2):.2f}"))
        self.assertEqual(to_decimal(3.1), Decimal(f"{round(3.10, 2):.2f}"))
        self.assertEqual(to_decimal(3.14), Decimal(f"{round(3.14, 2):.2f}"))
        self.assertEqual(to_decimal("3.1"), Decimal(f"{round(3.10, 2):.2f}"))
        self.assertEqual(to_decimal("3.14"), Decimal(f"{round(3.14, 2):.2f}"))
        self.assertEqual(to_decimal(Decimal(3.14)), Decimal(f"{round(3.14, 2):.2f}"))
