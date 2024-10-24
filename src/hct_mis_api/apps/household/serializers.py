from datetime import datetime
from typing import TYPE_CHECKING, Dict, Optional, Tuple

from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.payment.models import PaymentRecord
from hct_mis_api.apps.targeting.models import HouseholdSelection, TargetPopulation

if TYPE_CHECKING:
    from hct_mis_api.apps.household.models import Individual


def get_household_status(household: Household) -> Tuple[str, datetime]:
    if household.rdi_merge_status == Household.PENDING:
        return "imported", household.updated_at

    payment_records = PaymentRecord.objects.filter(household=household)
    if payment_records.exists():
        return "paid", payment_records.first().updated_at

    selections = HouseholdSelection.objects.filter(household=household)
    if selections.exists():
        selection = selections.order_by("updated_at").first()
        if selection.target_population.status == TargetPopulation.STATUS_PROCESSING:
            return "sent to cash assist", selection.updated_at
        return "targeted", selection.updated_at

    return "merged to population", household.created_at


def get_individual_info(individual: "Individual", tax_id: Optional[str]) -> Dict:
    return {
        "role": individual.role,
        "relationship": individual.relationship,
        "tax_id": tax_id,
    }


def get_household_info(
    household: Household, individual: Optional["Individual"] = None, tax_id: Optional[str] = None
) -> Dict:
    status, date = get_household_status(household)
    output = {"status": status, "date": date}
    if individual:
        output["individual"] = get_individual_info(individual, tax_id=tax_id)
    return {"info": output}


def serialize_by_individual(individual: "Individual", tax_id: str) -> Dict:
    return get_household_info(individual.household, individual, tax_id)


def serialize_by_household(household: Household) -> Dict:
    return get_household_info(household)
