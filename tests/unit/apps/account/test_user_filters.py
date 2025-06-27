from hct_mis_api.apps.account.fixtures import (
    PartnerFactory,
    RoleFactory,
    UserFactory,
    UserRoleFactory,
)
from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.utils import encode_id_base64_required
from hct_mis_api.apps.program.fixtures import ProgramFactory


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
          userRoles {
            businessArea {
              name
            }
            role {
              name
              permissions
            }
          }
          partnerRoles {
            businessArea {
              name
            }
            roles {
              name
              permissions
            }
          }
        }
      }
    }
  }
  """

    ALL_USERS_QUERY_FILTER_BY_PROGRAM = """
    query AllUsers(
      $program: String
      $businessArea: String!
      $orderBy: String
    ) {
      allUsers(
        program: $program
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

    ALL_USERS_QUERY_FILTER_BY_ROLES = """
    query AllUsers(
    $roles: [String]
    $businessArea: String!
    $orderBy: String
    ) {
      allUsers(
        roles: $roles
        businessArea: $businessArea
        orderBy: $orderBy
      ) {
        edges {
          node {
            username
            partner {
              name
            }
            userRoles {
              businessArea {
                name
              }
              role {
                name
                permissions
              }
            }
            partnerRoles {
              businessArea {
                name
              }
              roles {
                name
                permissions
              }
            }
          }
        }
      }
    }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        User.objects.all().delete()
        business_area = create_afghanistan()
        partner_unicef = PartnerFactory(name="UNICEF")
        cls.program = ProgramFactory(name="Test Program")

        # user with UNICEF partner without role in BA
        UserFactory(partner=partner_unicef, username="unicef_user_without_role")

        # user without access to BA
        partner_without_ba_role = PartnerFactory(name="Partner Without Access")
        UserFactory(partner=partner_without_ba_role, username="user_without_BA_role")

        cls.role = RoleFactory(name="Test Role")

        # user with role in BA
        user_with_test_role = UserFactory(username="user_with_test_role")
        UserRoleFactory(user=user_with_test_role, role=cls.role, business_area=business_area)

        # user with partner with role in BA and access to program
        role_management = RoleFactory(
            name="User Management View Role", permissions=[Permissions.USER_MANAGEMENT_VIEW_LIST.value]
        )
        partner_with_test_role = PartnerFactory(name="Partner With Test Role")
        cls.add_partner_role_in_business_area(
            partner=partner_with_test_role,
            business_area=business_area,
            roles=[cls.role, role_management],
        )
        cls.update_partner_access_to_program(
            partner=partner_with_test_role,
            program=cls.program,
        )
        cls.user = UserFactory(username="user_with_partner_with_test_role", partner=partner_with_test_role)

    def test_users_by_business_area(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.ALL_USERS_QUERY,
            variables={"businessArea": "afghanistan", "orderBy": "partner"},
            context={"user": self.user},
        )

    def test_users_by_program(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.ALL_USERS_QUERY_FILTER_BY_PROGRAM,
            variables={
                "businessArea": "afghanistan",
                "program": encode_id_base64_required(self.program.id, "Program"),
                "orderBy": "partner",
            },
            context={"user": self.user},
        )

    def test_users_by_roles(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.ALL_USERS_QUERY_FILTER_BY_ROLES,
            variables={"businessArea": "afghanistan", "roles": [str(self.role.id)], "orderBy": "partner"},
            context={"user": self.user},
        )
