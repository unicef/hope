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
            hctId
          }
        }
      }
    }
    """
    REGISTRATION_DATA_IMPORT_DATAHUB_QUERY = """
    query RegistrationDataImportDatahub($id: ID!) {
      registrationDataImportDatahub(id: $id) {
        name
        hctId
      }
    }
    """

    def setUp(self):
        super().setUp()
        self.user = UserFactory.create()
        self.to_create = [
            {
                "name": "Lorem Ipsum",
                "hct_id": "42191234-5a31-11ea-82b4-0242ac130003",
            },
            {
                "name": "Lorem Ipsum 2",
                "hct_id": "c2abeded-4aa0-422a-bfa2-b18dec20071f",
            },
            {
                "name": "Lorem Ipsum 3",
                "hct_id": "df7e419f-26bd-4a52-8698-0a201447a5f1",
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
