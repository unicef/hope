from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program


class TestUserFilter(APITestCase):
    ALL_USERS_QUERY = """
  query AllUsers(
    $businessArea: String!
    $orderBy: String
  ) {
    allUsers(
      businessArea: $businessArea
      orderBy: $orderBy
    ) {
      edges {
        node {
          username
          partner {
              name
          }
        }
      }
    }
  }
"""

    @classmethod
    def setUpTestData(cls) -> None:
        business_area = create_afghanistan()

        # user with UNICEF partner
        partner_unicef = PartnerFactory(name="UNICEF")
        cls.user_with_unicef_partner = UserFactory(partner=partner_unicef, username="unicef_user")

        # user with access to BA
        user_in_ba = UserFactory(username="user_in_ba", partner=None)
        cls.create_user_role_with_permissions(user_in_ba, [Permissions.GRIEVANCES_CREATE], business_area)

        # user with partner with access to BA
        program = ProgramFactory(name="Test Program", status=Program.DRAFT, business_area=business_area)
        partner_perms = {
            str(business_area.pk): {
                "roles": [],
                "programs": {str(program.pk): []},
            }
        }
        partner = PartnerFactory(name="Test Partner", permissions=partner_perms)
        UserFactory(partner=partner, username="user_with_partner_in_ba")

        # user without access to BA
        partner_no_perms = {}
        partner_without_ba_access = PartnerFactory(name="Partner Without Access", permissions=partner_no_perms)
        UserFactory(partner=partner_without_ba_access, username="user_without_BA_access")

    def test_users_by_business_area(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.ALL_USERS_QUERY,
            variables={"businessArea": "afghanistan", "orderBy": "partner"},
            context={"user": self.user_with_unicef_partner},
        )
