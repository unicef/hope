import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Union

from django.db.models import Sum

from hct_mis_api.apps.core.querysets import ExtendedQuerySetSequence
from hct_mis_api.apps.payment.models import Payment, PaymentRecord
from hct_mis_api.apps.payment.utils import get_quantity_in_usd

if TYPE_CHECKING:
    from hct_mis_api.apps.household.models import Household


def mark_as_failed(payment_item: Union[PaymentRecord, Payment]) -> None:
    payment_item.mark_as_failed()
    payment_item.save()

    recalculate_cash_received(payment_item.household)


def revert_mark_as_failed(
    payment_item: Union[PaymentRecord, Payment], delivered_quantity: Decimal, delivery_date: datetime.datetime
) -> None:
    payment_item.revert_mark_as_failed(delivered_quantity, delivery_date)
    payment_item.delivered_quantity_usd = get_quantity_in_usd(
        amount=delivered_quantity,
        currency=payment_item.parent.currency,
        exchange_rate=payment_item.parent.exchange_rate,
        currency_exchange_date=delivery_date,
    )
    payment_item.save()

    recalculate_cash_received(payment_item.household)


def recalculate_cash_received(household: "Household") -> None:
    payment_items = ExtendedQuerySetSequence(
        household.paymentrecord_set.all(), household.payment_set.exclude(excluded=True)
    )
    aggregated_delivered_quantity = payment_items.aggregate(
        total_cash_received=Sum("delivered_quantity"),
        total_cash_received_usd=Sum("delivered_quantity_usd"),
    )
    household.total_cash_received = aggregated_delivered_quantity["total_cash_received"]
    household.total_cash_received_usd = aggregated_delivered_quantity["total_cash_received_usd"]
    household.save(update_fields=("total_cash_received_usd", "total_cash_received_usd"))
