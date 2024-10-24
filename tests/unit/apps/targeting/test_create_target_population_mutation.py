from typing import Any, List

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import (
    FlexibleAttributeForPDUFactory,
    PeriodicFieldDataFactory,
    create_afghanistan,
)
from hct_mis_api.apps.core.models import (
    BusinessArea,
    DataCollectingType,
    FlexibleAttribute,
    PeriodicFieldData,
)
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program, ProgramCycle
from hct_mis_api.apps.targeting.models import TargetPopulation


class TestCreateTargetPopulationMutation(APITestCase):
    MUTATION_QUERY = """
    mutation CreateTargetPopulation($createTargetPopulationInput: CreateTargetPopulationInput!) {
      createTargetPopulation(input: $createTargetPopulationInput) {
        targetPopulation {
          name
          status
          totalHouseholdsCount
          totalIndividualsCount
          programCycle {
            status
          }
          hasEmptyCriteria
          hasEmptyIdsCriteria
            targetingCriteria {
            householdIds
            individualIds
            rules {
              filters {
                comparisonMethod
                fieldName
                arguments
                flexFieldClassification
              }
              individualsFiltersBlocks{
                individualBlockFilters{
                    comparisonMethod
                    fieldName
                    arguments
                    flexFieldClassification
                    roundNumber
                }
              }
            }
          }
        }
      }
    }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.user = UserFactory.create()
        cls.business_area = create_afghanistan()
        business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.program = ProgramFactory.create(
            name="program1", status=Program.ACTIVE, business_area=business_area, cycle__status=ProgramCycle.ACTIVE
        )
        cls.program_cycle = cls.program.cycles.first()
        create_household(
            {"size": 2, "residence_status": "HOST", "program": cls.program},
        )
        create_household(
            {"size": 3, "residence_status": "HOST", "program": cls.program},
        )
        create_household(
            {"size": 4, "residence_status": "HOST", "program": cls.program},
        )
        FlexibleAttribute.objects.create(
            name="flex_field_1",
            type=FlexibleAttribute.STRING,
            associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
        )
        pdu_data = PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.DECIMAL,
            number_of_rounds=1,
            rounds_names=["Round 1"],
        )
        FlexibleAttributeForPDUFactory(
            program=cls.program,
            label="PDU Field 1",
            pdu_data=pdu_data,
        )
        cls.variables = {
            "createTargetPopulationInput": {
                "name": "Example name 5",
                "businessAreaSlug": "afghanistan",
                "programId": cls.id_to_base64(cls.program.id, "ProgramNode"),
                "programCycleId": cls.id_to_base64(cls.program_cycle.id, "ProgramCycleNode"),
                "excludedIds": "",
                "targetingCriteria": {
                    "rules": [
                        {
                            "filters": [
                                {
                                    "comparisonMethod": "EQUALS",
                                    "fieldName": "size",
                                    "arguments": [3],
                                    "flexFieldClassification": "NOT_FLEX_FIELD",
                                }
                            ]
                        }
                    ]
                },
            }
        }

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
                "programCycleId": self.id_to_base64(self.program_cycle.id, "ProgramCycleNode"),
                "excludedIds": "",
                "targetingCriteria": {
                    "rules": [
                        {
                            "filters": [
                                {
                                    "comparisonMethod": "EQUALS",
                                    "fieldName": "size",
                                    "arguments": [3],
                                    "flexFieldClassification": "NOT_FLEX_FIELD",
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
                "programCycleId": self.id_to_base64(self.program_cycle.id, "ProgramCycleNode"),
                "excludedIds": "",
                "targetingCriteria": {
                    "rules": [
                        {
                            "filters": [
                                {
                                    "comparisonMethod": "CONTAINS",
                                    "arguments": [],
                                    "fieldName": "registration_data_import",
                                    "flexFieldClassification": "NOT_FLEX_FIELD",
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

    def test_targeting_in_draft_program(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.TARGETING_CREATE], self.program.business_area)
        self.program.status = Program.DRAFT
        self.program.save()

        response_error = self.graphql_request(
            request_string=TestCreateTargetPopulationMutation.MUTATION_QUERY,
            context={"user": self.user},
            variables=self.variables,
        )
        self.assertEqual(TargetPopulation.objects.count(), 0)
        assert "errors" in response_error
        self.assertIn(
            "Only Active program can be assigned to Targeting",
            response_error["errors"][0]["message"],
        )

    def test_targeting_unique_constraints(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.TARGETING_CREATE], self.program.business_area)

        self.assertEqual(TargetPopulation.objects.count(), 0)

        # First, response is ok and tp is created
        response_ok = self.graphql_request(
            request_string=TestCreateTargetPopulationMutation.MUTATION_QUERY,
            context={"user": self.user},
            variables=self.variables,
        )
        assert "errors" not in response_ok
        self.assertEqual(TargetPopulation.objects.count(), 1)

        # Second, response has error due to unique constraints
        response_error = self.graphql_request(
            request_string=TestCreateTargetPopulationMutation.MUTATION_QUERY,
            context={"user": self.user},
            variables=self.variables,
        )
        assert "errors" in response_error
        self.assertEqual(TargetPopulation.objects.count(), 1)
        self.assertIn(
            f"Target population with name: {self.variables['createTargetPopulationInput']['name']} and program: {self.program.name} already exists.",
            response_error["errors"][0]["message"],
        )

        # Third, we remove tp with given name, program and business area
        TargetPopulation.objects.first().delete()
        self.assertEqual(TargetPopulation.objects.count(), 0)

        # Fourth, we can create tp with the same name, program and business area like removed one
        response_ok = self.graphql_request(
            request_string=TestCreateTargetPopulationMutation.MUTATION_QUERY,
            context={"user": self.user},
            variables=self.variables,
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
            {"householdIds": "HH-1,", "individualIds": "", "rules": []},
            {"householdIds": "HH-1, HH-2, HH-3, ", "individualIds": "IND-33, IND-33, ", "rules": []},
            {"householdIds": "HH-1", "individualIds": "IND-33", "rules": []},
            {"householdIds": "", "individualIds": "IND-33", "rules": []},
            {"householdIds": "", "individualIds": "IND-33, IND-666", "rules": []},
            {"householdIds": "", "individualIds": "IND-666", "rules": []},
            {"householdIds": "HH-1, HH-666", "individualIds": "", "rules": []},
            {"householdIds": "HH-666", "individualIds": "", "rules": []},
            {"householdIds": "", "individualIds": "", "rules": []},
        ]

        for num, targeting_criteria in enumerate(targeting_criteria_list, 1):
            variables = {
                "createTargetPopulationInput": {
                    "name": f"Test name {num}",
                    "businessAreaSlug": "afghanistan",
                    "programId": self.id_to_base64(self.program.id, "ProgramNode"),
                    "programCycleId": self.id_to_base64(self.program_cycle.id, "ProgramCycleNode"),
                    "excludedIds": "",
                    "targetingCriteria": targeting_criteria,
                }
            }
            self.snapshot_graphql_request(
                request_string=TestCreateTargetPopulationMutation.MUTATION_QUERY,
                context={"user": self.user},
                variables=variables,
            )

    def test_create_mutation_with_flex_field(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.TARGETING_CREATE], self.program.business_area)

        variables = {
            "createTargetPopulationInput": {
                "name": "Example name 5 ",
                "businessAreaSlug": "afghanistan",
                "programId": self.id_to_base64(self.program.id, "ProgramNode"),
                "excludedIds": "",
                "programCycleId": self.id_to_base64(self.program_cycle.id, "ProgramCycleNode"),
                "targetingCriteria": {
                    "rules": [
                        {
                            "filters": [],
                            "individualsFiltersBlocks": [
                                {
                                    "individualBlockFilters": [
                                        {
                                            "comparisonMethod": "CONTAINS",
                                            "arguments": ["Average"],
                                            "fieldName": "flex_field_1",
                                            "flexFieldClassification": "FLEX_FIELD_BASIC",
                                        }
                                    ]
                                }
                            ],
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

    def test_create_mutation_with_pdu_flex_field(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.TARGETING_CREATE], self.program.business_area)

        variables = {
            "createTargetPopulationInput": {
                "name": "Example name 5 ",
                "businessAreaSlug": "afghanistan",
                "programId": self.id_to_base64(self.program.id, "ProgramNode"),
                "excludedIds": "",
                "programCycleId": self.id_to_base64(self.program_cycle.id, "ProgramCycleNode"),
                "targetingCriteria": {
                    "rules": [
                        {
                            "filters": [],
                            "individualsFiltersBlocks": [
                                {
                                    "individualBlockFilters": [
                                        {
                                            "comparisonMethod": "RANGE",
                                            "arguments": ["2", "3.5"],
                                            "fieldName": "pdu_field_1",
                                            "flexFieldClassification": "FLEX_FIELD_PDU",
                                            "roundNumber": "1",
                                        }
                                    ]
                                }
                            ],
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

    def test_create_mutation_with_pdu_flex_field_for_sw_program(self) -> None:
        program_sw = ProgramFactory(
            data_collecting_type__type=DataCollectingType.Type.SOCIAL,
            business_area=self.business_area,
            status=Program.ACTIVE,
        )
        self.create_user_role_with_permissions(self.user, [Permissions.TARGETING_CREATE], self.business_area)

        pdu_data = PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.DECIMAL,
            number_of_rounds=1,
            rounds_names=["Round 1"],
        )
        FlexibleAttributeForPDUFactory(
            program=program_sw,
            label="PDU Field 1 SW",
            pdu_data=pdu_data,
        )

        program_cycle = program_sw.cycles.first()

        variables = {
            "createTargetPopulationInput": {
                "name": "Example name 10 ",
                "businessAreaSlug": "afghanistan",
                "programId": self.id_to_base64(program_sw.id, "ProgramNode"),
                "excludedIds": "",
                "programCycleId": self.id_to_base64(program_cycle.id, "ProgramCycleNode"),
                "targetingCriteria": {
                    "rules": [
                        {
                            "filters": [
                                {
                                    "comparisonMethod": "RANGE",
                                    "arguments": ["2", "3.5"],
                                    "fieldName": "pdu_field_1_sw",
                                    "flexFieldClassification": "FLEX_FIELD_PDU",
                                    "roundNumber": "1",
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

    def test_create_targeting_if_program_cycle_finished(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.TARGETING_CREATE], self.program.business_area)
        self.program_cycle.status = Program.FINISHED
        self.program_cycle.save()

        response_error = self.graphql_request(
            request_string=TestCreateTargetPopulationMutation.MUTATION_QUERY,
            context={"user": self.user},
            variables=self.variables,
        )
        self.assertEqual(TargetPopulation.objects.count(), 0)
        assert "errors" in response_error
        self.assertIn(
            "Not possible to assign Finished Program Cycle to Targeting",
            response_error["errors"][0]["message"],
        )
