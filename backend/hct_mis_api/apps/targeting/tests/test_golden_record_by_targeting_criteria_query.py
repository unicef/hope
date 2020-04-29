from django.core.management import call_command

from core.base_test_case import APITestCase
from household.fixtures import (
    HouseholdFactory,
    IndividualFactory,
    create_household,
)


class GoldenRecordTargetingCriteriaQueryTestCase(APITestCase):
    QUERY = """
    query GoldenRecordFilter($targetingCriteria: TargetingCriteriaObjectType!) {
      goldenRecordByTargetingCriteria(targetingCriteria: $targetingCriteria) {
        totalCount
        edges {
          node {
            size
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
                            "fieldName": "size",
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
    FLEX_FIELD_VARIABLES = {
        "targetingCriteria": {
            "rules": [
                {
                    "filters": [
                        {
                            "comparisionMethod": "EQUALS",
                            "arguments": ["0"],
                            "fieldName": "unaccompanied_child_h_f",
                            "isFlexField": True,
                        }
                    ]
                }
            ]
        },
        "first": 10,
    }

    @classmethod
    def setUpTestData(cls):
        call_command("loadflexfieldsattributes")
        (household, individuals) = create_household(
            {"size": 1, "residence_status": "CITIZEN",},
        )
        cls.household_size_1 = household
        cls.household_residence_status_citizen = cls.household_size_1

        (household, individuals) = create_household(
            {"size": 2, "residence_status": "REFUGEE",},
        )
        cls.household_residence_status_refugee = household
        cls.household_size_2 = cls.household_residence_status_refugee

    def test_golden_record_by_targeting_criteria_size(self):
        self.snapshot_graphql_request(
            request_string=GoldenRecordTargetingCriteriaQueryTestCase.QUERY,
            variables=GoldenRecordTargetingCriteriaQueryTestCase.FAMILY_SIZE_2_VARIABLES,
        )

    def test_golden_record_by_targeting_criteria_residence_status(self):
        self.snapshot_graphql_request(
            request_string=GoldenRecordTargetingCriteriaQueryTestCase.QUERY,
            variables=GoldenRecordTargetingCriteriaQueryTestCase.RESIDENCE_STATUS_REFUGEE_VARIABLES,
        )

    def test_golden_record_by_targeting_criteria_flex_field(self):
        self.snapshot_graphql_request(
            request_string=GoldenRecordTargetingCriteriaQueryTestCase.QUERY,
            variables=GoldenRecordTargetingCriteriaQueryTestCase.FLEX_FIELD_VARIABLES,
        )
