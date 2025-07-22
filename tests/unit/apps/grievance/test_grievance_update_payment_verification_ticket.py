from typing import Any, Dict, List, Optional

from django.core.management import call_command

from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory
from extras.test_utils.factories.grievance import (
    TicketPaymentVerificationDetailsFactory,
)
from extras.test_utils.factories.household import create_household_and_individuals
from extras.test_utils.factories.payment import (
    PaymentFactory,
    PaymentPlanFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
)
from extras.test_utils.factories.program import ProgramFactory
from parameterized import parameterized

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.payment.models import PaymentVerification, PaymentVerificationPlan
from hct_mis_api.apps.program.models import Program


class TestGrievanceUpdatePaymentVerificationTicketQuery(APITestCase):
    QUERY = """
        mutation UpdateGrievanceTicketMutation($input: UpdateGrievanceTicketInput!) {
          updateGrievanceTicket(input: $input){
            grievanceTicket {
              paymentVerificationTicketDetails{
                newStatus
                newReceivedAmount
              }
            }
          }
        }
    """

    APPROVE_QUERY = """
        mutation ApprovePaymentDetails($grievanceTicketId: ID!, $approveStatus: Boolean!) {
          approvePaymentDetails(grievanceTicketId: $grievanceTicketId, approveStatus: $approveStatus) {
            grievanceTicket {
              paymentVerificationTicketDetails{
                approveStatus
              }
            }
          }
        }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        call_command("loadcountries")
        partner = PartnerFactory(name="Partner")
        cls.user = UserFactory.create(partner=partner)
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        country = geo_models.Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="Admin type one",
            country=country,
            area_level=2,
        )
        cls.admin_area = AreaFactory(name="City Test", area_type=area_type, p_code="asdfgfhghkjltr")

        cls.program = ProgramFactory(id="e6537f1e-27b5-4179-a443-d42498fb0478", status=Program.ACTIVE)
        cls.update_partner_access_to_program(partner, cls.program)
        PaymentPlanFactory(
            id="0272dd2d-c41e-435d-9587-6ba280678c54",
            unicef_id="B4M-21-CSH-00004",
            business_area=cls.business_area,
            program_cycle=cls.program.cycles.first(),
        )

        household, _ = create_household_and_individuals(
            {
                "id": "01780fad-9fa9-4e27-b3cd-7187c13452e5",
                "unicef_id": "HH-21-0000.8129",
                "business_area": cls.business_area,
            },
            [
                {
                    "full_name": "Jenna Franklin",
                    "given_name": "Jenna",
                    "family_name": "Franklin",
                    "phone_no": "001-296-358-5428-607",
                    "birth_date": "1969-11-29",
                    "id": "001A2C2D-22CA-4538-A36F-D454AF5EDD3E",
                    "unicef_id": "IND-21-0002.2658",
                },
            ],
        )

        payment_plan = PaymentPlanFactory(
            name="TEST",
            program_cycle=cls.program.cycles.first(),
            business_area=cls.business_area,
        )
        PaymentVerificationSummaryFactory(payment_plan=payment_plan)
        payment_verification_plan = PaymentVerificationPlanFactory(
            payment_plan=payment_plan, status=PaymentVerificationPlan.STATUS_ACTIVE
        )
        payment = PaymentFactory(
            parent=payment_plan,
            household=household,
            unicef_id="P8F-21-CSH-00031-123123",
            currency="PLN",
        )
        payment_verification = PaymentVerificationFactory(
            id="a76bfe6f-c767-4b7f-9671-6df10b8095cc",
            payment_verification_plan=payment_verification_plan,
            payment=payment,
            status=PaymentVerification.STATUS_RECEIVED_WITH_ISSUES,
        )
        cls.ticket = TicketPaymentVerificationDetailsFactory(payment_verification=payment_verification)
        cls.ticket.ticket.status = GrievanceTicket.STATUS_IN_PROGRESS
        cls.ticket.ticket.save()
        cls.maxDiff = None

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_UPDATE],
            ),
            ("without_permission", []),
        ]
    )
    def test_update_payment_verification_ticket_with_new_received_amount_extras(
        self, _: Any, permissions: List[Permissions]
    ) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        extras = {"newReceivedAmount": 1234.99, "newStatus": PaymentVerification.STATUS_RECEIVED}
        input_data = self._prepare_input(extras)

        self.snapshot_graphql_request(
            request_string=self.QUERY,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables=input_data,
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_APPROVE_PAYMENT_VERIFICATION],
            ),
            ("without_permission", []),
        ]
    )
    def test_payment_verification_ticket_approve_payment_details(self, _: Any, permissions: List[Permissions]) -> None:
        # update status for approval
        self.ticket.ticket.status = GrievanceTicket.STATUS_FOR_APPROVAL
        self.ticket.ticket.save()
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        input_data = {
            "grievanceTicketId": self.id_to_base64(self.ticket.ticket.id, "GrievanceTicketNode"),
            "approveStatus": True,
        }

        self.snapshot_graphql_request(
            request_string=self.APPROVE_QUERY,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables=input_data,
        )

    def _prepare_input(self, extras: Optional[Any] = None) -> Dict:
        input_data: Dict = {
            "input": {
                "ticketId": self.id_to_base64(self.ticket.ticket.id, "GrievanceTicketNode"),
            }
        }

        if extras:
            input_data["input"]["extras"] = {"ticketPaymentVerificationDetailsExtras": extras}

        return input_data
