"""Targeting-related factories."""

import factory
from factory.django import DjangoModelFactory

from hope.models import TargetingCriteriaRule

from .payment import PaymentPlanFactory


class TargetingCriteriaRuleFactory(DjangoModelFactory):
    class Meta:
        model = TargetingCriteriaRule

    payment_plan = factory.SubFactory(PaymentPlanFactory)
    household_ids = ""
    individual_ids = ""
