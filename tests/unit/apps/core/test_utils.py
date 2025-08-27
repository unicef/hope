from decimal import Decimal

from django.test import TestCase

from hope.apps.core.utils import get_count_and_percentage
from hope.models.payment import Payment
from hope.apps.payment.utils import get_payment_delivered_quantity_status_and_value


class TestCoreUtils(TestCase):
    def test_get_count_and_percentage(self) -> None:
        assert get_count_and_percentage(1) == {"count": 1, "percentage": 100.0}
        assert get_count_and_percentage(0) == {"count": 0, "percentage": 0.0}
        assert get_count_and_percentage(5, 1) == {"count": 5, "percentage": 500.0}
        assert get_count_and_percentage(20, 20) == {"count": 20, "percentage": 100.0}
        assert get_count_and_percentage(5, 25) == {"count": 5, "percentage": 20.0}

    def test_get_payment_delivered_quantity_status_and_value(self) -> None:
        with self.assertRaisesMessage(Exception, "Invalid delivered quantity"):
            get_payment_delivered_quantity_status_and_value(None, Decimal(10.00))
        with self.assertRaisesMessage(Exception, "Invalid delivered quantity"):
            get_payment_delivered_quantity_status_and_value("", Decimal(10.00))
        assert get_payment_delivered_quantity_status_and_value(-1, Decimal(10.00)) == (
            Payment.STATUS_ERROR,
            None,
        )
        assert get_payment_delivered_quantity_status_and_value(0, Decimal(10.00)) == (
            Payment.STATUS_NOT_DISTRIBUTED,
            0,
        )
        assert get_payment_delivered_quantity_status_and_value(5.00, Decimal(10.00)) == (
            Payment.STATUS_DISTRIBUTION_PARTIAL,
            Decimal(5.00),
        )
        assert get_payment_delivered_quantity_status_and_value(10.00, Decimal(10.00)) == (
            Payment.STATUS_DISTRIBUTION_SUCCESS,
            Decimal(10.00),
        )
        with self.assertRaisesMessage(Exception, "Invalid delivered quantity"):
            get_payment_delivered_quantity_status_and_value(20.00, Decimal(10.00))
