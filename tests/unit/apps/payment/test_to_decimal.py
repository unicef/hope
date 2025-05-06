from decimal import Decimal

from django.test import TestCase

from hct_mis_api.apps.payment.utils import to_decimal


class TestToDecimal(TestCase):
    def test_to_decimal(self) -> None:
        assert to_decimal(" ") is None
        assert to_decimal("") is None
        assert to_decimal(None) is None
        assert to_decimal(3) == Decimal(f"{round(3.0, 2):.2f}")
        assert to_decimal("3") == Decimal(f"{round(3.0, 2):.2f}")
        assert to_decimal(3.1) == Decimal(f"{round(3.1, 2):.2f}")
        assert to_decimal(3.14) == Decimal(f"{round(3.14, 2):.2f}")
        assert to_decimal("3.1") == Decimal(f"{round(3.1, 2):.2f}")
        assert to_decimal("3.14") == Decimal(f"{round(3.14, 2):.2f}")
        assert to_decimal(Decimal(3.14)) == Decimal(f"{round(3.14, 2):.2f}")
