from typing import TYPE_CHECKING, Any, List, Tuple
from unittest.mock import patch

import pytest
from parameterized import parameterized

from tests.extras.test_utils.factories.account import (
    BusinessAreaFactory,
    PartnerFactory,
    UserFactory,
)
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from tests.extras.test_utils.factories.core import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from tests.extras.test_utils.factories.household import (
    IndividualRoleInHouseholdFactory,
    create_household_and_individuals,
)
from hct_mis_api.apps.household.models import ROLE_PRIMARY
from tests.extras.test_utils.factories.payment import (
    PaymentPlanFactory,
    generate_delivery_mechanisms,
)
from hct_mis_api.apps.payment.models import PaymentPlan
from tests.extras.test_utils.factories.program import ProgramFactory
from hct_mis_api.apps.program.models import Program, ProgramCycle
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.steficon.fixtures import RuleCommitFactory
from hct_mis_api.apps.steficon.models import Rule
from hct_mis_api.apps.targeting.models import (
    TargetingCollectorBlockRuleFilter,
    TargetingCollectorRuleFilterBlock,
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
    TargetingIndividualBlockRuleFilter,
    TargetingIndividualRuleFilterBlock,
)
from hct_mis_api.contrib.vision.fixtures import FundsCommitmentFactory
from hct_mis_api.contrib.vision.models import FundsCommitmentItem

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
mutation setSteficonRuleOnPaymentPlanPaymentList($paymentPlanId: ID!, $steficonRuleId: ID!, $version: BigInt) {
    setSteficonRuleOnPaymentPlanPaymentList(paymentPlanId: $paymentPlanId, steficonRuleId: $steficonRuleId, version: $version) {
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


ASSIGN_FUNDS_COMMITMENTS = """
mutation AssignFundsCommitmentsMutation($paymentPlanId: ID!, $fundCommitmentItemsIds: [String]) {
  assignFundsCommitments(paymentPlanId: $paymentPlanId, fundCommitmentItemsIds: $fundCommitmentItemsIds){
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
        ]
    )
    def test_set_steficon_target_population_mutation(self, name: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        payment_plan = PaymentPlanFactory(
            name="TestSetSteficonTP",
            status=PaymentPlan.Status.TP_LOCKED,
            program_cycle=self.cycle,
            created_by=self.user,
        )

        rule_for_tp = RuleCommitFactory(rule__type=Rule.TYPE_TARGETING, version=11)

        rule_commit_id = self.id_to_base64(rule_for_tp.rule.id, "RuleCommitNode")
        self.snapshot_graphql_request(
            request_string=SET_STEFICON_RULE_ON_TP_MUTATION,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
            variables={
                "paymentPlanId": self.id_to_base64(payment_plan.id, "PaymentPlanNode"),
                "steficonRuleId": rule_commit_id,
                "version": payment_plan.version,
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
        payment_plan = PaymentPlanFactory(
            name="New PaymentPlan",
            status=PaymentPlan.Status.OPEN,
            program_cycle=self.cycle,
            created_by=self.user,
        )

        tcr = TargetingCriteriaRule.objects.create(
            household_ids="HH-001", individual_ids="IND-001", payment_plan=payment_plan
        )
        TargetingCriteriaRuleFilter.objects.create(
            targeting_criteria_rule=tcr,
            comparison_method="LESS_THAN",
            field_name="size",
            arguments=[1],
        )
        individuals_filters_block = TargetingIndividualRuleFilterBlock.objects.create(
            targeting_criteria_rule=tcr, target_only_hoh=False
        )
        TargetingIndividualBlockRuleFilter.objects.create(
            individuals_filters_block=individuals_filters_block,
            comparison_method="LESS_THAN",
            field_name="age",
            arguments=[40],
        )
        col_block = TargetingCollectorRuleFilterBlock.objects.create(targeting_criteria_rule=tcr)
        TargetingCollectorBlockRuleFilter.objects.create(
            collector_block_filters=col_block,
            comparison_method="EQUALS",
            field_name="delivery_data_field__random_name",
            arguments=[True],
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

    @pytest.mark.elasticsearch
    def test_assign_funds_commitments_mutation(self) -> None:
        ukr_ba = BusinessAreaFactory(name="Ukraine")
        FundsCommitmentFactory(
            funds_commitment_number="123",
            funds_commitment_item="001",
            business_area=self.business_area.code,
            office=self.business_area,
        )
        FundsCommitmentFactory(
            funds_commitment_number="123", funds_commitment_item="002", business_area=ukr_ba.code, office=ukr_ba
        )
        FundsCommitmentFactory(
            funds_commitment_number="345",
            funds_commitment_item="001",
            business_area=self.business_area.code,
            office=self.business_area,
        )
        FundsCommitmentFactory(
            funds_commitment_number="345",
            funds_commitment_item="002",
            business_area=self.business_area.code,
            office=self.business_area,
        )

        payment_plan = PaymentPlanFactory(
            name="FCTP1",
            status=PaymentPlan.Status.LOCKED,
            program_cycle=self.cycle,
            created_by=self.user,
        )
        payment_plan2 = PaymentPlanFactory(
            name="FCTP2",
            status=PaymentPlan.Status.LOCKED,
            program_cycle=self.cycle,
            created_by=self.user,
        )

        self.snapshot_graphql_request(
            request_string=ASSIGN_FUNDS_COMMITMENTS,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
            variables={
                "paymentPlanId": self.id_to_base64(payment_plan.id, "PaymentPlanNode"),
                "fundCommitmentItemsIds": [],
            },
        )

        self.create_user_role_with_permissions(self.user, [Permissions.PM_ASSIGN_FUNDS_COMMITMENTS], self.business_area)

        self.snapshot_graphql_request(
            request_string=ASSIGN_FUNDS_COMMITMENTS,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
            variables={
                "paymentPlanId": self.id_to_base64(payment_plan.id, "PaymentPlanNode"),
                "fundCommitmentItemsIds": [],
            },
        )

        payment_plan.status = PaymentPlan.Status.IN_REVIEW
        payment_plan.save()

        fc1 = FundsCommitmentItem.objects.get(
            funds_commitment_group__funds_commitment_number="123", funds_commitment_item="001"
        )
        fc1.payment_plan = payment_plan2
        fc1.save()
        self.snapshot_graphql_request(
            request_string=ASSIGN_FUNDS_COMMITMENTS,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
            variables={
                "paymentPlanId": self.id_to_base64(payment_plan.id, "PaymentPlanNode"),
                "fundCommitmentItemsIds": [fc1.rec_serial_number],
            },
        )

        fc2 = FundsCommitmentItem.objects.get(
            funds_commitment_group__funds_commitment_number="123", funds_commitment_item="002"
        )
        self.snapshot_graphql_request(
            request_string=ASSIGN_FUNDS_COMMITMENTS,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
            variables={
                "paymentPlanId": self.id_to_base64(payment_plan.id, "PaymentPlanNode"),
                "fundCommitmentItemsIds": [fc2.rec_serial_number],
            },
        )

        fc3 = FundsCommitmentItem.objects.get(
            funds_commitment_group__funds_commitment_number="345", funds_commitment_item="001"
        )
        fc3.payment_plan = payment_plan
        fc3.save()
        fc4 = FundsCommitmentItem.objects.get(
            funds_commitment_group__funds_commitment_number="345", funds_commitment_item="002"
        )
        self.snapshot_graphql_request(
            request_string=ASSIGN_FUNDS_COMMITMENTS,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
            variables={
                "paymentPlanId": self.id_to_base64(payment_plan.id, "PaymentPlanNode"),
                "fundCommitmentItemsIds": [fc4.rec_serial_number],
            },
        )
        payment_plan.refresh_from_db()
        self.assertEqual(payment_plan.funds_commitments.count(), 1)
        self.assertEqual(payment_plan.funds_commitments.first(), fc4)
