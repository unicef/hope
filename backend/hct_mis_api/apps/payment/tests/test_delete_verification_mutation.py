from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.payment.fixtures import (
    CashPlanFactory,
    create_payment_verification_plan_with_status,
)
from hct_mis_api.apps.payment.models import CashPlanPaymentVerification
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.targeting.fixtures import (
    TargetingCriteriaFactory,
    TargetPopulationFactory,
)


class TestDeleteVerificationMutation(APITestCase):
    MUTATION = """
        mutation DeleteVerification($cashPlanVerificationId: ID!){
          deleteCashPlanPaymentVerification(cashPlanVerificationId:$cashPlanVerificationId) {
            cashPlan{
                name
                verifications {
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
    def setUpTestData(cls):
        cls.user = UserFactory.create()
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        cls.program = ProgramFactory(business_area=cls.business_area)
        cls.program.admin_areas.set(Area.objects.order_by("?")[:3])
        cls.target_population = TargetPopulationFactory(
            created_by=cls.user,
            targeting_criteria=(TargetingCriteriaFactory()),
            business_area=cls.business_area,
        )
        cls.cash_plan = CashPlanFactory(
            name="TEST",
            program=cls.program,
            business_area=cls.business_area,
        )
        cls.verification = cls.cash_plan.verifications.first()

    @parameterized.expand(
        [
            ("with_permission", [Permissions.PAYMENT_VERIFICATION_DELETE]),
            ("without_permission", []),
        ]
    )
    def test_delete_pending_verification_plan(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        self.create_active_payment_verification_plan()
        cash_plan_payment_verification = self.create_pending_payment_verification_plan()

        self.snapshot_graphql_request(
            request_string=self.MUTATION,
            context={"user": self.user},
            variables={
                "cashPlanVerificationId": [
                    self.id_to_base64(cash_plan_payment_verification.id, "CashPlanPaymentVerificationNode")
                ]
            },
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.PAYMENT_VERIFICATION_DELETE]),
            ("without_permission", []),
        ]
    )
    def test_delete_active_verification_plan(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        cash_plan_payment_verification = self.create_active_payment_verification_plan()
        self.create_pending_payment_verification_plan()

        self.snapshot_graphql_request(
            request_string=self.MUTATION,
            context={"user": self.user},
            variables={
                "cashPlanVerificationId": [
                    self.id_to_base64(cash_plan_payment_verification.id, "CashPlanPaymentVerificationNode")
                ]
            },
        )

    def create_pending_payment_verification_plan(self):
        return create_payment_verification_plan_with_status(
            self.cash_plan,
            self.user,
            self.business_area,
            self.program,
            self.target_population,
            CashPlanPaymentVerification.STATUS_PENDING,
        )

    def create_active_payment_verification_plan(self):
        return create_payment_verification_plan_with_status(
            self.cash_plan,
            self.user,
            self.business_area,
            self.program,
            self.target_population,
            CashPlanPaymentVerification.STATUS_ACTIVE,
        )
