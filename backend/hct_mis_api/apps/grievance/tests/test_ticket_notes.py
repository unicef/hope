from django.core.management import call_command

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.grievance.fixtures import (
    GrievanceTicketFactory,
    TicketNoteFactory,
)


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

    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        call_command("loadcountries")
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        country = geo_models.Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="Admin type one",
            country=country,
            area_level=2,
        )
        AreaFactory(name="City Test", area_type=area_type, p_code="asdfgfhghkjltr")

        cls.user = UserFactory.create(first_name="John", last_name="Doe")
        cls.ticket_1 = GrievanceTicketFactory(id="5d64ef51-5ed5-4891-b1a3-44a24acb7720")
        cls.ticket_2 = GrievanceTicketFactory(id="1dd2dc43-d418-45bd-b9f7-7545dd4c13a5")

    def test_ticket_notes_query_all(self):
        TicketNoteFactory(
            description="This is a test note message",
            created_by=self.user,
            ticket=self.ticket_1,
        )
        variables = {"ticket": str(self.ticket_1.id)}
        self.snapshot_graphql_request(
            request_string=self.ALL_TICKET_NOTE_QUERY,
            context={"user": self.user},
            variables=variables,
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_ADD_NOTE],
            ),
            ("without_permission", []),
        ]
    )
    def test_create_ticket_note(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        input_data = {
            "noteInput": {
                "ticket": self.id_to_base64(self.ticket_2.id, "TicketNoteNode"),
                "description": "Example note description",
            }
        }
        self.snapshot_graphql_request(
            request_string=self.CREATE_TICKET_NOTE_MUTATION,
            context={"user": self.user},
            variables=input_data,
        )
