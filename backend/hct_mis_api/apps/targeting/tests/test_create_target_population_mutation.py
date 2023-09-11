from typing import Any, List

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.targeting.models import TargetPopulation


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
    def setUpTestData(cls) -> None:
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
        cls.program = ProgramFactory.create(name="program1", status=Program.ACTIVE, business_area=business_area)

    @parameterized.expand(
        [
            ("with_permission", [Permissions.TARGETING_CREATE]),
            ("without_permission", []),
        ]
    )
    def test_create_mutation(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.program.business_area)

        variables = {
            "createTargetPopulationInput": {
                "name": "Example name 5 ",
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

    @parameterized.expand(
        [
            ("with_permission", [Permissions.TARGETING_CREATE]),
            ("without_permission", []),
        ]
    )
    def test_create_mutation_with_comparison_method_contains(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.program.business_area)

        variables = {
            "createTargetPopulationInput": {
                "name": "Example name 5 ",
                "businessAreaSlug": "afghanistan",
                "programId": self.id_to_base64(self.program.id, "ProgramNode"),
                "excludedIds": "",
                "targetingCriteria": {
                    "rules": [
                        {
                            "filters": [
                                {
                                    "comparisonMethod": "CONTAINS",
                                    "arguments": [],
                                    "fieldName": "registration_data_import",
                                    "isFlexField": False,
                                }
                            ],
                            "individualsFiltersBlocks": [],
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

    def test_targeting_unique_constraints(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.TARGETING_CREATE], self.program.business_area)

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

        self.assertEqual(TargetPopulation.objects.count(), 0)

        # First, response is ok and tp is created
        response_ok = self.graphql_request(
            request_string=TestCreateTargetPopulationMutation.MUTATION_QUERY,
            context={"user": self.user},
            variables=variables,
        )
        assert "errors" not in response_ok
        self.assertEqual(TargetPopulation.objects.count(), 1)

        # Second, response has error due to unique constraints
        response_error = self.graphql_request(
            request_string=TestCreateTargetPopulationMutation.MUTATION_QUERY,
            context={"user": self.user},
            variables=variables,
        )
        assert "errors" in response_error
        self.assertEqual(TargetPopulation.objects.count(), 1)
        self.assertIn(
            f"Target population with name: {variables['createTargetPopulationInput']['name']}, program: {self.program.name} and business_area: {variables['createTargetPopulationInput']['businessAreaSlug']} already exists.",
            response_error["errors"][0]["message"],
        )

        # Third, we remove tp with given name, program and business area
        TargetPopulation.objects.first().delete()
        self.assertEqual(TargetPopulation.objects.count(), 0)

        # Fourth, we can create tp with the same name, program and business area like removed one
        response_ok = self.graphql_request(
            request_string=TestCreateTargetPopulationMutation.MUTATION_QUERY,
            context={"user": self.user},
            variables=variables,
        )
        assert "errors" not in response_ok
        self.assertEqual(TargetPopulation.objects.count(), 1)
