from collections import defaultdict
from decimal import Decimal
from typing import Any, Dict, List, TypedDict

from django.db.models import DecimalField, F, Sum

from hct_mis_api.apps.core.utils import encode_id_base64_required
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.payment.models import PaymentRecord


class QuantityType(TypedDict):
    total_delivered_quantity: Decimal
    currency: str


class ProgramType(TypedDict):
    id: str
    name: str
    quantity: List[QuantityType]


def programs_with_delivered_quantity(household: Household) -> List[Dict[str, Any]]:
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

    programs_dict: Dict[str, ProgramType] = defaultdict(dict)

    for program in programs:
        programs_dict[program["program_id"]]["id"] = encode_id_base64_required(program["program_id"], "Program")
        programs_dict[program["program_id"]]["name"] = program["program_name"]
        programs_dict[program["program_id"]]["quantity"] = programs_dict[program["program_id"]].get("quantity", [])

        programs_dict[program["program_id"]]["quantity"].append(
            {
                "total_delivered_quantity": program["total_delivered_quantity_usd"],
                "currency": "USD",
            }
        )

        if program["currency"] != "USD":
            programs_dict[program["program_id"]]["quantity"].append(
                {
                    "total_delivered_quantity": program["total_delivered_quantity"],
                    "currency": program["currency"],
                }
            )
    return list(programs_dict.values())
