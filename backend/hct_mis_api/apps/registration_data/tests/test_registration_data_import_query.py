from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from registration_data.fixtures import RegistrationDataImportFactory


class TestRegistrationDataImportQuery(APITestCase):
    multi_db = True

    ALL_REGISTRATION_DATA_IMPORT_DATAHUB_QUERY = """
    query AllRegistrationDataImports {
      allRegistrationDataImports {
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

    def setUp(self):
        super().setUp()
        self.user = UserFactory.create()
        self.to_create = [
            {
                "name": "Lorem Ipsum",
                "status": "IN_PROGRESS",
                "imported_by": self.user,
                "data_source": "XLS",
                "number_of_individuals": 123,
                "number_of_households": 54,
            },
            {
                "name": "Lorem Ipsum 2",
                "status": "DONE",
                "imported_by": self.user,
                "data_source": "XLS",
                "number_of_individuals": 323,
                "number_of_households": 154,
            },
            {
                "name": "Lorem Ipsum 3",
                "status": "IN_PROGRESS",
                "imported_by": self.user,
                "data_source": "XLS",
                "number_of_individuals": 423,
                "number_of_households": 184,
            },
        ]

        self.data = [
            RegistrationDataImportFactory(**item)
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
                    self.data[0].id, "RegistrationDataImport",
                )
            },
        )
