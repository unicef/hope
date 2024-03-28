from typing import Any, List

from parameterized import parameterized

from hct_mis_api.apps.household.models import Household
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
          hasEmptyCriteria
          hasEmptyIdsCriteria
            targetingCriteria{
            householdIds
            individualIds
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
        business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.program = ProgramFactory.create(name="program1", status=Program.ACTIVE, business_area=business_area)
        create_household(
            {"size": 2, "residence_status": "HOST", "program": cls.program},
        )
        create_household(
            {"size": 3, "residence_status": "HOST", "program": cls.program},
        )
        create_household(
            {"size": 4, "residence_status": "HOST", "program": cls.program},
        )

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

    def test_create_mutation_target_by_id(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.TARGETING_CREATE], self.program.business_area)
        hh_1 = Household.objects.filter(program_id=self.program.id, size=2).first()
        hh_2 = Household.objects.filter(program_id=self.program.id, size=3).first()
        hh_3 = Household.objects.filter(program_id=self.program.id, size=4).first()
        hh_1.unicef_id = "HH-1"
        hh_2.unicef_id = "HH-2"
        hh_3.unicef_id = "HH-3"
        hh_1.save()
        hh_2.save()
        hh_3.save()
        ind_hh_3 = hh_3.individuals.first()
        ind_hh_3.unicef_id = "IND-33"
        ind_hh_3.save()

        targeting_criteria_list = [
            {"householdIds": " HH-1,", "individualIds": "", "rules": []},
            {"householdIds": "HH-1, HH-2, HH-3, ", "individualIds": "IND-33, IND-33, ", "rules": []},
            {"householdIds": "HH-1", "individualIds": "IND-33", "rules": []},
            {"householdIds": "", "individualIds": "IND-33", "rules": []},
        ]

        for num, targeting_criteria in enumerate(targeting_criteria_list, 1):
            variables = {
                "createTargetPopulationInput": {
                    "name": f"Test name {num}",
                    "businessAreaSlug": "afghanistan",
                    "programId": self.id_to_base64(self.program.id, "ProgramNode"),
                    "excludedIds": "",
                    "targetingCriteria": targeting_criteria,
                }
            }
            self.snapshot_graphql_request(
                request_string=TestCreateTargetPopulationMutation.MUTATION_QUERY,
                context={"user": self.user},
                variables=variables,
            )
