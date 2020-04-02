from pprint import pprint

from django.db.models import Sum
from django.db.models.signals import post_save, pre_save, m2m_changed
from django.dispatch import receiver

from household.models import Household
from targeting.models import (
    TargetingCriteriaRuleFilter,
    TargetingCriteriaRule,
    TargetPopulation,
    HouseholdSelection,
    TargetingCriteria,
)


def calculate_candidate_counts(target_population):
    if target_population.status == "DRAFT":
        if target_population.candidate_list_targeting_criteria is None:
            return
        households = Household.objects.filter(
            target_population.candidate_list_targeting_criteria.get_query()
        )
    else:
        households = target_population.households
    households_count = households.count()
    individuals_count = households.aggregate(
        individuals_count=Sum("family_size")
    ).get("individuals_count")
    target_population.candidate_list_total_households = households_count
    target_population.candidate_list_total_individuals = individuals_count


def calculate_final_counts(target_population):
    if target_population.status == "DRAFT":
        target_population.final_list_total_households = None
        target_population.final_list_total_individuals = None
        return
    elif target_population.status == "APPROVED":
        if target_population.final_list_targeting_criteria is None:
            households = target_population.households
        else:
            households = target_population.households.filter(
                target_population.final_list_targeting_criteria.get_query()
            )
    else:
        households = target_population.final_list
    households_count = households.count()
    individuals_count = households.aggregate(
        individuals_count=Sum("family_size")
    ).get("individuals_count")
    target_population.final_list_total_households = households_count
    target_population.final_list_total_individuals = individuals_count


@receiver(post_save, sender=TargetingCriteriaRuleFilter)
def post_save_rule_filter(sender, instance, *args, **kwargs):
    try:
        target_population = (
            instance.targeting_criteria_rule.targeting_criteria.target_population_candidate
        )
        calculate_candidate_counts(target_population)
        target_population.save()
    except TargetPopulation.DoesNotExist:
        pass
    try:
        target_population = (
            instance.targeting_criteria_rule.targeting_criteria.target_population_final
        )
        calculate_final_counts(target_population)
        target_population.save()
    except TargetPopulation.DoesNotExist:
        pass


@receiver(post_save, sender=TargetingCriteriaRule)
def post_save_rule(sender, instance, *args, **kwargs):
    try:
        target_population = (
            instance.targeting_criteria.target_population_candidate
        )
        calculate_candidate_counts(target_population)
        target_population.save()
    except TargetPopulation.DoesNotExist:
        pass

    try:
        target_population = instance.targeting_criteria.target_population_final
        calculate_final_counts(target_population)
        target_population.save()
    except TargetPopulation.DoesNotExist:
        pass


@receiver(post_save, sender=TargetingCriteria)
def post_save_targeting_criteria(sender, instance, *args, **kwargs):
    try:
        target_population = instance.target_population_candidate
        calculate_candidate_counts(target_population)
        target_population.save()
    except TargetPopulation.DoesNotExist:
        pass

    try:
        target_population = instance.target_population_final
        calculate_final_counts(target_population)
        target_population.save()
    except TargetPopulation.DoesNotExist:
        pass


@receiver(pre_save, sender=TargetPopulation)
def pre_save_target_population(sender, instance, *args, **kwargs):
    calculate_candidate_counts(instance)
    calculate_final_counts(instance)


@receiver(m2m_changed, sender=TargetPopulation.households.through)
def households_changed(sender, instance, **kwargs):
    calculate_candidate_counts(instance)
    calculate_final_counts(instance)
    instance.save()


@receiver(post_save, sender=HouseholdSelection)
def post_save_households_selection(sender, instance, *args, **kwargs):
    calculate_candidate_counts(instance.target_population)
    calculate_final_counts(instance.target_population)
    instance.target_population.save()
