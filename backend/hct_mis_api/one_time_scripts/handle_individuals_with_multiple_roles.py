from django.db.models import Count  # ,Value, CharField
# from django.db.models.functions import Concat, Cast

from hct_mis_api.apps.household.models import IndividualRoleInHousehold, ROLE_ALTERNATE


def update_individuals_with_multiple_roles() -> None:
    multiple_roles_within_household_individual = IndividualRoleInHousehold.objects.values("household", "individual").annotate(Count('id')).order_by().filter(id__count__gt=1)
    for household_individual_pair in multiple_roles_within_household_individual:
        IndividualRoleInHousehold.objects.filter(household=household_individual_pair['household'], individual=household_individual_pair['individual'], role=ROLE_ALTERNATE).delete()

    # queries = [",".join([str(pair['household']), str(pair['individual'])])for pair in multiple_roles_within_household_individual]
    # ggg1 = IndividualRoleInHousehold.objects.annotate(household_individual_concat=Concat(
    #     Cast('household', output_field=CharField()), Value(','),
    #     Cast('individual', output_field=CharField()),
    #          )).filter(household_individual_concat__in=queries)
