from hct_mis_api.apps.account.fixtures import PartnerFactory, RoleFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan


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
        cls.create_user_role_with_permissions(
            cls.user_with_unicef_partner, [Permissions.USER_MANAGEMENT_VIEW_LIST], business_area
        )

        # user with access to BA
        user_in_ba = UserFactory(username="user_in_ba", partner=None)
        cls.create_user_role_with_permissions(user_in_ba, [Permissions.GRIEVANCES_CREATE], business_area)

        # user with partner with role in BA
        partner = PartnerFactory(name="Test Partner")
        role = RoleFactory(name="Partner Role", permissions=[Permissions.GRIEVANCES_CREATE])
        cls.add_partner_role_in_business_area(partner, business_area, [role])
        UserFactory(partner=partner, username="user_with_partner_in_ba")

        # user without access to BA
        partner_without_ba_access = PartnerFactory(name="Partner Without Access")
        UserFactory(partner=partner_without_ba_access, username="user_without_BA_access")

    def test_users_by_business_area(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.ALL_USERS_QUERY,
            variables={"businessArea": "afghanistan", "orderBy": "partner"},
            context={"user": self.user_with_unicef_partner},
        )
