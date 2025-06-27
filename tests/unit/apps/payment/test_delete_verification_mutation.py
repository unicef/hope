from typing import Any, List

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.payment.fixtures import (
    PaymentPlanFactory,
    PaymentVerificationSummaryFactory,
    create_payment_verification_plan_with_status,
)
from hct_mis_api.apps.payment.models import PaymentVerificationPlan
from hct_mis_api.apps.program.fixtures import ProgramFactory


class TestDeleteVerificationMutation(APITestCase):
    MUTATION = """
        mutation DeleteVerification($paymentVerificationPlanId: ID!){
          deletePaymentVerificationPlan(paymentVerificationPlanId:$paymentVerificationPlanId) {
            paymentPlan{
            objType
                verificationPlans {
                    edges {
                        node {
                            status
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
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        cls.program = ProgramFactory(business_area=cls.business_area)
        cls.program.admin_areas.set(Area.objects.order_by("?")[:3])
        cls.payment_plan = PaymentPlanFactory(
            name="TEST",
            program_cycle=cls.program.cycles.first(),
            business_area=cls.business_area,
            created_by=cls.user,
        )
        PaymentVerificationSummaryFactory(payment_plan=cls.payment_plan)
        cls.verification = cls.payment_plan.payment_verification_plans.first()

    @parameterized.expand(
        [
            ("with_permission", [Permissions.PAYMENT_VERIFICATION_DELETE]),
            ("without_permission", []),
        ]
    )
    def test_delete_pending_verification_plan(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        self.create_active_payment_verification_plan()
        payment_verification_plan = self.create_pending_payment_verification_plan()

        self.snapshot_graphql_request(
            request_string=self.MUTATION,
            context={"user": self.user},
            variables={
                "paymentVerificationPlanId": [
                    self.id_to_base64(payment_verification_plan.id, "PaymentVerificationPlanNode")
                ]
            },
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.PAYMENT_VERIFICATION_DELETE]),
            ("without_permission", []),
        ]
    )
    def test_delete_active_verification_plan(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        payment_verification_plan = self.create_active_payment_verification_plan()
        self.create_pending_payment_verification_plan()

        self.snapshot_graphql_request(
            request_string=self.MUTATION,
            context={"user": self.user},
            variables={
                "paymentVerificationPlanId": [
                    self.id_to_base64(payment_verification_plan.id, "PaymentVerificationPlanNode")
                ]
            },
        )

    def create_pending_payment_verification_plan(self) -> PaymentVerificationPlan:
        return create_payment_verification_plan_with_status(
            self.payment_plan,
            self.user,
            self.business_area,
            self.program,
            PaymentVerificationPlan.STATUS_PENDING,
        )

    def create_active_payment_verification_plan(self) -> PaymentVerificationPlan:
        return create_payment_verification_plan_with_status(
            self.payment_plan,
            self.user,
            self.business_area,
            self.program,
            PaymentVerificationPlan.STATUS_ACTIVE,
        )
