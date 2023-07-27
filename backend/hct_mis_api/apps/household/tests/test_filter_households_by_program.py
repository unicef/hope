from typing import Any, List

from django.conf import settings

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.program.fixtures import ProgramFactory


class TestFilterHouseholdsByProgram(APITestCase):
    fixtures = (f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json",)

    QUERY = """
        query AllHouseholds{
          allHouseholds(orderBy: "size", businessArea: "afghanistan") {
            edges {
              node {
                program {
                  name
                }
              }
            }
          }
        }
        """

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = UserFactory()
        cls.business_area = create_afghanistan()
        cls.program1 = ProgramFactory(name="Test program ONE", business_area=cls.business_area)
        cls.program2 = ProgramFactory(name="Test program TWO", business_area=cls.business_area)
        create_household({"program": cls.program1})
        create_household({"program": cls.program1})
        create_household({"program": cls.program2})

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_filter_households(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        headers = {
            "Business-Area": self.business_area.slug,
            "Program": self.id_to_base64(self.program1.id, "ProgramNode"),
        }
        self.snapshot_graphql_request(
            request_string=self.QUERY,
            context={"user": self.user, "headers": headers},
            variables={},
        )
