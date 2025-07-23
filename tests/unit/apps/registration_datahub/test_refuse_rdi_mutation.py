from typing import Any, List

from django.conf import settings

import pytest
from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.utils.elasticsearch_utils import rebuild_search_index

pytestmark = pytest.mark.usefixtures("django_elasticsearch_setup")


@pytest.mark.elasticsearch
class TestRefuseRdiMutation(APITestCase):
    databases = "__all__"
    fixtures = (f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json",)

    REFUSE_IMPORT_QUERY = """
      mutation RefuseRDI($id: ID!, $refuseReason: String) {
        refuseRegistrationDataImport(id: $id, refuseReason: $refuseReason) {
          registrationDataImport {
            status
            refuseReason
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

        cls.rdi = RegistrationDataImportFactory()

        rebuild_search_index()

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

        household = HouseholdFactory(registration_data_import=rdi)
        IndividualFactory(household=household)
        IndividualFactory(household=household)
        IndividualFactory(household=household)

        self.assertEqual(Household.objects.all().count(), 1)
        self.assertEqual(Individual.objects.all().count(), 3)

        self.graphql_request(
            request_string=self.REFUSE_IMPORT_QUERY,
            context={"user": self.user},
            variables={"id": self.id_to_base64(rdi.id, "RegistrationDataImportNode")},
        )

        self.assertEqual(Household.objects.all().count(), 0)
        self.assertEqual(Individual.objects.all().count(), 0)

    def test_refuse_registration_data_import_with_reason(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.RDI_REFUSE_IMPORT], self.business_area)

        rdi = RegistrationDataImportFactory(status=RegistrationDataImport.IN_REVIEW)
        imported_household = HouseholdFactory(registration_data_import=rdi)
        IndividualFactory(household=imported_household)

        self.snapshot_graphql_request(
            request_string=self.REFUSE_IMPORT_QUERY,
            context={"user": self.user},
            variables={
                "id": self.id_to_base64(rdi.id, "RegistrationDataImportNode"),
                "refuseReason": "This is refuse reason",
            },
        )
