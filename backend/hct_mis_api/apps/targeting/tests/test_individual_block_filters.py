from django.core.management import call_command
from django.test import TestCase

from core.models import BusinessArea
from household.fixtures import create_household_and_individuals
from household.models import Household, MALE
from targeting.models import (
    TargetingCriteria,
    TargetingCriteriaRule,
    TargetingIndividualBlockRuleFilter,
    TargetingIndividualRuleFilterBlock,
    TargetingCriteriaQueryingMixin,
    TargetingCriteriaRuleQueryingMixin,
    TargetingIndividualRuleFilterBlockMixin,
)


class TestIndividualBlockFilter(TestCase):
    def setUp(self):
        call_command("loadflexfieldsattributes")
        call_command("loadbusinessareas")
        business_area = BusinessArea.objects.first()
        (household, individuals) = create_household_and_individuals(
            {
                "business_area": business_area,
            },
            [{"sex": "MALE", "marital_status": "MARRIED"}],
        )
        self.household_targeted = household
        (household, individuals) = create_household_and_individuals(
            {
                "business_area": business_area,
            },
            [{"sex": "MALE", "marital_status": "SINGLE"}, {"sex": "FEMALE", "marital_status": "MARRIED"}],
        )
        self.not_targeted_household = household

    def test_all_individuals_are_female(self):
        query = Household.objects.all()
        tc = TargetingCriteria()
        tc.save()
        tcr = TargetingCriteriaRule()
        tcr.targeting_criteria = tc
        tcr.save()
        individuals_filters_block = TargetingIndividualRuleFilterBlock(targeting_criteria_rule=tcr)
        individuals_filters_block.save()
        married_rule_filter = TargetingIndividualBlockRuleFilter(
            individuals_filters_block=individuals_filters_block,
            comparision_method="EQUALS",
            field_name="marital_status",
            arguments=["MARRIED"],
        )
        married_rule_filter.save()
        sex_filter = TargetingIndividualBlockRuleFilter(
            individuals_filters_block=individuals_filters_block,
            comparision_method="EQUALS",
            field_name="sex",
            arguments=[MALE],
        )
        sex_filter.save()
        query = query.filter(tc.get_query())
        self.assertEqual(query.count(), 1)
        self.assertEqual(query.first().id, self.household_targeted.id)

    def test_all_individuals_are_female_on_mixins(self):
        query = Household.objects.all()
        married_rule_filter = TargetingIndividualBlockRuleFilter(
            comparision_method="EQUALS",
            field_name="marital_status",
            arguments=["MARRIED"],
        )
        sex_filter = TargetingIndividualBlockRuleFilter(
            comparision_method="EQUALS",
            field_name="sex",
            arguments=[MALE],
        )
        individuals_filters_block = TargetingIndividualRuleFilterBlockMixin(
            individual_block_filters=[married_rule_filter, sex_filter]
        )
        tcr = TargetingCriteriaRuleQueryingMixin(filters=[], individuals_filters_blocks=[individuals_filters_block])
        tc = TargetingCriteriaQueryingMixin(rules=[tcr])
        query = query.filter(tc.get_query())
        self.assertEqual(query.count(), 1)
        self.assertEqual(query.first().id, self.household_targeted.id)
