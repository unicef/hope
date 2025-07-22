from typing import Any, List

from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.household import (
    EntitlementCardFactory,
    create_household,
)
from extras.test_utils.factories.payment import (
    PaymentFactory,
    PaymentPlanFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
)
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from parameterized import parameterized

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.payment.models import PaymentVerification, PaymentVerificationPlan


class TestDiscardVerificationMutation(APITestCase):
    DISCARD_MUTATION = """
        mutation DiscardVerification($paymentVerificationPlanId: ID!){
          discardPaymentVerificationPlan(paymentVerificationPlanId:$paymentVerificationPlanId) {
            paymentPlan{
                objType
                verificationPlans {
                    edges {
                        node {
                            status
                            paymentRecordVerifications {
                                edges {
                                    node {
                                        status
                                    }
                                }
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
        super().setUpTestData()
        cls.user = UserFactory.create()
        create_afghanistan()
        payment_record_amount = 10
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        program = ProgramFactory(business_area=cls.business_area)
        program.admin_areas.set(Area.objects.order_by("?")[:3])

        payment_plan = PaymentPlanFactory(
            name="TEST",
            program_cycle=program.cycles.first(),
            business_area=cls.business_area,
        )
        PaymentVerificationSummaryFactory(payment_plan=payment_plan)
        payment_verification_plan = PaymentVerificationPlanFactory(
            payment_plan=payment_plan, verification_channel=PaymentVerificationPlan.VERIFICATION_CHANNEL_MANUAL
        )
        payment_verification_plan.status = PaymentVerificationPlan.STATUS_ACTIVE
        payment_verification_plan.save()
        for _ in range(payment_record_amount):
            registration_data_import = RegistrationDataImportFactory(
                imported_by=cls.user, business_area=cls.business_area
            )
            household, individuals = create_household(
                {
                    "registration_data_import": registration_data_import,
                    "admin_area": Area.objects.order_by("?").first(),
                    "program": program,
                },
                {"registration_data_import": registration_data_import},
            )

            payment = PaymentFactory(
                parent=payment_plan,
                household=household,
                currency="PLN",
            )
            PaymentVerificationFactory(
                payment_verification_plan=payment_verification_plan,
                payment=payment,
                status=PaymentVerification.STATUS_PENDING,
            )
            EntitlementCardFactory(household=household)
        cls.payment_plan = payment_plan
        cls.verification = payment_plan.payment_verification_plans.first()

    @parameterized.expand(
        [
            ("with_permission", [Permissions.PAYMENT_VERIFICATION_DISCARD]),
            ("without_permission", []),
        ]
    )
    def test_discard_active(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.DISCARD_MUTATION,
            context={"user": self.user},
            variables={
                "paymentVerificationPlanId": [self.id_to_base64(self.verification.id, "PaymentVerificationPlanNode")]
            },
        )
