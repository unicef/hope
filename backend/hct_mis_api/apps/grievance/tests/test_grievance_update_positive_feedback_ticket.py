from django.core.management import call_command

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import AdminAreaFactory, AdminAreaLevelFactory
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.grievance.fixtures import (
    PositiveFeedbackTicketWithoutExtrasFactory,
)
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.fixtures import create_household


class TestGrievanceUpdatePositiveFeedbackTicketQuery(APITestCase):
    QUERY = """
        mutation UpdateGrievanceTicket(
          $input: UpdateGrievanceTicketInput!
        ) {
          updateGrievanceTicket(input: $input) {
            grievanceTicket {
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

    def setUp(self):
        super().setUp()
        call_command("loadbusinessareas")
        call_command("loadcountries")
        self.user = UserFactory.create()
        self.business_area = BusinessArea.objects.get(slug="afghanistan")
        area_type = AdminAreaLevelFactory(
            name="Admin type one",
            admin_level=2,
            business_area=self.business_area,
        )
        self.admin_area = AdminAreaFactory(title="City Test", admin_area_level=area_type, p_code="asdfgfhghkjltr")

        country = geo_models.Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="Admin type one",
            country=country,
            area_level=2,
        )
        AreaFactory(name="City Test", area_type=area_type, p_code="asdfgfhghkjltr")

        self.household, self.individuals = create_household(
            {"size": 1, "business_area": self.business_area},
            {"given_name": "John", "family_name": "Doe", "middle_name": "", "full_name": "John Doe"},
        )
        self.ticket = PositiveFeedbackTicketWithoutExtrasFactory()
        self.ticket.ticket.status = GrievanceTicket.STATUS_NEW
        self.ticket.ticket.save()

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_UPDATE],
            ),
            ("without_permission", []),
        ]
    )
    def test_update_positive_feedback_ticket_without_extras(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        input_data = self._prepare_input()

        self.snapshot_graphql_request(
            request_string=self.QUERY,
            context={"user": self.user},
            variables=input_data,
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_UPDATE],
            ),
            ("without_permission", []),
        ]
    )
    def test_update_positive_feedback_ticket_with_household_extras(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        extras = {
            "household": self.id_to_base64(self.household.id, "HouseholdNode"),
        }
        input_data = self._prepare_input(extras)

        self.snapshot_graphql_request(
            request_string=self.QUERY,
            context={"user": self.user},
            variables=input_data,
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_UPDATE],
            ),
            ("without_permission", []),
        ]
    )
    def test_update_positive_feedback_ticket_with_individual_extras(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        extras = {
            "individual": self.id_to_base64(self.individuals[0].id, "IndividualNode"),
        }
        input_data = self._prepare_input(extras)

        self.snapshot_graphql_request(
            request_string=self.QUERY,
            context={"user": self.user},
            variables=input_data,
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_UPDATE],
            ),
            ("without_permission", []),
        ]
    )
    def test_update_positive_feedback_ticket_with_household_and_individual_extras(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        extras = {
            "household": self.id_to_base64(self.household.id, "HouseholdNode"),
            "individual": self.id_to_base64(self.individuals[0].id, "IndividualNode"),
        }
        input_data = self._prepare_input(extras)

        self.snapshot_graphql_request(
            request_string=self.QUERY,
            context={"user": self.user},
            variables=input_data,
        )

    def _prepare_input(self, extras=None):
        input_data = {
            "input": {
                "description": "Test Feedback",
                "assignedTo": self.id_to_base64(self.user.id, "UserNode"),
                "admin": self.admin_area.p_code,
                "language": "Polish, English",
                "ticketId": self.id_to_base64(self.ticket.ticket.id, "GrievanceTicketNode"),
            }
        }

        if extras:
            input_data["input"]["extras"] = {"category": {"positiveFeedbackTicketExtras": extras}}

        return input_data
