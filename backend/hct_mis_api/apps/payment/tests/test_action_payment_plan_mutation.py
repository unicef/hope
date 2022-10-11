from unittest.mock import patch

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import (
    IndividualRoleInHouseholdFactory,
    create_household_and_individuals,
)
from hct_mis_api.apps.household.models import ROLE_PRIMARY
from hct_mis_api.apps.payment.fixtures import (
    DeliveryMechanismPerPaymentPlanFactory,
    FinancialServiceProviderFactory,
    PaymentChannelFactory,
    PaymentFactory,
    PaymentPlanFactory,
    RealProgramFactory,
)
from hct_mis_api.apps.payment.models import GenericPayment
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
                      financeReview{
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
                    sentForFinanceReviewBy {
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
    def setUpTestData(cls):
        cls.user = UserFactory.create(first_name="Rachel", last_name="Walker")
        create_afghanistan()  # approve:2, authorize:2, finance_review:3
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        cls.payment_plan = PaymentPlanFactory.create(business_area=cls.business_area, program=RealProgramFactory())
        cls.registration_data_import = RegistrationDataImportFactory(business_area=cls.business_area)
        household, individuals = create_household_and_individuals(
            household_data={
                "registration_data_import": cls.registration_data_import,
                "business_area": cls.business_area,
            },
            individuals_data=[{}],
        )
        IndividualRoleInHouseholdFactory(household=household, individual=individuals[0], role=ROLE_PRIMARY)
        cls.payment_channel_1_cash = PaymentChannelFactory(
            individual=individuals[0],
            delivery_mechanism=GenericPayment.DELIVERY_TYPE_CASH,
        )

        cls.financial_service_provider = FinancialServiceProviderFactory(
            delivery_mechanisms=[GenericPayment.DELIVERY_TYPE_CASH]
        )
        DeliveryMechanismPerPaymentPlanFactory(
            payment_plan=cls.payment_plan,
            delivery_mechanism=GenericPayment.DELIVERY_TYPE_CASH,
            financial_service_provider=cls.financial_service_provider,
        )
        cls.payment = PaymentFactory(parent=cls.payment_plan, collector=individuals[0])

    @parameterized.expand(
        [
            ("without_permission", [], None, ["LOCK"]),
            ("not_possible_reject", [Permissions.PAYMENT_MODULE_VIEW_DETAILS], None, ["REJECT"]),
            (
                "lock_approve_authorize_reject",
                [Permissions.PAYMENT_MODULE_VIEW_DETAILS],
                None,
                ["LOCK", "LOCK_FSP", "SEND_FOR_APPROVAL", "APPROVE", "AUTHORIZE", "REJECT"],
            ),
            (
                "all_steps",
                [Permissions.PAYMENT_MODULE_VIEW_DETAILS],
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
            ("reject_if_accepted", [Permissions.PAYMENT_MODULE_VIEW_DETAILS], "ACCEPTED", ["REJECT"]),
            (
                "lock_unlock",
                [Permissions.PAYMENT_MODULE_VIEW_DETAILS],
                "LOCKED",
                ["UNLOCK", "LOCK", "UNLOCK"],
            ),
        ]
    )
    @patch("hct_mis_api.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0)
    def test_update_status_payment_plan(self, name, permissions, status, actions, get_exchange_rate_mock):
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
