from decimal import Decimal
from typing import Any

from django.db.models import DecimalField, Sum
from django.db.models.functions import Coalesce

from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.payment.models import Payment


def delivered_quantity_service(household: Household) -> list[dict[str, Any]]:
    payment_items = household.payment_set.all()
    quantity_in_usd = payment_items.exclude(status=Payment.STATUS_FORCE_FAILED).aggregate(
        total_delivered_quantity_usd=Coalesce(Sum("delivered_quantity_usd", output_field=DecimalField()), Decimal(0.0)),
    )
    quantities_per_currency = (
        payment_items.exclude(status=Payment.STATUS_FORCE_FAILED)
        .exclude(currency="USD")
        .values("currency")
        .annotate(
            total_delivered_quantity=Coalesce(Sum("delivered_quantity", output_field=DecimalField()), Decimal(0.0))
        )
    )

    result = [
        {
            "total_delivered_quantity": quantity_in_usd["total_delivered_quantity_usd"],
            "currency": "USD",
        }
    ]

    for quantity in quantities_per_currency:
        result.append(
            {
                "total_delivered_quantity": quantity["total_delivered_quantity"],
                "currency": quantity["currency"],
            }
        )

    return result
