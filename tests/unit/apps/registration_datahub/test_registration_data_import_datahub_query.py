from hct_mis_api.apps.core.base_test_case import APITestCase
from tests.extras.test_utils.factories.account import UserFactory
from tests.extras.test_utils.factories.registration_data import (
    RegistrationDataImportDatahubFactory,
)


class TestRegistrationDataImportDatahubQuery(APITestCase):
    databases = "__all__"

    REGISTRATION_DATA_IMPORT_DATAHUB_QUERY = """
    query RegistrationDataImportDatahub($id: ID!) {
      registrationDataImportDatahub(id: $id) {
        name
        hctId
      }
    }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.user = UserFactory.create()
        cls.to_create = [
            {"name": "Lorem Ipsum", "hct_id": "42191234-5a31-11ea-82b4-0242ac130003"},
            {"name": "Lorem Ipsum 2", "hct_id": "c2abeded-4aa0-422a-bfa2-b18dec20071f"},
            {"name": "Lorem Ipsum 3", "hct_id": "df7e419f-26bd-4a52-8698-0a201447a5f1"},
        ]

        cls.data = [RegistrationDataImportDatahubFactory(**item) for item in cls.to_create]

    def test_registration_data_import_datahub_query_single(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.REGISTRATION_DATA_IMPORT_DATAHUB_QUERY,
            context={"user": self.user},
            variables={
                "id": self.id_to_base64(
                    self.data[0].id,
                    "RegistrationDataImportDatahubNode",
                )
            },
        )
