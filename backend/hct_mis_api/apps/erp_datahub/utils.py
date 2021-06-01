from decimal import Decimal

from hct_mis_api.apps.core.exchange_rates import ExchangeRates
from hct_mis_api.apps.payment.models import PaymentRecord
from hct_mis_api.apps.program.models import CashPlan


def get_exchange_rate_for_cash_plan(cash_plan: CashPlan, exchange_rates_client=None):
    if exchange_rates_client is None:
        exchange_rates_client = ExchangeRates()

    exchange_rate = exchange_rates_client.get_exchange_rate_for_currency_code(
        cash_plan.currency, cash_plan.dispersion_date
    )

    return exchange_rate


def get_payment_record_delivered_quantity_in_usd(payment_record: PaymentRecord, exchange_rates_client=None):
    if (
        not payment_record.delivered_quantity
        or not payment_record.cash_plan
        or not payment_record.cash_plan.exchange_rate
    ):
        return None

    if exchange_rates_client is None:
        exchange_rates_client = ExchangeRates()

    exchange_rate = exchange_rates_client.get_exchange_rate_for_currency_code(
        payment_record.currency, payment_record.cash_plan.dispersion_date
    )
    if exchange_rate is None:
        exchange_rate = Decimal(1)
    else:
        exchange_rate = Decimal(exchange_rate)

    return Decimal(payment_record.delivered_quantity / exchange_rate).quantize(Decimal(".01"))
