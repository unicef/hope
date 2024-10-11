from typing import Any, List

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.payment.fixtures import CashPlanFactory, PaymentRecordFactory
from hct_mis_api.apps.payment.models import PaymentRecord
from hct_mis_api.apps.program.fixtures import ProgramFactory
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

        cls.cash_plan = CashPlanFactory.create(
            id="0e2927af-c84d-4852-bb0b-773efe059e05",
            business_area=cls.business_area,
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.PAYMENT_VERIFICATION_CREATE]),
            ("without_permission", []),
        ]
    )
    def test_create_cash_plan_payment_verification(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        (household, _) = create_household(household_args={"size": 1})
        PaymentRecordFactory.create(
            parent=self.cash_plan,
            business_area=self.cash_plan.business_area,
            delivered_quantity=1000,
            delivered_quantity_usd=None,
            household=household,
            status=PaymentRecord.STATUS_SUCCESS,
            currency="PLN",
        )
        # after .create(...), newly created PaymentRecord does not have `head_of_household` set
        # logic needs it to check record.head_of_household.phone_no
        # hence the below
        assert PaymentRecord.objects.count() == 1
        PaymentRecord.objects.all().update(head_of_household=household.head_of_household)

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
                    "cashOrPaymentPlanId": self.id_to_base64(self.cash_plan.id, "CashPlanNode"),
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
            "cashOrPaymentPlanId": self.id_to_base64(self.cash_plan.id, "CashPlanNode"),
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
                    "cashOrPaymentPlanId": self.id_to_base64(self.cash_plan.id, "CashPlanNode"),
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
                    "cashOrPaymentPlanId": self.id_to_base64(self.cash_plan.id, "CashPlanNode"),
                    "sampling": "FULL_LIST",
                    "fullListArguments": {"excludedAdminAreas": []},
                    "verificationChannel": "MANUAL",
                    "rapidProArguments": None,
                    "randomSamplingArguments": None,
                    "businessAreaSlug": "afghanistan",
                }
            },
        )
