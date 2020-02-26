from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from registration_datahub.fixtures import RegistrationDataImportDatahubFactory


class TestRegistrationDataImportDatahubQuery(APITestCase):
    multi_db = True

    ALL_REGISTRATION_DATA_IMPORT_DATAHUB_QUERY = """
    query AllRegistrationDataImportsDatahub {
      allRegistrationDataImportsDatahub {
        edges {
          node {
            name
            status
            dataSource
            importedBy
          }
        }
      }
    }
    """
    REGISTRATION_DATA_IMPORT_DATAHUB_QUERY = """
    query RegistrationDataImportDatahub($id: ID!) {
      registrationDataImportDatahub(id: $id) {
        name
        status
        dataSource
        importedBy
      }
    }
    """

    def setUp(self):
        super().setUp()
        self.user = UserFactory.create()
        self.to_create = [
            {
                "name": "Lorem Ipsum",
                "status": "IN_PROGRESS",
                "imported_by": "Super User",
                "data_source": "XLS",
            },
            {
                "name": "Lorem Ipsum 2",
                "status": "DONE",
                "imported_by": "Super User",
                "data_source": "XLS",
            },
            {
                "name": "Lorem Ipsum 3",
                "status": "IN_PROGRESS",
                "imported_by": "Super User",
                "data_source": "XLS",
            },
        ]

        self.data = [
            RegistrationDataImportDatahubFactory(**item)
            for item in self.to_create
        ]

    def test_registration_data_import_datahub_query_all(self):
        self.snapshot_graphql_request(
            request_string=self.ALL_REGISTRATION_DATA_IMPORT_DATAHUB_QUERY,
            context={"user": self.user},
        )

    def test_registration_data_import_datahub_query_single(self):
        self.snapshot_graphql_request(
            request_string=self.REGISTRATION_DATA_IMPORT_DATAHUB_QUERY,
            context={"user": self.user},
            variables={
                "id": self.id_to_base64(
                    self.data[0].id, "RegistrationDataImportDatahub",
                )
            },
        )
