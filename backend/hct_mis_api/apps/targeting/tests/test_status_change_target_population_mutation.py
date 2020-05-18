from django.core.management import call_command

from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from core.models import BusinessArea
from household.fixtures import create_household
from program.fixtures import ProgramFactory
from targeting.models import (
    TargetingCriteria,
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
    TargetPopulation,
)


class TestApproveTargetPopulationMutation(APITestCase):
    APPROVE_TARGET_MUTATION = """
            mutation ApproveTargetPopulation($id: ID!, $programId: ID!) {
              approveTargetPopulation(id: $id, programId: $programId) {
                targetPopulation {
                  status
                  households {
                    totalCount
                    edges {
                      node {
                        size
                        residenceStatus
                      }
                    }
                  }
                }
              }
            }
            """

    @classmethod
    def setUpTestData(cls):
        call_command("loadbusinessareas")
        cls.program = ProgramFactory.create(
            status="ACTIVE",
            business_area=BusinessArea.objects.order_by("?").first(),
        )
        cls.user = UserFactory.create()
        cls.households = []
        (household, individuals) = create_household(
            {"size": 1, "residence_status": "CITIZEN",},
        )
        cls.household_size_1 = household
        (household, individuals) = create_household(
            {"size": 2, "residence_status": "CITIZEN",},
        )
        cls.household_size_2 = household
        cls.households.append(cls.household_size_1)
        cls.households.append(cls.household_size_2)

        tp = TargetPopulation(name="Draft Target Population", status="DRAFT")

        tp.candidate_list_targeting_criteria = cls.get_targeting_criteria_for_rule(
            {
                "field_name": "residence_status",
                "arguments": ["CITIZEN"],
                "comparision_method": "EQUALS",
            }
        )
        tp.save()
        cls.target_population_draft = tp

        tp = TargetPopulation(
            name="Approved Target Population with final filters",
            status="APPROVED",
        )

        tp.candidate_list_targeting_criteria = cls.get_targeting_criteria_for_rule(
            {
                "field_name": "residence_status",
                "arguments": ["CITIZEN"],
                "comparision_method": "EQUALS",
            }
        )
        tp.final_list_targeting_criteria = cls.get_targeting_criteria_for_rule(
            {
                "field_name": "size",
                "arguments": [2],
                "comparision_method": "EQUALS",
            }
        )
        tp.save()
        tp.households.set(cls.households)
        cls.target_population_approved_with_final_rule = tp

        tp = TargetPopulation(
            name="Approved Target Population", status="APPROVED"
        )

        tp.candidate_list_targeting_criteria = cls.get_targeting_criteria_for_rule(
            {
                "field_name": "residence_status",
                "arguments": ["CITIZEN"],
                "comparision_method": "EQUALS",
            }
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
        rule_filter = TargetingCriteriaRuleFilter(
            **rule_filter, targeting_criteria_rule=rule
        )
        rule_filter.save()
        return targeting_criteria

    def test_approve_target_population(self):
        self.snapshot_graphql_request(
            request_string=self.APPROVE_TARGET_MUTATION,
            context={"user": self.user},
            variables={
                "id": self.id_to_base64(
                    self.target_population_draft.id, "TargetPopulation"
                ),
                "programId": self.id_to_base64(self.program.id, "Program"),
            },
        )

    def test_approve_fail_target_population(self):
        self.snapshot_graphql_request(
            request_string=self.APPROVE_TARGET_MUTATION,
            context={"user": self.user},
            variables={
                "id": self.id_to_base64(
                    self.target_population_approved_with_final_rule.id,
                    "TargetPopulation",
                ),
                "programId": self.id_to_base64(self.program.id, "Program"),
            },
        )


class TestUnapproveTargetPopulationMutation(APITestCase):
    UNAPPROVE_TARGET_MUTATION = """
            mutation UnapproveTargetPopulation($id: ID!) {
              unapproveTargetPopulation(id: $id) {
                targetPopulation {
                  status
                  households {
                    totalCount
                    edges {
                      node {
                        size
                        residenceStatus
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
        cls.households = []

        (household, individuals) = create_household(
            {"size": 1, "residence_status": "CITIZEN",},
        )
        cls.household_size_1 = household
        (household, individuals) = create_household(
            {"size": 2, "residence_status": "CITIZEN",},
        )
        cls.household_size_2 = household
        cls.households.append(cls.household_size_1)
        cls.households.append(cls.household_size_2)

        tp = TargetPopulation(name="Draft Target Population", status="DRAFT")

        tp.candidate_list_targeting_criteria = cls.get_targeting_criteria_for_rule(
            {
                "field_name": "residence_status",
                "arguments": ["CITIZEN"],
                "comparision_method": "EQUALS",
            }
        )
        tp.save()
        cls.target_population_draft = tp

        tp = TargetPopulation(
            name="Approved Target Population with final filters",
            status="APPROVED",
        )

        tp.candidate_list_targeting_criteria = cls.get_targeting_criteria_for_rule(
            {
                "field_name": "residence_status",
                "arguments": ["CITIZEN"],
                "comparision_method": "EQUALS",
            }
        )
        tp.final_list_targeting_criteria = cls.get_targeting_criteria_for_rule(
            {
                "field_name": "size",
                "arguments": [2],
                "comparision_method": "EQUALS",
            }
        )
        tp.save()
        tp.households.set(cls.households)
        cls.target_population_approved_with_final_rule = tp

        tp = TargetPopulation(
            name="Approved Target Population", status="APPROVED"
        )

        tp.candidate_list_targeting_criteria = cls.get_targeting_criteria_for_rule(
            {
                "field_name": "residence_status",
                "arguments": ["CITIZEN"],
                "comparision_method": "EQUALS",
            }
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
        rule_filter = TargetingCriteriaRuleFilter(
            **rule_filter, targeting_criteria_rule=rule
        )
        rule_filter.save()
        return targeting_criteria

    def test_unapprove_target_population(self):
        self.snapshot_graphql_request(
            request_string=self.UNAPPROVE_TARGET_MUTATION,
            context={"user": self.user},
            variables={
                "id": self.id_to_base64(
                    self.target_population_approved_with_final_rule.id,
                    "TargetPopulation",
                )
            },
        )

    def test_unapprove_fail_target_population(self):
        self.snapshot_graphql_request(
            request_string=self.UNAPPROVE_TARGET_MUTATION,
            context={"user": self.user},
            variables={
                "id": self.id_to_base64(
                    self.target_population_draft.id, "TargetPopulation"
                )
            },
        )


class TestFinalizeTargetPopulationMutation(APITestCase):
    FINALIZE_TARGET_MUTATION = """
            mutation FinalizeTargetPopulation($id: ID!) {
              finalizeTargetPopulation(id: $id) {
                targetPopulation {
                  status
                  finalList{
                    edges{
                      node{
                        size
                        residenceStatus
                      }
                    }
                  }
                  households {
                    totalCount
                    edges {
                      node {
                        size
                        residenceStatus
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
        cls.households = []

        (household, individuals) = create_household(
            {"size": 1, "residence_status": "CITIZEN",},
        )
        cls.household_size_1 = household
        (household, individuals) = create_household(
            {"size": 2, "residence_status": "CITIZEN",},
        )
        cls.household_size_2 = household
        cls.households.append(cls.household_size_1)
        cls.households.append(cls.household_size_2)

        tp = TargetPopulation(name="Draft Target Population", status="DRAFT")

        tp.candidate_list_targeting_criteria = cls.get_targeting_criteria_for_rule(
            {
                "field_name": "residence_status",
                "arguments": ["CITIZEN"],
                "comparision_method": "EQUALS",
            }
        )
        tp.save()
        cls.target_population_draft = tp

        tp = TargetPopulation(
            name="Approved Target Population with final filters",
            status="APPROVED",
        )

        tp.candidate_list_targeting_criteria = cls.get_targeting_criteria_for_rule(
            {
                "field_name": "residence_status",
                "arguments": ["CITIZEN"],
                "comparision_method": "EQUALS",
            }
        )
        tp.final_list_targeting_criteria = cls.get_targeting_criteria_for_rule(
            {
                "field_name": "size",
                "arguments": [2],
                "comparision_method": "EQUALS",
            }
        )
        tp.save()
        tp.households.set(cls.households)
        cls.target_population_approved_with_final_rule = tp

        tp = TargetPopulation(
            name="Approved Target Population", status="APPROVED"
        )

        tp.candidate_list_targeting_criteria = cls.get_targeting_criteria_for_rule(
            {
                "field_name": "residence_status",
                "arguments": ["CITIZEN"],
                "comparision_method": "EQUALS",
            }
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
        rule_filter = TargetingCriteriaRuleFilter(
            **rule_filter, targeting_criteria_rule=rule
        )
        rule_filter.save()
        return targeting_criteria

    def test_finalize_target_population_with_final_criteria(self):
        self.snapshot_graphql_request(
            request_string=self.FINALIZE_TARGET_MUTATION,
            context={"user": self.user},
            variables={
                "id": self.id_to_base64(
                    self.target_population_approved_with_final_rule.id,
                    "TargetPopulation",
                )
            },
        )

    def test_finalize_target_population(self):
        self.snapshot_graphql_request(
            request_string=self.FINALIZE_TARGET_MUTATION,
            context={"user": self.user},
            variables={
                "id": self.id_to_base64(
                    self.target_population_approved.id, "TargetPopulation"
                )
            },
        )

    def test_finalize_fail_target_population(self):
        self.snapshot_graphql_request(
            request_string=self.FINALIZE_TARGET_MUTATION,
            context={"user": self.user},
            variables={
                "id": self.id_to_base64(
                    self.target_population_draft.id, "TargetPopulation",
                )
            },
        )
