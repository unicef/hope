from django.db.models import QuerySet

from hct_mis_api.apps.core.models import StorageFile
from hct_mis_api.apps.household.models import (
    ROLE_PRIMARY,
    Household,
    IndividualRoleInHousehold,
)


def find_edopomoga_households(pk: int) -> QuerySet[Household]:
    storage_file = StorageFile.objects.get(pk=pk)
    return Household.objects.filter(storage_obj=storage_file, business_area__slug="ukraine").distinct()


def create_collector_for_household(household: Household) -> None:
    if household.representatives.count() > 0:
        return
    individual = household.head_of_household
    if not individual:
        print(f"No head of household for household {household.id}")
        return
    role = IndividualRoleInHousehold(role=ROLE_PRIMARY, individual=individual, household=household)
    role.save()


def create_collectors_for_households(pk: int = 3) -> None:
    households = find_edopomoga_households(pk)
    for household in households:
        create_collector_for_household(household)
