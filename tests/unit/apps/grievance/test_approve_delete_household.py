from django.core.management import call_command

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.models import Household
from tests.extras.test_utils.factories.account import UserFactory
from tests.extras.test_utils.factories.core import create_afghanistan
from tests.extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory
from tests.extras.test_utils.factories.grievance import (
    GrievanceTicketFactory,
    TicketDeleteHouseholdDetailsFactory,
)
from tests.extras.test_utils.factories.household import create_household
from tests.extras.test_utils.factories.program import ProgramFactory


class TestApproveDeleteHousehold(APITestCase):
    APPROVE_DELETE_HH_MUTATION = """
        mutation approveDeleteHousehold($grievanceTicketId: ID!, $approveStatus: Boolean!, $reasonHhId: String) {
          approveDeleteHousehold(grievanceTicketId: $grievanceTicketId, approveStatus: $approveStatus, reasonHhId: $reasonHhId) {
            grievanceTicket {
              deleteHouseholdTicketDetails {
                reasonHousehold {
                  withdrawn
                }
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

        cls.user = UserFactory.create()
        cls.business_area = BusinessArea.objects.first()

        country = geo_models.Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="Admin type one",
            country=country,
            area_level=2,
        )
        cls.admin_area_1 = AreaFactory(name="City Test", area_type=area_type, p_code="sfds323")

        program_one = ProgramFactory(name="Test program ONE", business_area=cls.business_area)
        cls.household, _ = create_household(household_args={"size": 1, "program": program_one})
        cls.household_withdraw, _ = create_household(
            household_args={"size": 1, "withdrawn": True, "program": program_one}
        )
        cls.household_test_1, _ = create_household(household_args={"size": 1, "program": program_one})
        cls.household_test_2, _ = create_household(household_args={"size": 1, "program": program_one})

        program2 = ProgramFactory(name="Test program TWO", business_area=cls.business_area)
        # household_test_1 has representation in program2
        create_household(household_args={"size": 1, "unicef_id": cls.household_test_1.unicef_id, "program": program2})

    def test_approve_delete_household(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.GRIEVANCES_APPROVE_DATA_CHANGE], self.business_area
        )
        self.household_withdraw.refresh_from_db()
        self.household_test_1.refresh_from_db()
        self.household_test_2.refresh_from_db()

        grievance_ticket = GrievanceTicketFactory(
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_HOUSEHOLD,
            admin2=self.admin_area_1,
            business_area=self.business_area,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
        )

        ticket_details = TicketDeleteHouseholdDetailsFactory(
            ticket=grievance_ticket,
            household=self.household,
            approve_status=True,
        )

        hh_withdraw = Household.objects.filter(id=self.household_withdraw.id).first()
        self.assertTrue(hh_withdraw.withdrawn)

        self.snapshot_graphql_request(
            request_string=self.APPROVE_DELETE_HH_MUTATION,
            context={"user": self.user},
            variables={
                "grievanceTicketId": self.id_to_base64(grievance_ticket.id, "GrievanceTicketNode"),
                "approveStatus": True,
                "reasonHhId": "",
            },
        )
        ticket_details.refresh_from_db()
        self.assertIsNone(ticket_details.reason_household)

        self.graphql_request(
            request_string=self.APPROVE_DELETE_HH_MUTATION,
            context={"user": self.user},
            variables={
                "grievanceTicketId": self.id_to_base64(grievance_ticket.id, "GrievanceTicketNode"),
                "approveStatus": True,
                "reasonHhId": self.household_withdraw.unicef_id,
            },
        )
        ticket_details.refresh_from_db()
        self.assertIsNone(ticket_details.reason_household)

        self.snapshot_graphql_request(
            request_string=self.APPROVE_DELETE_HH_MUTATION,
            context={"user": self.user},
            variables={
                "grievanceTicketId": self.id_to_base64(grievance_ticket.id, "GrievanceTicketNode"),
                "approveStatus": True,
                "reasonHhId": self.household_test_1.unicef_id,
            },
        )
        ticket_details.refresh_from_db()
        self.assertEqual(ticket_details.reason_household, self.household_test_1)

        self.snapshot_graphql_request(
            request_string=self.APPROVE_DELETE_HH_MUTATION,
            context={"user": self.user},
            variables={
                "grievanceTicketId": self.id_to_base64(grievance_ticket.id, "GrievanceTicketNode"),
                "approveStatus": True,
                "reasonHhId": "",
            },
        )
        ticket_details.refresh_from_db()
        self.assertIsNone(ticket_details.reason_household)

        self.snapshot_graphql_request(
            request_string=self.APPROVE_DELETE_HH_MUTATION,
            context={"user": self.user},
            variables={
                "grievanceTicketId": self.id_to_base64(grievance_ticket.id, "GrievanceTicketNode"),
                "approveStatus": True,
                "reasonHhId": "invalid_id",
            },
        )
        ticket_details.refresh_from_db()
        self.assertIsNone(ticket_details.reason_household)

        self.snapshot_graphql_request(
            request_string=self.APPROVE_DELETE_HH_MUTATION,
            context={"user": self.user},
            variables={
                "grievanceTicketId": self.id_to_base64(grievance_ticket.id, "GrievanceTicketNode"),
                "approveStatus": True,
                "reasonHhId": self.household_test_2.unicef_id,
            },
        )
        ticket_details.refresh_from_db()
        self.assertEqual(ticket_details.reason_household, self.household_test_2)
