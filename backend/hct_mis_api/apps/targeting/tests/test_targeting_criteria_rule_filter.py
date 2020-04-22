from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase

from household.fixtures import HouseholdFactory, IndividualFactory
from household.models import Household
from targeting.models import TargetingCriteriaRuleFilter


class TargetingCriteriaRuleFilterTestCase(TestCase):
    def setUp(self):
        households = []
        households.append(
            HouseholdFactory(size=1, residence_status="CITIZEN",)
        )
        IndividualFactory(
            household=households[-1],
            **{"dob": "1970-11-29", "years_in_school": 1,}
        )
        self.household_50_yo = households[-1]
        households.append(
            HouseholdFactory(size=1, residence_status="CITIZEN",)
        )
        IndividualFactory(
            household=households[-1],
            **{"dob": "1991-11-18", "years_in_school": 2,}
        )
        households.append(
            HouseholdFactory(size=1, residence_status="CITIZEN",)
        )
        IndividualFactory(
            household=households[-1],
            **{"dob": "1991-11-18", "years_in_school": 2,}
        )
        households.append(
            HouseholdFactory(size=2, residence_status="REFUGEE",)
        )
        self.household_size_2 = households[-1]
        self.household_refugee = households[-1]
        self.household_years_in_school_4 = households[-1]
        IndividualFactory(
            household=households[-1],
            **{"dob": "1991-11-18", "years_in_school": 2,}
        )
        IndividualFactory(
            household=households[-1],
            **{"dob": "1991-11-18", "years_in_school": 4,}
        )

        self.households = households

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
            comparision_method="EQUALS", field_name="size", arguments=[],
        )
        try:
            rule_filter.get_query()
            self.assertTrue(False)
        except ValidationError:
            self.assertTrue(True)

        rule_filter = TargetingCriteriaRuleFilter(
            comparision_method="EQUALS", field_name="size",
        )
        try:
            rule_filter.get_query()
            self.assertTrue(False)
        except ValidationError:
            self.assertTrue(True)

    def test_rule_filter_age_equal(self):
        rule_filter = TargetingCriteriaRuleFilter(
            comparision_method="EQUALS", field_name="age", arguments=[50]
        )
        query = rule_filter.get_query()
        queryset = self.get_households_queryset().filter(query)
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(self.household_50_yo.pk, queryset[0].pk)

    def test_rule_filter_age_not_equal(self):
        rule_filter = TargetingCriteriaRuleFilter(
            comparision_method="NOT_EQUALS", field_name="age", arguments=[50]
        )
        query = rule_filter.get_query()
        queryset = self.get_households_queryset().filter(query)
        self.assertEqual(queryset.count(), 3)
        self.assertTrue(self.household_50_yo.pk not in [h.pk for h in queryset])

    def test_rule_filter_age_range_1_49(self):
        rule_filter = TargetingCriteriaRuleFilter(
            comparision_method="RANGE", field_name="age", arguments=[1, 49]
        )
        query = rule_filter.get_query()
        queryset = self.get_households_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 3)
        self.assertTrue(self.household_50_yo.pk not in [h.pk for h in queryset])

    def test_rule_filter_age_range_1_50(self):
        rule_filter = TargetingCriteriaRuleFilter(
            comparision_method="RANGE", field_name="age", arguments=[1, 50]
        )
        query = rule_filter.get_query()
        queryset = self.get_households_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 4)
        self.assertTrue(self.household_50_yo.pk in [h.pk for h in queryset])

    def test_rule_filter_age_gt_40(self):
        rule_filter = TargetingCriteriaRuleFilter(
            comparision_method="GREATER_THAN", field_name="age", arguments=[40]
        )
        query = rule_filter.get_query()
        queryset = self.get_households_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 1)
        self.assertTrue(self.household_50_yo.pk in [h.pk for h in queryset])

    def test_rule_filter_age_lt_40(self):
        rule_filter = TargetingCriteriaRuleFilter(
            comparision_method="LESS_THAN", field_name="age", arguments=[40]
        )
        query = rule_filter.get_query()
        queryset = self.get_households_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 3)
        self.assertTrue(self.household_50_yo.pk not in [h.pk for h in queryset])

    def test_rule_filter_size_equals(self):
        rule_filter = TargetingCriteriaRuleFilter(
            comparision_method="EQUALS", field_name="size", arguments=[2]
        )
        query = rule_filter.get_query()
        queryset = self.get_households_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 1)
        self.assertTrue(
            self.household_size_2.pk in [h.pk for h in queryset]
        )

    def test_rule_filter_size_not_equals(self):
        rule_filter = TargetingCriteriaRuleFilter(
            comparision_method="NOT_EQUALS",
            field_name="size",
            arguments=[2],
        )
        query = rule_filter.get_query()
        queryset = self.get_households_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 3)
        self.assertTrue(
            self.household_size_2.pk not in [h.pk for h in queryset]
        )

    def test_rule_filter_size_in_range_0_1(self):
        rule_filter = TargetingCriteriaRuleFilter(
            comparision_method="RANGE",
            field_name="size",
            arguments=[0, 1],
        )
        query = rule_filter.get_query()
        queryset = self.get_households_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 3)
        self.assertTrue(
            self.household_size_2.pk not in [h.pk for h in queryset]
        )

    def test_rule_filter_size_not_in_range_0_1(self):
        rule_filter = TargetingCriteriaRuleFilter(
            comparision_method="NOT_IN_RANGE",
            field_name="size",
            arguments=[0, 1],
        )
        query = rule_filter.get_query()
        queryset = self.get_households_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 1)
        self.assertTrue(
            self.household_size_2.pk in [h.pk for h in queryset]
        )

    def test_rule_filter_size_gt_1(self):
        rule_filter = TargetingCriteriaRuleFilter(
            comparision_method="GREATER_THAN",
            field_name="size",
            arguments=[1],
        )
        query = rule_filter.get_query()
        queryset = self.get_households_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 1)
        self.assertTrue(
            self.household_size_2.pk in [h.pk for h in queryset]
        )

    def test_rule_filter_size_lt_2(self):
        rule_filter = TargetingCriteriaRuleFilter(
            comparision_method="LESS_THAN",
            field_name="size",
            arguments=[2],
        )
        query = rule_filter.get_query()
        queryset = self.get_households_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 3)
        self.assertTrue(
            self.household_size_2.pk not in [h.pk for h in queryset]
        )

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
        self.assertTrue(
            self.household_refugee.pk not in [h.pk for h in queryset]
        )

    def test_rule_filter_years_in_school_equals(self):
        rule_filter = TargetingCriteriaRuleFilter(
            comparision_method="EQUALS",
            field_name="years_in_school",
            arguments=[4],
        )
        query = rule_filter.get_query()
        queryset = self.get_households_queryset().filter(query).distinct()
        self.assertEqual(queryset.count(), 1)
        self.assertTrue(
            self.household_years_in_school_4.pk in [h.pk for h in queryset]
        )


class TargetingCriteriaFlexRuleFilterTestCase(TestCase):
    def setUp(self):
        call_command("loadflexfieldsattributes")
        self.household_total_households_2 = HouseholdFactory(
            size=1,
            flex_fields={
                "total_households_h_f": 2,
                "treatment_facility_h_f": [
                    "governent_health_center",
                    "other_public",
                    "private_doctor",
                ],
            },
        )
        IndividualFactory(household=self.household_total_households_2,)
        self.household_total_households_4 = HouseholdFactory(
            size=1,
            flex_fields={
                "total_households_h_f": 4,
                "treatment_facility_h_f": [
                    "governent_health_center",
                    "other_public",
                ],
            },
        )
        IndividualFactory(household=self.household_total_households_4,)
        HouseholdFactory(
            size=1, flex_fields={"ddd": 3, "treatment_facility_h_f": []},
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
            arguments=["other_public", "private_doctor",],
            is_flex_field=True,
        )
        query = rule_filter.get_query()
        queryset = Household.objects.filter(query)
        self.assertEqual(queryset.count(), 1)

    def test_rule_filter_select_multiple_treatment_facility_2(self):
        rule_filter = TargetingCriteriaRuleFilter(
            comparision_method="CONTAINS",
            field_name="treatment_facility_h_f",
            arguments=["other_public", "governent_health_center",],
            is_flex_field=True,
        )
        query = rule_filter.get_query()
        queryset = Household.objects.filter(query)
        self.assertEqual(queryset.count(), 2)

    def test_rule_filter_select_multiple_treatment_facility_not_contains(self):
        rule_filter = TargetingCriteriaRuleFilter(
            comparision_method="NOT_CONTAINS",
            field_name="treatment_facility_h_f",
            arguments=["other_public", "governent_health_center",],
            is_flex_field=True,
        )
        query = rule_filter.get_query()
        queryset = Household.objects.filter(query)
        self.assertEqual(queryset.count(), 1)

