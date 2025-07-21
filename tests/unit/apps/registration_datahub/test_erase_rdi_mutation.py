from django.conf import settings

from tests.extras.test_utils.factories.account import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from tests.extras.test_utils.factories.core import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from tests.extras.test_utils.factories.household import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.registration_data.models import RegistrationDataImport


class TestEraseRdiMutation(APITestCase):
    fixtures = (f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json",)

    ERASE_IMPORT_QUERY = """
      mutation EraseRegistrationDataImportMutation($id: ID!) {
        eraseRegistrationDataImport(id: $id) {
          registrationDataImport {
            erased
            status
          }
        }
      }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.user = UserFactory()
        create_afghanistan()
        cls.business_area_slug = "afghanistan"
        cls.business_area = BusinessArea.objects.get(slug=cls.business_area_slug)

        # Correct status
        cls.rdi_1 = RegistrationDataImportFactory(status=RegistrationDataImport.MERGE_ERROR)
        # Wrong status
        cls.rdi_2 = RegistrationDataImportFactory(status=RegistrationDataImport.IN_REVIEW)

    def test_erase_registration_data_import_removes_data_links(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.RDI_REFUSE_IMPORT], self.business_area)

        imported_household = HouseholdFactory(registration_data_import=self.rdi_1)
        IndividualFactory(household=imported_household)

        self.assertEqual(Household.objects.count(), 1)
        self.assertEqual(Individual.objects.count(), 1)

        self.graphql_request(
            request_string=self.ERASE_IMPORT_QUERY,
            context={"user": self.user},
            variables={"id": self.id_to_base64(self.rdi_1.id, "RegistrationDataImportNode")},
        )

        self.assertEqual(RegistrationDataImport.objects.filter(erased=True).count(), 1)

        self.assertEqual(Household.objects.count(), 0)
        self.assertEqual(Individual.objects.count(), 0)

    def test_erase_registration_data_import_raises_error_when_wrong_status(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.RDI_REFUSE_IMPORT], self.business_area)

        imported_household = HouseholdFactory(registration_data_import=self.rdi_2)
        IndividualFactory(household=imported_household)

        self.assertEqual(Household.objects.count(), 1)
        self.assertEqual(Individual.objects.count(), 1)

        abort_mutation_response = self.graphql_request(
            request_string=self.ERASE_IMPORT_QUERY,
            context={"user": self.user},
            variables={"id": self.id_to_base64(self.rdi_2.id, "RegistrationDataImportNode")},
        )

        assert "errors" in abort_mutation_response
        self.assertEqual(
            abort_mutation_response["errors"][0]["message"],
            "RDI can be erased only when status is: IMPORT_ERROR, MERGE_ERROR, DEDUPLICATION_FAILED",
        )

        self.assertEqual(RegistrationDataImport.objects.filter(erased=True).count(), 0)
        self.assertEqual(
            RegistrationDataImport.objects.filter(erased=False).count(), RegistrationDataImport.objects.count()
        )

        self.assertEqual(Household.objects.count(), 1)
        self.assertEqual(Individual.objects.count(), 1)
