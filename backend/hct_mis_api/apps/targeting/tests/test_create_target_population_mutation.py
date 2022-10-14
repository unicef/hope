from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program


class TestCreateTargetPopulationMutation(APITestCase):
    MUTATION_QUERY = """
    mutation CreateTargetPopulation($createTargetPopulationInput: CreateTargetPopulationInput!) {
      createTargetPopulation(input: $createTargetPopulationInput) {
        targetPopulation{
          name
          status
          totalHouseholdsCount
          totalIndividualsCount
            targetingCriteria{
            rules{
              filters{
                comparisonMethod
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
        create_afghanistan()
        create_household(
            {"size": 2, "residence_status": "HOST"},
        )
        create_household(
            {"size": 3, "residence_status": "HOST"},
        )
        create_household(
            {"size": 3, "residence_status": "HOST"},
        )
        business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.program = ProgramFactory.create(status=Program.ACTIVE, business_area=business_area)

    @parameterized.expand(
        [
            ("with_permission", [Permissions.TARGETING_CREATE]),
            ("without_permission", []),
        ]
    )
    def test_create_mutation(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.program.business_area)

        variables = {
            "createTargetPopulationInput": {
                "name": "Example name 5",
                "businessAreaSlug": "afghanistan",
                "programId": self.id_to_base64(self.program.id, "ProgramNode"),
                "excludedIds": "",
                "targetingCriteria": {
                    "rules": [
                        {
                            "filters": [
                                {
                                    "comparisonMethod": "EQUALS",
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
        self.snapshot_graphql_request(
            request_string=TestCreateTargetPopulationMutation.MUTATION_QUERY,
            context={"user": self.user},
            variables=variables,
        )
