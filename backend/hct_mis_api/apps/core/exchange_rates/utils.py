import logging
from decimal import Decimal

from django.db.models import Q

from hct_mis_api.apps.core.exchange_rates import ExchangeRates
from hct_mis_api.apps.payment.models import PaymentRecord

logger = logging.getLogger(__name__)


def fix_exchange_rates(all=None) -> None:

    all_payment_records = PaymentRecord.objects.all()
    if not all:
        all_payment_records = all_payment_records.filter(
            Q(delivered_quantity_usd__isnull=True) | Q(delivered_quantity_usd=0)
        )
    exchange_rates_client = ExchangeRates()

    for payment_record in all_payment_records:
        exchange_rate = exchange_rates_client.get_exchange_rate_for_currency_code(
            payment_record.currency, payment_record.cash_plan.dispersion_date
        )

        if exchange_rate is None:
            logger.info(f"exchange_rate not found for {payment_record.ca_id}")
            continue
        else:
            exchange_rate = Decimal(exchange_rate)
        payment_record.delivered_quantity_usd = Decimal(payment_record.delivered_quantity / exchange_rate).quantize(
            Decimal(".01")
        )

    PaymentRecord.objects.bulk_update(all_payment_records, ["delivered_quantity_usd"], 1000)
