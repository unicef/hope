from typing import Any, List

from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from parameterized import parameterized

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.registration_data.models import RegistrationDataImport


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
            biometricDeduplicated
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
        super().setUpTestData()
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.partner = PartnerFactory(name="Test1")
        cls.user = UserFactory(partner=cls.partner)
        cls.program_active = ProgramFactory(status="ACTIVE")
        cls.program_active_biometric_deduplication_enabled = ProgramFactory(
            status="ACTIVE", biometric_deduplication_enabled=True
        )
        cls.program_draft = ProgramFactory(status="DRAFT")
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
    def test_registration_data_import_datahub_query_all(
        self,
        _: Any,
        permissions: List[Permissions],
    ) -> None:
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
