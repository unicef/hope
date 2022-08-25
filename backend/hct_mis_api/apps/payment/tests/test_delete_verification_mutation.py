from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import AdminArea, BusinessArea
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.household.fixtures import EntitlementCardFactory, create_household
from hct_mis_api.apps.payment.fixtures import (
    CashPlanPaymentVerificationFactory,
    PaymentRecordFactory,
    PaymentVerificationFactory,
)
from hct_mis_api.apps.payment.models import (
    CashPlanPaymentVerification,
    PaymentVerification,
)
from hct_mis_api.apps.program.fixtures import CashPlanFactory, ProgramFactory
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
        cls.program.admin_areas.set(AdminArea.objects.order_by("?")[:3])
        cls.program.admin_areas_new.set(Area.objects.order_by("?")[:3])
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
        return self.create_payment_verification_plan_with_status(CashPlanPaymentVerification.STATUS_PENDING)

    def create_active_payment_verification_plan(self):
        return self.create_payment_verification_plan_with_status(CashPlanPaymentVerification.STATUS_ACTIVE)

    def create_payment_verification_plan_with_status(self, status):
        cash_plan_payment_verification = CashPlanPaymentVerificationFactory(cash_plan=self.cash_plan)
        cash_plan_payment_verification.status = status
        cash_plan_payment_verification.save()
        for _ in range(5):
            registration_data_import = RegistrationDataImportFactory(
                imported_by=self.user, business_area=self.business_area
            )
            household, _ = create_household(
                {
                    "registration_data_import": registration_data_import,
                    "admin_area": AdminArea.objects.order_by("?").first(),
                    "admin_area_new": Area.objects.order_by("?").first(),
                },
                {"registration_data_import": registration_data_import},
            )

            household.programs.add(self.program)

            payment_record = PaymentRecordFactory(
                cash_plan=self.cash_plan,
                household=household,
                target_population=self.target_population,
            )

            PaymentVerificationFactory(
                cash_plan_payment_verification=cash_plan_payment_verification,
                payment_record=payment_record,
                status=PaymentVerification.STATUS_PENDING,
            )
            EntitlementCardFactory(household=household)
        return cash_plan_payment_verification
