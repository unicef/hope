from django.db.models import Count, Q, Value, Case, When, FloatField, ExpressionWrapper, Sum, F

from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.targeting.models import HouseholdSelection, TargetPopulation


def get_new_households():
    households_new_count = (
        HouseholdSelection.objects.filter(
            (
                Q(
                    target_population__status__in=[
                        TargetPopulation.STATUS_READY_FOR_CASH_ASSIST,
                        TargetPopulation.STATUS_READY_FOR_PAYMENT_MODULE
                    ]
                )
                & Q(target_population__program__status=Program.FINISHED)
            )
            | Q(target_population__program__status=Program.ACTIVE)
        ).values("household", "target_population__program")
    )
    households_with_multiple_representations = households_new_count.annotate(Count("id")).values_list("household", flat=True)
    households_with_multiple_representations_list = list(households_with_multiple_representations)

    # new household representation count -1 to count only additional objects (exclude original representation)
    # returns dict with household id as key and number of additional representations as value
    additional_hh_representations = {}
    for hh in households_with_multiple_representations_list:
        if households_with_multiple_representations_list.count(hh) > 1:
            additional_hh_representations[hh] = households_with_multiple_representations_list.count(hh) - 1
    return additional_hh_representations


def calculate_count_of_related_objects(field_to_count: str) -> int:
    """
    Calculate individuals count for new households and individuals-related objects
    """
    return Household.objects.filter(id__in=households_in_programs.keys()).annotate(
        field_count=Count(field_to_count)
    ).annotate(
        value_to_multiply=Case(
            *[
                When(id=k, then=Value(v))
                for k, v in households_in_programs.items()
            ]
        )
    ).annotate(
        calculated_value=ExpressionWrapper(F("value_to_multiply") * F("field_count"), output_field=FloatField())
    ).aggregate(
        Sum("calculated_value")
    )["calculated_value__sum"]


households_in_programs = get_new_households()

household_count = sum(households_in_programs.values())


result = {
    "new_household_count": household_count,
    "new_individuals_count": calculate_count_of_related_objects("individuals"),
    "new_documents_count": calculate_count_of_related_objects("individuals__documents"),
    "new_identities_count": calculate_count_of_related_objects("individuals__identities"),
    "new_bank_accounts_count": calculate_count_of_related_objects("individuals__bank_account_info"),
    "new_entitlement_cards_count": calculate_count_of_related_objects("entitlement_cards"),
}
print(result)
