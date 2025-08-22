from django.core.management import call_command
from django.test import TestCase
from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import (
    FlexibleAttributeForPDUFactory,
    PeriodicFieldDataFactory,
    create_afghanistan,
)
from extras.test_utils.factories.household import create_household_and_individuals
from extras.test_utils.factories.payment import (
    AccountFactory,
    PaymentPlanFactory,
    generate_delivery_mechanisms,
)
from extras.test_utils.factories.program import ProgramFactory

from hope.apps.core.models import (
    DataCollectingType,
    FlexibleAttribute,
    PeriodicFieldData,
)
from hope.apps.household.models import (
    FEMALE,
    MALE,
    ROLE_PRIMARY,
    Household,
    IndividualRoleInHousehold,
)
from hope.apps.payment.models import AccountType
from hope.apps.targeting.choices import FlexFieldClassification
from hope.apps.targeting.models import (
    TargetingCollectorBlockRuleFilter,
    TargetingCollectorRuleFilterBlock,
    TargetingCriteriaRule,
    TargetingIndividualBlockRuleFilter,
    TargetingIndividualRuleFilterBlock,
)
from hope.apps.utils.models import MergeStatusModel


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
            [
                {"sex": "MALE", "marital_status": "SINGLE"},
                {"sex": "FEMALE", "marital_status": "MARRIED"},
            ],
        )
        cls.household_2_indiv = household
        cls.individual_2 = individuals[0]

    def test_all_individuals_are_female(self) -> None:
        queryset = Household.objects.all()
        payment_plan = PaymentPlanFactory(program_cycle=self.program_cycle, created_by=self.user)
        tcr = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)
        individuals_filters_block = TargetingIndividualRuleFilterBlock.objects.create(
            targeting_criteria_rule=tcr, target_only_hoh=False
        )
        TargetingIndividualBlockRuleFilter.objects.create(
            individuals_filters_block=individuals_filters_block,
            comparison_method="EQUALS",
            field_name="marital_status",
            arguments=["MARRIED"],
        )
        TargetingIndividualBlockRuleFilter.objects.create(
            individuals_filters_block=individuals_filters_block,
            comparison_method="EQUALS",
            field_name="sex",
            arguments=[MALE],
        )
        queryset = queryset.filter(payment_plan.get_query())
        assert queryset.count() == 1
        assert queryset.first().id == self.household_1_indiv.id

    def test_all_individuals_are_female_on_mixins(self) -> None:
        query = Household.objects.all()
        pp = PaymentPlanFactory()
        tcr = TargetingCriteriaRule.objects.create(payment_plan=pp)
        pp.rules.set([tcr])
        individuals_filters_block = TargetingIndividualRuleFilterBlock.objects.create(
            targeting_criteria_rule=tcr, target_only_hoh=False
        )
        TargetingIndividualBlockRuleFilter.objects.create(
            comparison_method="EQUALS",
            field_name="marital_status",
            arguments=["MARRIED"],
            individuals_filters_block=individuals_filters_block,
        )
        TargetingIndividualBlockRuleFilter.objects.create(
            comparison_method="EQUALS",
            field_name="sex",
            arguments=[MALE],
            individuals_filters_block=individuals_filters_block,
        )

        query = query.filter(pp.get_query())
        assert query.count() == 1
        assert query.first().id == self.household_1_indiv.id
        assert pp.get_individual_queryset().count() == 3
        assert pp.get_household_queryset().count() == 2

    def test_two_separate_blocks_on_mixins(self) -> None:
        query = Household.objects.all()

        pp = PaymentPlanFactory()
        tcr = TargetingCriteriaRule.objects.create(
            payment_plan=pp,
        )
        pp.rules.set([tcr])

        individuals_filters_block1 = TargetingIndividualRuleFilterBlock.objects.create(
            targeting_criteria_rule=tcr, target_only_hoh=False
        )
        TargetingIndividualBlockRuleFilter.objects.create(
            individuals_filters_block=individuals_filters_block1,
            comparison_method="EQUALS",
            field_name="marital_status",
            arguments=["MARRIED"],
        )
        TargetingIndividualBlockRuleFilter.objects.create(
            individuals_filters_block=individuals_filters_block1,
            comparison_method="EQUALS",
            field_name="sex",
            arguments=[FEMALE],
        )

        individuals_filters_block2 = TargetingIndividualRuleFilterBlock.objects.create(
            targeting_criteria_rule=tcr, target_only_hoh=False
        )
        TargetingIndividualBlockRuleFilter.objects.create(
            individuals_filters_block=individuals_filters_block2,
            comparison_method="EQUALS",
            field_name="marital_status",
            arguments=["SINGLE"],
        )
        TargetingIndividualBlockRuleFilter.objects.create(
            individuals_filters_block=individuals_filters_block2,
            comparison_method="EQUALS",
            field_name="sex",
            arguments=[MALE],
        )
        pp.refresh_from_db()
        query = query.filter(pp.get_query())
        assert query.count() == 1
        assert query.first().id == self.household_2_indiv.id

    def test_filter_on_flex_field_not_exist(self) -> None:
        payment_plan = PaymentPlanFactory(program_cycle=self.program_cycle, created_by=self.user)
        tcr = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)
        individuals_filters_block = TargetingIndividualRuleFilterBlock.objects.create(
            targeting_criteria_rule=tcr, target_only_hoh=False
        )
        query = Household.objects.all()
        TargetingIndividualBlockRuleFilter.objects.create(
            individuals_filters_block=individuals_filters_block,
            comparison_method="CONTAINS",
            field_name="flex_field_2",
            arguments=["Average"],
            flex_field_classification=FlexFieldClassification.FLEX_FIELD_BASIC,
        )

        with self.assertRaises(Exception) as e:
            query.filter(payment_plan.get_query())
        assert "There is no Flex Field Attributes associated with this fieldName flex_field_2" in str(e.exception)

    def test_filter_on_flex_field(self) -> None:
        payment_plan = PaymentPlanFactory(program_cycle=self.program_cycle, created_by=self.user)
        tcr = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)
        individuals_filters_block = TargetingIndividualRuleFilterBlock.objects.create(
            targeting_criteria_rule=tcr, target_only_hoh=False
        )
        FlexibleAttribute.objects.create(
            name="flex_field_1",
            type=FlexibleAttribute.STRING,
            associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
            label={"English(EN)": "value"},
        )
        query = Household.objects.all()
        TargetingIndividualBlockRuleFilter.objects.create(
            individuals_filters_block=individuals_filters_block,
            comparison_method="CONTAINS",
            field_name="flex_field_1",
            arguments=["Average"],
            flex_field_classification=FlexFieldClassification.FLEX_FIELD_BASIC,
        )
        query = query.filter(payment_plan.get_query())
        assert query.count() == 0

        self.individual_1.flex_fields["flex_field_1"] = "Average value"
        self.individual_1.save()

        query = query.filter(payment_plan.get_query())

        assert query.count() == 1
        assert query.first().id == self.household_1_indiv.id

    def test_filter_on_pdu_flex_field_not_exist(self) -> None:
        payment_plan = PaymentPlanFactory(program_cycle=self.program_cycle, created_by=self.user)
        tcr = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)

        individuals_filters_block = TargetingIndividualRuleFilterBlock.objects.create(
            targeting_criteria_rule=tcr, target_only_hoh=False
        )
        query = Household.objects.all()
        TargetingIndividualBlockRuleFilter.objects.create(
            individuals_filters_block=individuals_filters_block,
            comparison_method="RANGE",
            field_name="pdu_field_1",
            arguments=["2", "3"],
            round_number=1,
            flex_field_classification=FlexFieldClassification.FLEX_FIELD_PDU,
        )

        with self.assertRaises(Exception) as e:
            query.filter(payment_plan.get_query())
        assert (
            "There is no PDU Flex Field Attribute associated with this fieldName pdu_field_1 in program Test Program"
            in str(e.exception)
        )

    def test_filter_on_pdu_flex_field_no_round_number(self) -> None:
        payment_plan = PaymentPlanFactory(program_cycle=self.program_cycle, created_by=self.user)
        tcr = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)
        individuals_filters_block = TargetingIndividualRuleFilterBlock.objects.create(
            targeting_criteria_rule=tcr, target_only_hoh=False
        )
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
        TargetingIndividualBlockRuleFilter.objects.create(
            individuals_filters_block=individuals_filters_block,
            comparison_method="RANGE",
            field_name="pdu_field_1",
            arguments=["2", "3"],
            flex_field_classification=FlexFieldClassification.FLEX_FIELD_PDU,
        )

        with self.assertRaises(Exception) as e:
            query.filter(payment_plan.get_query())
        assert "Round number is missing for PDU Flex Field Attribute pdu_field_1" in str(e.exception)

    def test_filter_on_pdu_flex_field_incorrect_round_number(self) -> None:
        payment_plan = PaymentPlanFactory(program_cycle=self.program_cycle, created_by=self.user)
        tcr = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)
        individuals_filters_block = TargetingIndividualRuleFilterBlock.objects.create(
            targeting_criteria_rule=tcr, target_only_hoh=False
        )
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
        TargetingIndividualBlockRuleFilter.objects.create(
            individuals_filters_block=individuals_filters_block,
            comparison_method="RANGE",
            field_name="pdu_field_1",
            arguments=["2", "3"],
            round_number=3,
            flex_field_classification=FlexFieldClassification.FLEX_FIELD_PDU,
        )

        with self.assertRaises(Exception) as e:
            query.filter(payment_plan.get_query())
        assert "Round number 3 is greater than the number of rounds for PDU Flex Field Attribute pdu_field_1" in str(
            e.exception
        )

    def test_filter_on_pdu_flex_field(self) -> None:
        payment_plan = PaymentPlanFactory(program_cycle=self.program_cycle, created_by=self.user)
        tcr = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)
        individuals_filters_block = TargetingIndividualRuleFilterBlock.objects.create(
            targeting_criteria_rule=tcr, target_only_hoh=False
        )
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
        TargetingIndividualBlockRuleFilter.objects.create(
            individuals_filters_block=individuals_filters_block,
            comparison_method="RANGE",
            field_name="pdu_field_1",
            arguments=["2", "3"],
            round_number=1,
            flex_field_classification=FlexFieldClassification.FLEX_FIELD_PDU,
        )

        self.individual_1.flex_fields = {"pdu_field_1": {"1": {"value": None}, "2": {"value": None}}}
        self.individual_1.save()
        self.individual_2.flex_fields = {
            "pdu_field_1": {
                "1": {"value": 1, "collection_date": "2021-01-01"},
                "2": {"value": None},
            }
        }
        self.individual_2.save()

        query = query.filter(payment_plan.get_query())
        assert query.count() == 0

        self.individual_1.flex_fields["pdu_field_1"]["1"] = {
            "value": 2.5,
            "collection_date": "2021-01-01",
        }
        self.individual_1.save()

        query = query.filter(payment_plan.get_query())
        assert query.count() == 1
        assert query.first().id == self.household_1_indiv.id

    def test_collector_blocks(self) -> None:
        query = Household.objects.all().order_by("unicef_id")
        hh = query.first()
        IndividualRoleInHousehold.objects.create(
            individual=hh.individuals.first(),
            household=hh,
            role=ROLE_PRIMARY,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        collector = IndividualRoleInHousehold.objects.get(household_id=hh.pk, role=ROLE_PRIMARY).individual
        AccountFactory(
            individual=collector,
            data={"phone_number": "test123"},
            account_type=AccountType.objects.get(key="mobile"),
        )

        # Target population
        payment_plan = PaymentPlanFactory(program_cycle=self.program_cycle, created_by=self.user)
        tcr = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)
        col_block = TargetingCollectorRuleFilterBlock.objects.create(targeting_criteria_rule=tcr)
        TargetingCollectorBlockRuleFilter.objects.create(
            collector_block_filters=col_block,
            comparison_method="EQUALS",
            field_name="mobile__phone_number",
            arguments=[True],
        )
        payment_plan.rules.set([tcr])
        query = query.filter(payment_plan.get_query())
        assert query.count() == 1
        assert query.first().unicef_id == self.household_1_indiv.unicef_id

    def test_exclude_by_ids(self) -> None:
        payment_plan = PaymentPlanFactory(program_cycle=self.program_cycle, created_by=self.user)

        empty_basic_query = payment_plan.get_basic_query()
        assert str(empty_basic_query) == "(AND: ('withdrawn', False), (NOT (AND: ('unicef_id__in', []))))"

        payment_plan.excluded_ids = "HH-1, HH-2"
        payment_plan.save()
        payment_plan.refresh_from_db()

        basic_query_1 = payment_plan.get_basic_query()
        assert not payment_plan.is_social_worker_program
        assert str(basic_query_1) == "(AND: ('withdrawn', False), (NOT (AND: ('unicef_id__in', ['HH-1', 'HH-2']))))"

        self.program.data_collecting_type.type = DataCollectingType.Type.SOCIAL
        self.program.data_collecting_type.save()
        payment_plan.excluded_ids = "IND_01, IND-02"
        payment_plan.save()
        payment_plan.refresh_from_db()

        assert payment_plan.is_social_worker_program
        basic_query_2 = payment_plan.get_basic_query()
        assert (
            str(basic_query_2)
            == "(AND: ('withdrawn', False), (NOT (AND: ('individuals__unicef_id__in', ['IND_01', 'IND-02']))))"
        )
