from typing import Any, List

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.fixtures import (
    ImportedHouseholdFactory,
    ImportedIndividualFactory,
    RegistrationDataImportDatahubFactory,
)
from hct_mis_api.apps.registration_datahub.models import (
    ImportedHousehold,
    ImportedIndividual,
)


class TestRefuseRdiMutation(APITestCase):
    databases = "__all__"
    fixtures = ("hct_mis_api/apps/geo/fixtures/data.json",)

    REFUSE_IMPORT_QUERY = """
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
    def setUpTestData(cls) -> None:
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
    def test_refuse_registration_data_import(self, _: Any, permissions: List[Permissions], status: bool) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        self.rdi.status = status
        self.rdi.save()

        self.snapshot_graphql_request(
            request_string=self.REFUSE_IMPORT_QUERY,
            context={"user": self.user},
            variables={"id": self.id_to_base64(self.rdi.id, "RegistrationDataImportNode")},
        )

    def test_refuse_registration_data_import_removes_data_links(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.RDI_REFUSE_IMPORT], self.business_area)

        rdi = RegistrationDataImportFactory(status=RegistrationDataImport.IN_REVIEW)
        rdi_hub = RegistrationDataImportDatahubFactory()
        rdi.datahub_id = rdi_hub.id
        rdi.save()

        imported_household = ImportedHouseholdFactory(registration_data_import=rdi_hub)
        ImportedIndividualFactory(household=imported_household)
        ImportedIndividualFactory(household=imported_household)
        ImportedIndividualFactory(household=imported_household)

        self.assertEqual(ImportedHousehold.objects.all().count(), 1)
        self.assertEqual(ImportedIndividual.objects.all().count(), 3)

        self.graphql_request(
            request_string=self.REFUSE_IMPORT_QUERY,
            context={"user": self.user},
            variables={"id": self.id_to_base64(rdi.id, "RegistrationDataImportNode")},
        )

        self.assertEqual(ImportedHousehold.objects.all().count(), 0)
        self.assertEqual(ImportedIndividual.objects.all().count(), 0)
