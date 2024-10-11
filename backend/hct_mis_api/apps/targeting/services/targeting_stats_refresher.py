from datetime import datetime

from django.db.models import Count, Q
from django.utils import timezone

from dateutil.relativedelta import relativedelta

from hct_mis_api.apps.household.models import FEMALE, MALE, Household, Individual
from hct_mis_api.apps.targeting.models import TargetPopulation


def refresh_stats(target_population: TargetPopulation) -> TargetPopulation:
    households_ids = target_population.household_list.values_list("id", flat=True)

    delta18 = relativedelta(years=+18)
    date18ago = datetime.now() - delta18

    targeted_individuals = Individual.objects.filter(household__id__in=households_ids).aggregate(
        child_male_count=Count("id", distinct=True, filter=Q(birth_date__gt=date18ago, sex=MALE)),
        child_female_count=Count("id", distinct=True, filter=Q(birth_date__gt=date18ago, sex=FEMALE)),
        adult_male_count=Count("id", distinct=True, filter=Q(birth_date__lte=date18ago, sex=MALE)),
        adult_female_count=Count("id", distinct=True, filter=Q(birth_date__lte=date18ago, sex=FEMALE)),
        total_individuals_count=Count("id", distinct=True),
    )

    target_population.child_male_count = targeted_individuals["child_male_count"]
    target_population.child_female_count = targeted_individuals["child_female_count"]
    target_population.adult_male_count = targeted_individuals["adult_male_count"]
    target_population.adult_female_count = targeted_individuals["adult_female_count"]
    target_population.total_individuals_count = targeted_individuals["total_individuals_count"]
    target_population.total_households_count = households_ids.count()

    target_population.build_status = TargetPopulation.BUILD_STATUS_OK
    target_population.built_at = timezone.now()
    return target_population


def full_rebuild(target_population: TargetPopulation, batch_size: int = 10000) -> TargetPopulation:
    households = Household.objects.filter(
        business_area=target_population.business_area, program=target_population.program
    )
    households = households.filter(target_population.targeting_criteria.get_query())
    households = households.only("id")
    target_population.households.clear()

    index = 0
    while households_ids := households[index * batch_size : (index + 1) * batch_size]:
        target_population.households.add(*households_ids)
        index += 1
    return refresh_stats(target_population)
