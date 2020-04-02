import datetime as dt

from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from household.fixtures import HouseholdFactory, IndividualFactory
from targeting.fixtures import TargetPopulationFactory
from targeting.models import (
    TargetingCriteria,
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
    TargetPopulation,
    HouseholdSelection,
)


class TestTargetPopulationQuery(APITestCase):
    ALL_TARGET_POPULATION_QUERY = """
            query AllTargetPopulation($finalListTotalHouseholdsMin: Int) {
                allTargetPopulation(finalListTotalHouseholdsMin:$finalListTotalHouseholdsMin) {
                    edges {
                        node {
                             name
                             status
                            candidateListTotalHouseholds
                            candidateListTotalIndividuals
                            finalListTotalHouseholds
                            finalListTotalIndividuals
                        }
                    }
                }
            }
            """
    TARGET_POPULATION_QUERY = """
       query TargetPopulation($id:ID!) {
          targetPopulation(id:$id){
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
                """

    @classmethod
    def setUpTestData(cls):
        HouseholdFactory(
            family_size=1, residence_status="CITIZEN",
        )
        cls.household_family_size_1 = HouseholdFactory(
            family_size=1, residence_status="CITIZEN",
        )
        cls.household_residence_status_citizen = cls.household_family_size_1
        IndividualFactory(household=cls.household_family_size_1)
        cls.household_residence_status_refugee = HouseholdFactory(
            family_size=2, residence_status="REFUGEE",
        )
        cls.household_family_size_2 = cls.household_residence_status_refugee
        IndividualFactory(household=cls.household_residence_status_refugee)
        IndividualFactory(household=cls.household_residence_status_refugee)
        cls.user = UserFactory.create()
        targeting_criteria = cls.get_targeting_criteria_for_rule(
            {
                "field_name": "family_size",
                "arguments": [2],
                "comparision_method": "EQUALS",
            }
        )
        cls.target_population_family_size_2 = TargetPopulation(
            name="target_population_family_size_2",
            created_by=cls.user,
            candidate_list_targeting_criteria=targeting_criteria,
        )
        cls.target_population_family_size_2.save()
        targeting_criteria = cls.get_targeting_criteria_for_rule(
            {
                "field_name": "residence_status",
                "arguments": ["REFUGEE"],
                "comparision_method": "EQUALS",
            }
        )
        cls.target_population_residence_status = TargetPopulation(
            name="target_population_residence_status",
            created_by=cls.user,
            candidate_list_targeting_criteria=targeting_criteria,
        )
        cls.target_population_residence_status.save()

        targeting_criteria = cls.get_targeting_criteria_for_rule(
            {
                "field_name": "family_size",
                "arguments": [1],
                "comparision_method": "EQUALS",
            }
        )
        cls.target_population_family_size_1_approved = TargetPopulation(
            name="target_population_family_size_1_approved",
            created_by=cls.user,
            candidate_list_targeting_criteria=targeting_criteria,
            status="APPROVED",
        )
        cls.target_population_family_size_1_approved.save()
        HouseholdSelection.objects.create(
            household=cls.household_family_size_1,
            target_population=cls.target_population_family_size_1_approved,
        )

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

    def test_simple_all_targets_query(self):
        self.snapshot_graphql_request(
            request_string=TestTargetPopulationQuery.ALL_TARGET_POPULATION_QUERY,
        )

    def test_simple_all_targets_query_filter_finalListTotalHouseholdsMin(self):
        self.snapshot_graphql_request(
            request_string=TestTargetPopulationQuery.ALL_TARGET_POPULATION_QUERY,
            variables={"finalListTotalHouseholdsMin": 1},
        )

    def test_simple_target_query(self):
        self.snapshot_graphql_request(
            request_string=TestTargetPopulationQuery.TARGET_POPULATION_QUERY,
            variables={
                "id": self.id_to_base64(
                    self.target_population_family_size_1_approved.id,
                    "TargetPopulation",
                )
            },
        )

    def test_simple_target_query_2(self):
        self.snapshot_graphql_request(
            request_string=TestTargetPopulationQuery.TARGET_POPULATION_QUERY,
            variables={
                "id": self.id_to_base64(
                    self.target_population_residence_status.id,
                    "TargetPopulation",
                )
            },
        )


