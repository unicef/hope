from django.db.models import Count

from hct_mis_api.apps.household.models import ROLE_ALTERNATE, IndividualRoleInHousehold


def update_individuals_with_multiple_roles() -> None:
    multiple_roles_within_household_individual = (
        IndividualRoleInHousehold.objects.values("household", "individual")
        .annotate(Count("id"))
        .order_by()
        .filter(id__count__gt=1)
    )
    for household_individual_pair in multiple_roles_within_household_individual:
        IndividualRoleInHousehold.objects.filter(
            household=household_individual_pair["household"],
            individual=household_individual_pair["individual"],
            role=ROLE_ALTERNATE,
        ).delete()
