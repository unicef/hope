from typing import Any, List

from django.core.management import call_command

from parameterized import parameterized

from tests.extras.test_utils.factories.account import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from tests.extras.test_utils.factories.core import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo import models as geo_models
from tests.extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory
from tests.extras.test_utils.factories.grievance import (
    GrievanceTicketFactory,
    TicketNoteFactory,
)
from tests.extras.test_utils.factories.program import ProgramFactory
from hct_mis_api.apps.program.models import Program


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
    def setUpTestData(cls) -> None:
        super().setUpTestData()
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

        partner = PartnerFactory(name="Partner")
        cls.user = UserFactory.create(first_name="John", last_name="Doe", partner=partner)
        cls.ticket_1 = GrievanceTicketFactory(id="5d64ef51-5ed5-4891-b1a3-44a24acb7720")
        cls.ticket_2 = GrievanceTicketFactory(id="1dd2dc43-d418-45bd-b9f7-7545dd4c13a5")
        cls.program = ProgramFactory(business_area=BusinessArea.objects.first(), status=Program.ACTIVE)
        cls.update_partner_access_to_program(partner, cls.program)

    def test_ticket_notes_query_all(self) -> None:
        TicketNoteFactory(
            description="This is a test note message",
            created_by=self.user,
            ticket=self.ticket_1,
        )
        variables = {"ticket": str(self.ticket_1.id)}
        self.snapshot_graphql_request(
            request_string=self.ALL_TICKET_NOTE_QUERY,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
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
    def test_create_ticket_note(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        input_data = {
            "noteInput": {
                "ticket": self.id_to_base64(self.ticket_2.id, "TicketNoteNode"),
                "description": "Example note description",
            }
        }
        self.snapshot_graphql_request(
            request_string=self.CREATE_TICKET_NOTE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables=input_data,
        )
