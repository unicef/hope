from django.core.management import call_command

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.grievance.fixtures import TicketPaymentVerificationDetailsFactory
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.payment.fixtures import (
    PaymentRecordFactory,
    PaymentVerificationFactory,
    CashPlanPaymentVerificationFactory,
)
from hct_mis_api.apps.payment.models import PaymentVerification, CashPlanPaymentVerification
from hct_mis_api.apps.payment.fixtures import CashPlanFactory
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.targeting.fixtures import TargetingCriteriaFactory, TargetPopulationFactory


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
    def setUpTestData(cls):
        create_afghanistan()
        call_command("loadcountries")
        cls.user = UserFactory.create()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        country = geo_models.Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="Admin type one",
            country=country,
            area_level=2,
        )
        cls.admin_area = AreaFactory(name="City Test", area_type=area_type, p_code="asdfgfhghkjltr")

        program = ProgramFactory(id="e6537f1e-27b5-4179-a443-d42498fb0478")
        CashPlanFactory(
            id="0272dd2d-c41e-435d-9587-6ba280678c54",
            ca_id="B4M-21-CSH-00004",
            business_area=cls.business_area,
            program=program,
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

        cash_plan = CashPlanFactory(
            name="TEST",
            program=program,
            business_area=cls.business_area,
        )
        cash_plan_payment_verification = CashPlanPaymentVerificationFactory(
            cash_plan=cash_plan, status=CashPlanPaymentVerification.STATUS_ACTIVE
        )

        target_population = TargetPopulationFactory(
            id="6FFB6BB7-3D43-4ECE-BB0E-21FDE209AFAF",
            created_by=cls.user,
            targeting_criteria=(TargetingCriteriaFactory()),
            business_area=cls.business_area,
        )
        payment_record = PaymentRecordFactory(
            cash_plan=cash_plan,
            household=household,
            target_population=target_population,
            ca_id="P8F-21-CSH-00031-123123",
        )
        payment_verification = PaymentVerificationFactory(
            id="a76bfe6f-c767-4b7f-9671-6df10b8095cc",
            cash_plan_payment_verification=cash_plan_payment_verification,
            payment_record=payment_record,
            status=PaymentVerification.STATUS_RECEIVED_WITH_ISSUES,
        )
        cls.ticket = TicketPaymentVerificationDetailsFactory(payment_verification=payment_verification)
        cls.ticket.ticket.status = GrievanceTicket.STATUS_IN_PROGRESS
        cls.ticket.ticket.save()

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_UPDATE],
            ),
            ("without_permission", []),
        ]
    )
    def test_update_payment_verification_ticket_with_new_received_amount_extras(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        extras = {"newReceivedAmount": 1234.99, "newStatus": PaymentVerification.STATUS_RECEIVED}
        input_data = self._prepare_input(extras)

        self.snapshot_graphql_request(
            request_string=self.QUERY,
            context={"user": self.user},
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
    def test_payment_verification_ticket_approve_payment_details(self, _, permissions):
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
            context={"user": self.user},
            variables=input_data,
        )

    def _prepare_input(self, extras=None):
        input_data = {
            "input": {
                "ticketId": self.id_to_base64(self.ticket.ticket.id, "GrievanceTicketNode"),
            }
        }

        if extras:
            input_data["input"]["extras"] = {"ticketPaymentVerificationDetailsExtras": extras}

        return input_data
