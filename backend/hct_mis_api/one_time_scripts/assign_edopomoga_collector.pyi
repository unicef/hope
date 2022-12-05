from hct_mis_api.apps.core.models import StorageFile
from hct_mis_api.apps.household.models import Household, IndividualRoleInHousehold, ROLE_PRIMARY

def find_edopomoga_households():
    storage_file = StorageFile.objects.get(pk=3)
    return Household.objects.filter(storage_obj=storage_file, business_area__slug="ukraine").distinct()

def create_collector_for_household(household):
    if household.representatives.count() > 0:
        return
    individual = household.head_of_household
    if not individual:
        print("No head of household for household {}".format(household.id))
        return
    role = IndividualRoleInHousehold(role=ROLE_PRIMARY, individual=individual, household=household)
    role.save()

def create_collectors_for_households():
    households = find_edopomoga_households()
    for household in households:
        create_collector_for_household(household)
