from django.core.management import call_command

from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.household.models import MALE
from hct_mis_api.apps.program.fixtures import ProgramFactory


class GoldenRecordTargetingCriteriaWithBlockFiltersQueryTestCase(APITestCase):
    QUERY = """
    query GoldenRecordFilter($targetingCriteria: TargetingCriteriaObjectType!, $program: ID!) {
      goldenRecordByTargetingCriteria(targetingCriteria: $targetingCriteria, program: $program) {
        totalCount
        edges {
          node {
            size
            individuals{
                edges{
                    node{
                        sex
                        maritalStatus
                    }
                }
            }
          }
        }
      }
    }
    """
    VARIABLES = {
        "targetingCriteria": {
            "rules": [
                {
                    "filters": [],
                    "individualsFiltersBlocks": [
                        {
                            "individualBlockFilters": [
                                {
                                    "comparisionMethod": "EQUALS",
                                    "arguments": ["MARRIED"],
                                    "fieldName": "marital_status",
                                    "isFlexField": False,
                                },
                                {
                                    "comparisionMethod": "EQUALS",
                                    "arguments": [MALE],
                                    "fieldName": "sex",
                                    "isFlexField": False,
                                },
                            ]
                        }
                    ],
                }
            ]
        }
    }

    @classmethod
    def setUpTestData(cls):
        call_command("loadflexfieldsattributes")
        call_command("loadbusinessareas")
        business_area = BusinessArea.objects.first()
        cls.program = ProgramFactory(business_area=business_area, individual_data_needed=True)
        (household, individuals) = create_household_and_individuals(
            {
                "business_area": business_area,
            },
            [{"sex": "MALE", "marital_status": "MARRIED"}],
        )
        cls.household_targeted = household
        (household, individuals) = create_household_and_individuals(
            {
                "business_area": business_area,
            },
            [{"sex": "MALE", "marital_status": "SINGLE"}, {"sex": "FEMALE", "marital_status": "MARRIED"}],
        )
        cls.not_targeted_household = household

    def test_golden_record_by_targeting_criteria_size(self):
        variables = {
            "program": self.id_to_base64(self.program.id, "Program"),
            **GoldenRecordTargetingCriteriaWithBlockFiltersQueryTestCase.VARIABLES,
        }
        self.snapshot_graphql_request(
            request_string=GoldenRecordTargetingCriteriaWithBlockFiltersQueryTestCase.QUERY, variables=variables
        )
