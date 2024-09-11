from typing import Any, Dict, List

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
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
    PeriodicFieldData,
)
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.household.models import DISABLED
from hct_mis_api.apps.periodic_data_update.utils import populate_pdu_with_null_values
from hct_mis_api.apps.program.fixtures import ProgramCycleFactory, ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.targeting.choices import FlexFieldClassification
from hct_mis_api.apps.targeting.models import (
    TargetingCriteria,
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
    TargetingIndividualBlockRuleFilter,
    TargetingIndividualRuleFilterBlock,
    TargetPopulation,
)
from hct_mis_api.apps.targeting.services.targeting_stats_refresher import full_rebuild


class TestTargetPopulationQuery(APITestCase):
    ALL_TARGET_POPULATION_QUERY = """
            query AllTargetPopulation($totalHouseholdsCountMin: Int, $programCycle: String) {
                allTargetPopulation(totalHouseholdsCountMin: $totalHouseholdsCountMin, businessArea: "afghanistan", programCycle: $programCycle orderBy: "created_at") {
                    edges {
                        node {
                             name
                             status
                             totalHouseholdsCount
                             totalIndividualsCount
                        }
                    }
                }
            }
            """

    ALL_TARGET_POPULATION_ORDER_BY_CREATED_BY_QUERY = """
            query AllTargetPopulation($totalHouseholdsCountMin: Int) {
                allTargetPopulation(totalHouseholdsCountMin:$totalHouseholdsCountMin, businessArea: "afghanistan", orderBy: "created_by") {
                    edges {
                        node {
                             name
                             status
                             totalHouseholdsCount
                             totalIndividualsCount
                             createdBy {
                                firstName
                                lastName
                            }
                        }
                    }
                }
            }
            """

    TARGET_POPULATION_QUERY = """
       query TargetPopulation($id:ID!) {
          targetPopulation(id:$id){
            name
            status
            hasEmptyCriteria
            hasEmptyIdsCriteria
            totalHouseholdsCount
            totalIndividualsCount
            targetingCriteria{
              rules{
                filters{
                  comparisonMethod
                  fieldName
                  flexFieldClassification
                  arguments
                  fieldAttribute{
                    labelEn
                    type
                  }
                }
                individualsFiltersBlocks{
                  individualBlockFilters{
                    comparisonMethod
                    fieldName
                    arguments
                    flexFieldClassification
                    roundNumber
                    fieldAttribute
                    {
                      labelEn
                      type
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
        create_afghanistan()
        cls.partner = PartnerFactory(name="TestPartner")
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.program = ProgramFactory(name="test_program", status=Program.ACTIVE)
        cls.cycle_2 = ProgramCycleFactory(program=cls.program)

        _ = create_household(
            {"size": 1, "residence_status": "HOST", "business_area": cls.business_area, "program": cls.program},
        )
        (household, individuals) = create_household(
            {"size": 1, "residence_status": "HOST", "business_area": cls.business_area, "program": cls.program},
        )
        cls.household_size_1 = household
        cls.household_residence_status_citizen = cls.household_size_1
        (household, individuals) = create_household(
            {"size": 2, "residence_status": "REFUGEE", "business_area": cls.business_area, "program": cls.program},
        )
        cls.household_residence_status_refugee = household
        cls.household_size_2 = cls.household_residence_status_refugee

        cls.user = UserFactory(partner=cls.partner, first_name="Test", last_name="User")
        user_first = UserFactory(partner=cls.partner, first_name="First", last_name="User")
        user_second = UserFactory(partner=cls.partner, first_name="Second", last_name="User")
        user_third = UserFactory(partner=cls.partner, first_name="Third", last_name="User")
        targeting_criteria = cls.get_targeting_criteria_for_rule(
            {"field_name": "size", "arguments": [2], "comparison_method": "EQUALS"}
        )
        cls.target_population_size_2 = TargetPopulation(
            name="target_population_size_2",
            created_by=cls.user,
            targeting_criteria=targeting_criteria,
            business_area=cls.business_area,
            program=cls.program,
        )
        cls.target_population_size_2.save()
        cls.target_population_size_2 = full_rebuild(cls.target_population_size_2)
        cls.target_population_size_2.save()
        targeting_criteria = cls.get_targeting_criteria_for_rule(
            {"field_name": "residence_status", "arguments": ["REFUGEE"], "comparison_method": "EQUALS"}
        )
        cls.target_population_residence_status = TargetPopulation(
            name="target_population_residence_status",
            created_by=user_first,
            business_area=cls.business_area,
            targeting_criteria=targeting_criteria,
            program=cls.program,
            program_cycle=cls.cycle_2,
        )
        cls.target_population_residence_status.save()
        cls.target_population_residence_status = full_rebuild(cls.target_population_residence_status)
        cls.target_population_residence_status.save()

        targeting_criteria = cls.get_targeting_criteria_for_rule(
            {"field_name": "size", "arguments": [1], "comparison_method": "EQUALS"}
        )
        cls.target_population_size_1_approved = TargetPopulation(
            name="target_population_size_1_approved",
            created_by=user_second,
            targeting_criteria=targeting_criteria,
            status=TargetPopulation.STATUS_LOCKED,
            business_area=cls.business_area,
            program=cls.program,
        )
        cls.target_population_size_1_approved.save()
        cls.target_population_size_1_approved = full_rebuild(cls.target_population_size_1_approved)
        cls.target_population_size_1_approved.save()

        pdu_data_string = PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.STRING,
            number_of_rounds=2,
            rounds_names=["Round 1", "Round 2"],
        )
        cls.pdu_field_string = FlexibleAttributeForPDUFactory(
            program=cls.program,
            label="PDU Field STRING",
            pdu_data=pdu_data_string,
        )
        (household, individuals) = create_household(
            {"size": 3, "residence_status": "HOST", "business_area": cls.business_area, "program": cls.program},
        )
        individual_with_pdu_value = individuals[0]
        populate_pdu_with_null_values(cls.program, individual_with_pdu_value.flex_fields)
        individual_with_pdu_value.flex_fields[cls.pdu_field_string.name]["1"]["value"] = "some"
        individual_with_pdu_value.save()
        targeting_criteria = TargetingCriteria()
        targeting_criteria.save()
        rule = TargetingCriteriaRule(targeting_criteria=targeting_criteria)
        rule.save()
        individuals_filters_block = TargetingIndividualRuleFilterBlock(
            targeting_criteria_rule=rule, target_only_hoh=False
        )
        individuals_filters_block.save()
        rule_filter = TargetingIndividualBlockRuleFilter(
            individuals_filters_block=individuals_filters_block,
            comparison_method="EQUALS",
            field_name=cls.pdu_field_string.name,
            arguments=["some"],
            round_number=1,
            flex_field_classification=FlexFieldClassification.FLEX_FIELD_PDU,
        )
        rule_filter.save()
        cls.target_population_with_pdu_filter = TargetPopulation(
            name="target_population_with_pdu_filter",
            created_by=user_third,
            targeting_criteria=targeting_criteria,
            status=TargetPopulation.STATUS_LOCKED,
            business_area=cls.business_area,
            program=cls.program,
        )
        cls.target_population_with_pdu_filter.save()
        cls.target_population_with_pdu_filter = full_rebuild(cls.target_population_with_pdu_filter)
        cls.target_population_with_pdu_filter.save()

        (household, individuals) = create_household(
            {"size": 3, "residence_status": "HOST", "business_area": cls.business_area, "program": cls.program},
        )
        individual = individuals[0]
        individual.disability = DISABLED
        individual.save()
        targeting_criteria = TargetingCriteria()
        targeting_criteria.save()
        rule = TargetingCriteriaRule(targeting_criteria=targeting_criteria)
        rule.save()
        individuals_filters_block = TargetingIndividualRuleFilterBlock(
            targeting_criteria_rule=rule, target_only_hoh=False
        )
        individuals_filters_block.save()
        rule_filter = TargetingIndividualBlockRuleFilter(
            individuals_filters_block=individuals_filters_block,
            comparison_method="EQUALS",
            field_name="disability",
            arguments=["disabled"],
            flex_field_classification=FlexFieldClassification.NOT_FLEX_FIELD,
        )
        rule_filter.save()
        cls.target_population_with_individual_filter = TargetPopulation(
            name="target_population_with_individual_filter",
            created_by=user_third,
            targeting_criteria=targeting_criteria,
            status=TargetPopulation.STATUS_LOCKED,
            business_area=cls.business_area,
            program=cls.program,
        )
        cls.target_population_with_individual_filter.save()
        cls.target_population_with_individual_filter = full_rebuild(cls.target_population_with_individual_filter)
        cls.target_population_with_individual_filter.save()

        # SW Program
        cls.program_sw = ProgramFactory(
            name="test_program_sw",
            status=Program.ACTIVE,
            business_area=cls.business_area,
            data_collecting_type__type=DataCollectingType.Type.SOCIAL,
        )
        pdu_data_string_sw = PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.STRING,
            number_of_rounds=2,
            rounds_names=["Round 1", "Round 2"],
        )
        cls.pdu_field_string_for_sw = FlexibleAttributeForPDUFactory(
            program=cls.program_sw,
            label="PDU Field STRING for SW",
            pdu_data=pdu_data_string_sw,
        )
        targeting_criteria = cls.get_targeting_criteria_for_rule(
            {
                "field_name": cls.pdu_field_string.name,
                "arguments": ["Test"],
                "comparison_method": "EQUALS",
                "flex_field_classification": "FLEX_FIELD_PDU",
                "round_number": 1,
            }
        )
        cls.target_population_with_pdu_filter_for_sw = TargetPopulation(
            name="target_population_with_pdu_filter_for_sw",
            created_by=user_second,
            targeting_criteria=targeting_criteria,
            status=TargetPopulation.STATUS_LOCKED,
            business_area=cls.business_area,
            program=cls.program_sw,
        )
        cls.target_population_with_pdu_filter_for_sw.save()
        cls.target_population_with_pdu_filter_for_sw = full_rebuild(cls.target_population_with_pdu_filter_for_sw)
        cls.target_population_with_pdu_filter_for_sw.save()

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
                [Permissions.TARGETING_VIEW_LIST],
                {},
            ),
            ("without_permission", [], {}),
            (
                "with_permission_filter_totalHouseholdsCountMin",
                [Permissions.TARGETING_VIEW_LIST],
                {"totalHouseholdsCountMin": 1},
            ),
        ]
    )
    def test_simple_all_targets_query(self, _: Any, permissions: List[Permissions], variables: Dict) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area, self.program)

        self.snapshot_graphql_request(
            request_string=TestTargetPopulationQuery.ALL_TARGET_POPULATION_QUERY,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables=variables,
        )

    def test_all_targets_query_order_by_created_by(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.TARGETING_VIEW_LIST], self.business_area, self.program
        )

        self.snapshot_graphql_request(
            request_string=TestTargetPopulationQuery.ALL_TARGET_POPULATION_ORDER_BY_CREATED_BY_QUERY,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.TARGETING_VIEW_DETAILS],
            ),
            (
                "without_permission",
                [],
            ),
        ]
    )
    def test_simple_target_query(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area, self.program)
        self.snapshot_graphql_request(
            request_string=TestTargetPopulationQuery.TARGET_POPULATION_QUERY,
            context={"user": self.user},
            variables={
                "id": self.id_to_base64(
                    self.target_population_size_1_approved.id,
                    "TargetPopulationNode",
                )
            },
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.TARGETING_VIEW_DETAILS],
            ),
            (
                "without_permission",
                [],
            ),
        ]
    )
    def test_simple_target_query_next(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area, self.program)

        self.snapshot_graphql_request(
            request_string=TestTargetPopulationQuery.TARGET_POPULATION_QUERY,
            context={"user": self.user},
            variables={
                "id": self.id_to_base64(
                    self.target_population_residence_status.id,
                    "TargetPopulationNode",
                )
            },
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.TARGETING_VIEW_DETAILS],
            ),
            (
                "without_permission",
                [],
            ),
        ]
    )
    def test_simple_target_query_pdu(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area, self.program)
        self.snapshot_graphql_request(
            request_string=TestTargetPopulationQuery.TARGET_POPULATION_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                },
            },
            variables={
                "id": self.id_to_base64(
                    self.target_population_with_pdu_filter.id,
                    "TargetPopulationNode",
                )
            },
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.TARGETING_VIEW_DETAILS],
            ),
            (
                "without_permission",
                [],
            ),
        ]
    )
    def test_simple_target_query_pdu_for_sw_program(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area, self.program_sw)
        print("pduduuu")
        self.snapshot_graphql_request(
            request_string=TestTargetPopulationQuery.TARGET_POPULATION_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                    "Program": self.id_to_base64(self.program_sw.id, "ProgramNode"),
                },
            },
            variables={
                "id": self.id_to_base64(
                    self.target_population_with_pdu_filter_for_sw.id,
                    "TargetPopulationNode",
                )
            },
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.TARGETING_VIEW_DETAILS],
            ),
            (
                "without_permission",
                [],
            ),
        ]
    )
    def test_simple_target_query_individual_filter(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area, self.program)
        self.snapshot_graphql_request(
            request_string=TestTargetPopulationQuery.TARGET_POPULATION_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                },
            },
            variables={
                "id": self.id_to_base64(
                    self.target_population_with_individual_filter.id,
                    "TargetPopulationNode",
                )
            },
        )

    def test_all_targets_query_filter_by_cycle(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.TARGETING_VIEW_LIST], self.business_area, self.program
        )
        self.snapshot_graphql_request(
            request_string=TestTargetPopulationQuery.ALL_TARGET_POPULATION_QUERY,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables={"programCycle": self.id_to_base64(self.cycle_2.id, "ProgramCycleNode")},
        )
