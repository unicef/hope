from django.conf import settings

from hct_mis_api.apps.account.fixtures import (
    PartnerFactory,
    RoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)
from hct_mis_api.apps.account.models import User
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
            program {
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
            program {
              name
            }
            role {
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
              program {
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
              program {
                name
              }
              role {
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
        unicef_hq = PartnerFactory(name=settings.UNICEF_HQ_PARTNER, parent=partner_unicef)
        cls.program = ProgramFactory(name="Test Program")

        # user with UNICEF partner without role in BA
        UserFactory(partner=unicef_hq, username="unicef_user_without_role", email="unicef_user_without_role@email.com")

        # user without access to BA
        partner_without_ba_role = PartnerFactory(name="Partner Without Access")
        UserFactory(partner=partner_without_ba_role, username="user_without_BA_role", email="user_without_BA_role")

        cls.role = RoleFactory(name="Test Role", permissions=["USER_MANAGEMENT_VIEW_LIST"])

        # user with role in BA in different program
        user_with_test_role = UserFactory(username="user_with_test_role", partner=None, email="user_with_test_role@email.com")
        RoleAssignmentFactory(
            user=user_with_test_role,
            role=cls.role,
            business_area=business_area,
            program=ProgramFactory(name="Different Program", business_area=business_area),
        )

        # user with role in whole BA
        user_with_test_role_in_whole_ba = UserFactory(username="user_with_test_role_in_whole_ba", partner=None, email="user_with_test_role_in_whole_ba@email.com")
        RoleAssignmentFactory(user=user_with_test_role_in_whole_ba, role=cls.role, business_area=business_area)

        # user with partner with role in BA and access to program
        partner_with_test_role = PartnerFactory(name="Partner With Test Role")
        RoleAssignmentFactory(
            partner=partner_with_test_role, role=cls.role, business_area=business_area, program=cls.program
        )
        cls.user = UserFactory(username="user_with_partner_with_test_role", partner=partner_with_test_role, email="user_with_partner_with_test_role@email.com")

    def test_users_by_business_area(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.ALL_USERS_QUERY,
            variables={"businessArea": "afghanistan", "orderBy": "email"},
            context={"user": self.user},
        )

    def test_users_by_program(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.ALL_USERS_QUERY_FILTER_BY_PROGRAM,
            variables={
                "businessArea": "afghanistan",
                "program": encode_id_base64_required(self.program.id, "Program"),
                "orderBy": "email",
            },
            context={"user": self.user},
        )

    def test_users_by_roles(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.ALL_USERS_QUERY_FILTER_BY_ROLES,
            variables={"businessArea": "afghanistan", "roles": [str(self.role.id)], "orderBy": "email"},
            context={"user": self.user},
        )
