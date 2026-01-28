import factory
from factory.django import DjangoModelFactory

from extras.test_utils.factories import PaymentPlanFactory
from hope.models import TargetingCriteriaRule, TargetingCriteriaRuleFilter


class TargetingCriteriaRuleFilterFactory(DjangoModelFactory):
    field_name = "size"
    comparison_method = "EQUALS"
    arguments = [1, 10]

    class Meta:
        model = TargetingCriteriaRuleFilter


class TargetingCriteriaRuleFactory(DjangoModelFactory):
    payment_plan = factory.SubFactory(PaymentPlanFactory)

    class Meta:
        model = TargetingCriteriaRule
