from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase

from freezegun import freeze_time

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import (
    create_household,
    create_household_and_individuals,
)
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.targeting.models import (
    TargetingCriteriaRuleFilter,
    TargetingIndividualBlockRuleFilter,
)


class TargetingCriteriaRuleFilterTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        households = []
        create_afghanistan()
        business_area = BusinessArea.objects.first()
        (household, individuals) = create_household_and_individuals(
            {
                "size": 1,
                "residence_status": "HOST",
                "business_area": business_area,
                "first_registration_date": "1900-01-01",
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
                "first_registration_date": "1900-01-01",
            },
            [{"birth_date": "1991-11-18"}],
        )
        households.append(household)
        (household, individuals) = create_household_and_individuals(
            {
                "size": 1,
                "residence_status": "HOST",
                "business_area": business_area,
                "first_registration_date": "2100-01-01",
            },
            [{"birth_date": "1991-11-18"}],
        )

        households.append(household)

        (household, individuals) = create_household_and_individuals(
            {
                "size": 2,
                "residence_status": "REFUGEE",
                "business_area": business_area,
                "first_registration_date": "1900-01-01",
            },
            [{"birth_date": "1991-11-18"}],
        )

        households.append(household)
        cls.household_size_2 = household
        cls.household_refugee = household

        cls.households = households

    def get_households_queryset(self):
        return Household.objects.filter(pk__in=[h.pk for h in self.households])

    def test_wrong_arguments_count_validation(self):
        rule_filter = TargetingCriteriaRuleFilter(
            comparision_method="EQUALS",
            field_name="size",
            arguments=[2, 1],
        )
        try:
            rule_filter.get_query()
            self.assertTrue(False)
        except ValidationError:
            self.assertTrue(True)

        rule_filter = TargetingCriteriaRuleFilter(
            comparision_method="EQUALS",
            field_name="size",
            arguments=[],
        )
        try:
            rule_filter.get_query()
            self.assertTrue(False)
        except ValidationError:
            self.assertTrue(True)

        rule_filter = TargetingCriteriaRuleFilter(
            comparision_method="EQUALS",
            field_name="size",
        )
        try:
            rule_filter.get_query()
            self.assertTrue(False)
        except ValidationError:
            self.assertTrue(True)

    @freeze_time("2020-10-10")
    def test_rule_filter_age_equal(self):
        rule_filter = TargetingIndividualBlockRuleFilter(comparision_method="EQUALS", field_name="age", arguments=[50])
        query = rule_filter.get_query()
        queryset = Individual.objects.filter(query)
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(self.household_50_yo.pk, queryset[0].household.pk)

    @freeze_time("2020-10-10")
    def test_rule_filter_age_not_equal(self):
        rule_filter = TargetingIndividualBlockRuleFilter(
            comparision_method="NOT_EQUALS", field_name="age", arguments=[50]
        )
        query = rule_filter.get_query()
        queryset = Individual.objects.filter(query)
        self.assertEqual(queryset.count(), 3)
        self.assertTrue(self.household_50_yo.pk not in [h.household.pk for h in queryset])

    @freeze_time("2020-10-10")
    def test_rule_filter_age_range_1_49(self):
        rule_filter = TargetingIndividualBlockRuleFilter(
            comparision_method="RANGE", field_name="age", arguments=[1, 49]
        )
        query = rule_filter.get_query()
        queryset = Individual.objects.filter(query).distinct()
        self.assertEqual(queryset.count(), 3)
        self.assertTrue(self.household_50_yo.pk not in [h.household.pk for h in queryset])

    @freeze_time("2020-10-10")
    def test_rule_filter_age_range_1_50(self):
        rule_filter = TargetingIndividualBlockRuleFilter(
            comparision_method="RANGE", field_name="age", arguments=[1, 50]
        )
        query = rule_filter.get_query()
        queryset = Individual.objects.filter(query).distinct()
        self.assertEqual(queryset.count(), 4)
        self.assertTrue(self.household_50_yo.pk in [h.household.pk for h in queryset])

    @freeze_time("2020-10-10")
    def test_rule_filter_age_gt_40(self):
        rule_filter = TargetingIndividualBlockRuleFilter(
            comparision_method="GREATER_THAN", field_name="age", arguments=[40]
        )
        query = rule_filter.get_query()
        queryset = Individual.objects.filter(query).distinct()
        self.assertEqual(queryset.count(), 1)
        self.assertTrue(self.household_50_yo.pk in [h.household.pk for h in queryset])

    @freeze_time("2020-10-10")
    def test_rule_filter_age_lt_40(self):
        rule_filter = TargetingIndividualBlockRuleFilter(
            comparision_method="LESS_THAN", field_name="age", arguments=[40]
        )
        query = rule_filter.get_query()
        queryset = Individual.objects.filter(query).distinct()
        self.assertEqual(queryset.count(), 3)
        self.assertTrue(self.household_50_yo.pk not in [h.household.pk for h in queryset])

    @freeze_time("2020-09-28")
    def test_rule_filter_age_lt_49_should_contains_person_born_in_proper_year_before_birthday(self):
        rule_filter = TargetingIndividualBlockRuleFilter(
            comparision_method="LESS_THAN", field_name="age", arguments=[49]
        )
        query = rule_filter.get_query()
        queryset = Individual.objects.filter(query).distinct()
        self.assertEqual(queryset.count(), 4)
        self.assertTrue(self.household_50_yo.pk in [h.household.pk for h in queryset])

    @freeze_time("2020-09-29")
    def test_rule_filter_age_lt_49_shouldn_t_contains_person_born_in_proper_year_after_and_during_birthday(self):
        rule_filter = TargetingIndividualBlockRuleFilter(
            comparision_method="LESS_THAN", field_name="age", arguments=[49]
        )
        query = rule_filter.get_query()
        queryset = Individual.objects.filter(query).distinct()
        self.assertEqual(queryset.count(), 3)
        self.assertTrue(self.household_50_yo.pk not in [h.household.pk for h in queryset])

    def test_rule_filter_size_equals(self):
        rule_filter = TargetingCriteriaRuleFilter(comparision_method="EQUALS", field_name="size", arguments=[2])
        query = rule_filter.get_query()
        queryset = self.get_households_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 1)
        self.assertTrue(self.household_size_2.pk in [h.pk for h in queryset])

    def test_rule_filter_size_not_equals(self):
        rule_filter = TargetingCriteriaRuleFilter(
            comparision_method="NOT_EQUALS",
            field_name="size",
            arguments=[2],
        )
        query = rule_filter.get_query()
        queryset = self.get_households_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 3)
        self.assertTrue(self.household_size_2.pk not in [h.pk for h in queryset])

    def test_rule_filter_size_in_range_0_1(self):
        rule_filter = TargetingCriteriaRuleFilter(
            comparision_method="RANGE",
            field_name="size",
            arguments=[0, 1],
        )
        query = rule_filter.get_query()
        queryset = self.get_households_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 3)
        self.assertTrue(self.household_size_2.pk not in [h.pk for h in queryset])

    def test_rule_filter_size_not_in_range_0_1(self):
        rule_filter = TargetingCriteriaRuleFilter(
            comparision_method="NOT_IN_RANGE",
            field_name="size",
            arguments=[0, 1],
        )
        query = rule_filter.get_query()
        queryset = self.get_households_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 1)
        self.assertTrue(self.household_size_2.pk in [h.pk for h in queryset])

    def test_rule_filter_size_gte_2(self):
        rule_filter = TargetingCriteriaRuleFilter(
            comparision_method="GREATER_THAN",
            field_name="size",
            arguments=[2],
        )
        query = rule_filter.get_query()
        queryset = self.get_households_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 1)
        self.assertTrue(self.household_size_2.pk in [h.pk for h in queryset])

    def test_rule_filter_size_lte_1(self):
        rule_filter = TargetingCriteriaRuleFilter(
            comparision_method="LESS_THAN",
            field_name="size",
            arguments=[1],
        )
        query = rule_filter.get_query()
        queryset = self.get_households_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 3)
        self.assertTrue(self.household_size_2.pk not in [h.pk for h in queryset])

    def test_rule_filter_residence_status_equals(self):
        rule_filter = TargetingCriteriaRuleFilter(
            comparision_method="EQUALS",
            field_name="residence_status",
            arguments=["REFUGEE"],
        )
        query = rule_filter.get_query()
        queryset = self.get_households_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 1)
        self.assertTrue(self.household_refugee.pk in [h.pk for h in queryset])

    def test_rule_filter_residence_status_not_equals(self):
        rule_filter = TargetingCriteriaRuleFilter(
            comparision_method="NOT_EQUALS",
            field_name="residence_status",
            arguments=["REFUGEE"],
        )
        query = rule_filter.get_query()
        queryset = self.get_households_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 3)
        self.assertTrue(self.household_refugee.pk not in [h.pk for h in queryset])

    def test_rule_filter_registration_date_gte(self):
        rule_filter = TargetingCriteriaRuleFilter(
            comparision_method="GREATER_THAN",
            field_name="first_registration_date",
            arguments=["2000-01-01"],
        )
        query = rule_filter.get_query()
        queryset = self.get_households_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 1)


class TargetingCriteriaFlexRuleFilterTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("loadflexfieldsattributes")
        create_afghanistan()
        business_area = BusinessArea.objects.first()
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

    def test_rule_filter_household_total_households_4(self):
        rule_filter = TargetingCriteriaRuleFilter(
            comparision_method="EQUALS",
            field_name="total_households_h_f",
            arguments=[4],
            is_flex_field=True,
        )
        query = rule_filter.get_query()
        queryset = Household.objects.filter(query)
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(self.household_total_households_4.pk, queryset[0].pk)

    def test_rule_filter_select_multiple_treatment_facility(self):
        rule_filter = TargetingCriteriaRuleFilter(
            comparision_method="CONTAINS",
            field_name="treatment_facility_h_f",
            arguments=["other_public", "private_doctor"],
            is_flex_field=True,
        )
        query = rule_filter.get_query()
        queryset = Household.objects.filter(query)
        self.assertEqual(queryset.count(), 1)

    def test_rule_filter_select_multiple_treatment_facility_2(self):
        rule_filter = TargetingCriteriaRuleFilter(
            comparision_method="CONTAINS",
            field_name="treatment_facility_h_f",
            arguments=["other_public", "government_health_center"],
            is_flex_field=True,
        )
        query = rule_filter.get_query()
        queryset = Household.objects.filter(query)
        self.assertEqual(queryset.count(), 2)

    def test_rule_filter_select_multiple_treatment_facility_not_contains(self):
        rule_filter = TargetingCriteriaRuleFilter(
            comparision_method="NOT_CONTAINS",
            field_name="treatment_facility_h_f",
            arguments=["other_public", "government_health_center"],
            is_flex_field=True,
        )
        query = rule_filter.get_query()
        queryset = Household.objects.filter(query)
        self.assertEqual(queryset.count(), 1)

    def test_rule_filter_string_contains(self):
        rule_filter = TargetingCriteriaRuleFilter(
            comparision_method="CONTAINS",
            field_name="other_treatment_facility_h_f",
            arguments=["other"],
            is_flex_field=True,
        )
        query = rule_filter.get_query()
        queryset = Household.objects.filter(query)
        self.assertEqual(queryset.count(), 1)
