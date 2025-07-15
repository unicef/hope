from datetime import datetime

from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db.models import QuerySet
from django.test import TestCase
from django.utils import timezone

from freezegun import freeze_time
from pytz import utc

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.fixtures import (
    FlexibleAttributeForPDUFactory,
    PeriodicFieldDataFactory,
    create_afghanistan,
)
from hct_mis_api.apps.core.models import PeriodicFieldData
from hct_mis_api.apps.household.fixtures import (
    create_household,
    create_household_and_individuals,
)
from hct_mis_api.apps.household.models import (
    ROLE_PRIMARY,
    Household,
    Individual,
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
from hct_mis_api.apps.targeting.models import (
    TargetingCollectorBlockRuleFilter,
    TargetingCollectorRuleFilterBlock,
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
    TargetingIndividualBlockRuleFilter,
    TargetingIndividualRuleFilterBlock,
)
from hct_mis_api.apps.utils.models import MergeStatusModel


class TargetingCriteriaRuleFilterTestCase(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        generate_delivery_mechanisms()
        households = []
        business_area = create_afghanistan()
        cls.user = UserFactory()
        (household, individuals) = create_household_and_individuals(
            {
                "size": 1,
                "residence_status": "HOST",
                "business_area": business_area,
                "first_registration_date": timezone.make_aware(
                    datetime.strptime("1900-01-01", "%Y-%m-%d"), timezone=utc
                ),
            },
            [{"birth_date": "1970-09-29"}],
        )
        households.append(household)
        cls.household_50_yo = household
        (household, individuals) = create_household_and_individuals(
            {
                "size": 1,
                "residence_status": "HOST",
                "business_area": business_area,
                "first_registration_date": timezone.make_aware(
                    datetime.strptime("1900-01-01", "%Y-%m-%d"), timezone=utc
                ),
            },
            [{"birth_date": "1991-11-18"}],
        )
        households.append(household)
        (household, individuals) = create_household_and_individuals(
            {
                "size": 1,
                "residence_status": "HOST",
                "business_area": business_area,
                "first_registration_date": timezone.make_aware(
                    datetime.strptime("2100-01-01", "%Y-%m-%d"), timezone=utc
                ),
            },
            [{"birth_date": "1991-11-18"}],
        )

        households.append(household)

        (household, individuals) = create_household_and_individuals(
            {
                "size": 2,
                "residence_status": "REFUGEE",
                "business_area": business_area,
                "first_registration_date": timezone.make_aware(
                    datetime.strptime("1900-01-01", "%Y-%m-%d"), timezone=utc
                ),
            },
            [{"birth_date": "1991-11-18"}],
        )

        households.append(household)
        cls.household_size_2 = household
        cls.household_refugee = household

        cls.households = households

    def get_households_queryset(self) -> QuerySet[Household]:
        return Household.objects.filter(pk__in=[h.pk for h in self.households])

    def test_wrong_arguments_count_validation(self) -> None:
        rule_filter = TargetingCriteriaRuleFilter(
            comparison_method="EQUALS",
            field_name="size",
            arguments=[2, 1],
        )
        try:
            rule_filter.get_query()
            self.assertTrue(False)
        except ValidationError:
            self.assertTrue(True)

        rule_filter = TargetingCriteriaRuleFilter(
            comparison_method="EQUALS",
            field_name="size",
            arguments=[],
        )
        try:
            rule_filter.get_query()
            self.assertTrue(False)
        except ValidationError:
            self.assertTrue(True)

        rule_filter = TargetingCriteriaRuleFilter(
            comparison_method="EQUALS",
            field_name="size",
        )
        try:
            rule_filter.get_query()
            self.assertTrue(False)
        except ValidationError:
            self.assertTrue(True)

    @freeze_time("2020-10-10")
    def test_rule_filter_age_equal(self) -> None:
        rule_filter = TargetingIndividualBlockRuleFilter(comparison_method="EQUALS", field_name="age", arguments=[50])
        query = rule_filter.get_query()
        queryset = Individual.objects.filter(query)
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(self.household_50_yo.pk, queryset[0].household.pk)

    @freeze_time("2020-10-10")
    def test_rule_filter_age_not_equal(self) -> None:
        rule_filter = TargetingIndividualBlockRuleFilter(
            comparison_method="NOT_EQUALS", field_name="age", arguments=[50]
        )
        query = rule_filter.get_query()
        queryset = Individual.objects.filter(query)
        self.assertEqual(queryset.count(), 3)
        self.assertTrue(self.household_50_yo.pk not in [h.household.pk for h in queryset])

    @freeze_time("2020-10-10")
    def test_rule_filter_age_range_1_49(self) -> None:
        rule_filter = TargetingIndividualBlockRuleFilter(comparison_method="RANGE", field_name="age", arguments=[1, 49])
        query = rule_filter.get_query()
        queryset = Individual.objects.filter(query).distinct()
        self.assertEqual(queryset.count(), 3)
        self.assertTrue(self.household_50_yo.pk not in [h.household.pk for h in queryset])

    @freeze_time("2020-10-10")
    def test_rule_filter_age_range_1_50(self) -> None:
        rule_filter = TargetingIndividualBlockRuleFilter(comparison_method="RANGE", field_name="age", arguments=[1, 50])
        query = rule_filter.get_query()
        queryset = Individual.objects.filter(query).distinct()
        self.assertEqual(queryset.count(), 4)
        self.assertTrue(self.household_50_yo.pk in [h.household.pk for h in queryset])

    @freeze_time("2020-10-10")
    def test_rule_filter_age_gt_40(self) -> None:
        rule_filter = TargetingIndividualBlockRuleFilter(
            comparison_method="GREATER_THAN", field_name="age", arguments=[40]
        )
        query = rule_filter.get_query()
        queryset = Individual.objects.filter(query).distinct()
        self.assertEqual(queryset.count(), 1)
        self.assertTrue(self.household_50_yo.pk in [h.household.pk for h in queryset])

    @freeze_time("2020-10-10")
    def test_rule_filter_age_lt_40(self) -> None:
        rule_filter = TargetingIndividualBlockRuleFilter(
            comparison_method="LESS_THAN", field_name="age", arguments=[40]
        )
        query = rule_filter.get_query()
        queryset = Individual.objects.filter(query).distinct()
        self.assertEqual(queryset.count(), 3)
        self.assertTrue(self.household_50_yo.pk not in [h.household.pk for h in queryset])

    @freeze_time("2020-09-28")
    def test_rule_filter_age_lt_49_should_contains_person_born_in_proper_year_before_birthday(self) -> None:
        rule_filter = TargetingIndividualBlockRuleFilter(
            comparison_method="LESS_THAN", field_name="age", arguments=[49]
        )
        query = rule_filter.get_query()
        queryset = Individual.objects.filter(query).distinct()
        self.assertEqual(queryset.count(), 4)
        self.assertTrue(self.household_50_yo.pk in [h.household.pk for h in queryset])

    @freeze_time("2020-09-29")
    def test_rule_filter_age_lt_49_shouldn_t_contains_person_born_in_proper_year_after_and_during_birthday(
        self,
    ) -> None:
        rule_filter = TargetingIndividualBlockRuleFilter(
            comparison_method="LESS_THAN", field_name="age", arguments=[49]
        )
        query = rule_filter.get_query()
        queryset = Individual.objects.filter(query).distinct()
        self.assertEqual(queryset.count(), 3)
        self.assertTrue(self.household_50_yo.pk not in [h.household.pk for h in queryset])

    def test_rule_filter_size_equals(self) -> None:
        rule_filter = TargetingCriteriaRuleFilter(comparison_method="EQUALS", field_name="size", arguments=[2])
        query = rule_filter.get_query()
        queryset = self.get_households_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 1)
        self.assertTrue(self.household_size_2.pk in [h.pk for h in queryset])

    def test_rule_filter_size_not_equals(self) -> None:
        rule_filter = TargetingCriteriaRuleFilter(
            comparison_method="NOT_EQUALS",
            field_name="size",
            arguments=[2],
        )
        query = rule_filter.get_query()
        queryset = self.get_households_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 3)
        self.assertTrue(self.household_size_2.pk not in [h.pk for h in queryset])

    def test_rule_filter_size_in_range_0_1(self) -> None:
        rule_filter = TargetingCriteriaRuleFilter(
            comparison_method="RANGE",
            field_name="size",
            arguments=[0, 1],
        )
        query = rule_filter.get_query()
        queryset = self.get_households_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 3)
        self.assertTrue(self.household_size_2.pk not in [h.pk for h in queryset])

    def test_rule_filter_size_not_in_range_0_1(self) -> None:
        rule_filter = TargetingCriteriaRuleFilter(
            comparison_method="NOT_IN_RANGE",
            field_name="size",
            arguments=[0, 1],
        )
        query = rule_filter.get_query()
        queryset = self.get_households_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 1)
        self.assertTrue(self.household_size_2.pk in [h.pk for h in queryset])

    def test_rule_filter_size_gte_2(self) -> None:
        rule_filter = TargetingCriteriaRuleFilter(
            comparison_method="GREATER_THAN",
            field_name="size",
            arguments=[2],
        )
        query = rule_filter.get_query()
        queryset = self.get_households_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 1)
        self.assertTrue(self.household_size_2.pk in [h.pk for h in queryset])

    def test_rule_filter_size_lte_1(self) -> None:
        rule_filter = TargetingCriteriaRuleFilter(
            comparison_method="LESS_THAN",
            field_name="size",
            arguments=[1],
        )
        query = rule_filter.get_query()
        queryset = self.get_households_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 3)
        self.assertTrue(self.household_size_2.pk not in [h.pk for h in queryset])

    def test_rule_filter_residence_status_equals(self) -> None:
        rule_filter = TargetingCriteriaRuleFilter(
            comparison_method="EQUALS",
            field_name="residence_status",
            arguments=["REFUGEE"],
        )
        query = rule_filter.get_query()
        queryset = self.get_households_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 1)
        self.assertTrue(self.household_refugee.pk in [h.pk for h in queryset])

    def test_rule_filter_residence_status_not_equals(self) -> None:
        rule_filter = TargetingCriteriaRuleFilter(
            comparison_method="NOT_EQUALS",
            field_name="residence_status",
            arguments=["REFUGEE"],
        )
        query = rule_filter.get_query()
        queryset = self.get_households_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 3)
        self.assertTrue(self.household_refugee.pk not in [h.pk for h in queryset])

    def test_rule_filter_registration_date_gte(self) -> None:
        rule_filter = TargetingCriteriaRuleFilter(
            comparison_method="GREATER_THAN",
            field_name="first_registration_date",
            arguments=["2000-01-01T00:00:00Z"],
        )
        query = rule_filter.get_query()
        queryset = self.get_households_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 1)

    def test_rule_filter_collector_arg_yes(self) -> None:
        # add Ind role and wallet
        hh = self.households[0]
        IndividualRoleInHousehold.objects.create(
            individual=hh.individuals.first(), household=hh, role=ROLE_PRIMARY, rdi_merge_status=MergeStatusModel.MERGED
        )
        collector = IndividualRoleInHousehold.objects.get(household_id=hh.pk, role=ROLE_PRIMARY).individual
        AccountFactory(
            individual=collector, data={"number": "test123"}, account_type=AccountType.objects.get(key="bank")
        )
        payment_plan = PaymentPlanFactory(program_cycle=hh.program.cycles.first(), created_by=self.user)
        tcr = TargetingCriteriaRule(payment_plan=payment_plan)
        col_block = TargetingCollectorRuleFilterBlock(targeting_criteria_rule=tcr)
        rule_filter = TargetingCollectorBlockRuleFilter(
            collector_block_filters=col_block,
            comparison_method="EQUALS",
            field_name="bank__number",
            arguments=[True],
        )
        query = rule_filter.get_query()
        queryset = self.get_households_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().unicef_id, hh.unicef_id)

    def test_rule_filter_collector_arg_no(self) -> None:
        # add Ind role and wallet
        hh = self.households[2]
        IndividualRoleInHousehold.objects.create(
            individual=hh.individuals.first(), household=hh, role=ROLE_PRIMARY, rdi_merge_status=MergeStatusModel.MERGED
        )
        collector = IndividualRoleInHousehold.objects.get(household_id=hh.pk, role=ROLE_PRIMARY).individual
        AccountFactory(individual=collector, data={"other__random_name": "test123"})
        # Target population
        payment_plan = PaymentPlanFactory(program_cycle=hh.program.cycles.first(), created_by=self.user)
        tcr = TargetingCriteriaRule(payment_plan=payment_plan)
        col_block = TargetingCollectorRuleFilterBlock(targeting_criteria_rule=tcr)
        rule_filter = TargetingCollectorBlockRuleFilter(
            collector_block_filters=col_block,
            comparison_method="EQUALS",
            field_name="delivery_data_field__random_name",
            arguments=[False],
        )
        query = rule_filter.get_query()
        queryset = self.get_households_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().unicef_id, hh.unicef_id)

    def test_rule_filter_collector_without_arg(self) -> None:
        # all HH list, no collector' filter
        payment_plan = PaymentPlanFactory(program_cycle=self.households[0].program.cycles.first(), created_by=self.user)
        tcr = TargetingCriteriaRule(payment_plan=payment_plan)
        col_block = TargetingCollectorRuleFilterBlock(targeting_criteria_rule=tcr)
        rule_filter = TargetingCollectorBlockRuleFilter(
            collector_block_filters=col_block,
            comparison_method="EQUALS",
            field_name="delivery_data_field__random_name",
            arguments=[],
        )
        query = rule_filter.get_query()
        queryset = self.get_households_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 4)

    def test_tc_rule_query_for_ind_hh_ids(self) -> None:
        payment_plan = PaymentPlanFactory(program_cycle=self.households[0].program.cycles.first())
        tcr = TargetingCriteriaRule(
            payment_plan=payment_plan, household_ids="HH-1, HH-2", individual_ids="IND-11, IND-22"
        )

        query = tcr.get_query()
        self.assertEqual(
            str(query),
            "(AND: (OR: ('unicef_id__in', ['HH-1', 'HH-2']), ('individuals__unicef_id__in', ['IND-11', 'IND-22'])))",
        )

        tcr.household_ids = ""
        tcr.individual_ids = "IND-33, IND-44"
        tcr.save()
        tcr.refresh_from_db()
        query = tcr.get_query()
        self.assertEqual(str(query), "(AND: ('individuals__unicef_id__in', ['IND-33', 'IND-44']))")

        tcr.household_ids = "HH-88, HH-99"
        tcr.individual_ids = ""
        tcr.save()
        tcr.refresh_from_db()
        query = tcr.get_query()
        self.assertEqual(str(query), "(AND: ('unicef_id__in', ['HH-88', 'HH-99']))")


class TargetingCriteriaFlexRuleFilterTestCase(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        call_command("loadflexfieldsattributes")
        business_area = create_afghanistan()
        (household, individuals) = create_household(
            {
                "size": 1,
                "flex_fields": {
                    "total_households_h_f": 2,
                    "treatment_facility_h_f": ["government_health_center", "other_public", "private_doctor"],
                    "other_treatment_facility_h_f": "testing other",
                },
                "business_area": business_area,
            }
        )
        cls.household_total_households_2 = household
        cls.other_treatment_facility = household
        (household, individuals) = create_household(
            {
                "size": 1,
                "flex_fields": {
                    "total_households_h_f": 4,
                    "treatment_facility_h_f": ["government_health_center", "other_public"],
                },
                "business_area": business_area,
            }
        )
        cls.household_total_households_4 = household
        create_household(
            {"size": 1, "flex_fields": {"ddd": 3, "treatment_facility_h_f": []}, "business_area": business_area}
        )

    def test_rule_filter_household_total_households_4(self) -> None:
        rule_filter = TargetingCriteriaRuleFilter(
            comparison_method="EQUALS",
            field_name="total_households_h_f",
            arguments=[4],
            flex_field_classification=FlexFieldClassification.FLEX_FIELD_BASIC,
        )
        query = rule_filter.get_query()
        queryset = Household.objects.filter(query)
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(self.household_total_households_4.pk, queryset[0].pk)

    def test_rule_filter_select_multiple_treatment_facility(self) -> None:
        rule_filter = TargetingCriteriaRuleFilter(
            comparison_method="CONTAINS",
            field_name="treatment_facility_h_f",
            arguments=["other_public", "private_doctor"],
            flex_field_classification=FlexFieldClassification.FLEX_FIELD_BASIC,
        )
        query = rule_filter.get_query()
        queryset = Household.objects.filter(query)
        self.assertEqual(queryset.count(), 1)

    def test_rule_filter_select_multiple_treatment_facility_2(self) -> None:
        rule_filter = TargetingCriteriaRuleFilter(
            comparison_method="CONTAINS",
            field_name="treatment_facility_h_f",
            arguments=["other_public", "government_health_center"],
            flex_field_classification=FlexFieldClassification.FLEX_FIELD_BASIC,
        )
        query = rule_filter.get_query()
        queryset = Household.objects.filter(query)
        self.assertEqual(queryset.count(), 2)

    def test_rule_filter_select_multiple_treatment_facility_not_contains(self) -> None:
        rule_filter = TargetingCriteriaRuleFilter(
            comparison_method="NOT_CONTAINS",
            field_name="treatment_facility_h_f",
            arguments=["other_public", "government_health_center"],
            flex_field_classification=FlexFieldClassification.FLEX_FIELD_BASIC,
        )
        query = rule_filter.get_query()
        queryset = Household.objects.filter(query)
        self.assertEqual(queryset.count(), 1)

    def test_rule_filter_string_contains(self) -> None:
        rule_filter = TargetingCriteriaRuleFilter(
            comparison_method="CONTAINS",
            field_name="other_treatment_facility_h_f",
            arguments=["other"],
            flex_field_classification=FlexFieldClassification.FLEX_FIELD_BASIC,
        )
        query = rule_filter.get_query()
        queryset = Household.objects.filter(query)
        self.assertEqual(queryset.count(), 1)


class TargetingCriteriaPDUFlexRuleFilterTestCase(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        call_command("loadflexfieldsattributes")
        business_area = create_afghanistan()
        cls.user = UserFactory()
        cls.program = ProgramFactory(name="Test Program for PDU Flex Rule Filter", business_area=business_area)
        cls.program_cycle = cls.program.cycles.first()

        pdu_data_string = PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.STRING,
            number_of_rounds=2,
            rounds_names=["Round 1", "Round 2"],
        )
        cls.pdu_field_string = FlexibleAttributeForPDUFactory(
            program=cls.program,
            label="PDU Field STRING",
            pdu_data=pdu_data_string,
        )

        pdu_data_decimal = PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.DECIMAL,
            number_of_rounds=1,
            rounds_names=["Round 1"],
        )
        cls.pdu_field_decimal = FlexibleAttributeForPDUFactory(
            program=cls.program,
            label="PDU Field DECIMAL",
            pdu_data=pdu_data_decimal,
        )

        pdu_data_date = PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.DATE,
            number_of_rounds=1,
            rounds_names=["Round 1"],
        )
        cls.pdu_field_date = FlexibleAttributeForPDUFactory(
            program=cls.program,
            label="PDU Field DATE",
            pdu_data=pdu_data_date,
        )

        pdu_data_boolean = PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.BOOL,
            number_of_rounds=1,
            rounds_names=["Round 1"],
        )
        cls.pdu_field_boolean = FlexibleAttributeForPDUFactory(
            program=cls.program,
            label="PDU Field BOOLEAN",
            pdu_data=pdu_data_boolean,
        )

        (household, individuals) = create_household(
            {
                "size": 1,
                "business_area": business_area,
                "program": cls.program,
            },
            {
                "flex_fields": {
                    cls.pdu_field_string.name: {"1": {"value": None}, "2": {"value": None}},
                    cls.pdu_field_decimal.name: {"1": {"value": 2.5}},
                    cls.pdu_field_date.name: {"1": {"value": "2020-10-10"}},
                    cls.pdu_field_boolean.name: {"1": {"value": True}},
                },
                "business_area": business_area,
            },
        )
        cls.individual1 = individuals[0]
        cls.other_treatment_facility = household
        (household, individuals) = create_household(
            {
                "size": 1,
                "business_area": business_area,
                "program": cls.program,
            },
            {
                "flex_fields": {
                    cls.pdu_field_string.name: {
                        "1": {"value": "some value", "collection_date": "2020-10-10"},
                        "2": {"value": None},
                    },
                    cls.pdu_field_decimal.name: {"1": {"value": 3}},
                    cls.pdu_field_date.name: {"1": {"value": None}},
                    cls.pdu_field_boolean.name: {"1": {"value": True}},
                },
                "business_area": business_area,
            },
        )
        cls.individual2 = individuals[0]
        (household, individuals) = create_household(
            {
                "size": 1,
                "business_area": business_area,
                "program": cls.program,
            },
            {
                "flex_fields": {
                    cls.pdu_field_string.name: {
                        "1": {"value": "different value", "collection_date": "2020-10-10"},
                        "2": {"value": None},
                    },
                    cls.pdu_field_decimal.name: {"1": {"value": 4}},
                    cls.pdu_field_date.name: {"1": {"value": "2020-02-10"}},
                    cls.pdu_field_boolean.name: {"1": {"value": None}},
                },
                "business_area": business_area,
            },
        )
        cls.individual3 = individuals[0]
        (household, individuals) = create_household(
            {
                "size": 1,
                "business_area": business_area,
                "program": cls.program,
            },
            {
                "flex_fields": {
                    cls.pdu_field_string.name: {
                        "1": {"value": "other value", "collection_date": "2020-10-10"},
                        "2": {"value": None},
                    },
                    cls.pdu_field_decimal.name: {"1": {"value": None}},
                    cls.pdu_field_date.name: {"1": {"value": "2022-10-10"}},
                    cls.pdu_field_boolean.name: {"1": {"value": False}},
                },
                "business_area": business_area,
            },
        )
        cls.individual4 = individuals[0]
        cls.individuals = [cls.individual1, cls.individual2, cls.individual3, cls.individual4]

    def get_individuals_queryset(self) -> QuerySet[Household]:
        return Individual.objects.filter(pk__in=[ind.pk for ind in self.individuals])

    def test_rule_filter_pdu_string_contains(self) -> None:
        payment_plan = PaymentPlanFactory(program_cycle=self.program_cycle, created_by=self.user)
        tcr = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)
        individuals_filters_block = TargetingIndividualRuleFilterBlock.objects.create(
            targeting_criteria_rule=tcr, target_only_hoh=False
        )
        rule_filter = TargetingIndividualBlockRuleFilter(
            individuals_filters_block=individuals_filters_block,
            comparison_method="CONTAINS",
            field_name=self.pdu_field_string.name,
            arguments=["some"],
            round_number=1,
            flex_field_classification=FlexFieldClassification.FLEX_FIELD_PDU,
        )
        query = rule_filter.get_query()

        queryset = self.get_individuals_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 1)
        self.assertIn(self.individual2, queryset)

    def test_rule_filter_pdu_string_is_null(self) -> None:
        payment_plan = PaymentPlanFactory(program_cycle=self.program_cycle, created_by=self.user)
        tcr = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)
        individuals_filters_block = TargetingIndividualRuleFilterBlock.objects.create(
            targeting_criteria_rule=tcr, target_only_hoh=False
        )
        rule_filter = TargetingIndividualBlockRuleFilter(
            individuals_filters_block=individuals_filters_block,
            comparison_method="IS_NULL",
            field_name=self.pdu_field_string.name,
            arguments=[None],
            round_number=1,
            flex_field_classification=FlexFieldClassification.FLEX_FIELD_PDU,
        )
        query = rule_filter.get_query()

        queryset = self.get_individuals_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 1)
        self.assertIn(self.individual1, queryset)

    def test_rule_filter_pdu_decimal_range(self) -> None:
        payment_plan = PaymentPlanFactory(program_cycle=self.program_cycle, created_by=self.user)
        tcr = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)

        individuals_filters_block = TargetingIndividualRuleFilterBlock.objects.create(
            targeting_criteria_rule=tcr, target_only_hoh=False
        )
        rule_filter = TargetingIndividualBlockRuleFilter(
            individuals_filters_block=individuals_filters_block,
            comparison_method="RANGE",
            field_name=self.pdu_field_decimal.name,
            arguments=["2", "3"],
            round_number=1,
            flex_field_classification=FlexFieldClassification.FLEX_FIELD_PDU,
        )
        query = rule_filter.get_query()

        queryset = self.get_individuals_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 2)
        self.assertIn(self.individual1, queryset)
        self.assertIn(self.individual2, queryset)

    def test_rule_filter_pdu_decimal_greater_than(self) -> None:
        payment_plan = PaymentPlanFactory(program_cycle=self.program_cycle, created_by=self.user)
        tcr = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)
        individuals_filters_block = TargetingIndividualRuleFilterBlock.objects.create(
            targeting_criteria_rule=tcr, target_only_hoh=False
        )
        rule_filter = TargetingIndividualBlockRuleFilter(
            individuals_filters_block=individuals_filters_block,
            comparison_method="GREATER_THAN",
            field_name=self.pdu_field_decimal.name,
            arguments=["2.5"],
            round_number=1,
            flex_field_classification=FlexFieldClassification.FLEX_FIELD_PDU,
        )
        query = rule_filter.get_query()

        queryset = self.get_individuals_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 3)
        self.assertIn(self.individual1, queryset)
        self.assertIn(self.individual2, queryset)
        self.assertIn(self.individual3, queryset)

    def test_rule_filter_pdu_decimal_less_than(self) -> None:
        payment_plan = PaymentPlanFactory(program_cycle=self.program_cycle, created_by=self.user)
        tcr = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)
        individuals_filters_block = TargetingIndividualRuleFilterBlock.objects.create(
            targeting_criteria_rule=tcr, target_only_hoh=False
        )
        rule_filter = TargetingIndividualBlockRuleFilter(
            individuals_filters_block=individuals_filters_block,
            comparison_method="LESS_THAN",
            field_name=self.pdu_field_decimal.name,
            arguments=["2.5"],
            round_number=1,
            flex_field_classification=FlexFieldClassification.FLEX_FIELD_PDU,
        )
        query = rule_filter.get_query()
        queryset = self.get_individuals_queryset().filter(query).distinct()

        self.assertEqual(queryset.count(), 1)
        self.assertIn(self.individual1, queryset)

    def test_rule_filter_pdu_decimal_is_null(self) -> None:
        payment_plan = PaymentPlanFactory(program_cycle=self.program_cycle, created_by=self.user)
        tcr = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)
        individuals_filters_block = TargetingIndividualRuleFilterBlock.objects.create(
            targeting_criteria_rule=tcr, target_only_hoh=False
        )
        rule_filter = TargetingIndividualBlockRuleFilter(
            individuals_filters_block=individuals_filters_block,
            comparison_method="IS_NULL",
            field_name=self.pdu_field_decimal.name,
            arguments=[None],
            round_number=1,
            flex_field_classification=FlexFieldClassification.FLEX_FIELD_PDU,
        )
        query = rule_filter.get_query()

        queryset = self.get_individuals_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 1)
        self.assertIn(self.individual4, queryset)

    def test_rule_filter_pdu_date_range(self) -> None:
        payment_plan = PaymentPlanFactory(program_cycle=self.program_cycle, created_by=self.user)
        tcr = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)
        individuals_filters_block = TargetingIndividualRuleFilterBlock.objects.create(
            targeting_criteria_rule=tcr, target_only_hoh=False
        )
        rule_filter = TargetingIndividualBlockRuleFilter(
            individuals_filters_block=individuals_filters_block,
            comparison_method="RANGE",
            field_name=self.pdu_field_date.name,
            arguments=["2020-02-10", "2020-10-10"],
            round_number=1,
            flex_field_classification=FlexFieldClassification.FLEX_FIELD_PDU,
        )
        query = rule_filter.get_query()

        queryset = self.get_individuals_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 2)
        self.assertIn(self.individual1, queryset)
        self.assertIn(self.individual3, queryset)

    def test_rule_filter_pdu_date_greater_than(self) -> None:
        payment_plan = PaymentPlanFactory(program_cycle=self.program_cycle, created_by=self.user)
        tcr = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)
        individuals_filters_block = TargetingIndividualRuleFilterBlock.objects.create(
            targeting_criteria_rule=tcr, target_only_hoh=False
        )
        rule_filter = TargetingIndividualBlockRuleFilter(
            individuals_filters_block=individuals_filters_block,
            comparison_method="GREATER_THAN",
            field_name=self.pdu_field_date.name,
            arguments=["2020-10-11"],
            round_number=1,
            flex_field_classification=FlexFieldClassification.FLEX_FIELD_PDU,
        )
        query = rule_filter.get_query()

        queryset = self.get_individuals_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 1)
        self.assertIn(self.individual4, queryset)

    def test_rule_filter_pdu_date_less_than(self) -> None:
        payment_plan = PaymentPlanFactory(program_cycle=self.program_cycle, created_by=self.user)
        tcr = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)
        individuals_filters_block = TargetingIndividualRuleFilterBlock.objects.create(
            targeting_criteria_rule=tcr, target_only_hoh=False
        )
        rule_filter = TargetingIndividualBlockRuleFilter(
            individuals_filters_block=individuals_filters_block,
            comparison_method="LESS_THAN",
            field_name=self.pdu_field_date.name,
            arguments=["2020-10-11"],
            round_number=1,
            flex_field_classification=FlexFieldClassification.FLEX_FIELD_PDU,
        )
        query = rule_filter.get_query()
        queryset = self.get_individuals_queryset().filter(query).distinct()

        self.assertEqual(queryset.count(), 2)
        self.assertIn(self.individual1, queryset)
        self.assertIn(self.individual3, queryset)

    def test_rule_filter_pdu_date_is_null(self) -> None:
        payment_plan = PaymentPlanFactory(program_cycle=self.program_cycle, created_by=self.user)
        tcr = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)
        individuals_filters_block = TargetingIndividualRuleFilterBlock.objects.create(
            targeting_criteria_rule=tcr, target_only_hoh=False
        )
        rule_filter = TargetingIndividualBlockRuleFilter(
            individuals_filters_block=individuals_filters_block,
            comparison_method="IS_NULL",
            field_name=self.pdu_field_date.name,
            arguments=[None],
            round_number=1,
            flex_field_classification=FlexFieldClassification.FLEX_FIELD_PDU,
        )
        query = rule_filter.get_query()

        queryset = self.get_individuals_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 1)
        self.assertIn(self.individual2, queryset)

    def test_rule_filter_pdu_boolean_true(self) -> None:
        payment_plan = PaymentPlanFactory(program_cycle=self.program_cycle, created_by=self.user)
        tcr = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)
        individuals_filters_block = TargetingIndividualRuleFilterBlock.objects.create(
            targeting_criteria_rule=tcr, target_only_hoh=False
        )
        rule_filter = TargetingIndividualBlockRuleFilter(
            individuals_filters_block=individuals_filters_block,
            comparison_method="EQUALS",
            field_name=self.pdu_field_boolean.name,
            arguments=[True],
            round_number=1,
            flex_field_classification=FlexFieldClassification.FLEX_FIELD_PDU,
        )
        query = rule_filter.get_query()

        queryset = self.get_individuals_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 2)
        self.assertIn(self.individual1, queryset)
        self.assertIn(self.individual2, queryset)

    def test_rule_filter_pdu_boolean_false(self) -> None:
        payment_plan = PaymentPlanFactory(program_cycle=self.program_cycle, created_by=self.user)
        tcr = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)
        individuals_filters_block = TargetingIndividualRuleFilterBlock.objects.create(
            targeting_criteria_rule=tcr, target_only_hoh=False
        )
        rule_filter = TargetingIndividualBlockRuleFilter(
            individuals_filters_block=individuals_filters_block,
            comparison_method="EQUALS",
            field_name=self.pdu_field_boolean.name,
            arguments=[False],
            round_number=1,
            flex_field_classification=FlexFieldClassification.FLEX_FIELD_PDU,
        )
        query = rule_filter.get_query()

        queryset = self.get_individuals_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 1)
        self.assertIn(self.individual4, queryset)

    def test_rule_filter_pdu_boolean_is_null(self) -> None:
        payment_plan = PaymentPlanFactory(program_cycle=self.program_cycle, created_by=self.user)
        tcr = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)
        individuals_filters_block = TargetingIndividualRuleFilterBlock.objects.create(
            targeting_criteria_rule=tcr, target_only_hoh=False
        )
        rule_filter = TargetingIndividualBlockRuleFilter(
            individuals_filters_block=individuals_filters_block,
            comparison_method="IS_NULL",
            field_name=self.pdu_field_boolean.name,
            arguments=[None],
            round_number=1,
            flex_field_classification=FlexFieldClassification.FLEX_FIELD_PDU,
        )
        query = rule_filter.get_query()

        queryset = self.get_individuals_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 1)
        self.assertIn(self.individual3, queryset)
