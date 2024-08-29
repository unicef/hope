from typing import Any, List
from unittest import mock
from unittest.mock import MagicMock, patch

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.registration_data.models import (
    DeduplicationEngineSimilarityPair,
    RegistrationDataImport,
)


class TestRegistrationDataImportQuery(APITestCase):
    databases = "__all__"

    ALL_REGISTRATION_DATA_IMPORT_DATAHUB_QUERY = """
    query AllRegistrationDataImports {
      allRegistrationDataImports(orderBy: "-name", businessArea: "afghanistan") {
        edges {
          node {
            name
            status
            dataSource
            numberOfIndividuals
            numberOfHouseholds
            batchDuplicatesCountAndPercentage{
              count
              percentage
            }
            batchUniqueCountAndPercentage{
              count
              percentage
            }
            goldenRecordDuplicatesCountAndPercentage{
              count
              percentage
            }
            goldenRecordPossibleDuplicatesCountAndPercentage{
              count
              percentage
            }
            goldenRecordUniqueCountAndPercentage{
              count
              percentage
            }
            totalHouseholdsCountWithValidPhoneNo
            isDeduplicated
            canMerge
            biometricDeduplicationEnabled
          }
        }
      }
    }
    """
    REGISTRATION_DATA_IMPORT_DATAHUB_QUERY = """
    query RegistrationDataImport($id: ID!) {
      registrationDataImport(id: $id) {
        name
        status
        dataSource
        numberOfIndividuals
        numberOfHouseholds
      }
    }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.partner = PartnerFactory(name="Test1")
        cls.user = UserFactory(partner=cls.partner)
        cls.program_active = ProgramFactory(status="ACTIVE")
        cls.program_active_biometric_deduplication_enabled = ProgramFactory(
            status="ACTIVE", biometric_deduplication_enabled=True
        )
        cls.program_draft = ProgramFactory(status="ACTIVE")
        cls.to_create = [
            {
                "name": "Lorem Ipsum",
                "status": "IN_REVIEW",
                "imported_by": cls.user,
                "data_source": "XLS",
                "number_of_individuals": 123,
                "number_of_households": 54,
                "program": cls.program_active,
            },
            {
                "name": "Lorem Ipsum 2",
                "status": "IN_REVIEW",
                "imported_by": cls.user,
                "data_source": "XLS",
                "number_of_individuals": 323,
                "number_of_households": 154,
                "program": cls.program_active_biometric_deduplication_enabled,
                "deduplication_engine_status": RegistrationDataImport.DEDUP_ENGINE_FINISHED,
            },
            {
                "name": "Lorem Ipsum 3",
                "status": "IN_REVIEW",
                "imported_by": cls.user,
                "data_source": "XLS",
                "number_of_individuals": 323,
                "number_of_households": 154,
                "program": cls.program_active_biometric_deduplication_enabled,
                "deduplication_engine_status": RegistrationDataImport.DEDUP_ENGINE_IN_PROGRESS,
            },
            {
                "name": "Lorem Ipsum 4",
                "status": "IN_REVIEW",
                "imported_by": cls.user,
                "data_source": "XLS",
                "number_of_individuals": 423,
                "number_of_households": 184,
                "program": cls.program_draft,
            },
        ]

        cls.data = [RegistrationDataImportFactory(**item, business_area=cls.business_area) for item in cls.to_create]

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.RDI_VIEW_LIST],
            ),
            (
                "without_permission",
                [],
            ),
        ]
    )
    @patch.dict(
        "os.environ",
        {"DEDUPLICATION_ENGINE_API_KEY": "dedup_api_key", "DEDUPLICATION_ENGINE_API_URL": "http://dedup-fake-url.com"},
    )
    @patch("hct_mis_api.apps.registration_datahub.apis.deduplication_engine.DeduplicationEngineAPI")
    @patch(
        "hct_mis_api.apps.registration_datahub.services.biometric_deduplication.BiometricDeduplicationService.get_duplicates_for_rdi_against_batch"
    )
    @patch(
        "hct_mis_api.apps.registration_datahub.services.biometric_deduplication.BiometricDeduplicationService.get_duplicates_for_rdi_against_population"
    )
    def test_registration_data_import_datahub_query_all(
        self,
        _: Any,
        permissions: List[Permissions],
        mock_deduplication_api: mock.Mock,
        mock_get_duplicates_for_rdi_against_batch: mock.Mock,
        mock_get_duplicates_for_rdi_against_population: mock.Mock,
    ) -> None:
        mock_deduplication_api_instance = MagicMock()
        mock_deduplication_api.return_value = mock_deduplication_api_instance
        mock_get_duplicates_for_rdi_against_batch.return_value = DeduplicationEngineSimilarityPair.objects.all()
        mock_get_duplicates_for_rdi_against_population.return_value = DeduplicationEngineSimilarityPair.objects.all()

        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        self.snapshot_graphql_request(
            request_string=self.ALL_REGISTRATION_DATA_IMPORT_DATAHUB_QUERY,
            context={"user": self.user},
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.RDI_VIEW_DETAILS],
            ),
            (
                "without_permission",
                [],
            ),
        ]
    )
    def test_registration_data_import_datahub_query_single_with_permission(
        self, _: Any, permissions: List[Permissions]
    ) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        self.snapshot_graphql_request(
            request_string=self.REGISTRATION_DATA_IMPORT_DATAHUB_QUERY,
            context={"user": self.user},
            variables={
                "id": self.id_to_base64(
                    self.data[0].id,
                    "RegistrationDataImportNode",
                )
            },
        )

    def test_registration_data_status_choices(self) -> None:
        self.snapshot_graphql_request(
            request_string="""
            query registrationDataStatusChoices {
              registrationDataStatusChoices {
                name
                value
              }
            }
            """,
            context={"user": self.user},
        )
