from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from household.fixtures import HouseholdFactory, IndividualFactory
from targeting.models import (
    TargetPopulation,
    TargetingCriteria,
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
    HouseholdSelection,
)


class CandidateListTargetingCriteriaQueryTestCase(APITestCase):
    QUERY = """
    query CandidateListByTargetingCriteria($targetPopulation: ID!) {
      candidateHouseholdsListByTargetingCriteria (targetPopulation:$targetPopulation){
        totalCount
        edges {
          node {
            familySize
            residenceStatus
          }
        }
      }
    }
    """
    QUERY_FIRST_10 = """
        query CandidateListByTargetingCriteria($targetPopulation: ID!) {
          candidateHouseholdsListByTargetingCriteria (targetPopulation:$targetPopulation, first: 10){
            totalCount
            edges {
              node {
                familySize
                residenceStatus
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

    def test_candidate_households_list_by_targeting_criteria_family_size(self):
        self.snapshot_graphql_request(
            request_string=CandidateListTargetingCriteriaQueryTestCase.QUERY,
            variables={
                "targetPopulation": self.id_to_base64(
                    self.target_population_family_size_2.id, "TargetPopulation"
                )
            },
        )

    def test_candidate_households_list_by_targeting_criteria_residence_status(
        self,
    ):
        self.snapshot_graphql_request(
            request_string=CandidateListTargetingCriteriaQueryTestCase.QUERY,
            variables={
                "targetPopulation": self.id_to_base64(
                    self.target_population_residence_status.id,
                    "TargetPopulation",
                )
            },
        )

    def test_candidate_households_list_by_targeting_criteria_approved(self):
        self.snapshot_graphql_request(
            request_string=CandidateListTargetingCriteriaQueryTestCase.QUERY,
            variables={
                "targetPopulation": self.id_to_base64(
                    self.target_population_family_size_1_approved.id,
                    "TargetPopulation",
                )
            },
        )

    def test_candidate_households_list_by_targeting_criteria_first_10(self):
        self.snapshot_graphql_request(
            request_string=CandidateListTargetingCriteriaQueryTestCase.QUERY_FIRST_10,
            variables={
                "targetPopulation": self.id_to_base64(
                    self.target_population_family_size_2.id, "TargetPopulation"
                )
            },
        )