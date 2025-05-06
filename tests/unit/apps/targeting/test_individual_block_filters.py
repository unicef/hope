from django.core.management import call_command
from django.test import TestCase

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.fixtures import (
    FlexibleAttributeForPDUFactory,
    PeriodicFieldDataFactory,
    create_afghanistan,
)
from hct_mis_api.apps.core.models import FlexibleAttribute, PeriodicFieldData
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.household.models import (
    FEMALE,
    MALE,
    ROLE_PRIMARY,
    Household,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.payment.fixtures import (
    AccountFactory,
    PaymentPlanFactory,
    generate_delivery_mechanisms,
)
from hct_mis_api.apps.payment.models import AccountType
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.targeting.choices import FlexFieldClassification
from hct_mis_api.apps.targeting.fixtures import TargetingCriteriaFactory
from hct_mis_api.apps.targeting.models import (
    TargetingCollectorBlockRuleFilter,
    TargetingCollectorRuleFilterBlock,
    TargetingCriteriaQueryingBase,
    TargetingCriteriaRule,
    TargetingCriteriaRuleQueryingBase,
    TargetingIndividualBlockRuleFilter,
    TargetingIndividualRuleFilterBlock,
    TargetingIndividualRuleFilterBlockBase,
)
from hct_mis_api.apps.targeting.services.targeting_service import (
    TargetingCollectorRuleFilterBlockBase,
)
from hct_mis_api.apps.utils.models import MergeStatusModel
import pytest


class TestIndividualBlockFilter(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        call_command("loadflexfieldsattributes")
        generate_delivery_mechanisms()
        cls.business_area = create_afghanistan()
        cls.user = UserFactory()
        cls.program = ProgramFactory(business_area=cls.business_area, name="Test Program")
        cls.program_cycle = cls.program.cycles.first()
        (household, individuals) = create_household_and_individuals(
            {
                "business_area": cls.business_area,
                "program": cls.program,
            },
            [{"sex": "MALE", "marital_status": "MARRIED"}],
        )
        cls.household_1_indiv = household
        cls.individual_1 = individuals[0]
        (household, individuals) = create_household_and_individuals(
            {
                "business_area": cls.business_area,
                "program": cls.program,
            },
            [{"sex": "MALE", "marital_status": "SINGLE"}, {"sex": "FEMALE", "marital_status": "MARRIED"}],
        )
        cls.household_2_indiv = household
        cls.individual_2 = individuals[0]

    def test_all_individuals_are_female(self) -> None:
        queryset = Household.objects.all()
        tc = TargetingCriteriaFactory()
        PaymentPlanFactory(targeting_criteria=tc, program_cycle=self.program_cycle, created_by=self.user)
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
        assert queryset.count() == 1
        assert queryset.first().id == self.household_1_indiv.id

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
        tcr = TargetingCriteriaRuleQueryingBase(
            filters=[], individuals_filters_blocks=[individuals_filters_block], collectors_filters_blocks=[]
        )
        tc = TargetingCriteriaQueryingBase(rules=[tcr])
        query = query.filter(tc.get_query())
        assert query.count() == 1
        assert query.first().id == self.household_1_indiv.id

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
            filters=[],
            individuals_filters_blocks=[individuals_filters_block1, individuals_filters_block2],
            collectors_filters_blocks=[],
        )
        tc = TargetingCriteriaQueryingBase(rules=[tcr])
        query = query.filter(tc.get_query())
        assert query.count() == 1
        assert query.first().id == self.household_2_indiv.id

    def test_filter_on_flex_field_not_exist(self) -> None:
        tc = TargetingCriteriaFactory()
        PaymentPlanFactory(targeting_criteria=tc, program_cycle=self.program_cycle, created_by=self.user)
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

        with pytest.raises(Exception) as e:
            query.filter(tc.get_query())
        assert "There is no Flex Field Attributes associated with this fieldName flex_field_2" in str(e.value)

    def test_filter_on_flex_field(self) -> None:
        tc = TargetingCriteriaFactory()
        PaymentPlanFactory(targeting_criteria=tc, program_cycle=self.program_cycle, created_by=self.user)
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
            label={"English(EN)": "value"},
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
        assert query.count() == 0

        self.individual_1.flex_fields["flex_field_1"] = "Average value"
        self.individual_1.save()

        query = query.filter(tc.get_query())

        assert query.count() == 1
        assert query.first().id == self.household_1_indiv.id

    def test_filter_on_pdu_flex_field_not_exist(self) -> None:
        tc = TargetingCriteriaFactory()
        PaymentPlanFactory(targeting_criteria=tc, program_cycle=self.program_cycle, created_by=self.user)
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

        with pytest.raises(Exception) as e:
            query.filter(tc.get_query())
        assert (
            "There is no PDU Flex Field Attribute associated with this fieldName pdu_field_1 in program Test Program"
            in str(e.value)
        )

    def test_filter_on_pdu_flex_field_no_round_number(self) -> None:
        tc = TargetingCriteriaFactory()
        PaymentPlanFactory(targeting_criteria=tc, program_cycle=self.program_cycle, created_by=self.user)
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

        with pytest.raises(Exception) as e:
            query.filter(tc.get_query())
        assert "Round number is missing for PDU Flex Field Attribute pdu_field_1" in str(e.value)

    def test_filter_on_pdu_flex_field_incorrect_round_number(self) -> None:
        tc = TargetingCriteriaFactory()
        PaymentPlanFactory(targeting_criteria=tc, program_cycle=self.program_cycle, created_by=self.user)
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

        with pytest.raises(Exception) as e:
            query.filter(tc.get_query())
        assert "Round number 3 is greater than the number of rounds for PDU Flex Field Attribute pdu_field_1" in str(
            e.value
        )

    def test_filter_on_pdu_flex_field(self) -> None:
        tc = TargetingCriteriaFactory()
        PaymentPlanFactory(targeting_criteria=tc, program_cycle=self.program_cycle, created_by=self.user)
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
        assert query.count() == 0

        self.individual_1.flex_fields["pdu_field_1"]["1"] = {"value": 2.5, "collection_date": "2021-01-01"}
        self.individual_1.save()

        query = query.filter(tc.get_query())
        assert query.count() == 1
        assert query.first().id == self.household_1_indiv.id

    def test_collector_blocks(self) -> None:
        query = Household.objects.all().order_by("unicef_id")
        hh = query.first()
        IndividualRoleInHousehold.objects.create(
            individual=hh.individuals.first(), household=hh, role=ROLE_PRIMARY, rdi_merge_status=MergeStatusModel.MERGED
        )
        collector = IndividualRoleInHousehold.objects.get(household_id=hh.pk, role=ROLE_PRIMARY).individual
        AccountFactory(
            individual=collector, data={"phone_number": "test123"}, account_type=AccountType.objects.get(key="mobile")
        )
        # Target population
        tc = TargetingCriteriaFactory()
        PaymentPlanFactory(targeting_criteria=tc, program_cycle=self.program_cycle, created_by=self.user)
        tcr = TargetingCriteriaRule()
        tcr.targeting_criteria = tc
        tcr.save()
        col_block = TargetingCollectorRuleFilterBlock(targeting_criteria_rule=tcr)
        collector_filter = TargetingCollectorBlockRuleFilter(
            collector_block_filters=col_block,
            comparison_method="EQUALS",
            field_name="mobile__phone_number",
            arguments=["Yes"],
        )
        collectors_filters_block = TargetingCollectorRuleFilterBlockBase(collector_block_filters=[collector_filter])
        tcr = TargetingCriteriaRuleQueryingBase(
            filters=[],
            individuals_filters_blocks=[],
            collectors_filters_blocks=[collectors_filters_block],
        )
        tc = TargetingCriteriaQueryingBase(rules=[tcr])
        query = query.filter(tc.get_query())
        assert query.count() == 1
        assert query.first().unicef_id == self.household_1_indiv.unicef_id
