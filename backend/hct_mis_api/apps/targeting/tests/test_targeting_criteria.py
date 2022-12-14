from typing import Any, Dict, List

from django.core.management import call_command

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.targeting.models import (
    TargetingCriteria,
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
    TargetPopulation,
)
from hct_mis_api.apps.household.models import Household


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
    def create_criteria_with_tp(cls, *args, **kwargs):
        criteria = cls.get_targeting_criteria_for_rule(*args, **kwargs)
        TargetPopulation(
            name="tp",
            created_by=cls.user,
            business_area=cls.business_area,
            targeting_criteria=criteria,
        )
        return criteria

    def test_size(self) -> None:
        criteria = self.create_criteria_with_tp(
            {
                "comparison_method": "EQUALS",
                "arguments": [2],
                "field_name": "size",
                "is_flex_field": False,
            }
        )
        assert Household.objects.filter(criteria.get_query()).distinct().count() == 1

    def test_residence_status(self) -> None:
        criteria = self.create_criteria_with_tp(
            {
                "comparison_method": "EQUALS",
                "arguments": ["REFUGEE"],
                "field_name": "residence_status",
                "is_flex_field": False,
            }
        )
        assert Household.objects.filter(criteria.get_query()).distinct().count() == 1

    def test_flex_field_variables(self):
        criteria = self.create_criteria_with_tp(
            {
                "comparison_method": "EQUALS",
                "arguments": ["0"],
                "field_name": "unaccompanied_child_h_f",
                "is_flex_field": True,
            }
        )
        assert Household.objects.filter(criteria.get_query()).distinct().count() == 0

    def test_select_many_variables(self):
        criteria = self.create_criteria_with_tp(
            {
                "comparison_method": "CONTAINS",
                "arguments": ["other_public", "pharmacy", "other_private"],
                "field_name": "treatment_facility_h_f",
                "is_flex_field": True,
            }
        )
        assert Household.objects.filter(criteria.get_query()).distinct().count() == 0
