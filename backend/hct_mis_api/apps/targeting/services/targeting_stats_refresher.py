from django.db.models import Count, Sum
from django.db.models.functions import Coalesce
from django.utils import timezone

from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.targeting.models import TargetPopulation


def refresh_stats(target_population: TargetPopulation) -> TargetPopulation:
    targeting_details = target_population.household_list.annotate(
        child_male=Coalesce("male_age_group_0_5_count", 0)
        + Coalesce("male_age_group_6_11_count", 0)
        + Coalesce("male_age_group_12_17_count", 0)
        + Coalesce("male_age_group_0_5_disabled_count", 0)
        + Coalesce("male_age_group_6_11_disabled_count", 0)
        + Coalesce("male_age_group_12_17_disabled_count", 0),
        child_female=Coalesce("female_age_group_0_5_count", 0)
        + Coalesce("female_age_group_6_11_count", 0)
        + Coalesce("female_age_group_12_17_count", 0)
        + Coalesce("female_age_group_0_5_disabled_count", 0)
        + Coalesce("female_age_group_6_11_disabled_count", 0)
        + Coalesce("female_age_group_12_17_disabled_count", 0),
        adult_male=Coalesce("male_age_group_18_59_count", 0)
        + Coalesce("male_age_group_60_count", 0)
        + Coalesce("male_age_group_18_59_disabled_count", 0)
        + Coalesce("male_age_group_60_disabled_count", 0),
        adult_female=Coalesce("female_age_group_18_59_count", 0)
        + Coalesce("female_age_group_60_count", 0)
        + Coalesce("female_age_group_18_59_disabled_count", 0)
        + Coalesce("female_age_group_60_disabled_count", 0),
    ).aggregate(
        child_male_count=Sum("child_male"),
        child_female_count=Sum("child_female"),
        adult_male_count=Sum("adult_male"),
        adult_female_count=Sum("adult_female"),
        total_individuals_count=Sum("size"),
        total_households_count=Count("id"),
    )

    for key, value in targeting_details.items():
        setattr(target_population, key, value)

    target_population.build_status = TargetPopulation.BUILD_STATUS_OK
    target_population.built_at = timezone.now()
    return target_population


def full_rebuild(target_population: TargetPopulation) -> TargetPopulation:
    households = Household.objects.filter(business_area=target_population.business_area)
    households = households.filter(target_population.targeting_criteria.get_query())
    target_population.households.set(households)
    return refresh_stats(target_population)
