from typing import Dict, List

from django.core.management import call_command

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import (
    create_household,
    create_household_and_individuals,
)
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.targeting.models import (
    TargetingCriteria,
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
    TargetingIndividualBlockRuleFilter,
    TargetingIndividualRuleFilterBlock,
    TargetPopulation,
)


class TestTargetingCriteriaQuery(APITestCase):
    @staticmethod
    def get_targeting_criteria_for_rule(rule_filter: Dict) -> TargetingCriteria:
        targeting_criteria = TargetingCriteria()
        targeting_criteria.save()
        rule = TargetingCriteriaRule(targeting_criteria=targeting_criteria)
        rule.save()
        rule_filter = TargetingCriteriaRuleFilter(**rule_filter, targeting_criteria_rule=rule)
        rule_filter.save()
        return targeting_criteria

    @classmethod
    def setUpTestData(cls) -> None:
        call_command("loadflexfieldsattributes")
        create_afghanistan()
        cls.user = UserFactory.create()
        cls.business_area = BusinessArea.objects.first()

        (household, individuals) = create_household(
            {"size": 1, "residence_status": "HOST", "business_area": cls.business_area},
        )
        (household, individuals) = create_household(
            {"size": 2, "residence_status": "REFUGEE", "business_area": cls.business_area},
        )

        assert Household.objects.all().distinct().count() == 2

    @classmethod
    def create_criteria(cls, *args, **kwargs):
        criteria = cls.get_targeting_criteria_for_rule(*args, **kwargs)
        TargetPopulation(
            name="tp",
            created_by=cls.user,
            business_area=cls.business_area,
            targeting_criteria=criteria,
        )
        criteria.save()
        return criteria

    def test_size(self) -> None:
        criteria = self.create_criteria(
            {
                "comparison_method": "EQUALS",
                "arguments": [2],
                "field_name": "size",
                "is_flex_field": False,
            }
        )
        assert Household.objects.filter(criteria.get_query()).distinct().count() == 1

    def test_residence_status(self) -> None:
        criteria = self.create_criteria(
            {
                "comparison_method": "EQUALS",
                "arguments": ["REFUGEE"],
                "field_name": "residence_status",
                "is_flex_field": False,
            }
        )
        assert Household.objects.filter(criteria.get_query()).distinct().count() == 1

    def test_flex_field_variables(self):
        criteria = self.create_criteria(
            {
                "comparison_method": "EQUALS",
                "arguments": ["0"],
                "field_name": "unaccompanied_child_h_f",
                "is_flex_field": True,
            }
        )
        assert Household.objects.filter(criteria.get_query()).distinct().count() == 0

    def test_select_many_variables(self):
        criteria = self.create_criteria(
            {
                "comparison_method": "CONTAINS",
                "arguments": ["other_public", "pharmacy", "other_private"],
                "field_name": "treatment_facility_h_f",
                "is_flex_field": True,
            }
        )
        assert Household.objects.filter(criteria.get_query()).distinct().count() == 0


class TestTargetingCriteriaIndividualRules(APITestCase):
    @staticmethod
    def get_targeting_criteria_for_filters(filters: List[Dict]) -> TargetingCriteria:
        targeting_criteria = TargetingCriteria()
        targeting_criteria.save()
        rule = TargetingCriteriaRule(targeting_criteria=targeting_criteria)
        rule.save()
        filter_block = TargetingIndividualRuleFilterBlock(targeting_criteria_rule=rule)
        filter_block.save()
        for filter in filters:
            print("Creating filter", filter)
            block_filter = TargetingIndividualBlockRuleFilter(**filter, individuals_filters_block=filter_block)
            block_filter.save()
        return targeting_criteria

    @classmethod
    def create_criteria(cls, *args, **kwargs):
        criteria = cls.get_targeting_criteria_for_filters(*args, **kwargs)
        TargetPopulation(
            name="tp",
            created_by=cls.user,
            business_area=cls.business_area,
            targeting_criteria=criteria,
        )
        criteria.save()
        return criteria

    @classmethod
    def setUpTestData(cls) -> None:
        call_command("loadflexfieldsattributes")
        create_afghanistan()
        cls.user = UserFactory.create()
        cls.business_area = BusinessArea.objects.first()

        (household, individuals) = create_household_and_individuals(
            {"business_area": cls.business_area},
            [
                {
                    "sex": "MALE",
                    "marital_status": "MARRIED",
                    "observed_disability": ["SEEING", "HEARING", "WALKING", "MEMORY", "SELF_CARE", "COMMUNICATING"],
                    "seeing_disability": "LOT_DIFFICULTY",
                    "hearing_disability": "SOME_DIFFICULTY",
                    "physical_disability": "SOME_DIFFICULTY",
                    "memory_disability": "LOT_DIFFICULTY",
                    "selfcare_disability": "CANNOT_DO",
                    "comms_disability": "SOME_DIFFICULTY",
                    "business_area": cls.business_area,
                },
            ],
        )
        (household, individuals) = create_household_and_individuals(
            {"business_area": cls.business_area},
            [
                {
                    "sex": "MALE",
                    "marital_status": "SINGLE",
                    "business_area": cls.business_area,
                },
                {
                    "sex": "FEMALE",
                    "marital_status": "MARRIED",
                    "business_area": cls.business_area,
                },
            ],
        )

        assert Household.objects.all().distinct().count() == 2

    def test_marital_status(self) -> None:
        # TODO
        # 2 households, one with married only, one with married and single
        # choosing 2 comparisons - married and single (AND)
        # only 1 matches both
        criteria = self.create_criteria(
            [
                {
                    "comparison_method": "EQUALS",
                    "arguments": ["MARRIED"],
                    "field_name": "marital_status",
                    "is_flex_field": False,
                },
                {
                    "comparison_method": "EQUALS",
                    "arguments": ["SINGLE"],
                    "field_name": "marital_status",
                    "is_flex_field": False,
                },
            ]
        )
        print(criteria.get_query())
        print(Household.objects.filter(criteria.get_query()).distinct())
        assert Household.objects.filter(criteria.get_query()).distinct().count() == 2
