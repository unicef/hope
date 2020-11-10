from django.core.management import call_command

from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from core.fixtures import AdminAreaTypeFactory, AdminAreaFactory
from core.models import BusinessArea
from grievance.fixtures import TicketNoteFactory, GrievanceTicketFactory


class TestTicketNotes(APITestCase):
    CREATE_TICKET_NOTE_MUTATION = """
    mutation CreateTicketNote($noteInput: CreateTicketNoteInput!) {
      createTicketNote(noteInput: $noteInput) {
        grievanceTicketNote {
          description
          createdBy {
            firstName
            lastName
          }
        }
      }
    }
    """

    ALL_TICKET_NOTE_QUERY = """
    query AllTicketNotes($ticket: UUID!) {
      allTicketNotes(ticket: $ticket) {
        edges {
          node {
            createdBy {
              firstName
              lastName
            }
            description
          }
        }
      }
    }
    """

    def setUp(self):
        super().setUp()
        call_command("loadbusinessareas")
        business_area = BusinessArea.objects.get(slug="afghanistan")
        area_type = AdminAreaTypeFactory(name="Admin type one", admin_level=2, business_area=business_area)
        AdminAreaFactory(title="City Test", admin_area_type=area_type)
        self.user = UserFactory.create(first_name="John", last_name="Doe")
        self.ticket_1 = GrievanceTicketFactory(id="5d64ef51-5ed5-4891-b1a3-44a24acb7720")
        self.ticket_2 = GrievanceTicketFactory(id="1dd2dc43-d418-45bd-b9f7-7545dd4c13a5")

    def test_ticket_notes_query_all(self):
        TicketNoteFactory(
            description="This is a test note message", created_by=self.user, ticket=self.ticket_1,
        )
        variables = {"ticket": str(self.ticket_1.id)}
        self.snapshot_graphql_request(
            request_string=self.ALL_TICKET_NOTE_QUERY, context={"user": self.user}, variables=variables,
        )

    def test_create_ticket_note(self):
        input_data = {
            "noteInput": {
                "ticket": self.id_to_base64(self.ticket_2.id, "TicketNoteNode"),
                "description": "Example note description",
            }
        }
        self.snapshot_graphql_request(
            request_string=self.CREATE_TICKET_NOTE_MUTATION, context={"user": self.user}, variables=input_data,
        )
