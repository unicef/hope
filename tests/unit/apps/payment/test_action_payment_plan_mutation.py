from typing import Any, List
from unittest.mock import patch

from django.utils import timezone

from constance.test import override_config
from freezegun import freeze_time
from parameterized import parameterized

from tests.extras.test_utils.factories.account import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from tests.extras.test_utils.factories.core import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from tests.extras.test_utils.factories.household import (
    IndividualRoleInHouseholdFactory,
    create_household_and_individuals,
)
from hct_mis_api.apps.household.models import ROLE_PRIMARY
from tests.extras.test_utils.factories.payment import (
    FinancialServiceProviderFactory,
    PaymentFactory,
    PaymentPlanFactory,
    generate_delivery_mechanisms,
)
from hct_mis_api.apps.payment.models import (
    AcceptanceProcessThreshold,
    DeliveryMechanism,
    FinancialServiceProvider,
    PaymentPlan,
)
from tests.extras.test_utils.factories.fixtures import ProgramCycleFactory
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory


class TestActionPaymentPlanMutation(APITestCase):
    MUTATION = """
        mutation ActionPaymentPlanMutation($input: ActionPaymentPlanInput!) {
          actionPaymentPlanMutation(input: $input) {
            paymentPlan {
              status
              approvalProcess {
                totalCount
                edges {
                  node {
                    actions {
                      approval{
                        info
                        comment
                      }
                      authorization{
                        info
                        comment
                      }
                      financeRelease{
                        info
                        comment
                      }
                      reject{
                        info
                        comment
                      }
                    }
                    rejectedOn
                    sentForApprovalBy {
                      firstName
                      lastName
                    }
                    sentForAuthorizationBy {
                      firstName
                      lastName
                    }
                    sentForFinanceReleaseBy {
                      firstName
                      lastName
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
        generate_delivery_mechanisms()
        cls.user = UserFactory.create(first_name="Rachel", last_name="Walker")
        cls.business_area = create_afghanistan()
        AcceptanceProcessThreshold.objects.create(
            business_area=BusinessArea.objects.first(),
            approval_number_required=2,
            authorization_number_required=2,
            finance_release_number_required=3,
        )

        cls.financial_service_provider = FinancialServiceProviderFactory(
            communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
            payment_gateway_id="Abc",
        )
        dm_cash = DeliveryMechanism.objects.get(code="cash")
        cls.financial_service_provider.delivery_mechanisms.set([dm_cash])
        cls.payment_plan = PaymentPlanFactory.create(
            business_area=cls.business_area,
            program_cycle=ProgramCycleFactory(),
            created_by=cls.user,
            delivery_mechanism=dm_cash,
            financial_service_provider=cls.financial_service_provider,
        )
        cls.registration_data_import = RegistrationDataImportFactory(business_area=cls.business_area)
        household, individuals = create_household_and_individuals(
            household_data={
                "registration_data_import": cls.registration_data_import,
                "business_area": cls.business_area,
            },
            individuals_data=[{}],
        )
        IndividualRoleInHouseholdFactory(household=household, individual=individuals[0], role=ROLE_PRIMARY)

        PaymentFactory(parent=cls.payment_plan, collector=individuals[0], currency="PLN")

    @parameterized.expand(
        [
            ("without_permission", [], None, ["LOCK"]),
            ("not_possible_reject", [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE], None, ["REJECT"]),
            (
                "lock_approve_authorize_reject",
                [
                    Permissions.PM_LOCK_AND_UNLOCK,
                    Permissions.PM_LOCK_AND_UNLOCK_FSP,
                    Permissions.PM_SEND_FOR_APPROVAL,
                    Permissions.PM_ACCEPTANCE_PROCESS_APPROVE,
                    Permissions.PM_ACCEPTANCE_PROCESS_AUTHORIZE,
                ],
                None,
                ["LOCK", "LOCK_FSP", "SEND_FOR_APPROVAL", "APPROVE", "AUTHORIZE", "REJECT"],
            ),
            (
                "all_steps",
                [
                    Permissions.PM_SEND_FOR_APPROVAL,
                    Permissions.PM_ACCEPTANCE_PROCESS_APPROVE,
                    Permissions.PM_ACCEPTANCE_PROCESS_AUTHORIZE,
                    Permissions.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW,
                ],
                "LOCKED_FSP",
                [
                    "SEND_FOR_APPROVAL",
                    "APPROVE",
                    "APPROVE",
                    "AUTHORIZE",
                    "AUTHORIZE",
                    "REVIEW",
                    "REVIEW",
                    "REVIEW",
                ],
            ),
            ("reject_if_accepted", [Permissions.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW], "ACCEPTED", ["REJECT"]),
            (
                "lock_unlock",
                [Permissions.PM_LOCK_AND_UNLOCK],
                "LOCKED",
                ["UNLOCK", "LOCK", "UNLOCK"],
            ),
        ]
    )
    @patch("hct_mis_api.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0)
    @patch("hct_mis_api.apps.payment.notifications.MailjetClient.send_email")
    @override_config(PM_ACCEPTANCE_PROCESS_USER_HAVE_MULTIPLE_APPROVALS=True)
    def test_update_status_payment_plan(
        self,
        name: Any,
        permissions: List[Permissions],
        status: str,
        actions: List[str],
        get_exchange_rate_mock: Any,
        send_mock: Any,
    ) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        if status:
            self.payment_plan.status = status
            self.payment_plan.save()
        for action in actions:
            self.snapshot_graphql_request(
                request_string=self.MUTATION,
                context={"user": self.user},
                variables={
                    "input": {
                        "paymentPlanId": self.id_to_base64(self.payment_plan.id, "PaymentPlanNode"),
                        "action": action,
                        "comment": f"{name}, action: {action}",
                    }
                },
            )

    @freeze_time("2021-01-01")
    @patch("hct_mis_api.apps.payment.notifications.PaymentNotification.__init__")
    @override_config(SEND_PAYMENT_PLANS_NOTIFICATION=True)
    @override_config(PM_ACCEPTANCE_PROCESS_USER_HAVE_MULTIPLE_APPROVALS=True)
    def test_call_email_notification(self, mock_init: Any) -> None:
        self.create_user_role_with_permissions(
            self.user,
            [
                Permissions.PM_SEND_FOR_APPROVAL,
                Permissions.PM_ACCEPTANCE_PROCESS_APPROVE,
                Permissions.PM_ACCEPTANCE_PROCESS_AUTHORIZE,
                Permissions.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW,
            ],
            self.business_area,
        )
        self.payment_plan.status = "LOCKED_FSP"
        self.payment_plan.save()
        actions = [
            "SEND_FOR_APPROVAL",
            "APPROVE",
            "APPROVE",
            "AUTHORIZE",
            "AUTHORIZE",
            "REVIEW",
            "REVIEW",
            "REVIEW",
        ]
        for action in actions:
            self.graphql_request(
                request_string=self.MUTATION,
                context={"user": self.user},
                variables={
                    "input": {
                        "paymentPlanId": self.id_to_base64(self.payment_plan.id, "PaymentPlanNode"),
                        "action": action,
                    }
                },
            )
        self.assertEqual(
            mock_init.call_count,
            4,
        )
        mock_init.assert_any_call(
            self.payment_plan, PaymentPlan.Action.SEND_FOR_APPROVAL.value, self.user, f"{timezone.now():%-d %B %Y}"
        )
        mock_init.assert_any_call(
            self.payment_plan, PaymentPlan.Action.APPROVE.value, self.user, f"{timezone.now():%-d %B %Y}"
        )
        mock_init.assert_any_call(
            self.payment_plan, PaymentPlan.Action.AUTHORIZE.value, self.user, f"{timezone.now():%-d %B %Y}"
        )
        mock_init.assert_any_call(
            self.payment_plan, PaymentPlan.Action.REVIEW.value, self.user, f"{timezone.now():%-d %B %Y}"
        )

    def test_send_xlsx_password_action(self) -> None:
        self.create_user_role_with_permissions(
            self.user,
            [
                Permissions.PM_SEND_XLSX_PASSWORD,
            ],
            self.business_area,
        )
        self.payment_plan.status = PaymentPlan.Status.ACCEPTED
        self.payment_plan.save()

        self.graphql_request(
            request_string=self.MUTATION,
            context={"user": self.user},
            variables={
                "input": {
                    "paymentPlanId": self.id_to_base64(self.payment_plan.id, "PaymentPlanNode"),
                    "action": "SEND_XLSX_PASSWORD",
                }
            },
        )
        self.payment_plan.refresh_from_db()
        self.assertIsNone(self.payment_plan.background_action_status)
