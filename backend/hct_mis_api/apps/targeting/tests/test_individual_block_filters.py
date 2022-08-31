from django.core.management import call_command
from django.test import TestCase

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.household.models import FEMALE, MALE, Household
from hct_mis_api.apps.targeting.models import (
    TargetingCriteria,
    TargetingCriteriaQueryingBase,
    TargetingCriteriaRule,
    TargetingCriteriaRuleQueryingBase,
    TargetingIndividualBlockRuleFilter,
    TargetingIndividualRuleFilterBlock,
    TargetingIndividualRuleFilterBlockBase,
    TargetPopulation,
)


class TestIndividualBlockFilter(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("loadflexfieldsattributes")
        create_afghanistan()
        business_area = BusinessArea.objects.first()
        (household, individuals) = create_household_and_individuals(
            {
                "business_area": business_area,
            },
            [{"sex": "MALE", "marital_status": "MARRIED"}],
        )
        cls.household_1_indiv = household
        (household, individuals) = create_household_and_individuals(
            {
                "business_area": business_area,
            },
            [{"sex": "MALE", "marital_status": "SINGLE"}, {"sex": "FEMALE", "marital_status": "MARRIED"}],
        )
        cls.household_2_indiv = household

    def test_all_individuals_are_female(self):
        queryset = Household.objects.all()
        tp = TargetPopulation()
        tc = TargetingCriteria()
        tc.target_population = tp
        tc.save()
        tcr = TargetingCriteriaRule()
        tcr.targeting_criteria = tc
        tcr.save()
        individuals_filters_block = TargetingIndividualRuleFilterBlock(
            targeting_criteria_rule=tcr, target_only_hoh=False
        )
        individuals_filters_block.save()
        married_rule_filter = TargetingIndividualBlockRuleFilter(
            individuals_filters_block=individuals_filters_block,
            comparison_method="EQUALS",
            field_name="marital_status",
            arguments=["MARRIED"],
        )
        married_rule_filter.save()
        sex_filter = TargetingIndividualBlockRuleFilter(
            individuals_filters_block=individuals_filters_block,
            comparison_method="EQUALS",
            field_name="sex",
            arguments=[MALE],
        )
        sex_filter.save()
        queryset = queryset.filter(tc.get_query())
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, self.household_1_indiv.id)

    def test_all_individuals_are_female_on_mixins(self):
        query = Household.objects.all()
        married_rule_filter = TargetingIndividualBlockRuleFilter(
            comparison_method="EQUALS",
            field_name="marital_status",
            arguments=["MARRIED"],
        )
        sex_filter = TargetingIndividualBlockRuleFilter(
            comparison_method="EQUALS",
            field_name="sex",
            arguments=[MALE],
        )
        individuals_filters_block = TargetingIndividualRuleFilterBlockBase(
            individual_block_filters=[married_rule_filter, sex_filter], target_only_hoh=False
        )
        tcr = TargetingCriteriaRuleQueryingBase(filters=[], individuals_filters_blocks=[individuals_filters_block])
        tc = TargetingCriteriaQueryingBase(rules=[tcr])
        query = query.filter(tc.get_query())
        self.assertEqual(query.count(), 1)
        self.assertEqual(query.first().id, self.household_1_indiv.id)

    def test_two_separate_blocks_on_mixins(self):
        query = Household.objects.all()
        married_rule_filter = TargetingIndividualBlockRuleFilter(
            comparison_method="EQUALS",
            field_name="marital_status",
            arguments=["MARRIED"],
        )
        single_rule_filter = TargetingIndividualBlockRuleFilter(
            comparison_method="EQUALS",
            field_name="marital_status",
            arguments=["SINGLE"],
        )
        male_sex_filter = TargetingIndividualBlockRuleFilter(
            comparison_method="EQUALS",
            field_name="sex",
            arguments=[MALE],
        )
        female_sex_filter = TargetingIndividualBlockRuleFilter(
            comparison_method="EQUALS",
            field_name="sex",
            arguments=[FEMALE],
        )
        individuals_filters_block1 = TargetingIndividualRuleFilterBlockBase(
            individual_block_filters=[married_rule_filter, female_sex_filter], target_only_hoh=False
        )
        individuals_filters_block2 = TargetingIndividualRuleFilterBlockBase(
            individual_block_filters=[single_rule_filter, male_sex_filter], target_only_hoh=False
        )
        tcr = TargetingCriteriaRuleQueryingBase(
            filters=[], individuals_filters_blocks=[individuals_filters_block1, individuals_filters_block2]
        )
        tc = TargetingCriteriaQueryingBase(rules=[tcr])
        query = query.filter(tc.get_query())
        self.assertEqual(query.count(), 1)
        self.assertEqual(query.first().id, self.household_2_indiv.id)
