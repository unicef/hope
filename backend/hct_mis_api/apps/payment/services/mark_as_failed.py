import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from django.db.models import Sum

from hct_mis_api.apps.core.exchange_rates import ExchangeRates
from hct_mis_api.apps.core.exchange_rates.utils import (
    calculate_delivery_quantity_in_usd,
)
from hct_mis_api.apps.payment.models import PaymentRecord

if TYPE_CHECKING:
    from hct_mis_api.apps.household.models import Household


def mark_as_failed(payment_record: PaymentRecord) -> None:
    payment_record.mark_as_failed()
    payment_record.save()

    recalculate_cash_received(payment_record.household)


def revert_mark_as_failed(
    payment_record: PaymentRecord, delivered_quantity: Decimal, delivery_date: datetime.datetime
) -> None:
    payment_record.revert_mark_as_failed(delivered_quantity, delivery_date)
    calculate_delivery_quantity_in_usd(ExchangeRates(), payment_record)
    payment_record.save()

    recalculate_cash_received(payment_record.household)


def recalculate_cash_received(household: "Household") -> None:
    aggregated_delivered_quantity = household.payment_records.aggregate(
        total_cash_received=Sum("delivered_quantity"),
        total_cash_received_usd=Sum("delivered_quantity_usd"),
    )
    household.total_cash_received = aggregated_delivered_quantity["total_cash_received"]
    household.total_cash_received_usd = aggregated_delivered_quantity["total_cash_received_usd"]
    household.save(update_fields=("total_cash_received_usd", "total_cash_received_usd"))
