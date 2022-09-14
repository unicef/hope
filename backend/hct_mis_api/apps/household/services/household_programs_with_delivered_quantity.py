from django.db.models import Sum, F, DecimalField

from hct_mis_api.apps.core.querysets import ExtendedQuerySetSequence
from hct_mis_api.apps.household.models import Household


def programs_with_delivered_quantity(household: Household):
    payment_items = ExtendedQuerySetSequence(household.paymentrecord_set.all(), household.payment_set.all())
    programs = (
        payment_items.select_related("parent__program")
        .values("parent__program")
        .order_by("parent__program")
        .annotate(
            total_delivered_quantity=Sum("delivered_quantity", output_field=DecimalField()),
            total_delivered_quantity_usd=Sum("delivered_quantity_usd", output_field=DecimalField()),
            program_name=F("parent__program__name"),
            currency=F("currency"),
            program_id=F("parent__program__id"),
            program_created_at=F("parent__program__created_at"),
        )
        .order_by("program_created_at")
        .merge_by(
            "parent__program",
            aggregated_fields=["total_delivered_quantity", "total_delivered_quantity_usd"],
            regular_fields=["program_name", "program_id", "program_created_at", "currency"],
        )
    )

    programs_dict = {}

    for program in programs:
        if program["program_id"] not in programs_dict.keys():
            programs_dict[program["program_id"]] = {
                "id": program["program_id"],
                "name": program["program_name"],
                "quantity": [
                    {
                        "total_delivered_quantity": program["total_delivered_quantity_usd"],
                        "currency": "USD",
                    }
                ],
            }
        if program["currency"] != "USD":
            programs_dict[program["program_id"]]["quantity"].append(
                {
                    "total_delivered_quantity": program["total_delivered_quantity"],
                    "currency": program["currency"],
                }
            )

    return programs_dict.values()
