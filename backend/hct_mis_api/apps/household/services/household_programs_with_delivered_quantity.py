from decimal import Decimal
from typing import Any, Dict, List

from django.db.models import DecimalField, Sum
from django.db.models.functions import Coalesce

from hct_mis_api.apps.core.querysets import ExtendedQuerySetSequence
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.payment.models import PaymentRecord


def delivered_quantity_service(household: Household) -> List[Dict[str, Any]]:
    payment_items = ExtendedQuerySetSequence(household.paymentrecord_set.all(), household.payment_set.all())
    quantity_in_usd = payment_items.exclude(status=PaymentRecord.STATUS_FORCE_FAILED).aggregate(
        total_delivered_quantity_usd=Coalesce(Sum("delivered_quantity_usd", output_field=DecimalField()), Decimal(0.0)),
    )
    quantities_per_currency = (
        payment_items.exclude(status=PaymentRecord.STATUS_FORCE_FAILED)
        .exclude(currency="USD")
        .values("currency")
        .annotate(
            total_delivered_quantity=Coalesce(Sum("delivered_quantity", output_field=DecimalField()), Decimal(0.0))
        )
        .merge_by(
            "currency",
            aggregated_fields=["total_delivered_quantity"],
            regular_fields=["currency"],
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
