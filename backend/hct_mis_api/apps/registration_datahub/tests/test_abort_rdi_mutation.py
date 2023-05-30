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


class TestAbortRdiMutation(APITestCase):
    databases = "__all__"
    fixtures = ("hct_mis_api/apps/geo/fixtures/data.json",)

    ABORT_IMPORT_QUERY = """
      mutation AbortRegistrationDataImportMutation(
        $id: ID!
      ) {
        abortRegistrationDataImport(
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

        # Correct status
        cls.rdi_1 = RegistrationDataImportFactory(status=RegistrationDataImport.MERGE_ERROR)
        cls.rdi_hub_1 = RegistrationDataImportDatahubFactory()
        cls.rdi_1.datahub_id = cls.rdi_hub_1.id
        cls.rdi_1.save()

        # Wrong status
        cls.rdi_2 = RegistrationDataImportFactory(status=RegistrationDataImport.IN_REVIEW)
        cls.rdi_hub_2 = RegistrationDataImportDatahubFactory()
        cls.rdi_2.datahub_id = cls.rdi_hub_2.id
        cls.rdi_2.save()

    def test_abort_registration_data_import_removes_data_links(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.RDI_REFUSE_IMPORT], self.business_area)

        imported_household = ImportedHouseholdFactory(registration_data_import=self.rdi_hub_1)
        ImportedIndividualFactory(household=imported_household)

        self.assertEqual(ImportedHousehold.objects.count(), 1)
        self.assertEqual(ImportedIndividual.objects.count(), 1)

        self.graphql_request(
            request_string=self.ABORT_IMPORT_QUERY,
            context={"user": self.user},
            variables={"id": self.id_to_base64(self.rdi_1.id, "RegistrationDataImportNode")},
        )

        self.assertEqual(RegistrationDataImport.objects.filter(status=RegistrationDataImport.ABORTED).count(), 1)

        self.assertEqual(ImportedHousehold.objects.count(), 0)
        self.assertEqual(ImportedIndividual.objects.count(), 0)

    def test_abort_registration_data_import_raises_error_when_wrong_status(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.RDI_REFUSE_IMPORT], self.business_area)

        imported_household = ImportedHouseholdFactory(registration_data_import=self.rdi_hub_2)
        ImportedIndividualFactory(household=imported_household)

        self.assertEqual(ImportedHousehold.objects.count(), 1)
        self.assertEqual(ImportedIndividual.objects.count(), 1)

        abort_mutation_response = self.graphql_request(
            request_string=self.ABORT_IMPORT_QUERY,
            context={"user": self.user},
            variables={"id": self.id_to_base64(self.rdi_2.id, "RegistrationDataImportNode")},
        )

        assert "errors" in abort_mutation_response
        self.assertEqual(
            abort_mutation_response["errors"][0]["message"],
            "RDI can be aborted only when status is: IMPORT_ERROR, MERGE_ERROR, DEDUPLICATION_FAILED",
        )

        self.assertEqual(RegistrationDataImport.objects.filter(status=RegistrationDataImport.ABORTED).count(), 0)

        self.assertEqual(ImportedHousehold.objects.count(), 1)
        self.assertEqual(ImportedIndividual.objects.count(), 1)
