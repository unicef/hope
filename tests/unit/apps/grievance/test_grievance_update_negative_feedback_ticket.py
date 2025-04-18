from typing import Any, List

from django.core.management import call_command

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.grievance.fixtures import (
    NegativeFeedbackTicketWithoutExtrasFactory,
)
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program


class TestGrievanceUpdateNegativeFeedbackTicketQuery(APITestCase):
    QUERY = """
        mutation UpdateGrievanceTicket(
          $input: UpdateGrievanceTicketInput!
        ) {
          updateGrievanceTicket(input: $input) {
            grievanceTicket {
              negativeFeedbackTicketDetails {
                household {
                  size
                }
                individual {
                  fullName
                }
              }
            }
          }
        }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        call_command("loadcountries")
        partner = PartnerFactory(name="Partner")
        cls.user = UserFactory.create(partner=partner)

        country = geo_models.Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="Admin type one",
            country=country,
            area_level=2,
        )
        cls.admin_area = AreaFactory(name="City Test", area_type=area_type, p_code="asdfgfhghkjltr")

        cls.household, cls.individuals = create_household(
            {"size": 1, "business_area": cls.business_area},
            {"given_name": "John", "family_name": "Doe", "middle_name": "", "full_name": "John Doe"},
        )
        cls.ticket = NegativeFeedbackTicketWithoutExtrasFactory()
        cls.ticket.ticket.status = GrievanceTicket.STATUS_NEW
        cls.ticket.ticket.save()
        cls.program = ProgramFactory(business_area=BusinessArea.objects.first(), status=Program.ACTIVE)
        cls.update_partner_access_to_program(partner, cls.program)

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_UPDATE],
            ),
            ("without_permission", []),
        ]
    )
    def test_update_negative_feedback_ticket_not_supported(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.QUERY,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables={
                "input": {
                    "description": "Test Feedback",
                    "assignedTo": self.id_to_base64(self.user.id, "UserNode"),
                    "admin": encode_id_base64(str(self.admin_area.id), "Area"),
                    "language": "Polish, English",
                    "ticketId": self.id_to_base64(self.ticket.ticket.id, "GrievanceTicketNode"),
                }
            },
        )
