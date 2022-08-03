from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import DocumentFactory, create_household
from hct_mis_api.apps.household.models import ROLE_PRIMARY, IndividualRoleInHousehold
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.targeting.models import (
    HouseholdSelection,
    TargetingCriteria,
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
    TargetPopulation,
)


class FinalListTargetingCriteriaQueryTestCase(APITestCase):
    QUERY = """
    query FinalListByTargetingCriteria($targetPopulation: ID!, $targetingCriteria: TargetingCriteriaObjectType, $businessArea: String) {
      finalHouseholdsListByTargetingCriteria (
        targetPopulation:$targetPopulation, targetingCriteria: $targetingCriteria,
        businessArea: $businessArea
        excludedIds: ""
      ){
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
    FAMILY_SIZE_1_TARGETING_CRITERIA = {
        "rules": [
            {"filters": [{"comparisionMethod": "EQUALS", "arguments": [1], "fieldName": "size", "isFlexField": False}]}
        ]
    }

    FAMILY_SIZE_2_TARGETING_CRITERIA = {
        "rules": [
            {"filters": [{"comparisionMethod": "EQUALS", "arguments": [2], "fieldName": "size", "isFlexField": False}]}
        ]
    }

    @classmethod
    def setUpTestData(cls):
        cls.generate_document_types_for_all_countries()
        create_afghanistan()
        cls.households = []
        cls.business_area = BusinessArea.objects.first()
        program = ProgramFactory(business_area=cls.business_area, individual_data_needed=True)
        _ = create_household(
            {"size": 1, "residence_status": "HOST", "business_area": cls.business_area},
        )
        (household, individuals) = create_household(
            {"size": 1, "residence_status": "HOST", "business_area": cls.business_area},
        )
        cls.household_status_host = household
        cls.households.append(household)
        (household, individuals) = create_household(
            {"size": 1, "residence_status": "IDP", "business_area": cls.business_area},
        )
        cls.household_size_1 = household
        cls.households.append(cls.household_size_1)
        cls.household_residence_status_citizen = cls.household_size_1

        (household, individuals) = create_household(
            {"size": 2, "residence_status": "REFUGEE", "business_area": cls.business_area},
        )
        cls.household_residence_status_refugee = household
        cls.households.append(cls.household_residence_status_refugee)
        cls.household_size_2 = cls.household_residence_status_refugee
        cls.user = UserFactory.create()
        targeting_criteria = cls.get_targeting_criteria_for_rule(
            {"field_name": "size", "arguments": [2], "comparision_method": "EQUALS"}
        )
        cls.target_population_size_2 = TargetPopulation(
            name="target_population_size_2",
            created_by=cls.user,
            final_list_targeting_criteria=targeting_criteria,
            status=TargetPopulation.STATUS_LOCKED,
            program=program,
        )
        cls.target_population_size_2.households.set(cls.households)
        cls.target_population_size_2.save()
        targeting_criteria = cls.get_targeting_criteria_for_rule(
            {"field_name": "residence_status", "arguments": ["HOST"], "comparision_method": "EQUALS"}
        )
        cls.target_population_residence_status = TargetPopulation(
            name="target_population_residence_status",
            created_by=cls.user,
            final_list_targeting_criteria=targeting_criteria,
            status=TargetPopulation.STATUS_LOCKED,
            program=program,
        )
        cls.target_population_residence_status.households.set(cls.households)
        cls.target_population_residence_status.save()
        targeting_criteria = cls.get_targeting_criteria_for_rule(
            {"field_name": "size", "arguments": [1], "comparision_method": "EQUALS"}
        )
        cls.target_population_size_1_finalized = TargetPopulation(
            name="target_population_size_1_finalized",
            created_by=cls.user,
            final_list_targeting_criteria=targeting_criteria,
            status=TargetPopulation.STATUS_PROCESSING,
            program=program,
        )
        cls.target_population_size_1_finalized.save()
        HouseholdSelection.objects.create(
            household=cls.household_size_1,
            final=True,
            target_population=cls.target_population_size_1_finalized,
        )
        cls.variables = {"businessArea": cls.business_area.slug}

    @staticmethod
    def get_targeting_criteria_for_rule(rule_filter):
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
    def test_final_households_list_by_targeting_criteria_size(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=FinalListTargetingCriteriaQueryTestCase.QUERY,
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
    def test_final_households_list_by_targeting_criteria_residence_status(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=FinalListTargetingCriteriaQueryTestCase.QUERY,
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
    def test_final_households_list_by_targeting_criteria_finalized(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=FinalListTargetingCriteriaQueryTestCase.QUERY,
            context={"user": self.user},
            variables={
                "targetPopulation": self.id_to_base64(
                    self.target_population_size_1_finalized.id,
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
    def test_final_households_list_by_targeting_criteria_size_1_edit(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=FinalListTargetingCriteriaQueryTestCase.QUERY,
            context={"user": self.user},
            variables={
                "targetPopulation": self.id_to_base64(
                    self.target_population_residence_status.id,
                    "TargetPopulationNode",
                ),
                "targetingCriteria": self.FAMILY_SIZE_1_TARGETING_CRITERIA,
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
    def test_final_households_list_by_targeting_criteria_size_2_edit(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=FinalListTargetingCriteriaQueryTestCase.QUERY,
            context={"user": self.user},
            variables={
                "targetPopulation": self.id_to_base64(
                    self.target_population_residence_status.id,
                    "TargetPopulationNode",
                ),
                "targetingCriteria": self.FAMILY_SIZE_2_TARGETING_CRITERIA,
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
    def test_final_households_list_without_invalid_documents(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        household = self.household_status_host
        individual = IndividualRoleInHousehold.objects.get(household=household, role=ROLE_PRIMARY).individual
        individual.household = household
        individual.save()
        DocumentFactory.create(individual=individual, status="INVALID")

        self.snapshot_graphql_request(
            request_string=FinalListTargetingCriteriaQueryTestCase.QUERY,
            context={"user": self.user},
            variables={
                "targetPopulation": self.id_to_base64(
                    self.target_population_residence_status.id, "TargetPopulationNode"
                ),
                **self.variables,
            },
        )
