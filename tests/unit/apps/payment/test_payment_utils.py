from decimal import Decimal
from unittest.mock import Mock, patch

from django.utils import timezone
import pytest
from test_utils.factories.core import CurrencyFactory

from hope.apps.payment.utils import get_number_of_samples, get_quantity_in_usd

pytestmark = pytest.mark.django_db


@pytest.fixture
def currency():
    return CurrencyFactory()


def test_get_quantity_in_usd_returns_none_for_none_amount(currency) -> None:
    result = get_quantity_in_usd(
        amount=None,  # type: ignore[arg-type]
        currency=currency,
        exchange_rate=2,
        currency_exchange_date=timezone.now(),
    )
    assert result is None


def test_get_quantity_in_usd_returns_zero_for_zero_amount(currency) -> None:
    result = get_quantity_in_usd(
        amount=Decimal(0),
        currency=currency,
        exchange_rate=2,
        currency_exchange_date=timezone.now(),
    )
    assert result == Decimal(0)


def test_get_quantity_in_usd_uses_provided_client_for_falsy_exchange_rate(currency) -> None:
    exchange_rates_client = Mock()
    exchange_rates_client.get_exchange_rate_for_currency_code.return_value = 2

    result = get_quantity_in_usd(
        amount=Decimal(10),
        currency=currency,
        exchange_rate=0,
        currency_exchange_date=timezone.now(),
        exchange_rates_client=exchange_rates_client,
    )

    exchange_rates_client.get_exchange_rate_for_currency_code.assert_called_once()
    assert result == Decimal("5.00")


@patch("hope.apps.payment.utils.ExchangeRates")
def test_get_quantity_in_usd_creates_exchange_rates_client_for_falsy_exchange_rate(
    exchange_rates_cls: Mock, currency
) -> None:
    exchange_rates_client = Mock()
    exchange_rates_client.get_exchange_rate_for_currency_code.return_value = 4
    exchange_rates_cls.return_value = exchange_rates_client

    result = get_quantity_in_usd(
        amount=Decimal(12),
        currency=currency,
        exchange_rate=0,
        currency_exchange_date=timezone.now(),
    )

    exchange_rates_cls.assert_called_once()
    exchange_rates_client.get_exchange_rate_for_currency_code.assert_called_once()
    assert result == Decimal("3.00")


def test_get_quantity_in_usd_returns_none_when_lookup_returns_none(currency) -> None:
    exchange_rates_client = Mock()
    exchange_rates_client.get_exchange_rate_for_currency_code.return_value = None

    result = get_quantity_in_usd(
        amount=Decimal(12),
        currency=currency,
        exchange_rate=0,
        currency_exchange_date=timezone.now(),
        exchange_rates_client=exchange_rates_client,
    )

    exchange_rates_client.get_exchange_rate_for_currency_code.assert_called_once()
    assert result is None


@patch("hope.apps.payment.utils.ExchangeRates")
def test_get_quantity_in_usd_does_not_lookup_when_exchange_rate_provided(exchange_rates_cls: Mock, currency) -> None:
    result = get_quantity_in_usd(
        amount=Decimal(10),
        currency=currency,
        exchange_rate=2,
        currency_exchange_date=timezone.now(),
    )

    exchange_rates_cls.assert_not_called()
    assert result == Decimal("5.00")


@pytest.mark.parametrize(
    ("sample_count", "confidence_interval", "margin_of_error", "expected"),
    [
        (100, 0.95, 0.05, 100),
        (1000, 0.95, 0.05, 417),
        (10000, 0.95, 0.05, 555),
        (1000, 0.99, 0.01, 1000),
        (1000, 0.95, 0.5, 6),
        (5, 0.95, 0.05, 5),
        (1, 0.95, 0.05, 1),
    ],
)
def test_get_number_of_samples(
    sample_count: int, confidence_interval: float, margin_of_error: float, expected: int
) -> None:
    result = get_number_of_samples(sample_count, confidence_interval, margin_of_error)
    assert result == expected


def test_get_number_of_samples_zero_margin_of_error_uses_fallback() -> None:
    result = get_number_of_samples(100, 0.95, 0)
    assert result > 0


def test_get_number_of_samples_never_exceeds_population() -> None:
    result = get_number_of_samples(10, 0.99, 0.01)
    assert result <= 10
