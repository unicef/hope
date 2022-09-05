from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory


class TestRefuseRdiMutation(APITestCase):
    databases = "__all__"

    QUERY = """
      mutation RefuseRegistrationDataImportMutation(
        $id: ID!
      ) {
        refuseRegistrationDataImport(
          id: $id
        ) {
          registrationDataImport {
            status
          }
        }
      }
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        create_afghanistan()
        cls.business_area_slug = "afghanistan"
        cls.business_area = BusinessArea.objects.get(slug=cls.business_area_slug)

        cls.rdi = RegistrationDataImportFactory()

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.RDI_REFUSE_IMPORT],
                "IN_REVIEW",
            ),
            (
                "with_permission",
                [Permissions.RDI_REFUSE_IMPORT],
                "MERGED",
            ),
            (
                "without_permission",
                [],
                "IN_REVIEW",
            ),
        ]
    )
    def test_refuse_registration_data_import(self, _, permissions, status):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        self.rdi.status = status
        self.rdi.save()

        self.snapshot_graphql_request(
            request_string=self.QUERY,
            context={"user": self.user},
            variables={"id": self.id_to_base64(self.rdi.id, "RegistrationDataImportNode")},
        )
