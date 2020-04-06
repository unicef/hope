from core.base_test_case import APITestCase
from household.fixtures import HouseholdFactory, IndividualFactory


class GoldenRecordTargetingCriteriaQueryTestCase(APITestCase):
    QUERY = """
    query GoldenRecordFilter($targetingCriteria: TargetingCriteriaObjectType!) {
      goldenRecordByTargetingCriteria(targetingCriteria: $targetingCriteria) {
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
    FAMILY_SIZE_2_VARIABLES = {
        "targetingCriteria": {
            "rules": [
                {
                    "filters": [
                        {
                            "comparisionMethod": "EQUALS",
                            "arguments": [2],
                            "fieldName": "family_size",
                            "isFlexField": False,
                        }
                    ]
                }
            ]
        }
    }

    RESIDENCE_STATUS_REFUGEE_VARIABLES = {
        "targetingCriteria": {
            "rules": [
                {
                    "filters": [
                        {
                            "comparisionMethod": "EQUALS",
                            "arguments": ["REFUGEE"],
                            "fieldName": "residence_status",
                            "isFlexField": False,
                        }
                    ]
                }
            ]
        }
    }

    @classmethod
    def setUpTestData(cls):
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

    def test_golden_record_by_targeting_criteria_family_size(self):
        self.snapshot_graphql_request(
            request_string=GoldenRecordTargetingCriteriaQueryTestCase.QUERY,
            variables=GoldenRecordTargetingCriteriaQueryTestCase.FAMILY_SIZE_2_VARIABLES,
        )

    def test_golden_record_by_targeting_criteria_residence_status(self):
        self.snapshot_graphql_request(
            request_string=GoldenRecordTargetingCriteriaQueryTestCase.QUERY,
            variables=GoldenRecordTargetingCriteriaQueryTestCase.RESIDENCE_STATUS_REFUGEE_VARIABLES,
        )
