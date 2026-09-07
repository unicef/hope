from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from rest_framework import serializers

from hope.models import Household, Payment, PaymentPlan
from hope.models.utils import MergeStatusModel

if TYPE_CHECKING:
    from hope.models import Individual


class HouseholdStatusIndividualSerializer(serializers.Serializer):
    role = serializers.CharField(allow_null=True)
    relationship = serializers.CharField(allow_null=True)
    tax_id = serializers.CharField(allow_null=True)


class HouseholdStatusInfoSerializer(serializers.Serializer):
    status = serializers.CharField()
    date = serializers.DateTimeField(allow_null=True)
    individual = HouseholdStatusIndividualSerializer(required=False)


class HouseholdStatusResponseSerializer(serializers.Serializer):
    info = HouseholdStatusInfoSerializer()


def get_household_status(
    household: Household | None,
) -> tuple[str, datetime | None]:
    if household.rdi_merge_status == MergeStatusModel.PENDING:
        return "imported", household.updated_at
    if household.rdi_merge_status == MergeStatusModel.MERGED:
        payments = Payment.objects.filter(household=household, delivered_quantity__isnull=False)
        if payments.exists():
            return "paid", payments.first().delivery_date

    if selections := Payment.objects.filter(
        household=household, parent__status__in=PaymentPlan.PRE_PAYMENT_PLAN_STATUSES
    ).exists():
        selection = selections.order_by("updated_at").first()
        return "targeted", selection.updated_at

    return "merged to population", household.created_at


def get_individual_info(individual: "Individual", tax_id: str | None) -> dict:
    return {
        "role": individual.role,
        "relationship": individual.relationship,
        "tax_id": tax_id,
    }


def get_household_info(
    household: Household | None,
    individual: Optional["Individual"] = None,
    tax_id: str | None = None,
) -> dict[str, Any]:
    status, date = get_household_status(household)
    output: dict = {"status": status, "date": date}
    if individual:
        output["individual"] = get_individual_info(individual, tax_id=tax_id)
    return {"info": output}


def serialize_by_individual(individual: "Individual", tax_id: str) -> dict:
    return get_household_info(individual.household, individual, tax_id)


def serialize_by_household(household: Household | None) -> dict:
    return get_household_info(household)
