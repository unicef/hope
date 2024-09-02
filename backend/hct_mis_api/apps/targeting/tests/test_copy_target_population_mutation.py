from typing import Any, Dict, List

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.targeting.models import (
    TargetingCriteria,
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
    TargetPopulation,
)


class TestCopyTargetPopulationMutation(APITestCase):
    COPY_TARGET_MUTATION = """
            mutation CopyTargetPopulation($input: CopyTargetPopulationMutationInput!) {
              copyTargetPopulation(input: $input) {
                targetPopulation {
                    name
                    status
                    totalHouseholdsCount
                    totalIndividualsCount
                    targetingCriteria{
                      rules{
                        filters{
                          comparisonMethod
                          fieldName
                          flexFieldClassification
                          arguments
                        }
                      }
                      householdIds
                      individualIds
                    }
                }
              }
            }
            """
    COPY_TARGET_MUTATION_WITH_ID = """
                mutation CopyTargetPopulation($input: CopyTargetPopulationMutationInput!) {
                  copyTargetPopulation(input: $input) {
                    targetPopulation {
                        id
                    }
                  }
                }
                """

    @classmethod
    def setUpTestData(cls) -> None:
        partner = PartnerFactory(name="Partner")
        cls.user = UserFactory.create(partner=partner)
        cls.business_area = create_afghanistan()
        cls.program = ProgramFactory(status=Program.ACTIVE, business_area=cls.business_area)
        cls.cycle = cls.program.cycles.first()
        (household, individuals) = create_household(
            {
                "size": 1,
                "residence_status": "HOST",
                "business_area": cls.business_area,
                "program": cls.program,
                "unicef_id": "HH-1",
            },
        )
        individual = individuals[0]
        individual.unicef_id = "IND-1"
        individual.save()
        cls.household = household
        cls.update_partner_access_to_program(partner, cls.program)
        tp = TargetPopulation(
            name="Original Target Population", status="LOCKED", business_area=cls.business_area, program=cls.program
        )

        tp.targeting_criteria = cls.get_targeting_criteria_for_rule(
            {"field_name": "size", "arguments": [1], "comparison_method": "EQUALS"}
        )
        tp.save()
        tp.households.add(cls.household)
        cls.target_population = tp
        cls.empty_target_population_1 = TargetPopulation(
            name="emptyTargetPopulation1", status="LOCKED", business_area=cls.business_area, program=cls.program
        )
        cls.empty_target_population_1.save()

        cls.target_population_with_household_ids = TargetPopulation(
            name="Target Population with household ids",
            status="LOCKED",
            business_area=cls.business_area,
            program=cls.program,
        )
        targeting_criteria_hh_ids = TargetingCriteria(household_ids=[cls.household.unicef_id])
        targeting_criteria_hh_ids.save()
        cls.target_population_with_household_ids.targeting_criteria = targeting_criteria_hh_ids
        cls.target_population_with_household_ids.save()

        cls.target_population_with_individual_ids = TargetPopulation(
            name="Target Population with individual ids",
            status="LOCKED",
            business_area=cls.business_area,
            program=cls.program,
        )
        targeting_criteria_hh_ids = TargetingCriteria(individual_ids=[individual.unicef_id])
        targeting_criteria_hh_ids.save()
        cls.target_population_with_individual_ids.targeting_criteria = targeting_criteria_hh_ids
        cls.target_population_with_individual_ids.save()

    @staticmethod
    def get_targeting_criteria_for_rule(rule_filter: Dict) -> TargetingCriteria:
        targeting_criteria = TargetingCriteria()
        targeting_criteria.save()
        rule = TargetingCriteriaRule(targeting_criteria=targeting_criteria)
        rule.save()
        rule_filter = TargetingCriteriaRuleFilter(**rule_filter, targeting_criteria_rule=rule)
        rule_filter.save()
        return targeting_criteria

    @parameterized.expand(
        [
            ("with_permission", [Permissions.TARGETING_DUPLICATE]),
            ("without_permission", []),
        ]
    )
    def test_copy_target(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.COPY_TARGET_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables={
                "input": {
                    "targetPopulationData": {
                        "id": self.id_to_base64(self.target_population.id, "TargetPopulationNode"),
                        "name": "Test New Copy Name",
                        "programCycleId": self.id_to_base64(self.cycle.id, "ProgramCycleNode"),
                    }
                }
            },
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.TARGETING_DUPLICATE], True),
            ("without_permission", [], False),
        ]
    )
    def test_copy_target_ids(self, _: Any, permissions: List[Permissions], should_have_copy: bool) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        graphql_request = self.client.execute(
            self.COPY_TARGET_MUTATION_WITH_ID,
            variables={
                "input": {
                    "targetPopulationData": {
                        "id": self.id_to_base64(self.target_population.id, "TargetPopulationNode"),
                        "name": "Test New Copy Name 1",
                        "programCycleId": self.id_to_base64(self.cycle.id, "ProgramCycleNode"),
                    }
                }
            },
            context=self.generate_context(
                **{"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}}
            ),
        )
        if should_have_copy:
            target_population_copy = TargetPopulation.objects.get(
                id=decode_id_string(graphql_request["data"]["copyTargetPopulation"]["targetPopulation"]["id"])
            )
            self.assertNotEqual(target_population_copy.id, self.target_population.id)
            self.assertNotEqual(
                target_population_copy.targeting_criteria.id,
                self.target_population.targeting_criteria.id,
            )
            rule_copy = target_population_copy.targeting_criteria.rules.first()
            rule = self.target_population.targeting_criteria.rules.first()
            self.assertNotEqual(
                rule_copy.id,
                rule.id,
            )
            filter_copy = rule_copy.filters.first()
            filter = rule.filters.first()
            self.assertNotEqual(
                filter_copy.id,
                filter.id,
            )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.TARGETING_DUPLICATE]),
            ("without_permission", []),
        ]
    )
    def test_copy_empty_target_1(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.COPY_TARGET_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables={
                "input": {
                    "targetPopulationData": {
                        "id": self.id_to_base64(
                            self.empty_target_population_1.id,
                            "TargetPopulationNode",
                        ),
                        "name": "test_copy_empty_target_1",
                        "programCycleId": self.id_to_base64(self.cycle.id, "ProgramCycleNode"),
                    }
                }
            },
        )

    def test_copy_with_unique_name_constraint(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.TARGETING_DUPLICATE], self.business_area)

        response_error = self.graphql_request(
            request_string=self.COPY_TARGET_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables={
                "input": {
                    "targetPopulationData": {
                        "id": self.id_to_base64(
                            self.empty_target_population_1.id,
                            "TargetPopulationNode",
                        ),
                        "name": self.empty_target_population_1.name,
                        "programCycleId": self.id_to_base64(self.cycle.id, "ProgramCycleNode"),
                    }
                }
            },
        )
        assert "errors" in response_error
        self.assertIn(
            f"Target population with name: {self.empty_target_population_1.name} and program: {self.program.name} already exists.",
            response_error["errors"][0]["message"],
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.TARGETING_DUPLICATE]),
            ("without_permission", []),
        ]
    )
    def test_copy_with_household_ids(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.COPY_TARGET_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables={
                "input": {
                    "targetPopulationData": {
                        "id": self.id_to_base64(self.target_population_with_household_ids.id, "TargetPopulationNode"),
                        "name": "Test New Copy Name",
                        "programCycleId": self.id_to_base64(self.cycle.id, "ProgramCycleNode"),
                    }
                }
            },
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.TARGETING_DUPLICATE]),
            ("without_permission", []),
        ]
    )
    def test_copy_with_individual_ids(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.COPY_TARGET_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables={
                "input": {
                    "targetPopulationData": {
                        "id": self.id_to_base64(self.target_population_with_individual_ids.id, "TargetPopulationNode"),
                        "name": "Test New Copy Name",
                        "programCycleId": self.id_to_base64(self.cycle.id, "ProgramCycleNode"),
                    }
                }
            },
        )
