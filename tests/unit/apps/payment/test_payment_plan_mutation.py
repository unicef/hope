from typing import TYPE_CHECKING, Any, List, Tuple
from unittest.mock import patch

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.household.fixtures import (
    IndividualRoleInHouseholdFactory,
    create_household_and_individuals,
)
from hct_mis_api.apps.household.models import ROLE_PRIMARY
from hct_mis_api.apps.payment.fixtures import (
    PaymentPlanFactory,
    generate_delivery_mechanisms,
)
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program, ProgramCycle
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.steficon.fixtures import RuleCommitFactory
from hct_mis_api.apps.steficon.models import Rule
from hct_mis_api.apps.targeting.fixtures import TargetingCriteriaFactory
from hct_mis_api.apps.targeting.models import (
    TargetingCollectorBlockRuleFilter,
    TargetingCollectorRuleFilterBlock,
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
    TargetingIndividualBlockRuleFilter,
    TargetingIndividualRuleFilterBlock,
)

if TYPE_CHECKING:
    from hct_mis_api.apps.household.models import Household, Individual

CREATE_PAYMENT_PLAN_MUTATION = """
mutation CreatePaymentPlan($input: CreatePaymentPlanInput!) {
    createPaymentPlan(input: $input) {
        paymentPlan {
            name
            status
        }
    }
}
"""

UPDATE_PAYMENT_PLAN_MUTATION = """
mutation UpdatePaymentPlan($input: UpdatePaymentPlanInput!) {
    updatePaymentPlan(input: $input) {
        paymentPlan {
            name
            status
        }
    }
}
"""

DELETE_PAYMENT_PLAN_MUTATION = """
mutation DeletePaymentPlan($paymentPlanId: ID!) {
    deletePaymentPlan(paymentPlanId: $paymentPlanId) {
        paymentPlan {
            name
            status
            isRemoved
        }
    }
}
"""

SET_STEFICON_RULE_ON_TP_MUTATION = """
mutation setSteficonRuleOnTargetPopulation($paymentPlanId: ID!, $steficonRuleId: ID) {
    setSteficonRuleOnTargetPopulation(paymentPlanId: $paymentPlanId, steficonRuleId: $steficonRuleId) {
        paymentPlan {
            name
            status
        }
    }
}
"""

COPY_TARGETING_CRITERIA = """
mutation CopyTargetingCriteriaMutation($paymentPlanId: ID!, $programCycleId: ID!, $name: String!) {
  copyTargetingCriteria(name: $name, paymentPlanId: $paymentPlanId, programCycleId: $programCycleId){
    paymentPlan{
      name
      status
    }
  }
}
"""


class TestPaymentPlanMutation(APITestCase):
    @classmethod
    def create_household_and_individual(cls) -> Tuple["Household", "Individual"]:
        household, individuals = create_household_and_individuals(
            household_data={
                "registration_data_import": cls.registration_data_import,
                "business_area": cls.business_area,
                "program": cls.program,
            },
            individuals_data=[{}],
        )
        IndividualRoleInHouseholdFactory(household=household, individual=individuals[0], role=ROLE_PRIMARY)
        return household, individuals[0]

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        partner = PartnerFactory(name="Partner")
        cls.user = UserFactory.create(partner=partner)
        cls.program = ProgramFactory(status=Program.ACTIVE, cycle__title="Cycle1")
        cls.cycle = cls.program.cycles.first()
        cls.registration_data_import = RegistrationDataImportFactory(
            business_area=cls.business_area, program=cls.program
        )
        cls.household_1, cls.individual_1 = cls.create_household_and_individual()
        cls.household_1.refresh_from_db()
        cls.household_2, cls.individual_2 = cls.create_household_and_individual()
        cls.household_2.refresh_from_db()

        cls.data_collecting_type = DataCollectingType.objects.create(
            code="full", description="Full individual collected", active=True, type="STANDARD"
        )
        cls.data_collecting_type.limit_to.add(cls.business_area)
        generate_delivery_mechanisms()

    @parameterized.expand(
        [
            ("without_permission", []),
            ("with_permission", [Permissions.PM_CREATE]),
        ]
    )
    @patch("hct_mis_api.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0)
    def test_create_targeting_mutation(
        self, _: Any, permissions: List[Permissions], mock_get_exchange_rate: Any
    ) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        self.snapshot_graphql_request(
            request_string=CREATE_PAYMENT_PLAN_MUTATION,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
            variables={
                "input": {
                    "name": "paymentPlanName",
                    "programCycleId": self.id_to_base64(self.cycle.id, "ProgramCycleNode"),
                    "excludedIds": "",
                    "targetingCriteria": {
                        "flagExcludeIfActiveAdjudicationTicket": False,
                        "flagExcludeIfOnSanctionList": False,
                        "rules": [
                            {
                                "collectorsFiltersBlocks": [],
                                "householdsFiltersBlocks": [],
                                "householdIds": f"{self.household_1.unicef_id}, {self.household_2.unicef_id}",
                                "individualIds": "",
                                "individualsFiltersBlocks": [],
                            }
                        ],
                    },
                },
            },
        )

    @parameterized.expand(
        [
            ("without_permission", []),
            ("with_permission", [Permissions.PM_CREATE]),
            ("with_tp_permission", [Permissions.TARGETING_UPDATE]),
        ]
    )
    @patch("hct_mis_api.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0)
    def test_update_targeting_mutation(
        self, name: Any, permissions: List[Permissions], mock_get_exchange_rate: Any
    ) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        payment_plan = PaymentPlanFactory(
            name="OldName", status=PaymentPlan.Status.TP_OPEN, program_cycle=self.cycle, created_by=self.user
        )
        self.snapshot_graphql_request(
            request_string=UPDATE_PAYMENT_PLAN_MUTATION,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
            variables={
                "input": {
                    "paymentPlanId": self.id_to_base64(payment_plan.id, "PaymentPlanNode"),
                    "name": f"NewPaymentPlanName_{name}",
                    "targetingCriteria": {
                        "flagExcludeIfActiveAdjudicationTicket": False,
                        "flagExcludeIfOnSanctionList": False,
                        "rules": [
                            {
                                "collectorsFiltersBlocks": [],
                                "householdsFiltersBlocks": [],
                                "householdIds": f"{self.household_1.unicef_id}",
                                "individualIds": "",
                                "individualsFiltersBlocks": [],
                            }
                        ],
                    },
                },
            },
        )

    @parameterized.expand(
        [
            ("without_permission", []),
            ("with_permission", [Permissions.PM_CREATE]),
        ]
    )
    def test_delete_payment_plan_mutation(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        payment_plan = PaymentPlanFactory(
            name="DeletePaymentPlan",
            status=PaymentPlan.Status.OPEN,
            program_cycle=self.cycle,
            created_by=self.user,
        )
        self.snapshot_graphql_request(
            request_string=DELETE_PAYMENT_PLAN_MUTATION,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
            variables={
                "paymentPlanId": self.id_to_base64(payment_plan.id, "PaymentPlanNode"),
            },
        )

    @parameterized.expand(
        [
            ("without_permission", []),
            ("with_permission", [Permissions.TARGETING_UPDATE]),
            ("with_permission_without_rule_engine_id", [Permissions.TARGETING_UPDATE]),
        ]
    )
    def test_set_steficon_target_population_mutation(self, name: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        payment_plan = PaymentPlanFactory(
            name="TestSetSteficonTP",
            status=PaymentPlan.Status.OPEN,
            program_cycle=self.cycle,
            created_by=self.user,
        )

        rule_for_tp = RuleCommitFactory(rule__type=Rule.TYPE_TARGETING, version=11)

        rule_commit_id = (
            self.id_to_base64(rule_for_tp.rule.id, "RuleCommitNode")
            if name != "with_permission_without_rule_engine_id"
            else None
        )
        self.snapshot_graphql_request(
            request_string=SET_STEFICON_RULE_ON_TP_MUTATION,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
            variables={
                "paymentPlanId": self.id_to_base64(payment_plan.id, "PaymentPlanNode"),
                "steficonRuleId": rule_commit_id,
            },
        )

    @parameterized.expand(
        [
            ("without_permission", []),
            ("with_permission", [Permissions.TARGETING_DUPLICATE]),
        ]
    )
    def test_copy_target_criteria_mutation(self, name: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        # create criteria
        tc = TargetingCriteriaFactory()
        tcr = TargetingCriteriaRule(household_ids="HH-001", individual_ids="IND-001")
        tcr.targeting_criteria = tc
        tcr.save()
        TargetingCriteriaRuleFilter.objects.create(
            targeting_criteria_rule=tcr,
            comparison_method="LESS_THAN",
            field_name="size",
            arguments=[1],
        )
        individuals_filters_block = TargetingIndividualRuleFilterBlock(
            targeting_criteria_rule=tcr, target_only_hoh=False
        )
        individuals_filters_block.save()
        TargetingIndividualBlockRuleFilter.objects.create(
            individuals_filters_block=individuals_filters_block,
            comparison_method="LESS_THAN",
            field_name="age",
            arguments=[40],
        )
        col_block = TargetingCollectorRuleFilterBlock(targeting_criteria_rule=tcr)
        col_block.save()
        TargetingCollectorBlockRuleFilter.objects.create(
            collector_block_filters=col_block,
            comparison_method="EQUALS",
            field_name="delivery_data_field__random_name",
            arguments=["Yes"],
        )

        payment_plan = PaymentPlanFactory(
            name="New PaymentPlan",
            status=PaymentPlan.Status.OPEN,
            program_cycle=self.cycle,
            created_by=self.user,
            targeting_criteria=tc,
        )

        self.cycle.status = ProgramCycle.FINISHED
        self.cycle.save()
        # invalid cycle status
        self.snapshot_graphql_request(
            request_string=COPY_TARGETING_CRITERIA,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
            variables={
                "paymentPlanId": self.id_to_base64(payment_plan.id, "PaymentPlanNode"),
                "programCycleId": self.id_to_base64(self.cycle.id, "CycleNode"),
                "name": "New PaymentPlan",
            },
        )

        if name == "with_permission":
            self.cycle.status = ProgramCycle.ACTIVE
            self.cycle.save()
            # name duplicated
            self.snapshot_graphql_request(
                request_string=COPY_TARGETING_CRITERIA,
                context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
                variables={
                    "paymentPlanId": self.id_to_base64(payment_plan.id, "PaymentPlanNode"),
                    "programCycleId": self.id_to_base64(self.cycle.id, "CycleNode"),
                    "name": "New PaymentPlan",
                },
            )

            self.assertEqual(TargetingCollectorRuleFilterBlock.objects.all().count(), 1)
            self.assertEqual(TargetingCollectorBlockRuleFilter.objects.all().count(), 1)
            self.assertEqual(TargetingCriteriaRule.objects.all().count(), 1)
            self.assertEqual(PaymentPlan.objects.all().count(), 1)

            self.snapshot_graphql_request(
                request_string=COPY_TARGETING_CRITERIA,
                context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
                variables={
                    "paymentPlanId": self.id_to_base64(payment_plan.id, "PaymentPlanNode"),
                    "programCycleId": self.id_to_base64(self.cycle.id, "CycleNode"),
                    "name": "Let's have One new Payment Plan XD",
                },
            )

            self.assertEqual(TargetingCollectorRuleFilterBlock.objects.all().count(), 2)
            self.assertEqual(TargetingCollectorBlockRuleFilter.objects.all().count(), 2)
            self.assertEqual(TargetingCriteriaRule.objects.all().count(), 2)
            self.assertEqual(PaymentPlan.objects.all().count(), 2)
