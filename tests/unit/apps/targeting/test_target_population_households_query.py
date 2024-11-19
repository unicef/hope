from typing import Any, Dict, List

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.program.fixtures import get_program_with_dct_type_and_name
from hct_mis_api.apps.targeting.models import (
    HouseholdSelection,
    TargetingCriteria,
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
    TargetPopulation,
)


class TargetPopulationHouseholdsQueryTestCase(APITestCase):
    QUERY = """
    query TargetPopulationHouseholds($targetPopulation: ID!, $businessArea: String) {
      targetPopulationHouseholds (targetPopulation:$targetPopulation, businessArea: $businessArea){
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
    QUERY_FIRST_10 = """
        query TargetPopulationHouseholds($targetPopulation: ID!, $businessArea: String) {
          targetPopulationHouseholds (targetPopulation:$targetPopulation, first: 10, businessArea: $businessArea){
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

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        _ = create_household(
            {"size": 1, "residence_status": "HOST", "business_area": cls.business_area},
        )
        (household, individuals) = create_household(
            {"size": 1, "residence_status": "HOST", "business_area": cls.business_area},
        )
        cls.household_size_1 = household
        cls.household_residence_status_citizen = household

        (household, individuals) = create_household(
            {"size": 2, "residence_status": "REFUGEE", "business_area": cls.business_area},
        )
        cls.household_residence_status_refugee = household
        cls.household_size_2 = household
        cls.partner = PartnerFactory(name="TestPartner")
        cls.user = UserFactory(partner=cls.partner)
        cls.program = get_program_with_dct_type_and_name()
        cls.program_cycle = cls.program.cycles.first()
        targeting_criteria = cls.get_targeting_criteria_for_rule(
            {"field_name": "size", "arguments": [2], "comparison_method": "EQUALS"}
        )
        cls.target_population_size_2 = TargetPopulation(
            name="target_population_size_2",
            created_by=cls.user,
            targeting_criteria=targeting_criteria,
            business_area=cls.business_area,
            program=cls.program,
            program_cycle=cls.program_cycle,
        )
        cls.target_population_size_2.save()
        targeting_criteria = cls.get_targeting_criteria_for_rule(
            {"field_name": "residence_status", "arguments": ["REFUGEE"], "comparison_method": "EQUALS"}
        )
        cls.target_population_residence_status = TargetPopulation(
            name="target_population_residence_status",
            created_by=cls.user,
            targeting_criteria=targeting_criteria,
            business_area=cls.business_area,
            program=cls.program,
            program_cycle=cls.program_cycle,
        )
        cls.target_population_residence_status.save()

        targeting_criteria = cls.get_targeting_criteria_for_rule(
            {"field_name": "size", "arguments": [1], "comparison_method": "EQUALS"}
        )
        cls.target_population_size_1_approved = TargetPopulation(
            name="target_population_size_1_approved",
            created_by=cls.user,
            targeting_criteria=targeting_criteria,
            status="LOCKED",
            business_area=cls.business_area,
            program=cls.program,
            program_cycle=cls.program_cycle,
        )
        cls.target_population_size_1_approved.save()
        HouseholdSelection.objects.create(
            household=cls.household_size_1,
            target_population=cls.target_population_size_1_approved,
        )
        cls.variables = {"businessArea": cls.business_area.slug}

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
            (
                "with_permission",
                [Permissions.TARGETING_VIEW_DETAILS],
            ),
            ("without_permission", []),
        ]
    )
    def test_candidate_households_list_by_targeting_criteria_size(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=TargetPopulationHouseholdsQueryTestCase.QUERY,
            context={"user": self.user},
            variables={
                "targetPopulation": self.id_to_base64(self.target_population_size_2.id, "TargetPopulationNode"),
                **self.variables,
            },
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.TARGETING_VIEW_DETAILS],
            ),
            ("without_permission", []),
        ]
    )
    def test_candidate_households_list_by_targeting_criteria_residence_status(
        self, _: Any, permissions: List[Permissions]
    ) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=TargetPopulationHouseholdsQueryTestCase.QUERY,
            context={"user": self.user},
            variables={
                "targetPopulation": self.id_to_base64(
                    self.target_population_residence_status.id,
                    "TargetPopulationNode",
                ),
                **self.variables,
            },
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.TARGETING_VIEW_DETAILS],
            ),
            ("without_permission", []),
        ]
    )
    def test_candidate_households_list_by_targeting_criteria_approved(
        self, _: Any, permissions: List[Permissions]
    ) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=TargetPopulationHouseholdsQueryTestCase.QUERY,
            context={"user": self.user},
            variables={
                "targetPopulation": self.id_to_base64(
                    self.target_population_size_1_approved.id,
                    "TargetPopulationNode",
                ),
                **self.variables,
            },
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.TARGETING_VIEW_DETAILS],
            ),
            ("without_permission", []),
        ]
    )
    def test_candidate_households_list_by_targeting_criteria_first_10(
        self, _: Any, permissions: List[Permissions]
    ) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=TargetPopulationHouseholdsQueryTestCase.QUERY_FIRST_10,
            context={"user": self.user},
            variables={
                "targetPopulation": self.id_to_base64(self.target_population_size_2.id, "TargetPopulationNode"),
                **self.variables,
            },
        )
