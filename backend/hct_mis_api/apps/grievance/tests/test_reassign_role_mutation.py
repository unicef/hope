from django.core.management import call_command

from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from core.fixtures import AdminAreaTypeFactory, AdminAreaFactory
from core.models import BusinessArea
from grievance.fixtures import GrievanceTicketFactory, TicketDeleteIndividualDetailsFactory
from grievance.models import GrievanceTicket
from household.fixtures import HouseholdFactory, IndividualFactory
from household.models import IndividualRoleInHousehold, ROLE_PRIMARY
from program.fixtures import ProgramFactory


class TestRoleReassignMutation(APITestCase):
    REASSIGN_ROLE_MUTATION = """
    mutation ReassignRole(
      $grievanceTicketId: ID!, 
      $householdId: ID!, 
      $individualId: ID!, 
      $role: String!
    ) {
      reassignRole(
        grievanceTicketId: $grievanceTicketId, 
        householdId: $householdId, 
        individualId: $individualId, 
        role: $role
      ) {
        household {
          id
        }
        individual {
          id
        }
      }
    }
    """

    def setUp(self):
        super().setUp()
        call_command("loadbusinessareas")
        self.user = UserFactory.create()
        self.business_area = BusinessArea.objects.get(slug="afghanistan")
        area_type = AdminAreaTypeFactory(name="Admin type one", admin_level=2, business_area=self.business_area,)
        self.admin_area = AdminAreaFactory(title="City Test", admin_area_type=area_type)
        program_one = ProgramFactory(name="Test program ONE", business_area=BusinessArea.objects.first())

        self.household = HouseholdFactory.build(id="b5cb9bb2-a4f3-49f0-a9c8-a2f260026054")
        self.household.registration_data_import.imported_by.save()
        self.household.registration_data_import.save()
        self.household.programs.add(program_one)

        self.individual = IndividualFactory(
            **{
                "id": "d4848d8e-4a1c-49e9-b1c0-1e994047164a",
                "full_name": "Benjamin Butler",
                "given_name": "Benjamin",
                "family_name": "Butler",
                "phone_no": "(953)682-4596",
                "birth_date": "1943-07-30",
                "household": None,
            },
        )

        self.household.head_of_household = self.individual
        self.household.save()

        self.individual.household = self.household
        self.individual.save()

        self.household.refresh_from_db()
        self.individual.refresh_from_db()

        self.role = IndividualRoleInHousehold.objects.create(
            household=self.household, individual=self.individual, role=ROLE_PRIMARY,
        )

        self.grievance_ticket = GrievanceTicketFactory(
            id="43c59eda-6664-41d6-9339-05efcb11da82",
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL,
            admin=self.admin_area.title,
            business_area=self.business_area,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
        )
        TicketDeleteIndividualDetailsFactory(
            ticket=self.grievance_ticket, individual=self.individual, approve_status=True,
        )

    def test_role_reassignment(self):
        variables = {
            "grievanceTicketId": self.id_to_base64(self.grievance_ticket.id, "GrievanceTicketNode"),
            "householdId": self.id_to_base64(self.household.id, "HouseholdNode"),
            "individualId": self.id_to_base64(self.individual.id, "IndividualNode"),
            "role": ROLE_PRIMARY,
        }
        self.graphql_request(
            request_string=self.REASSIGN_ROLE_MUTATION, context={"user": self.user}, variables=variables,
        )

        self.grievance_ticket.refresh_from_db()
        ticket_details = self.grievance_ticket.delete_individual_ticket_details
        role_reassign_data = ticket_details.role_reassign_data

        expected_data = {
            str(self.role.id): {
                "role": "PRIMARY",
                "household": "b5cb9bb2-a4f3-49f0-a9c8-a2f260026054",
                "individual": "d4848d8e-4a1c-49e9-b1c0-1e994047164a",
            }
        }
        self.assertEqual(role_reassign_data, expected_data)
