from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from household.fixtures import HouseholdFactory, create_household


class TestCreateTargetPopulationMutation(APITestCase):
    MUTATION_QUERY = """
    mutation CreateTargetPopulation($createTargetPopulationInput: CreateTargetPopulationInput!) {
      createTargetPopulation(input: $createTargetPopulationInput) {
        targetPopulation{
          name
          status
          candidateListTotalHouseholds
          candidateListTotalIndividuals
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
        }
      }
    }
    """
    VARIABLES = {
        "createTargetPopulationInput": {
            "name": "Example name 5",
            "targetingCriteria": {
                "rules": [
                    {
                        "filters": [
                            {
                                "comparisionMethod": "EQUALS",
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

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create()
        create_household(
            {"size": 2, "residence_status": "CITIZEN", },
        )
        create_household(
            {"size": 3, "residence_status": "CITIZEN", },
        )
        create_household(
            {"size": 3, "residence_status": "CITIZEN", },
        )

    def test_create_mutation(self):
        self.snapshot_graphql_request(
            request_string=TestCreateTargetPopulationMutation.MUTATION_QUERY,
            context={"user": self.user},
            variables=TestCreateTargetPopulationMutation.VARIABLES,
        )
