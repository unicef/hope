from typing import Any, List

from django.core.management import call_command

from parameterized import parameterized

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.program.models import Program
from tests.extras.test_utils.factories.account import PartnerFactory, UserFactory
from tests.extras.test_utils.factories.core import create_afghanistan
from tests.extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory
from tests.extras.test_utils.factories.household import create_household
from tests.extras.test_utils.factories.program import ProgramFactory


class TestGrievanceCreatePositiveFeedbackTicketQuery(APITestCase):
    CREATE_GRIEVANCE_MUTATION = """
    mutation CreateGrievanceTicket($input: CreateGrievanceTicketInput!) {
      createGrievanceTicket(input: $input) {
        grievanceTickets{
          category
          admin
          language
          description
          consent
          positiveFeedbackTicketDetails {
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
        create_afghanistan()
        call_command("loadcountries")
        partner = PartnerFactory(name="Partner")
        cls.user = UserFactory.create(partner=partner)
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.program = ProgramFactory(status=Program.ACTIVE, business_area=cls.business_area)
        cls.update_partner_access_to_program(partner, cls.program)

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

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_CREATE],
            ),
            ("without_permission", []),
        ]
    )
    def test_create_positive_feedback_ticket_not_supported(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.CREATE_GRIEVANCE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables={
                "input": {
                    "description": "Test Feedback",
                    "assignedTo": self.id_to_base64(self.user.id, "UserNode"),
                    "category": GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
                    "admin": encode_id_base64(str(self.admin_area.id), "Area"),
                    "language": "Polish, English",
                    "consent": True,
                    "businessArea": "afghanistan",
                }
            },
        )
