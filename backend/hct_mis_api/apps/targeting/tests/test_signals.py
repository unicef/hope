from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from household.fixtures import HouseholdFactory, IndividualFactory, create_household
from targeting.models import (
    TargetingCriteria,
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
    TargetPopulation,
)


class TestTargetPopulationQuery(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.households = []
        (household, individuals) = create_household(
            {"size": 1, "residence_status": "CITIZEN", },
        )
        cls.household_size_1_citizen = household
        (household, individuals) = create_household(
            {"size": 1, "residence_status": "CITIZEN", },
        )
        household = household
        cls.households.append(household)


        (household, individuals) = create_household(
            {"size": 1, "residence_status": "IDP", },
        )
        cls.household_size_1 = household

        cls.households.append(cls.household_size_1)
        cls.household_residence_status_citizen = cls.household_size_1

        (household, individuals) = create_household(
            {"size": 2, "residence_status": "REFUGEE", },
        )

        cls.household_residence_status_refugee = household
        cls.households.append(cls.household_residence_status_refugee)
        cls.household_size_2 = cls.household_residence_status_refugee
        cls.user = UserFactory.create()

    @staticmethod
    def get_targeting_criteria_for_rule(rule_filter):
        targeting_criteria = TargetingCriteria()
        targeting_criteria.save()
        rule = TargetingCriteriaRule(targeting_criteria=targeting_criteria)
        rule.save()
        rule_filter = TargetingCriteriaRuleFilter(
            **rule_filter, targeting_criteria_rule=rule
        )
        rule_filter.save()
        return targeting_criteria

    def test_counts_for_draft(self):
        targeting_criteria = self.get_targeting_criteria_for_rule(
            {
                "field_name": "size",
                "arguments": [2],
                "comparision_method": "EQUALS",
            }
        )
        tp = TargetPopulation(
            name="target_population_size_2",
            created_by=self.user,
            candidate_list_targeting_criteria=targeting_criteria,
            status="DRAFT",
        )
        tp.save()

        tp.refresh_from_db()
        self.assertEqual(tp.candidate_list_total_households, 1)
        self.assertEqual(tp.candidate_list_total_individuals, 2)
        self.assertEqual(tp.final_list_total_households, None)
        self.assertEqual(tp.final_list_total_individuals, None)

    def test_counts_for_draft_changed_criteria(self):
        targeting_criteria = self.get_targeting_criteria_for_rule(
            {
                "field_name": "size",
                "arguments": [2],
                "comparision_method": "EQUALS",
            }
        )
        tp = TargetPopulation(
            name="target_population_size_2",
            created_by=self.user,
            candidate_list_targeting_criteria=targeting_criteria,
            status="DRAFT",
        )
        tp.save()

        tp.refresh_from_db()
        self.assertEqual(tp.candidate_list_total_households, 1)
        self.assertEqual(tp.candidate_list_total_individuals, 2)

        filter = targeting_criteria.rules.first().filters.first()
        filter.arguments = [1]
        filter.save()
        tp.refresh_from_db()
        self.assertEqual(tp.candidate_list_total_households, 3)
        self.assertEqual(tp.candidate_list_total_individuals, 3)

    def test_counts_for_approved(self):
        tp = TargetPopulation(
            name="target_population_size_2",
            created_by=self.user,
            status="APPROVED",
        )
        tp.save()
        tp.households.add(self.household_size_2)
        tp.refresh_from_db()
        self.assertEqual(tp.candidate_list_total_households, 1)
        self.assertEqual(tp.candidate_list_total_individuals, 2)
        self.assertEqual(tp.final_list_total_households, 1)
        self.assertEqual(tp.final_list_total_individuals, 2)

    def test_counts_for_approved_with_additional_rules(self):
        targeting_criteria = self.get_targeting_criteria_for_rule(
            {
                "field_name": "size",
                "arguments": [1],
                "comparision_method": "EQUALS",
            }
        )
        tp = TargetPopulation(
            name="target_population_size_2",
            created_by=self.user,
            status="APPROVED",
            candidate_list_targeting_criteria=targeting_criteria,
        )
        tp.save()
        tp.households.add(self.household_size_1)
        tp.households.add(self.household_size_1_citizen)
        tp.refresh_from_db()
        self.assertEqual(tp.candidate_list_total_households, 2)
        self.assertEqual(tp.candidate_list_total_individuals, 2)
        self.assertEqual(tp.final_list_total_households, 2)
        self.assertEqual(tp.final_list_total_individuals, 2)

        targeting_criteria = self.get_targeting_criteria_for_rule(
            {
                "field_name": "residence_status",
                "arguments": ["CITIZEN"],
                "comparision_method": "EQUALS",
            }
        )
        tp.final_list_targeting_criteria = targeting_criteria
        tp.save()
        tp.refresh_from_db()
        self.assertEqual(tp.candidate_list_total_households, 2)
        self.assertEqual(tp.candidate_list_total_individuals, 2)
        self.assertEqual(tp.final_list_total_households, 1)
        self.assertEqual(tp.final_list_total_individuals, 1)
        idp_filter = TargetingCriteriaRuleFilter(
            **{
                "field_name": "residence_status",
                "arguments": ["IDP"],
                "comparision_method": "EQUALS",
                "targeting_criteria_rule": tp.final_list_targeting_criteria.rules.first(),
            }
        )
        idp_filter.save()
        tp.refresh_from_db()
        self.assertEqual(tp.candidate_list_total_households, 2)
        self.assertEqual(tp.candidate_list_total_individuals, 2)
        self.assertEqual(tp.final_list_total_households, 0)
        self.assertEqual(tp.final_list_total_individuals, None)

    def test_counts_for_finalized(self):
        tp = TargetPopulation(
            name="target_population_size_2",
            created_by=self.user,
            status="FINALIZED",
        )
        tp.save()
        tp.households.add(self.household_size_2)
        tp.refresh_from_db()
        self.assertEqual(tp.candidate_list_total_households, 1)
        self.assertEqual(tp.candidate_list_total_individuals, 2)
        self.assertEqual(tp.final_list_total_households, 1)
        self.assertEqual(tp.final_list_total_individuals, 2)
        tp.final_list_targeting_criteria = self.get_targeting_criteria_for_rule(
            {
                "field_name": "residence_status",
                "arguments": ["IDP"],
                "comparision_method": "EQUALS",
            }
        )
        tp.save()
        tp.refresh_from_db()
        self.assertEqual(tp.candidate_list_total_households, 1)
        self.assertEqual(tp.candidate_list_total_individuals, 2)
        self.assertEqual(tp.final_list_total_households, 1)
        self.assertEqual(tp.final_list_total_individuals, 2)
