import copy
from typing import Any, Dict, List

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
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
            flagExcludeIfActiveAdjudicationTicket
            flagExcludeIfOnSanctionList
            rules{
                filters{
                    comparisonMethod
                    fieldName
                    arguments
                    flexFieldClassification
                }
            }
        }
    }
    validationErrors
    }
}
"""
VARIABLES: Dict = {
    "updateTargetPopulationInput": {
        "targetingCriteria": {
            "flagExcludeIfOnSanctionList": True,
            "rules": [
                {
                    "filters": [
                        {
                            "comparisonMethod": "EQUALS",
                            "fieldName": "size",
                            "arguments": [3],
                            "flexFieldClassification": "NOT_FLEX_FIELD",
                        }
                    ]
                }
            ],
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
                            "flexFieldClassification": "NOT_FLEX_FIELD",
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
                            "flexFieldClassification": "NOT_FLEX_FIELD",
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
                            "flexFieldClassification": "NOT_FLEX_FIELD",
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
                            "flexFieldClassification": "FLEX_FIELD_BASIC",
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
                            "flexFieldClassification": "NOT_FLEX_FIELD",
                        }
                    ]
                }
            ]
        },
    }
}


class TestUpdateTargetPopulationMutation(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        partner = PartnerFactory(name="Partner")
        cls.user = UserFactory.create(partner=partner)
        create_household({"size": 2, "residence_status": "HOST", "business_area": cls.business_area})
        create_household({"size": 3, "residence_status": "HOST", "business_area": cls.business_area})
        create_household({"size": 3, "residence_status": "HOST", "business_area": cls.business_area})
        cls.program = ProgramFactory(status=Program.ACTIVE, business_area=cls.business_area)
        cls.update_partner_access_to_program(partner, cls.program)
        cls.draft_target_population = TargetPopulation(
            name="draft_target_population",
            targeting_criteria=cls.get_targeting_criteria_for_rule(
                {"field_name": "size", "arguments": [2], "comparison_method": "EQUALS"}
            ),
            created_by=cls.user,
            business_area=cls.business_area,
            program=cls.program,
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
            program=cls.program,
        )
        cls.approved_target_population.save()
        cls.approved_target_population.households.set(Household.objects.all())
        cls.target_populations = [cls.draft_target_population, cls.approved_target_population]

    @staticmethod
    def get_targeting_criteria_for_rule(rule_filter: Dict) -> TargetingCriteria:
        # TODO: this function is copy-pasted in many places
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
    def test_update_mutation_correct_variables(
        self, name: str, permissions: List[Permissions], population_index: int, should_be_updated: bool
    ) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        variables: Dict = copy.deepcopy(VARIABLES)
        variables["updateTargetPopulationInput"]["id"] = self.id_to_base64(
            self.target_populations[population_index].id, "TargetPopulationNode"
        )
        variables["updateTargetPopulationInput"]["name"] = f"{name} updated"

        self.snapshot_graphql_request(
            request_string=MUTATION_QUERY,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
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
    def test_fail_update(self, _: Any, variables: Dict) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.TARGETING_UPDATE], self.business_area)

        variables = copy.deepcopy(variables)
        variables["updateTargetPopulationInput"]["id"] = self.id_to_base64(
            self.draft_target_population.id, "TargetPopulationNode"
        )
        variables["updateTargetPopulationInput"]["name"] = "draft_target_population wrong"

        self.snapshot_graphql_request(
            request_string=MUTATION_QUERY,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables=variables,
        )
        updated_target_population = TargetPopulation.objects.get(id=self.draft_target_population.id)

        assert "wrong" not in updated_target_population.name

    def test_update_name_unique_constraint(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.TARGETING_UPDATE], self.business_area)
        variables = copy.deepcopy(VARIABLES)
        variables["updateTargetPopulationInput"]["id"] = self.id_to_base64(
            self.draft_target_population.id, "TargetPopulationNode"
        )
        variables["updateTargetPopulationInput"]["name"] = self.approved_target_population.name

        response_error = self.graphql_request(
            request_string=MUTATION_QUERY,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables=variables,
        )
        assert "errors" in response_error
        self.assertIn(
            f"Target population with name: {variables['updateTargetPopulationInput']['name']} and program: {self.program.name} already exists.",
            response_error["errors"][0]["message"],
        )

    def test_fail_update_for_incorrect_status(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.TARGETING_UPDATE], self.business_area)
        target_population_with_incorrect_status = TargetPopulation(
            name="target_population_with_incorrect_status",
            targeting_criteria=self.get_targeting_criteria_for_rule(
                {"field_name": "size", "arguments": [2], "comparison_method": "EQUALS"}
            ),
            created_by=self.user,
            business_area=self.business_area,
            program=self.program,
            status=TargetPopulation.STATUS_PROCESSING,
        )
        target_population_with_incorrect_status.save()

        variables = copy.deepcopy(VARIABLES)
        variables["updateTargetPopulationInput"]["id"] = self.id_to_base64(
            target_population_with_incorrect_status.id, "TargetPopulationNode"
        )

        response_error = self.graphql_request(
            request_string=MUTATION_QUERY,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables=variables,
        )
        assert "errors" in response_error
        self.assertIn(
            "Finalized Target Population can't be changed",
            response_error["errors"][0]["message"],
        )
