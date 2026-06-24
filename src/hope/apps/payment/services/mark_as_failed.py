import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from django.db.models import Sum
from rest_framework.exceptions import ValidationError as DRFValidationError

from hope.apps.activity_log.utils import copy_model_object
from hope.apps.payment.utils import get_quantity_in_usd, log_payment_change
from hope.models import Payment

if TYPE_CHECKING:
    from hope.models import Household


def mark_as_failed(payment_item: Payment, user_id: str | None = None) -> None:
    if payment_item.parent.is_payment_gateway:
        raise DRFValidationError("Payments in payment gateway plans cannot be manually marked as failed")

    old_payment = copy_model_object(payment_item)
    payment_item.mark_as_failed()
    payment_item.save()
    log_payment_change(old_payment, payment_item, user_id)

    recalculate_cash_received(payment_item.household)


def revert_mark_as_failed(
    payment_item: Payment,
    delivered_quantity: Decimal,
    delivery_date: datetime.datetime,
    user_id: str | None = None,
) -> None:
    if payment_item.parent.is_payment_gateway:
        raise DRFValidationError("Payments in payment gateway plans cannot be manually marked as failed")

    old_payment = copy_model_object(payment_item)
    payment_item.revert_mark_as_failed(delivered_quantity, delivery_date)
    payment_item.delivered_quantity_usd = get_quantity_in_usd(
        amount=delivered_quantity,
        currency=payment_item.parent.currency,
        exchange_rate=payment_item.parent.exchange_rate,
        currency_exchange_date=delivery_date,
    )
    payment_item.save()
    log_payment_change(old_payment, payment_item, user_id)

    recalculate_cash_received(payment_item.household)


def recalculate_cash_received(household: "Household") -> None:
    aggregated_delivered_quantity = household.payment_set.eligible().aggregate(
        total_cash_received=Sum("delivered_quantity"),
        total_cash_received_usd=Sum("delivered_quantity_usd"),
    )
    household.total_cash_received = aggregated_delivered_quantity["total_cash_received"]
    household.total_cash_received_usd = aggregated_delivered_quantity["total_cash_received_usd"]
    household.save(update_fields=("total_cash_received_usd", "total_cash_received_usd"))
