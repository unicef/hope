import json
from datetime import date

from django.core.management import call_command

from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from core.fixtures import AdminAreaTypeFactory, AdminAreaFactory
from core.models import BusinessArea
from grievance.fixtures import (
    GrievanceTicketFactory,
    TicketAddIndividualDetailsFactory,
    TicketIndividualDataUpdateDetailsFactory,
    TicketHouseholdDataUpdateDetailsFactory,
)
from grievance.models import GrievanceTicket
from household.fixtures import HouseholdFactory, IndividualFactory
from household.models import SINGLE
from program.fixtures import ProgramFactory


class TestGrievanceApproveDataChangeMutation(APITestCase):
    APPROVE_ADD_INDIVIDUAL_MUTATION = """
    mutation ApproveAddIndividual($grievanceTicketId: ID!, $approveStatus: Boolean!) {
      approveAddIndividual(grievanceTicketId: $grievanceTicketId, approveStatus: $approveStatus) {
        grievanceTicket {
          id
          addIndividualTicketDetails {
            approveStatus
          }
        }
      }
    }
    """

    APPROVE_INDIVIDUAL_DATA_CHANGE_GRIEVANCE_MUTATION = """
    mutation ApproveIndividualDataChange($grievanceTicketId: ID!, $individualApproveData: JSONString) {
      approveIndividualDataChange(
        grievanceTicketId: $grievanceTicketId, individualApproveData: $individualApproveData
      ) {
        grievanceTicket {
          id
          individualDataUpdateTicketDetails {
            individualData
          }
        }
      }
    }
    """

    APPROVE_HOUSEHOLD_DATA_CHANGE_GRIEVANCE_MUTATION = """
    mutation ApproveHouseholdDataChange($grievanceTicketId: ID!, $householdApproveData: JSONString) {
      approveHouseholdDataChange(
        grievanceTicketId: $grievanceTicketId, householdApproveData: $householdApproveData
      ) {
        grievanceTicket {
          id
          householdDataUpdateTicketDetails {
            householdData
          }
        }
      }
    }
    """

    def setUp(self):
        super().setUp()
        call_command("loadbusinessareas")
        self.user = UserFactory.create()
        self.business_area = BusinessArea.objects.get(slug="afghanistan")
        area_type = AdminAreaTypeFactory(
            name="Admin type one",
            admin_level=2,
            business_area=self.business_area,
        )
        self.admin_area_1 = AdminAreaFactory(title="City Test", admin_area_type=area_type)
        self.admin_area_2 = AdminAreaFactory(title="City Example", admin_area_type=area_type)
        program_one = ProgramFactory(
            name="Test program ONE",
            business_area=BusinessArea.objects.first(),
        )

        household_one = HouseholdFactory.build(id="07a901ed-d2a5-422a-b962-3570da1d5d07")
        household_one.registration_data_import.imported_by.save()
        household_one.registration_data_import.save()
        household_one.programs.add(program_one)

        self.individuals_to_create = [
            {
                "full_name": "Benjamin Butler",
                "given_name": "Benjamin",
                "family_name": "Butler",
                "phone_no": "(953)682-4596",
                "birth_date": "1943-07-30",
            },
            {
                "full_name": "Robin Ford",
                "given_name": "Robin",
                "family_name": "Ford",
                "phone_no": "+18663567905",
                "birth_date": "1946-02-15",
            },
        ]

        self.individuals = [
            IndividualFactory(household=household_one, **individual) for individual in self.individuals_to_create
        ]
        household_one.head_of_household = self.individuals[0]
        household_one.save()
        self.household_one = household_one

        self.add_individual_grievance_ticket = GrievanceTicketFactory(
            id="43c59eda-6664-41d6-9339-05efcb11da82",
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
            admin=self.admin_area_1.title,
            business_area=self.business_area,
        )
        TicketAddIndividualDetailsFactory(
            ticket=self.add_individual_grievance_ticket,
            household=self.household_one,
            individual_data={
                "given_name": "Test",
                "full_name": "Test Example",
                "family_name": "Example",
                "sex": "MALE",
                "birth_date": date(year=1980, month=2, day=1).isoformat(),
                "marital_status": SINGLE,
            },
            approve_status=False,
        )

        self.individual_data_change_grievance_ticket = GrievanceTicketFactory(
            id="acd57aa1-efd8-4c81-ac19-b8cabebe8089",
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
            admin=self.admin_area_1.title,
            business_area=self.business_area,
        )
        TicketIndividualDataUpdateDetailsFactory(
            ticket=self.individual_data_change_grievance_ticket,
            individual=self.individuals[0],
            individual_data={
                "given_name": {"value": "Test"},
                "full_name": {"value": "Test Example"},
                "family_name": {"value": "Example"},
                "sex": {"value": "MALE"},
                "birth_date": {"value": date(year=1980, month=2, day=1).isoformat()},
                "marital_status": {"value": SINGLE},
            },
        )

        self.household_data_change_grievance_ticket = GrievanceTicketFactory(
            id="72ee7d98-6108-4ef0-85bd-2ef20e1d5410",
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE,
            admin=self.admin_area_1.title,
            business_area=self.business_area,
        )
        TicketHouseholdDataUpdateDetailsFactory(
            ticket=self.household_data_change_grievance_ticket,
            household=self.household_one,
            household_data={"village": {"value": "Test Village"}, "size": {"value": 19}},
        )

    def test_approve_add_individual(self):
        self.snapshot_graphql_request(
            request_string=self.APPROVE_ADD_INDIVIDUAL_MUTATION,
            context={"user": self.user},
            variables={
                "grievanceTicketId": self.id_to_base64(self.add_individual_grievance_ticket.id, "GrievanceTicketNode"),
                "approveStatus": True,
            },
        )

    def test_approve_update_individual(self):
        self.snapshot_graphql_request(
            request_string=self.APPROVE_INDIVIDUAL_DATA_CHANGE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables={
                "grievanceTicketId": self.id_to_base64(
                    self.individual_data_change_grievance_ticket.id, "GrievanceTicketNode"
                ),
                "individualApproveData": json.dumps({"givenName": True, "fullName": True, "familyName": True}),
            },
        )

    def test_approve_update_household(self):
        self.snapshot_graphql_request(
            request_string=self.APPROVE_HOUSEHOLD_DATA_CHANGE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables={
                "grievanceTicketId": self.id_to_base64(
                    self.household_data_change_grievance_ticket.id, "GrievanceTicketNode"
                ),
                "householdApproveData": json.dumps({"village": True}),
            },
        )
