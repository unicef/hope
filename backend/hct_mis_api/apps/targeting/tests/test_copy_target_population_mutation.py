from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.targeting.models import (
    TargetingCriteria,
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
    TargetPopulation,
)


class TestCopyTargetPopulationMutation(APITestCase):
    COPY_TARGET_MUTATION = """
            mutation CopyTargetPopulation($input: CopyTargetPopulationMutationInput!) {
              copyTargetPopulation(input: $input) {
                targetPopulation {
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
                          isFlexField
                          arguments
                        }
                      }
                    }
                    finalListTargetingCriteria{
                      rules{
                        filters{
                          comparisionMethod
                          fieldName
                          isFlexField
                          arguments
                        }
                      }
                    }
                }
              }
            }
            """
    COPY_TARGET_MUTATION_WITH_ID = """
                mutation CopyTargetPopulation($input: CopyTargetPopulationMutationInput!) {
                  copyTargetPopulation(input: $input) {
                    targetPopulation {
                        id
                    }
                  }
                }
                """

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create()
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        (household, individuals) = create_household(
            {"size": 1, "residence_status": "HOST", "business_area": cls.business_area},
        )
        cls.household = household
        tp = TargetPopulation(name="Original Target Population", status="LOCKED", business_area=cls.business_area)

        tp.targeting_criteria = cls.get_targeting_criteria_for_rule(
            {"field_name": "size", "arguments": [1], "comparision_method": "EQUALS"}
        )
        tp.final_list_targeting_criteria = cls.get_targeting_criteria_for_rule(
            {"field_name": "size", "arguments": [2], "comparision_method": "EQUALS"}
        )
        tp.save()
        tp.households.add(cls.household)
        cls.target_population = tp
        cls.empty_target_population_1 = TargetPopulation(
            name="emptyTargetPopulation1", status="LOCKED", business_area=cls.business_area
        )
        cls.empty_target_population_1.save()

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
            ("with_permission", [Permissions.TARGETING_DUPLICATE]),
            ("without_permission", []),
        ]
    )
    def test_copy_target(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.COPY_TARGET_MUTATION,
            context={"user": self.user},
            variables={
                "input": {
                    "targetPopulationData": {
                        "id": self.id_to_base64(self.target_population.id, "TargetPopulationNode"),
                        "name": "Test New Copy Name",
                    }
                }
            },
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.TARGETING_DUPLICATE], True),
            ("without_permission", [], False),
        ]
    )
    def test_copy_target_ids(self, _, permissions, should_have_copy):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        graphql_request = self.client.execute(
            self.COPY_TARGET_MUTATION_WITH_ID,
            variables={
                "input": {
                    "targetPopulationData": {
                        "id": self.id_to_base64(self.target_population.id, "TargetPopulationNode"),
                        "name": "Test New Copy Name 1",
                    }
                }
            },
            context=self.generate_context(**{"user": self.user}),
        )
        if should_have_copy:
            target_population_copy = TargetPopulation.objects.get(
                id=decode_id_string(graphql_request["data"]["copyTargetPopulation"]["targetPopulation"]["id"])
            )
            self.assertNotEqual(target_population_copy.id, self.target_population.id)
            self.assertNotEqual(
                target_population_copy.targeting_criteria.id,
                self.target_population.targeting_criteria.id,
            )
            rule_copy = target_population_copy.targeting_criteria.rules.first()
            rule = self.target_population.targeting_criteria.rules.first()
            self.assertNotEqual(
                rule_copy.id,
                rule.id,
            )
            filter_copy = rule_copy.filters.first()
            filter = rule.filters.first()
            self.assertNotEqual(
                filter_copy.id,
                filter.id,
            )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.TARGETING_DUPLICATE]),
            ("without_permission", []),
        ]
    )
    def test_copy_empty_target_1(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.COPY_TARGET_MUTATION,
            context={"user": self.user},
            variables={
                "input": {
                    "targetPopulationData": {
                        "id": self.id_to_base64(
                            self.empty_target_population_1.id,
                            "TargetPopulationNode",
                        ),
                        "name": "test_copy_empty_target_1",
                    }
                }
            },
        )
