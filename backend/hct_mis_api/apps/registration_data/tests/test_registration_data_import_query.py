from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory


class TestRegistrationDataImportQuery(APITestCase):
    databases = "__all__"

    ALL_REGISTRATION_DATA_IMPORT_DATAHUB_QUERY = """
    query AllRegistrationDataImports {
      allRegistrationDataImports(orderBy: "-name", businessArea: "afghanistan") {
        edges {
          node {
            name
            status
            dataSource
            numberOfIndividuals
            numberOfHouseholds
          }
        }
      }
    }
    """
    REGISTRATION_DATA_IMPORT_DATAHUB_QUERY = """
    query RegistrationDataImport($id: ID!) {
      registrationDataImport(id: $id) {
        name
        status
        dataSource
        numberOfIndividuals
        numberOfHouseholds
      }
    }
    """

    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.user = UserFactory.create()
        cls.to_create = [
            {
                "name": "Lorem Ipsum",
                "status": "IN_REVIEW",
                "imported_by": cls.user,
                "data_source": "XLS",
                "number_of_individuals": 123,
                "number_of_households": 54,
            },
            {
                "name": "Lorem Ipsum 2",
                "status": "IN_REVIEW",
                "imported_by": cls.user,
                "data_source": "XLS",
                "number_of_individuals": 323,
                "number_of_households": 154,
            },
            {
                "name": "Lorem Ipsum 3",
                "status": "IN_REVIEW",
                "imported_by": cls.user,
                "data_source": "XLS",
                "number_of_individuals": 423,
                "number_of_households": 184,
            },
        ]

        cls.data = [RegistrationDataImportFactory(**item, business_area=cls.business_area) for item in cls.to_create]

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.RDI_VIEW_LIST],
            ),
            (
                "without_permission",
                [],
            ),
        ]
    )
    def test_registration_data_import_datahub_query_all(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        self.snapshot_graphql_request(
            request_string=self.ALL_REGISTRATION_DATA_IMPORT_DATAHUB_QUERY,
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
    def test_registration_data_import_datahub_query_single_with_permission(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        self.snapshot_graphql_request(
            request_string=self.REGISTRATION_DATA_IMPORT_DATAHUB_QUERY,
            context={"user": self.user},
            variables={
                "id": self.id_to_base64(
                    self.data[0].id,
                    "RegistrationDataImportNode",
                )
            },
        )
