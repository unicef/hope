import unittest

from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from household.fixtures import RegistrationDataImportFactory
from registration_data.models import RegistrationDataImport


@unittest.skip("Not supporting deleting Registration Data Import")
class TestDeleteRegistrationDataImport(APITestCase):
    DELETE_PROGRAM_MUTATION = """
    mutation DeleteRegistrationDataImport($registrationDataImportId: String!) {
      deleteRegistrationDataImport(
        registrationDataImportId: $registrationDataImportId
      ) {
          ok
      }
    }
    """

    def setUp(self):
        super().setUp()
        self.user = UserFactory.create()
        self.reg_data_import = RegistrationDataImportFactory.create()

    def test_delete_reg_data_import_not_authenticated(self):
        self.snapshot_graphql_request(
            request_string=self.DELETE_PROGRAM_MUTATION,
            variables={
                "registrationDataImportId": self.id_to_base64(
                    self.reg_data_import.id, "RegistrationDataImport",
                )
            },
        )

    def test_delete_reg_data_import_authenticated(self):
        self.snapshot_graphql_request(
            request_string=self.DELETE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                "registrationDataImportId": self.id_to_base64(
                    self.reg_data_import.id, "RegistrationDataImport",
                )
            },
        )

        assert not RegistrationDataImport.objects.filter(
            id=self.reg_data_import.id,
        ).exists()
