from django.core.management import call_command
from django.test import TestCase

from core.models import BusinessArea
from household.fixtures import create_household_and_individuals
from household.models import Household, MALE
from targeting.models import (
    TargetingCriteria,
    TargetingCriteriaRule,
    TargetingIndividualSubcriteriaRuleFilter,
    TargetingIndividualSubcriteriaRuleFilterBlock,
    TargetingCriteriaQueryingMixin,
    TargetingCriteriaRuleQueryingMixin,
    TargetingIndividualSubcriteriaRuleFilterBlockMixin,
)


class TestIndividualSubcriteria(TestCase):
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
        subcriteria_block = TargetingIndividualSubcriteriaRuleFilterBlock(targeting_criteria_rule=tcr)
        subcriteria_block.save()
        married_rule_filter = TargetingIndividualSubcriteriaRuleFilter(
            subcriteria_block=subcriteria_block,
            comparision_method="EQUALS",
            field_name="marital_status",
            arguments=["MARRIED"],
        )
        married_rule_filter.save()
        sex_filter = TargetingIndividualSubcriteriaRuleFilter(
            subcriteria_block=subcriteria_block,
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
        married_rule_filter = TargetingIndividualSubcriteriaRuleFilter(
            comparision_method="EQUALS",
            field_name="marital_status",
            arguments=["MARRIED"],
        )
        sex_filter = TargetingIndividualSubcriteriaRuleFilter(
            comparision_method="EQUALS",
            field_name="sex",
            arguments=[MALE],
        )
        subcriteria_block = TargetingIndividualSubcriteriaRuleFilterBlockMixin(
            individual_subcriteria_filters=[married_rule_filter, sex_filter]
        )
        tcr = TargetingCriteriaRuleQueryingMixin(filters=[], subcriteria_blocks=[subcriteria_block])
        tc = TargetingCriteriaQueryingMixin(rules=[tcr])
        query = query.filter(tc.get_query())
        self.assertEqual(query.count(), 1)
        self.assertEqual(query.first().id, self.household_targeted.id)
