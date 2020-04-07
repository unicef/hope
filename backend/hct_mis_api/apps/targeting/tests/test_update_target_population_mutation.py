import copy

from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from household.fixtures import HouseholdFactory
from household.models import Household
from targeting.models import (
    TargetingCriteria,
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
    TargetPopulation,
)


class TestUpdateTargetPopulationMutation(APITestCase):
    MUTATION_QUERY = """
    mutation UpdateTargetPopulation($updateTargetPopulationInput: UpdateTargetPopulationInput!) {
      updateTargetPopulation(input: $updateTargetPopulationInput) {
        targetPopulation{
          name
          status
          candidateListTotalHouseholds
          candidateListTotalIndividuals
          finalListTotalHouseholds
          finalListTotalIndividuals
            candidateListTargetingCriteria{
            rules{
              filters{
                comparisionMethod
                fieldName
                arguments
                isFlexField
              }
            }
          }
          finalListTargetingCriteria{
            rules{
              filters{
                comparisionMethod
                fieldName
                arguments
                isFlexField
              }
            }
          }
        }
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
                                "comparisionMethod": "EQUALS",
                                "fieldName": "family_size",
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
                                "comparisionMethod": "EQUALS",
                                "fieldName": "family_size",
                                "arguments": [3, 3],
                                "isFlexField": False,
                            }
                        ]
                    }
                ]
            },
        }
    }
    VARIABLES_WRONG_COMPARISION_METHOD = {
        "updateTargetPopulationInput": {
            "targetingCriteria": {
                "rules": [
                    {
                        "filters": [
                            {
                                "comparisionMethod": "CONTAINS",
                                "fieldName": "family_size",
                                "arguments": [3],
                                "isFlexField": False,
                            }
                        ]
                    }
                ]
            },
        }
    }
    VARIABLES_UNKNOWN_COMPARISION_METHOD = {
        "updateTargetPopulationInput": {
            "targetingCriteria": {
                "rules": [
                    {
                        "filters": [
                            {
                                "comparisionMethod": "BLABLA",
                                "fieldName": "family_size",
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
                                "comparisionMethod": "EQUALS",
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
                                "comparisionMethod": "EQUALS",
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

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create()
        HouseholdFactory(
            family_size=2, residence_status="CITIZEN",
        )
        HouseholdFactory(
            family_size=3, residence_status="CITIZEN",
        )
        HouseholdFactory(
            family_size=3, residence_status="CITIZEN",
        )
        cls.draft_target_population = TargetPopulation(
            name="draft_target_population",
            candidate_list_targeting_criteria=cls.get_targeting_criteria_for_rule(
                {
                    "field_name": "family_size",
                    "arguments": [2],
                    "comparision_method": "EQUALS",
                }
            ),
        )
        cls.draft_target_population.save()
        cls.approved_target_population = TargetPopulation(
            name="approved_target_population",
            candidate_list_targeting_criteria=cls.get_targeting_criteria_for_rule(
                {
                    "field_name": "family_size",
                    "arguments": [1],
                    "comparision_method": "GREATER_THAN",
                }
            ),
            status="APPROVED",
        )
        cls.approved_target_population.save()
        cls.approved_target_population.households.set(Household.objects.all())

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

    def test_update_draft_mutation(self):
        variables = copy.deepcopy(TestUpdateTargetPopulationMutation.VARIABLES)
        variables["updateTargetPopulationInput"]["id"] = self.id_to_base64(
            self.draft_target_population.id, "TargetPopulation"
        )
        variables["updateTargetPopulationInput"][
            "name"
        ] = "draft_target_population updated"

        self.snapshot_graphql_request(
            request_string=TestUpdateTargetPopulationMutation.MUTATION_QUERY,
            context={"user": self.user},
            variables=variables,
        )

    def test_update_approved_mutation(self):
        variables = copy.deepcopy(TestUpdateTargetPopulationMutation.VARIABLES)
        variables["updateTargetPopulationInput"]["id"] = self.id_to_base64(
            self.approved_target_population.id, "TargetPopulation"
        )

        self.snapshot_graphql_request(
            request_string=TestUpdateTargetPopulationMutation.MUTATION_QUERY,
            context={"user": self.user},
            variables=variables,
        )

    def test_fail_update_draft_mutation_wrong_args_count(self):
        variables = copy.deepcopy(
            TestUpdateTargetPopulationMutation.VARIABLES_WRONG_ARGS_COUNT
        )
        variables["updateTargetPopulationInput"]["id"] = self.id_to_base64(
            self.draft_target_population.id, "TargetPopulation"
        )
        variables["updateTargetPopulationInput"][
            "name"
        ] = "draft_target_population wrong"

        self.snapshot_graphql_request(
            request_string=TestUpdateTargetPopulationMutation.MUTATION_QUERY,
            context={"user": self.user},
            variables=variables,
        )

    def test_fail_update_draft_mutation_wrong_comparision_method(self):
        variables = copy.deepcopy(
            TestUpdateTargetPopulationMutation.VARIABLES_WRONG_COMPARISION_METHOD
        )
        variables["updateTargetPopulationInput"]["id"] = self.id_to_base64(
            self.draft_target_population.id, "TargetPopulation"
        )
        variables["updateTargetPopulationInput"][
            "name"
        ] = "draft_target_population wrong"

        self.snapshot_graphql_request(
            request_string=TestUpdateTargetPopulationMutation.MUTATION_QUERY,
            context={"user": self.user},
            variables=variables,
        )

    def test_fail_update_draft_mutation_unknown_comparision_method(self):
        variables = copy.deepcopy(
            TestUpdateTargetPopulationMutation.VARIABLES_UNKNOWN_COMPARISION_METHOD
        )
        variables["updateTargetPopulationInput"]["id"] = self.id_to_base64(
            self.draft_target_population.id, "TargetPopulation"
        )
        variables["updateTargetPopulationInput"][
            "name"
        ] = "draft_target_population wrong"

        self.snapshot_graphql_request(
            request_string=TestUpdateTargetPopulationMutation.MUTATION_QUERY,
            context={"user": self.user},
            variables=variables,
        )

    def test_fail_update_draft_mutation_unknown_flex_field_name(self):
        variables = copy.deepcopy(
            TestUpdateTargetPopulationMutation.VARIABLES_UNKNOWN_FLEX_FIELD_NAME
        )
        variables["updateTargetPopulationInput"]["id"] = self.id_to_base64(
            self.draft_target_population.id, "TargetPopulation"
        )
        variables["updateTargetPopulationInput"][
            "name"
        ] = "draft_target_population wrong"

        self.snapshot_graphql_request(
            request_string=TestUpdateTargetPopulationMutation.MUTATION_QUERY,
            context={"user": self.user},
            variables=variables,
        )

    def test_fail_update_draft_mutation_unknown_core_field_name(self):
        variables = copy.deepcopy(
            TestUpdateTargetPopulationMutation.VARIABLES_UNKNOWN_CORE_FIELD_NAME
        )
        variables["updateTargetPopulationInput"]["id"] = self.id_to_base64(
            self.draft_target_population.id, "TargetPopulation"
        )
        variables["updateTargetPopulationInput"][
            "name"
        ] = "draft_target_population wrong"

        self.snapshot_graphql_request(
            request_string=TestUpdateTargetPopulationMutation.MUTATION_QUERY,
            context={"user": self.user},
            variables=variables,
        )
