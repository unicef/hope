import copy

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.targeting.models import (
    TargetingCriteria,
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
    TargetPopulation,
)

MUTATION_QUERY = """
mutation UpdateTargetPopulation($updateTargetPopulationInput: UpdateTargetPopulationInput!) {
    updateTargetPopulation(input: $updateTargetPopulationInput) {
    targetPopulation{
        name
        status
        totalHouseholdsCount
        totalIndividualsCount
        targetingCriteria{
        rules{
            filters{
            comparisonMethod
            fieldName
            arguments
            isFlexField
            }
        }
        }
    }
    validationErrors
    }
}
"""
VARIABLES = {
    "updateTargetPopulationInput": {
        "targetingCriteria": {
            "rules": [
                {
                    "filters": [
                        {
                            "comparisonMethod": "EQUALS",
                            "fieldName": "size",
                            "arguments": [3],
                            "isFlexField": False,
                        }
                    ]
                }
            ]
        },
    }
}

VARIABLES_WRONG_ARGS_COUNT = {
    "updateTargetPopulationInput": {
        "targetingCriteria": {
            "rules": [
                {
                    "filters": [
                        {
                            "comparisonMethod": "EQUALS",
                            "fieldName": "size",
                            "arguments": [3, 3],
                            "isFlexField": False,
                        }
                    ]
                }
            ]
        },
    }
}
VARIABLES_WRONG_COMPARISON_METHOD = {
    "updateTargetPopulationInput": {
        "targetingCriteria": {
            "rules": [
                {
                    "filters": [
                        {
                            "comparisonMethod": "CONTAINS",
                            "fieldName": "size",
                            "arguments": [3],
                            "isFlexField": False,
                        }
                    ]
                }
            ]
        },
    }
}
VARIABLES_UNKNOWN_COMPARISON_METHOD = {
    "updateTargetPopulationInput": {
        "targetingCriteria": {
            "rules": [
                {
                    "filters": [
                        {
                            "comparisonMethod": "BLABLA",
                            "fieldName": "size",
                            "arguments": [3],
                            "isFlexField": False,
                        }
                    ]
                }
            ]
        },
    }
}
VARIABLES_UNKNOWN_FLEX_FIELD_NAME = {
    "updateTargetPopulationInput": {
        "targetingCriteria": {
            "rules": [
                {
                    "filters": [
                        {
                            "comparisonMethod": "EQUALS",
                            "fieldName": "foo_bar",
                            "arguments": [3],
                            "isFlexField": True,
                        }
                    ]
                }
            ]
        },
    }
}
VARIABLES_UNKNOWN_CORE_FIELD_NAME = {
    "updateTargetPopulationInput": {
        "targetingCriteria": {
            "rules": [
                {
                    "filters": [
                        {
                            "comparisonMethod": "EQUALS",
                            "fieldName": "foo_bar",
                            "arguments": [3],
                            "isFlexField": False,
                        }
                    ]
                }
            ]
        },
    }
}


class TestUpdateTargetPopulationMutation(APITestCase):
    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.user = UserFactory.create()
        create_household({"size": 2, "residence_status": "HOST", "business_area": cls.business_area})
        create_household({"size": 3, "residence_status": "HOST", "business_area": cls.business_area})
        create_household({"size": 3, "residence_status": "HOST", "business_area": cls.business_area})
        cls.draft_target_population = TargetPopulation(
            name="draft_target_population",
            targeting_criteria=cls.get_targeting_criteria_for_rule(
                {"field_name": "size", "arguments": [2], "comparison_method": "EQUALS"}
            ),
            created_by=cls.user,
            business_area=cls.business_area,
        )
        cls.draft_target_population.save()
        cls.approved_target_population = TargetPopulation(
            name="approved_target_population",
            targeting_criteria=cls.get_targeting_criteria_for_rule(
                {"field_name": "size", "arguments": [1], "comparison_method": "GREATER_THAN"}
            ),
            status="LOCKED",
            created_by=cls.user,
            business_area=cls.business_area,
        )
        cls.approved_target_population.save()
        cls.approved_target_population.households.set(Household.objects.all())
        cls.target_populations = [cls.draft_target_population, cls.approved_target_population]

    @staticmethod
    def get_targeting_criteria_for_rule(rule_filter):
        targeting_criteria = TargetingCriteria()
        targeting_criteria.save()
        rule = TargetingCriteriaRule(targeting_criteria=targeting_criteria)
        rule.save()
        rule_filter = TargetingCriteriaRuleFilter(**rule_filter, targeting_criteria_rule=rule)
        rule_filter.save()
        return targeting_criteria

    @parameterized.expand(
        [
            ("with_permission_draft", [Permissions.TARGETING_UPDATE], 0, True),
            ("without_permission_draft", [], 0, False),
            ("with_permission_approved", [Permissions.TARGETING_UPDATE], 1, False),
            ("without_permission_approved", [], 1, False),
        ]
    )
    def test_update_mutation_correct_variables(self, name, permissions, population_index, should_be_updated):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        variables = copy.deepcopy(VARIABLES)
        variables["updateTargetPopulationInput"]["id"] = self.id_to_base64(
            self.target_populations[population_index].id, "TargetPopulationNode"
        )
        variables["updateTargetPopulationInput"]["name"] = f"{name} updated"

        self.snapshot_graphql_request(
            request_string=MUTATION_QUERY,
            context={"user": self.user},
            variables=variables,
        )
        updated_target_population = TargetPopulation.objects.get(id=self.target_populations[population_index].id)
        if should_be_updated:
            assert "updated" in updated_target_population.name
        else:
            assert "updated" not in updated_target_population.name

    @parameterized.expand(
        [
            ("wrong_args_count", VARIABLES_WRONG_ARGS_COUNT),
            ("wrong_comparison_method", VARIABLES_WRONG_COMPARISON_METHOD),
            ("unknown_comparison_method", VARIABLES_UNKNOWN_COMPARISON_METHOD),
            ("unknown_flex_field_name", VARIABLES_UNKNOWN_FLEX_FIELD_NAME),
            ("unknown_core_field_name", VARIABLES_UNKNOWN_CORE_FIELD_NAME),
        ]
    )
    def test_fail_update(self, _, variables):
        self.create_user_role_with_permissions(self.user, [Permissions.TARGETING_UPDATE], self.business_area)

        variables = copy.deepcopy(variables)
        variables["updateTargetPopulationInput"]["id"] = self.id_to_base64(
            self.draft_target_population.id, "TargetPopulationNode"
        )
        variables["updateTargetPopulationInput"]["name"] = "draft_target_population wrong"

        self.snapshot_graphql_request(
            request_string=MUTATION_QUERY,
            context={"user": self.user},
            variables=variables,
        )
        updated_target_population = TargetPopulation.objects.get(id=self.draft_target_population.id)

        assert "wrong" not in updated_target_population.name
