from django.core.management import call_command

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import AdminAreaFactory, AdminAreaLevelFactory
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.grievance.fixtures import TicketPaymentVerificationDetailsFactory
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.fixtures import IndividualFactory, HouseholdFactory
from hct_mis_api.apps.payment.fixtures import PaymentVerificationFactory, PaymentRecordFactory
from hct_mis_api.apps.payment.models import PaymentVerification


class TestGrievanceUpdatePaymentVerificationTicketQuery(APITestCase):
    QUERY = """
        mutation UpdateGrievanceTicket(
          $input: UpdateGrievanceTicketInput!
        ) {
          updateGrievanceTicket(input: $input) {
            grievanceTicket {
            }
          }
        }
    """

    # APPROVE_QUERY = """
    #
    # """

    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        call_command("loadcountries")
        cls.user = UserFactory.create()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        area_type = AdminAreaLevelFactory(
            name="Admin type one",
            admin_level=2,
            business_area=cls.business_area,
        )
        cls.admin_area = AdminAreaFactory(title="City Test", admin_area_level=area_type, p_code="asdfgfhghkjltr")

        country = geo_models.Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="Admin type one",
            country=country,
            area_level=2,
        )
        AreaFactory(name="City Test", area_type=area_type, p_code="asdfgfhghkjltr")

        p_record = PaymentRecordFactory(household=HouseholdFactory(head_of_household=IndividualFactory(household=None)))
        payment_verification = PaymentVerificationFactory(payment_record=p_record,
                                                          status=PaymentVerification.STATUS_RECEIVED_WITH_ISSUES)
        cls.ticket = TicketPaymentVerificationDetailsFactory(payment_verification=payment_verification)
        cls.ticket.ticket.status = GrievanceTicket.STATUS_NEW
        cls.ticket.ticket.save()

    # @parameterized.expand(
    #     [
    #         (
    #                 "with_permission",
    #                 [Permissions.GRIEVANCES_UPDATE],
    #         ),
    #         ("without_permission", []),
    #     ]
    # )
    def test_update_payment_verification_ticket_with_new_received_amount_extras(self):
        self.create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_UPDATE], self.business_area)

        extras = {
            "newReceivedAmount": 1234.99
        }
        input_data = self._prepare_input(extras)

        self.snapshot_graphql_request(
            request_string=self.QUERY,
            context={"user": self.user},
            variables=input_data,
        )

    # @parameterized.expand(
    #     [
    #         (
    #                 "with_permission",
    #                 [Permissions.GRIEVANCES_UPDATE],
    #         ),
    #         ("without_permission", []),
    #     ]
    # )
    # def test_update_payment_verification_ticket_with_new_status_extras(self, _, permissions):
    #     self.create_user_role_with_permissions(self.user, permissions, self.business_area)
    #
    #     extras = {
    #         "newStatus": PaymentVerification.STATUS_NOT_RECEIVED
    #     }
    #     input_data = self._prepare_input(extras)
    #
    #     self.snapshot_graphql_request(
    #         request_string=self.QUERY,
    #         context={"user": self.user},
    #         variables=input_data,
    #     )

    # @parameterized.expand(
    #     [
    #         (
    #                 "with_permission",
    #                 [Permissions.GRIEVANCES_APPROVE_PAYMENT_VERIFICATION],
    #         ),
    #         ("without_permission", []),
    #     ]
    # )
    # def test_payment_verification_ticket_approve_payment_details(self, _, permissions):
    #     self.create_user_role_with_permissions(self.user, permissions, self.business_area)
    #
    #     input_data = self._prepare_input()
    #
    #     self.snapshot_graphql_request(
    #         request_string=self.APPROVE_QUERY,
    #         context={"user": self.user},
    #         variables=input_data,
    #     )

    def _prepare_input(self, extras=None):
        input_data = {
            "input": {
                "ticketId": self.id_to_base64(self.ticket_details.ticket.id, "GrievanceTicketNode"),
            }
        }

        if extras:
            input_data["input"]["extras"] = {"ticketPaymentVerificationDetailsExtras": extras}

        return input_data
