from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.targeting.models import (
    TargetingCriteria,
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
    TargetPopulation,
)


class TestApproveTargetPopulationMutation(APITestCase):
    APPROVE_TARGET_MUTATION = """
            mutation LockTargetPopulation($id: ID!) {
              lockTargetPopulation(id: $id) {
                targetPopulation {
                  status
                  householdList {
                    totalCount
                  }
                }
              }
            }
            """

    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.user = UserFactory.create()
        cls.households = []
        (household, individuals) = create_household(
            {"size": 1, "residence_status": "HOST", "business_area": cls.business_area},
        )
        cls.household_size_1 = household
        (household, individuals) = create_household(
            {"size": 2, "residence_status": "HOST", "business_area": cls.business_area},
        )
        cls.household_size_2 = household
        cls.households.append(cls.household_size_1)
        cls.households.append(cls.household_size_2)

        tp = TargetPopulation(
            name="Draft Target Population", status=TargetPopulation.STATUS_OPEN, business_area=cls.business_area
        )

        tp.targeting_criteria = cls.get_targeting_criteria_for_rule(
            {"field_name": "residence_status", "arguments": ["HOST"], "comparison_method": "EQUALS"}
        )
        tp.save()
        cls.target_population_draft = tp

        tp = TargetPopulation(
            name="Approved Target Population with final filters",
            status=TargetPopulation.STATUS_LOCKED,
            business_area=cls.business_area,
        )

        tp.targeting_criteria = cls.get_targeting_criteria_for_rule(
            {"field_name": "residence_status", "arguments": ["HOST"], "comparison_method": "EQUALS"}
        )
        tp.save()
        tp.households.set(cls.households)
        cls.target_population_approved_with_final_rule = tp

        tp = TargetPopulation(
            name="Approved Target Population", status=TargetPopulation.STATUS_LOCKED, business_area=cls.business_area
        )

        tp.targeting_criteria = cls.get_targeting_criteria_for_rule(
            {"field_name": "residence_status", "arguments": ["HOST"], "comparison_method": "EQUALS"}
        )
        tp.save()
        tp.households.set(cls.households)
        cls.target_population_approved = tp

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
            ("with_permission", [Permissions.TARGETING_LOCK]),
            ("without_permission", []),
        ]
    )
    def test_approve_target_population(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.APPROVE_TARGET_MUTATION,
            context={"user": self.user},
            variables={
                "id": self.id_to_base64(self.target_population_draft.id, "TargetPopulationNode"),
            },
        )

    def test_approve_fail_target_population(self):
        self.create_user_role_with_permissions(self.user, [Permissions.TARGETING_LOCK], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.APPROVE_TARGET_MUTATION,
            context={"user": self.user},
            variables={
                "id": self.id_to_base64(
                    self.target_population_approved_with_final_rule.id,
                    "TargetPopulationNode",
                )
            },
        )


class TestUnapproveTargetPopulationMutation(APITestCase):
    UNAPPROVE_TARGET_MUTATION = """
            mutation UnlockTargetPopulation($id: ID!) {
              unlockTargetPopulation(id: $id) {
                targetPopulation {
                  status
                  households {
                    totalCount
                  }
                }
              }
            }
            """

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create()
        cls.households = []
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        (household, individuals) = create_household(
            {"size": 1, "residence_status": "HOST", "business_area": cls.business_area},
        )
        cls.household_size_1 = household
        (household, individuals) = create_household(
            {"size": 2, "residence_status": "HOST", "business_area": cls.business_area},
        )
        cls.household_size_2 = household
        cls.households.append(cls.household_size_1)
        cls.households.append(cls.household_size_2)

        tp = TargetPopulation(
            name="Draft Target Population", status=TargetPopulation.STATUS_OPEN, business_area=cls.business_area
        )

        tp.targeting_criteria = cls.get_targeting_criteria_for_rule(
            {"field_name": "residence_status", "arguments": ["HOST"], "comparison_method": "EQUALS"}
        )
        tp.save()
        cls.target_population_draft = tp

        tp = TargetPopulation(
            name="Approved Target Population with final filters",
            status=TargetPopulation.STATUS_LOCKED,
            business_area=cls.business_area,
        )

        tp.targeting_criteria = cls.get_targeting_criteria_for_rule(
            {"field_name": "residence_status", "arguments": ["HOST"], "comparison_method": "EQUALS"}
        )
        tp.save()
        tp.households.set(cls.households)
        cls.target_population_approved_with_final_rule = tp

        tp = TargetPopulation(
            name="Approved Target Population", status=TargetPopulation.STATUS_LOCKED, business_area=cls.business_area
        )

        tp.targeting_criteria = cls.get_targeting_criteria_for_rule(
            {"field_name": "residence_status", "arguments": ["HOST"], "comparison_method": "EQUALS"}
        )
        tp.save()
        tp.households.set(cls.households)
        cls.target_population_approved = tp

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
            ("with_permission", [Permissions.TARGETING_UNLOCK]),
            ("without_permission", []),
        ]
    )
    def test_unapprove_target_population(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.UNAPPROVE_TARGET_MUTATION,
            context={"user": self.user},
            variables={
                "id": self.id_to_base64(
                    self.target_population_approved_with_final_rule.id,
                    "TargetPopulationNode",
                )
            },
        )

    def test_unapprove_fail_target_population(self):
        self.create_user_role_with_permissions(self.user, [Permissions.TARGETING_UNLOCK], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.UNAPPROVE_TARGET_MUTATION,
            context={"user": self.user},
            variables={"id": self.id_to_base64(self.target_population_draft.id, "TargetPopulationNode")},
        )


class TestFinalizeTargetPopulationMutation(APITestCase):
    FINALIZE_TARGET_MUTATION = """
            mutation FinalizeTargetPopulation($id: ID!) {
              finalizeTargetPopulation(id: $id) {
                targetPopulation {
                  status
                  householdList{
                    totalCount
                  }
                  households {
                    totalCount
                  }
                }
              }
            }
            """

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create()
        cls.households = []
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        (household, individuals) = create_household(
            {"size": 1, "residence_status": "HOST", "business_area": cls.business_area},
        )
        cls.household_size_1 = household
        (household, individuals) = create_household(
            {"size": 2, "residence_status": "HOST", "business_area": cls.business_area},
        )
        cls.household_size_2 = household
        cls.households.append(cls.household_size_1)
        cls.households.append(cls.household_size_2)

        tp = TargetPopulation(
            name="Draft Target Population", status=TargetPopulation.STATUS_OPEN, business_area=cls.business_area
        )

        tp.targeting_criteria = cls.get_targeting_criteria_for_rule(
            {"field_name": "residence_status", "arguments": ["HOST"], "comparison_method": "EQUALS"}
        )
        tp.save()
        cls.target_population_draft = tp

        tp = TargetPopulation(
            name="Approved Target Population with final filters",
            status=TargetPopulation.STATUS_LOCKED,
            business_area=cls.business_area,
        )

        tp.targeting_criteria = cls.get_targeting_criteria_for_rule(
            {"field_name": "residence_status", "arguments": ["HOST"], "comparison_method": "EQUALS"}
        )
        program = ProgramFactory(business_area=cls.business_area, status=Program.ACTIVE)
        tp.program = program
        tp.save()
        tp.households.set(cls.households)
        cls.target_population_approved_with_final_rule = tp

        tp = TargetPopulation(
            name="Approved Target Population", status=TargetPopulation.STATUS_LOCKED, business_area=cls.business_area
        )

        tp.targeting_criteria = cls.get_targeting_criteria_for_rule(
            {"field_name": "residence_status", "arguments": ["HOST"], "comparison_method": "EQUALS"}
        )
        program = ProgramFactory(business_area=cls.business_area, status=Program.ACTIVE)
        tp.program = program
        tp.save()
        tp.households.set(cls.households)
        cls.target_population_approved = tp

    @staticmethod
    def get_targeting_criteria_for_rule(rule_filter):
        targeting_criteria = TargetingCriteria()
        targeting_criteria.save()
        rule = TargetingCriteriaRule(targeting_criteria=targeting_criteria)
        rule.save()
        rule_filter = TargetingCriteriaRuleFilter(**rule_filter, targeting_criteria_rule=rule)
        rule_filter.save()
        return targeting_criteria

    def test_finalize_target_population_with_final_criteria(self):
        self.create_user_role_with_permissions(self.user, [Permissions.TARGETING_SEND], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.FINALIZE_TARGET_MUTATION,
            context={"user": self.user},
            variables={
                "id": self.id_to_base64(
                    self.target_population_approved_with_final_rule.id,
                    "TargetPopulationNode",
                )
            },
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.TARGETING_SEND]),
            ("without_permission", []),
        ]
    )
    def test_finalize_target_population(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.FINALIZE_TARGET_MUTATION,
            context={"user": self.user},
            variables={"id": self.id_to_base64(self.target_population_approved.id, "TargetPopulationNode")},
        )

    def test_finalize_fail_target_population(self):
        self.create_user_role_with_permissions(self.user, [Permissions.TARGETING_SEND], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.FINALIZE_TARGET_MUTATION,
            context={"user": self.user},
            variables={
                "id": self.id_to_base64(
                    self.target_population_draft.id,
                    "TargetPopulationNode",
                )
            },
        )
