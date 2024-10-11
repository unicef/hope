from django.core.management import call_command
from django.test import TestCase

from hct_mis_api.apps.core.fixtures import (
    FlexibleAttributeForPDUFactory,
    PeriodicFieldDataFactory,
    create_afghanistan,
)
from hct_mis_api.apps.core.models import FlexibleAttribute, PeriodicFieldData
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.household.models import FEMALE, MALE, Household
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.targeting.choices import FlexFieldClassification
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
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        call_command("loadflexfieldsattributes")
        cls.business_area = create_afghanistan()
        cls.program = ProgramFactory(business_area=cls.business_area, name="Test Program")
        (household, individuals) = create_household_and_individuals(
            {
                "business_area": cls.business_area,
            },
            [{"sex": "MALE", "marital_status": "MARRIED"}],
        )
        cls.household_1_indiv = household
        cls.individual_1 = individuals[0]
        (household, individuals) = create_household_and_individuals(
            {
                "business_area": cls.business_area,
            },
            [{"sex": "MALE", "marital_status": "SINGLE"}, {"sex": "FEMALE", "marital_status": "MARRIED"}],
        )
        cls.household_2_indiv = household
        cls.individual_2 = individuals[0]

    def test_all_individuals_are_female(self) -> None:
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

    def test_all_individuals_are_female_on_mixins(self) -> None:
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

    def test_two_separate_blocks_on_mixins(self) -> None:
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

    def test_filter_on_flex_field_not_exist(self) -> None:
        tp = TargetPopulation(program=self.program)
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
        query = Household.objects.all()
        flex_field_filter = TargetingIndividualBlockRuleFilter(
            individuals_filters_block=individuals_filters_block,
            comparison_method="CONTAINS",
            field_name="flex_field_2",
            arguments=["Average"],
            flex_field_classification=FlexFieldClassification.FLEX_FIELD_BASIC,
        )
        flex_field_filter.save()

        with self.assertRaises(Exception) as e:
            query.filter(tc.get_query())
        self.assertIn(
            "There is no Flex Field Attributes associated with this fieldName flex_field_2",
            str(e.exception),
        )

    def test_filter_on_flex_field(self) -> None:
        tp = TargetPopulation(program=self.program)
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
        FlexibleAttribute.objects.create(
            name="flex_field_1",
            type=FlexibleAttribute.STRING,
            associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
        )
        query = Household.objects.all()
        flex_field_filter = TargetingIndividualBlockRuleFilter(
            individuals_filters_block=individuals_filters_block,
            comparison_method="CONTAINS",
            field_name="flex_field_1",
            arguments=["Average"],
            flex_field_classification=FlexFieldClassification.FLEX_FIELD_BASIC,
        )
        flex_field_filter.save()
        query = query.filter(tc.get_query())
        self.assertEqual(query.count(), 0)

        self.individual_1.flex_fields["flex_field_1"] = "Average value"
        self.individual_1.save()

        query = query.filter(tc.get_query())

        self.assertEqual(query.count(), 1)
        self.assertEqual(query.first().id, self.household_1_indiv.id)

    def test_filter_on_pdu_flex_field_not_exist(self) -> None:
        tp = TargetPopulation(program=self.program)
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
        query = Household.objects.all()
        pdu_filter = TargetingIndividualBlockRuleFilter(
            individuals_filters_block=individuals_filters_block,
            comparison_method="RANGE",
            field_name="pdu_field_1",
            arguments=["2", "3"],
            round_number=1,
            flex_field_classification=FlexFieldClassification.FLEX_FIELD_PDU,
        )
        pdu_filter.save()

        with self.assertRaises(Exception) as e:
            query.filter(tc.get_query())
        self.assertIn(
            "There is no PDU Flex Field Attribute associated with this fieldName pdu_field_1 in program Test Program",
            str(e.exception),
        )

    def test_filter_on_pdu_flex_field_no_round_number(self) -> None:
        tp = TargetPopulation(program=self.program)
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
        pdu_data = PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.DECIMAL,
            number_of_rounds=2,
            rounds_names=["Round 1", "Round 2"],
        )
        FlexibleAttributeForPDUFactory(
            program=self.program,
            label="PDU Field 1",
            pdu_data=pdu_data,
        )
        query = Household.objects.all()
        pdu_filter = TargetingIndividualBlockRuleFilter(
            individuals_filters_block=individuals_filters_block,
            comparison_method="RANGE",
            field_name="pdu_field_1",
            arguments=["2", "3"],
            flex_field_classification=FlexFieldClassification.FLEX_FIELD_PDU,
        )
        pdu_filter.save()

        with self.assertRaises(Exception) as e:
            query.filter(tc.get_query())
        self.assertIn(
            "Round number is missing for PDU Flex Field Attribute pdu_field_1",
            str(e.exception),
        )

    def test_filter_on_pdu_flex_field_incorrect_round_number(self) -> None:
        tp = TargetPopulation(program=self.program)
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
        pdu_data = PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.DECIMAL,
            number_of_rounds=2,
            rounds_names=["Round 1", "Round 2"],
        )
        FlexibleAttributeForPDUFactory(
            program=self.program,
            label="PDU Field 1",
            pdu_data=pdu_data,
        )
        query = Household.objects.all()
        pdu_filter = TargetingIndividualBlockRuleFilter(
            individuals_filters_block=individuals_filters_block,
            comparison_method="RANGE",
            field_name="pdu_field_1",
            arguments=["2", "3"],
            round_number=3,
            flex_field_classification=FlexFieldClassification.FLEX_FIELD_PDU,
        )
        pdu_filter.save()

        with self.assertRaises(Exception) as e:
            query.filter(tc.get_query())
        self.assertIn(
            "Round number 3 is greater than the number of rounds for PDU Flex Field Attribute pdu_field_1",
            str(e.exception),
        )

    def test_filter_on_pdu_flex_field(self) -> None:
        tp = TargetPopulation(program=self.program)
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
        pdu_data = PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.DECIMAL,
            number_of_rounds=2,
            rounds_names=["Round 1", "Round 2"],
        )
        FlexibleAttributeForPDUFactory(
            program=self.program,
            label="PDU Field 1",
            pdu_data=pdu_data,
        )
        query = Household.objects.all()
        pdu_filter = TargetingIndividualBlockRuleFilter.objects.create(
            individuals_filters_block=individuals_filters_block,
            comparison_method="RANGE",
            field_name="pdu_field_1",
            arguments=["2", "3"],
            round_number=1,
            flex_field_classification=FlexFieldClassification.FLEX_FIELD_PDU,
        )
        pdu_filter.save()

        self.individual_1.flex_fields = {"pdu_field_1": {"1": {"value": None}, "2": {"value": None}}}
        self.individual_1.save()
        self.individual_2.flex_fields = {
            "pdu_field_1": {"1": {"value": 1, "collection_date": "2021-01-01"}, "2": {"value": None}}
        }
        self.individual_2.save()

        query = query.filter(tc.get_query())
        self.assertEqual(query.count(), 0)

        self.individual_1.flex_fields["pdu_field_1"]["1"] = {"value": 2.5, "collection_date": "2021-01-01"}
        self.individual_1.save()

        query = query.filter(tc.get_query())
        self.assertEqual(query.count(), 1)
        self.assertEqual(query.first().id, self.household_1_indiv.id)
