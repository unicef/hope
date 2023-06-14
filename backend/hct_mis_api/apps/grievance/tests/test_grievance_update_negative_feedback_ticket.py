from typing import Any, List

from django.core.management import call_command

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.grievance.fixtures import (
    NegativeFeedbackTicketWithoutExtrasFactory,
)
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.fixtures import create_household


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
        cls.business_area = create_afghanistan()
        call_command("loadcountries")
        cls.user = UserFactory.create()

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
            context={"user": self.user},
            variables={
                "input": {
                    "description": "Test Feedback",
                    "assignedTo": self.id_to_base64(self.user.id, "UserNode"),
                    "admin": self.admin_area.p_code,
                    "language": "Polish, English",
                    "ticketId": self.id_to_base64(self.ticket.ticket.id, "GrievanceTicketNode"),
                }
            },
        )
