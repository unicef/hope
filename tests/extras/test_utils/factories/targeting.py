"""Targeting-related factories."""

import factory
from factory.django import DjangoModelFactory

from hope.models import TargetingCriteriaRule, TargetingCriteriaRuleFilter

from .payment import PaymentPlanFactory


class TargetingCriteriaRuleFactory(DjangoModelFactory):
    payment_plan = factory.SubFactory(PaymentPlanFactory)
    household_ids = ""
    individual_ids = ""

    class Meta:
        model = TargetingCriteriaRule


class TargetingCriteriaRuleFilterFactory(DjangoModelFactory):
    field_name = "size"
    comparison_method = "EQUALS"
    arguments = [1, 10]
    targeting_criteria_rule = factory.SubFactory(TargetingCriteriaRuleFactory)

    class Meta:
        model = TargetingCriteriaRuleFilter
