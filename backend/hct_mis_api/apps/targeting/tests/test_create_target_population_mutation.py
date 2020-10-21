from django.core.management import call_command

from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from core.models import BusinessArea
from household.fixtures import create_household
from program.fixtures import ProgramFactory


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



    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create()
        call_command("loadbusinessareas")
        create_household(
            {"size": 2, "residence_status": "HOST"},
        )
        create_household(
            {"size": 3, "residence_status": "HOST"},
        )
        create_household(
            {"size": 3, "residence_status": "HOST"},
        )
        business_area = BusinessArea.objects.first()
        cls.program = ProgramFactory.create(status="ACTIVE", business_area=business_area)

    def test_create_mutation(self):
        variables = {
            "createTargetPopulationInput": {
                "name": "Example name 5",
                "businessAreaSlug": "afghanistan",
                "programId": self.id_to_base64(self.program.id, "Program"),
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
                "businessAreaSlug": "afghanistan",
            }
        }
        self.snapshot_graphql_request(
            request_string=TestCreateTargetPopulationMutation.MUTATION_QUERY,
            context={"user": self.user},
            variables=variables,
        )
