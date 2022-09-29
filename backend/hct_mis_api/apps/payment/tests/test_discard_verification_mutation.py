from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.household.fixtures import EntitlementCardFactory, create_household
from hct_mis_api.apps.payment.fixtures import (
    CashPlanFactory,
    PaymentRecordFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
)
from hct_mis_api.apps.payment.models import PaymentVerification, PaymentVerificationPlan
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.targeting.fixtures import (
    TargetingCriteriaFactory,
    TargetPopulationFactory,
)


class TestDiscardVerificationMutation(APITestCase):

    DISCARD_MUTATION = """
        mutation DiscardVerification($paymentVerificationPlanId: ID!){
          discardPaymentVerificationPlan(paymentVerificationPlanId:$paymentVerificationPlanId) {
            cashPlan{
                name
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
    def setUpTestData(cls):
        cls.user = UserFactory.create()
        create_afghanistan()
        payment_record_amount = 10
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        program = ProgramFactory(business_area=cls.business_area)
        program.admin_areas.set(Area.objects.order_by("?")[:3])
        targeting_criteria = TargetingCriteriaFactory()

        target_population = TargetPopulationFactory(
            created_by=cls.user,
            targeting_criteria=targeting_criteria,
            business_area=cls.business_area,
        )
        cash_plan = CashPlanFactory(
            name="TEST",
            program=program,
            business_area=cls.business_area,
        )
        payment_verification_plan = PaymentVerificationPlanFactory(
            cash_plan=cash_plan, verification_channel=PaymentVerificationPlan.VERIFICATION_CHANNEL_MANUAL
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
                },
                {"registration_data_import": registration_data_import},
            )

            household.programs.add(program)

            payment_record = PaymentRecordFactory(
                parent=cash_plan,
                household=household,
                target_population=target_population,
            )
            PaymentVerificationFactory(
                payment_verification_plan=payment_verification_plan,
                payment_record=payment_record,
                status=PaymentVerification.STATUS_PENDING,
            )
            EntitlementCardFactory(household=household)
        cls.cash_plan = cash_plan
        cls.verification = cash_plan.payment_verification_plans.first()

    @parameterized.expand(
        [
            ("with_permission", [Permissions.PAYMENT_VERIFICATION_DISCARD]),
            ("without_permission", []),
        ]
    )
    def test_discard_active(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.DISCARD_MUTATION,
            context={"user": self.user},
            variables={
                "paymentVerificationPlanId": [self.id_to_base64(self.verification.id, "PaymentVerificationPlanNode")]
            },
        )
