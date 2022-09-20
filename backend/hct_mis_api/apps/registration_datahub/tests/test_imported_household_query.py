from django.core.management import call_command

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.registration_datahub.fixtures import ImportedHouseholdFactory


class TestImportedHouseholdQuery(APITestCase):
    databases = "__all__"
    fixtures = ("hct_mis_api/apps/geo/fixtures/data.json",)

    ALL_IMPORTED_HOUSEHOLD_QUERY = """
    query AllImportedHouseholds{
      allImportedHouseholds(businessArea: "afghanistan", orderBy: "size") {
        edges {
          node {
            size
            countryOrigin
            address
          }
        }
      }
    }
    """
    IMPORTED_HOUSEHOLD_QUERY = """
    query ImportedHousehold($id: ID!) {
      importedHousehold(id: $id) {
        size
        countryOrigin
        address
      }
    }
    """

    @classmethod
    def setUpTestData(cls):
        call_command("loadbusinessareas")
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.user = UserFactory.create()
        sizes_list = (2, 4, 5, 1, 3, 11, 14)
        cls.households = [
            ImportedHouseholdFactory(
                size=size,
                address="Lorem Ipsum",
                country_origin="PL",
            )
            for size in sizes_list
        ]
        for household in cls.households:
            household.registration_data_import.business_area_slug = "afghanistan"
            household.registration_data_import.save()

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.RDI_VIEW_DETAILS],
            ),
            (
                "without_permission",
                [],
            ),
        ]
    )
    def test_imported_household_query_all(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.ALL_IMPORTED_HOUSEHOLD_QUERY,
            context={"user": self.user},
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.RDI_VIEW_DETAILS],
            ),
            (
                "without_permission",
                [],
            ),
        ]
    )
    def test_imported_household_query_single(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.IMPORTED_HOUSEHOLD_QUERY,
            context={"user": self.user},
            variables={"id": self.id_to_base64(self.households[0].id, "ImportedHouseholdNode")},
        )
