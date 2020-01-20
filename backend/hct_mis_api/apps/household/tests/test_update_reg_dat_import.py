from account.fixtures import UserFactory
from core.tests import APITestCase
from household.fixtures import RegistrationDataImportFactory


class TestUpdateRegistrationDataImport(APITestCase):
    UPDATE_REGISTRATION_DATA_IMPORT_MUTATION = """
    mutation UpdateRegistrationDataImport(
      $registrationDataImportData: UpdateRegistrationDataImportInput
    ) {
      updateRegistrationDataImport(
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
        self.registration_data_import = RegistrationDataImportFactory.create()
        self.registration_data_import_variables = {
            'registrationDataImportData': {
                'id': self.id_to_base64(
                    self.registration_data_import.id,
                    'RegistrationDataImport',
                ),
                'name': 'Test name',
                'status': 'DONE',
                'importDate': '2019-12-20T15:00:00',
                'importedById': self.id_to_base64(self.user.id, 'User'),
                'dataSource': 'XLS',
                'numberOfIndividuals': 300,
                'numberOfHouseholds': 67,
            }
        }

    def test_update_reg_data_import_not_authenticated(self):
        self.snapshot_graphql_request(
            request_string=self.UPDATE_REGISTRATION_DATA_IMPORT_MUTATION,
            variables=self.registration_data_import_variables,
        )

    def test_update_reg_data_import_authenticated(self):
        self.snapshot_graphql_request(
            request_string=self.UPDATE_REGISTRATION_DATA_IMPORT_MUTATION,
            context={'user': self.user},
            variables=self.registration_data_import_variables,
        )
