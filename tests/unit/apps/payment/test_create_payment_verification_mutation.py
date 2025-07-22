from typing import Any, List

from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.household import create_household
from extras.test_utils.factories.payment import (
    PaymentFactory,
    PaymentPlanFactory,
    PaymentVerificationSummaryFactory,
)
from extras.test_utils.factories.program import ProgramFactory
from parameterized import parameterized

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.payment.models import Payment
from hct_mis_api.apps.program.models import Program


class TestCreatePaymentVerificationMutation(APITestCase):
    MUTATION = """
        mutation createPaymentVerificationPlan( $input: CreatePaymentVerificationInput! ) {
            createPaymentVerificationPlan(input: $input) {
                paymentPlan {
                    id
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

        cls.active_program = ProgramFactory(status=Program.ACTIVE)
        cls.finished_program = ProgramFactory(status=Program.FINISHED)

        cls.payment_plan = PaymentPlanFactory.create(
            id="0e2927af-c84d-4852-bb0b-773efe059e05",
            business_area=cls.business_area,
        )
        PaymentVerificationSummaryFactory.create(payment_plan=cls.payment_plan)

    @parameterized.expand(
        [
            ("with_permission", [Permissions.PAYMENT_VERIFICATION_CREATE]),
            ("without_permission", []),
        ]
    )
    def test_create_cash_plan_payment_verification(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        (household, _) = create_household(household_args={"size": 1})
        PaymentFactory.create(
            parent=self.payment_plan,
            business_area=self.payment_plan.business_area,
            delivered_quantity=1000,
            delivered_quantity_usd=None,
            household=household,
            status=Payment.STATUS_SUCCESS,
            currency="PLN",
        )
        # after .create(...), newly created PaymentRecord does not have `head_of_household` set
        # logic needs it to check record.head_of_household.phone_no
        # hence the below
        assert Payment.objects.count() == 1
        Payment.objects.all().update(collector=household.head_of_household)

        self.snapshot_graphql_request(
            request_string=self.MUTATION,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.active_program.id, "ProgramNode"),
                },
            },
            variables={
                "input": {
                    "cashOrPaymentPlanId": self.id_to_base64(self.payment_plan.id, "PaymentPlanNode"),
                    "sampling": "FULL_LIST",
                    "fullListArguments": {"excludedAdminAreas": []},
                    "verificationChannel": "MANUAL",
                    "rapidProArguments": None,
                    "randomSamplingArguments": None,
                    "businessAreaSlug": "afghanistan",
                }
            },
        )

    def test_create_cash_plan_payment_verification_when_invalid_arguments(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PAYMENT_VERIFICATION_CREATE], self.business_area)

        defaults = {
            "cashOrPaymentPlanId": self.id_to_base64(self.payment_plan.id, "PaymentPlanNode"),
            "businessAreaSlug": "afghanistan",
        }

        self.snapshot_graphql_request(
            request_string=self.MUTATION,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.active_program.id, "ProgramNode"),
                },
            },
            variables={
                "input": {
                    **defaults,
                    "verificationChannel": "MANUAL",
                    "rapidProArguments": None,
                    "sampling": "FULL_LIST",
                    "fullListArguments": None,
                    "randomSamplingArguments": {
                        "confidenceInterval": 1.0,
                        "marginOfError": 1.1,
                    },
                }
            },
        )
        self.snapshot_graphql_request(
            request_string=self.MUTATION,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.active_program.id, "ProgramNode"),
                },
            },
            variables={
                "input": {
                    **defaults,
                    "verificationChannel": "MANUAL",
                    "rapidProArguments": None,
                    "sampling": "RANDOM",
                    "fullListArguments": {"excludedAdminAreas": []},
                    "randomSamplingArguments": None,
                }
            },
        )
        self.snapshot_graphql_request(
            request_string=self.MUTATION,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.active_program.id, "ProgramNode"),
                },
            },
            variables={
                "input": {
                    **defaults,
                    "sampling": "RANDOM",
                    "fullListArguments": {"excludedAdminAreas": []},
                    "randomSamplingArguments": {
                        "confidenceInterval": 1.0,
                        "marginOfError": 1.1,
                    },
                    "verificationChannel": "MANUAL",
                    "rapidProArguments": {
                        "flowId": 123,
                    },
                }
            },
        )

    def test_can_t_create_cash_plan_payment_verification_when_there_are_not_available_payment_record(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PAYMENT_VERIFICATION_CREATE], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.MUTATION,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.active_program.id, "ProgramNode"),
                },
            },
            variables={
                "input": {
                    "cashOrPaymentPlanId": self.id_to_base64(self.payment_plan.id, "PaymentPlanNode"),
                    "sampling": "FULL_LIST",
                    "fullListArguments": {"excludedAdminAreas": []},
                    "verificationChannel": "MANUAL",
                    "rapidProArguments": None,
                    "randomSamplingArguments": None,
                    "businessAreaSlug": "afghanistan",
                }
            },
        )

    def test_create_cash_plan_payment_verification_when_program_is_finished(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PAYMENT_VERIFICATION_CREATE], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.MUTATION,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.finished_program.id, "ProgramNode"),
                },
            },
            variables={
                "input": {
                    "cashOrPaymentPlanId": self.id_to_base64(self.payment_plan.id, "PaymentPlanNode"),
                    "sampling": "FULL_LIST",
                    "fullListArguments": {"excludedAdminAreas": []},
                    "verificationChannel": "MANUAL",
                    "rapidProArguments": None,
                    "randomSamplingArguments": None,
                    "businessAreaSlug": "afghanistan",
                }
            },
        )
