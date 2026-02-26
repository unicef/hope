from decimal import Decimal
from unittest.mock import Mock, patch

from django.utils import timezone

from hope.apps.payment.utils import get_quantity_in_usd


def test_get_quantity_in_usd_uses_provided_client_for_falsy_exchange_rate() -> None:
    exchange_rates_client = Mock()
    exchange_rates_client.get_exchange_rate_for_currency_code.return_value = 2

    result = get_quantity_in_usd(
        amount=Decimal(10),
        currency="PLN",
        exchange_rate=0,
        currency_exchange_date=timezone.now(),
        exchange_rates_client=exchange_rates_client,
    )

    exchange_rates_client.get_exchange_rate_for_currency_code.assert_called_once()
    assert result == Decimal("5.00")


@patch("hope.apps.payment.utils.ExchangeRates")
def test_get_quantity_in_usd_creates_exchange_rates_client_for_falsy_exchange_rate(exchange_rates_cls: Mock) -> None:
    exchange_rates_client = Mock()
    exchange_rates_client.get_exchange_rate_for_currency_code.return_value = 4
    exchange_rates_cls.return_value = exchange_rates_client

    result = get_quantity_in_usd(
        amount=Decimal(12),
        currency="PLN",
        exchange_rate=0,
        currency_exchange_date=timezone.now(),
    )

    exchange_rates_cls.assert_called_once()
    exchange_rates_client.get_exchange_rate_for_currency_code.assert_called_once()
    assert result == Decimal("3.00")
