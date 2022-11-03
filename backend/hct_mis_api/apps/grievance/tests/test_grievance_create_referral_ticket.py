from typing import Dict
from django.core.management import call_command

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.fixtures import create_household


class TestGrievanceCreateReferralTicketQuery(APITestCase):
    CREATE_GRIEVANCE_MUTATION = """
    mutation CreateGrievanceTicket($input: CreateGrievanceTicketInput!) {
      createGrievanceTicket(input: $input) {
        grievanceTickets{
          category
          admin
          language
          description
          consent
          referralTicketDetails {
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
    def setUpTestData(cls):
        create_afghanistan()
        call_command("loadcountries")
        cls.user = UserFactory.create()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

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
    def test_create_referral_ticket_without_extras(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        input_data = self._prepare_input()

        self.snapshot_graphql_request(
            request_string=self.CREATE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables=input_data,
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
    def test_create_referral_ticket_with_household_extras(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        extras = {
            "household": self.id_to_base64(self.household.id, "HouseholdNode"),
        }
        input_data = self._prepare_input(extras)

        self.snapshot_graphql_request(
            request_string=self.CREATE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables=input_data,
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
    def test_create_referral_ticket_with_individual_extras(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        extras = {
            "individual": self.id_to_base64(self.individuals[0].id, "IndividualNode"),
        }
        input_data = self._prepare_input(extras)

        self.snapshot_graphql_request(
            request_string=self.CREATE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables=input_data,
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
    def test_create_referral_ticket_with_household_and_individual_extras(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        extras = {
            "household": self.id_to_base64(self.household.id, "HouseholdNode"),
            "individual": self.id_to_base64(self.individuals[0].id, "IndividualNode"),
        }
        input_data = self._prepare_input(extras)

        self.snapshot_graphql_request(
            request_string=self.CREATE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables=input_data,
        )

    def _prepare_input(self, extras=None) -> Dict:
        input_data = {
            "input": {
                "description": "Test Feedback",
                "assignedTo": self.id_to_base64(self.user.id, "UserNode"),
                "category": GrievanceTicket.CATEGORY_REFERRAL,
                "admin": self.admin_area.p_code,
                "language": "Polish, English",
                "consent": True,
                "businessArea": "afghanistan",
            }
        }

        if extras:
            input_data["input"]["extras"] = {"category": {"referralTicketExtras": extras}}

        return input_data
