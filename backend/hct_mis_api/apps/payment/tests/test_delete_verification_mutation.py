from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.household.fixtures import EntitlementCardFactory, create_household
from hct_mis_api.apps.payment.fixtures import (
    PaymentVerificationPlanFactory,
    PaymentRecordFactory,
    PaymentVerificationFactory,
)
from hct_mis_api.apps.payment.models import (
    PaymentVerificationPlan,
    PaymentVerification,
)
from hct_mis_api.apps.payment.fixtures import CashPlanFactory
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
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
        cls.verification = cls.cash_plan.verification_plans.first()

    @parameterized.expand(
        [
            ("with_permission", [Permissions.PAYMENT_VERIFICATION_DELETE]),
            ("without_permission", []),
        ]
    )
    def test_delete_pending_verification_plan(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        self.create_active_payment_verification_plan()
        payment_verification_plan = self.create_pending_payment_verification_plan()

        self.snapshot_graphql_request(
            request_string=self.MUTATION,
            context={"user": self.user},
            variables={
                "cashPlanVerificationId": [
                    self.id_to_base64(payment_verification_plan.id, "CashPlanPaymentVerificationNode")
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
        payment_verification_plan = self.create_active_payment_verification_plan()
        self.create_pending_payment_verification_plan()

        self.snapshot_graphql_request(
            request_string=self.MUTATION,
            context={"user": self.user},
            variables={
                "cashPlanVerificationId": [
                    self.id_to_base64(payment_verification_plan.id, "CashPlanPaymentVerificationNode")
                ]
            },
        )

    def create_pending_payment_verification_plan(self):
        return self.create_payment_verification_plan_with_status(PaymentVerificationPlan.STATUS_PENDING)

    def create_active_payment_verification_plan(self):
        return self.create_payment_verification_plan_with_status(PaymentVerificationPlan.STATUS_ACTIVE)

    def create_payment_verification_plan_with_status(self, status):
        payment_verification_plan = PaymentVerificationPlanFactory(cash_plan=self.cash_plan)
        payment_verification_plan.status = status
        payment_verification_plan.save()
        for _ in range(5):
            registration_data_import = RegistrationDataImportFactory(
                imported_by=self.user, business_area=self.business_area
            )
            household, _ = create_household(
                {
                    "registration_data_import": registration_data_import,
                    "admin_area": Area.objects.order_by("?").first(),
                },
                {"registration_data_import": registration_data_import},
            )

            household.programs.add(self.program)

            payment_record = PaymentRecordFactory(
                parent=self.cash_plan,
                household=household,
                target_population=self.target_population,
            )

            PaymentVerificationFactory(
                payment_verification_plan=payment_verification_plan,
                payment_record=payment_record,
                status=PaymentVerification.STATUS_PENDING,
            )
            EntitlementCardFactory(household=household)
        return payment_verification_plan
