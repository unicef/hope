from django.core.management import call_command
from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea, AdminArea
from hct_mis_api.apps.household.fixtures import (
    create_household,
    EntitlementCardFactory,
)
from hct_mis_api.apps.payment.fixtures import (
    PaymentRecordFactory,
    CashPlanPaymentVerificationFactory,
    PaymentVerificationFactory,
)
from hct_mis_api.apps.payment.models import PaymentVerification, CashPlanPaymentVerification
from hct_mis_api.apps.program.fixtures import ProgramFactory, CashPlanFactory
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.targeting.fixtures import TargetingCriteriaFactory, TargetPopulationFactory


class TestDiscardVerificationMutation(APITestCase):

    DISCARD_MUTATION = """
        mutation DiscardVerification($cashPlanVerificationId: ID!){
          discardCashPlanPaymentVerification(cashPlanVerificationId:$cashPlanVerificationId) {
            cashPlan{
                name
                verificationStatus
                verifications {
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

    # verification = None

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create()
        call_command("loadbusinessareas")
        payment_record_amount = 10
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        program = ProgramFactory(business_area=cls.business_area)
        program.admin_areas.set(AdminArea.objects.order_by("?")[:3])
        targeting_criteria = TargetingCriteriaFactory()

        target_population = TargetPopulationFactory(
            created_by=cls.user,
            candidate_list_targeting_criteria=targeting_criteria,
            business_area=cls.business_area,
        )
        cash_plan = CashPlanFactory.build(
            program=program,
            business_area=cls.business_area,
        )
        cash_plan.name = "TEST"
        cash_plan.save()
        cash_plan_payment_verification = CashPlanPaymentVerificationFactory(cash_plan=cash_plan)
        cash_plan_payment_verification.status = CashPlanPaymentVerification.STATUS_ACTIVE
        cash_plan_payment_verification.save()
        for _ in range(payment_record_amount):
            registration_data_import = RegistrationDataImportFactory(
                imported_by=cls.user, business_area=cls.business_area
            )
            household, individuals = create_household(
                {
                    "registration_data_import": registration_data_import,
                    "admin_area": AdminArea.objects.order_by("?").first(),
                },
                {"registration_data_import": registration_data_import},
            )

            household.programs.add(program)

            payment_record = PaymentRecordFactory(
                cash_plan=cash_plan,
                household=household,
                target_population=target_population,
            )

            PaymentVerificationFactory(
                cash_plan_payment_verification=cash_plan_payment_verification,
                payment_record=payment_record,
                status=PaymentVerification.STATUS_PENDING,
            )
            EntitlementCardFactory(household=household)
        cls.cash_plan = cash_plan
        cls.verification = cash_plan.verifications.first()

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
                "cashPlanVerificationId": [self.id_to_base64(self.verification.id, "CashPlanPaymentVerificationNode")]
            },
        )
