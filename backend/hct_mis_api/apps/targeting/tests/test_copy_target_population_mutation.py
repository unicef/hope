from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from core.utils import decode_id_string
from household.fixtures import HouseholdFactory
from targeting.models import (
    TargetingCriteria,
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
    TargetPopulation,
    HouseholdSelection,
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
        cls.household = HouseholdFactory(
            family_size=1, residence_status="CITIZEN",
        )
        tp = TargetPopulation(
            name="Original Target Population", status="APPROVED"
        )

        tp.candidate_list_targeting_criteria = cls.get_targeting_criteria_for_rule(
            {
                "field_name": "family_size",
                "arguments": [1],
                "comparision_method": "EQUALS",
            }
        )
        tp.final_list_targeting_criteria = cls.get_targeting_criteria_for_rule(
            {
                "field_name": "family_size",
                "arguments": [2],
                "comparision_method": "EQUALS",
            }
        )
        tp.save()
        tp.households.add(cls.household)
        cls.target_population = tp

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

    def test_copy_target(self):
        self.snapshot_graphql_request(
            request_string=self.COPY_TARGET_MUTATION,
            context={"user": self.user},
            variables={
                "input": {
                    "targetPopulationData": {
                        "id": self.id_to_base64(
                            self.target_population.id, "TargetPopulation"
                        ),
                        "name": "Test New Copy Name",
                    }
                }
            },
        )

    def test_copy_target_ids(self):
        graphql_request = self.client.execute(
            self.COPY_TARGET_MUTATION_WITH_ID,
            variables={
                "input": {
                    "targetPopulationData": {
                        "id": self.id_to_base64(
                            self.target_population.id, "TargetPopulation"
                        ),
                        "name": "Test New Copy Name 1",
                    }
                }
            },
            context=self.generate_context(**{"user": self.user}),
        )
        target_population_copy = TargetPopulation.objects.get(
            id=decode_id_string(
                graphql_request["data"]["copyTargetPopulation"][
                    "targetPopulation"
                ]["id"]
            )
        )
        self.assertNotEqual(
            target_population_copy.id, self.target_population.id
        )
        self.assertNotEqual(
            target_population_copy.candidate_list_targeting_criteria.id,
            self.target_population.candidate_list_targeting_criteria.id,
        )
        self.assertNotEqual(
            target_population_copy.final_list_targeting_criteria.id,
            self.target_population.final_list_targeting_criteria.id,
        )
        rule_copy = (
            target_population_copy.candidate_list_targeting_criteria.rules.first()
        )
        rule = (
            self.target_population.candidate_list_targeting_criteria.rules.first()
        )
        self.assertNotEqual(
            rule_copy.id, rule.id,
        )
        filter_copy = rule_copy.filters.first()
        filter = rule.filters.first()
        self.assertNotEqual(
            filter_copy.id, filter.id,
        )
        household_selection_copy = HouseholdSelection.objects.filter(
            target_population=target_population_copy
        ).first()
        household_selection = HouseholdSelection.objects.filter(
            target_population=self.target_population
        ).first()
        self.assertNotEqual(
            household_selection_copy.id, household_selection.id,
        )
