import logging
from decimal import Decimal

from hct_mis_api.apps.core.exchange_rates import ExchangeRates
from hct_mis_api.apps.payment.models import Payment

logger = logging.getLogger(__name__)


def calculate_delivery_quantity_in_usd(exchange_rates_client: ExchangeRates, payment: Payment) -> None:
    exchange_rate = exchange_rates_client.get_exchange_rate_for_currency_code(
        payment.currency, payment.parent.dispersion_date
    )

    if exchange_rate is None:
        logger.info(f"exchange_rate not found for {payment.ca_id}")
        return
    exchange_rate = Decimal(exchange_rate)
    payment.delivered_quantity_usd = Decimal(payment.delivered_quantity / exchange_rate).quantize(Decimal(".01"))
