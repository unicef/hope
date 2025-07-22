from unittest.mock import MagicMock, patch

from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.household import create_household
from extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory
from extras.test_utils.factories.program import ProgramFactory
from parameterized import parameterized

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.accountability.models import Survey
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.program.models import Program


class TestCreateCommunicationMessage(APITestCase):
    MUTATION = """
mutation CreateAccountabilityCommunicationMessage (
  $input: CreateAccountabilityCommunicationMessageInput!
) {
  createAccountabilityCommunicationMessage (
    input: $input
  ) {
    message {
      title
      body
      createdBy {
        firstName
        lastName
      }
      households {
        totalCount
      }
      paymentPlan {
        name
      }
      registrationDataImport {
        name
        status
      }
      fullListArguments
      randomSamplingArguments
      sampleSize
    }
  }
}
    """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        partner = PartnerFactory(name="Partner")
        cls.user = UserFactory(first_name="John", last_name="Wick", partner=partner)
        cls.program = ProgramFactory(status=Program.ACTIVE)
        cls.update_partner_access_to_program(partner, cls.program)
        cls.payment_plan = PaymentPlanFactory(
            name="Test Message Payment Plan",
            business_area=cls.business_area,
            status=PaymentPlan.Status.TP_PROCESSING,
            created_by=cls.user,
            program_cycle=cls.program.cycles.first(),
        )

        cls.households = [create_household()[0] for _ in range(14)]
        for hh in cls.households:
            PaymentFactory(
                parent=cls.payment_plan,
                household=hh,
            )

        cls.sampling_data = {
            Survey.SAMPLING_FULL_LIST: {
                "fullListArguments": {
                    "excludedAdminAreas": [],
                },
            },
            Survey.SAMPLING_RANDOM: {
                "randomSamplingArguments": {
                    "age": {"min": 20, "max": 80},
                    # "sex": MALE,
                    "confidenceInterval": 0.8,
                    "marginOfError": 80,
                    "excludedAdminAreas": [],
                },
            },
        }

    def test_create_accountability_communication_message_without_permission(self) -> None:
        self.create_user_role_with_permissions(self.user, [], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.MUTATION,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                },
            },
            variables={
                "input": {
                    "title": "Test message",
                    "body": "Test body",
                    "paymentPlan": self.id_to_base64(self.payment_plan.id, "PaymentPlanNode"),
                    "samplingType": Survey.SAMPLING_FULL_LIST,
                    **self.sampling_data[Survey.SAMPLING_FULL_LIST],
                },
            },
        )

    @parameterized.expand(
        [
            (Survey.SAMPLING_FULL_LIST,),
            (Survey.SAMPLING_RANDOM,),
        ]
    )
    def test_create_accountability_communication_message_by_target_population(self, sampling_type: str) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_CREATE], self.business_area
        )
        broadcast_message_mock = MagicMock(return_value=None)
        with (
            patch("hct_mis_api.apps.core.services.rapid_pro.api.RapidProAPI.__init__", MagicMock(return_value=None)),
            patch("hct_mis_api.apps.core.services.rapid_pro.api.RapidProAPI.broadcast_message", broadcast_message_mock),
        ):
            self.snapshot_graphql_request(
                request_string=self.MUTATION,
                context={
                    "user": self.user,
                    "headers": {
                        "Business-Area": self.business_area.slug,
                        "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    },
                },
                variables={
                    "input": {
                        "title": "Test message",
                        "body": "Test body",
                        "paymentPlan": self.id_to_base64(self.payment_plan.id, "PaymentPlanNode"),
                        "samplingType": sampling_type,
                        **self.sampling_data[sampling_type],
                    },
                },
            )
            self.assertEqual(broadcast_message_mock.call_count, 1)
            if sampling_type == Survey.SAMPLING_FULL_LIST:
                self.assertEqual(len(broadcast_message_mock.call_args[0][0]), self.payment_plan.payment_items.count())
            self.assertEqual(broadcast_message_mock.call_args[0][1], "Test body")

    @parameterized.expand(
        [
            (Survey.SAMPLING_FULL_LIST,),
            (Survey.SAMPLING_RANDOM,),
        ]
    )
    def test_create_accountability_communication_message_by_households(self, sampling_type: str) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_CREATE], self.business_area
        )
        broadcast_message_mock = MagicMock(return_value=None)
        with (
            patch("hct_mis_api.apps.core.services.rapid_pro.api.RapidProAPI.__init__", MagicMock(return_value=None)),
            patch("hct_mis_api.apps.core.services.rapid_pro.api.RapidProAPI.broadcast_message", broadcast_message_mock),
        ):
            self.snapshot_graphql_request(
                request_string=self.MUTATION,
                context={
                    "user": self.user,
                    "headers": {
                        "Business-Area": self.business_area.slug,
                        "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    },
                },
                variables={
                    "input": {
                        "title": "Test message",
                        "body": "Test body",
                        "households": [self.id_to_base64(hh.id, "HouseholdNode") for hh in self.households],
                        "samplingType": sampling_type,
                        **self.sampling_data[sampling_type],
                    },
                },
            )
            self.assertEqual(broadcast_message_mock.call_count, 1)
            if sampling_type == Survey.SAMPLING_FULL_LIST:
                self.assertEqual(len(broadcast_message_mock.call_args[0][0]), len(self.households))
            self.assertEqual(broadcast_message_mock.call_args[0][1], "Test body")
