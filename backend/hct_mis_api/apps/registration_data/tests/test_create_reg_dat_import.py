import unittest

from account.fixtures import UserFactory
from core.base_test_case import APITestCase


@unittest.skip("Not supporting creating Registration Data Import")
class TestCreateRegistrationDataImport(APITestCase):
    CREATE_REGISTRATION_DATA_IMPORT_MUTATION = """
    mutation CreateRegistrationDataImport(
      $registrationDataImportData: CreateRegistrationDataImportInput!
    ) {
      createRegistrationDataImport(
        registrationDataImportData: $registrationDataImportData
      ) {
        registrationDataImport {
          name
          status
          importDate
          dataSource
          numberOfIndividuals
          numberOfHouseholds
        }
      }
    }
    """

    def setUp(self):
        super().setUp()
        self.user = UserFactory.create()
        self.registration_data_import = {
            "registrationDataImportData": {
                "name": "Test name",
                "status": "IN_REVIEW",
                "importDate": "2019-12-20T15:00:00",
                "importedById": self.id_to_base64(self.user.id, "User"),
                "dataSource": "XLS",
                "numberOfIndividuals": 300,
                "numberOfHouseholds": 67,
            }
        }

    def test_create_reg_data_import_not_authenticated(self):
        self.snapshot_graphql_request(
            request_string=self.CREATE_REGISTRATION_DATA_IMPORT_MUTATION,
            variables=self.registration_data_import,
        )

    def test_create_reg_data_import_authenticated(self):
        self.snapshot_graphql_request(
            request_string=self.CREATE_REGISTRATION_DATA_IMPORT_MUTATION,
            context={"user": self.user},
            variables=self.registration_data_import,
        )
