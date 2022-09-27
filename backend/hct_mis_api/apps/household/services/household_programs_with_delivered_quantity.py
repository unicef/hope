from django.db.models import DecimalField, F, Sum

from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.payment.models import PaymentRecord


def programs_with_delivered_quantity(household: Household):
    programs = (
        household.payment_records.exclude(status=PaymentRecord.STATUS_FORCE_FAILED)
        .annotate(program=F("cash_plan__program"))
        .values("program")
        .annotate(
            total_delivered_quantity=Sum("delivered_quantity", output_field=DecimalField()),
            total_delivered_quantity_usd=Sum("delivered_quantity_usd", output_field=DecimalField()),
            currency=F("currency"),
            program_name=F("cash_plan__program__name"),
            program_id=F("cash_plan__program__id"),
        )
        .order_by("cash_plan__program__created_at")
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
