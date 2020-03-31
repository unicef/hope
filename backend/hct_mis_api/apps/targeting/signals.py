from pprint import pprint

from django.db.models import Sum
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from household.models import Household
from targeting.models import (
    TargetingCriteriaRuleFilter,
    TargetingCriteriaRule,
    TargetPopulation,
)


def calculate_candidate_counts(target_population):
    if target_population.status == "DRAFT":
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
        target_population.candidate_list_total_households = 0
        target_population.candidate_list_total_individuals = 0
        target_population.save()
        return
    elif target_population.status == "APPROVE":
        households = target_population.households.filter(
            target_population.final_list_targeting_criteria.get_query()
        )
    else:
        households = target_population.final_list
    households_count = households.count()
    individuals_count = households.aggregate(
        individuals_count=Sum("family_size")
    ).get("individuals_count")
    target_population.candidate_list_total_households = households_count
    target_population.candidate_list_total_individuals = individuals_count
    target_population.save()


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
def post_save_rule_filter(sender, instance, *args, **kwargs):
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


@receiver(post_save, sender=TargetingCriteriaRule)
def post_save_rule_filter(sender, instance, *args, **kwargs):
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


@receiver(pre_save, sender=TargetPopulation)
def post_save_target_population(sender, instance, *args, **kwargs):
    try:
        old = sender.objects.get(pk=instance.pk)
    except TargetPopulation.DoesNotExist:
        calculate_candidate_counts(instance)
        return
    try:
        if (
            old.candidate_list_targeting_criteria
            != instance.candidate_list_targeting_criteria
        ):
            calculate_candidate_counts(instance)
    except TargetPopulation.DoesNotExist:
        pass
    try:
        if (
            old.final_list_targeting_criteria
            != instance.final_list_targeting_criteria
        ):
            calculate_final_counts(instance)
    except TargetPopulation.DoesNotExist:
        pass
