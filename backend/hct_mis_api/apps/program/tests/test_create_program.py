from typing import Any, List

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType


class TestCreateProgram(APITestCase):
    CREATE_PROGRAM_MUTATION = """
    mutation CreateProgram($programData: CreateProgramInput!) {
      createProgram(programData: $programData) {
        program {
          name
          status
          startDate
          endDate
          budget
          description
          frequencyOfPayments
          sector
          scope
          cashPlus
          populationGoal
          administrativeAreasOfImplementation
          dataCollectingType {
            code
            description
            active
            individualFiltersAvailable
          }
        }
        validationErrors
      }
    }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()
        cls.user = UserFactory.create()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.data_collecting_type = DataCollectingType.objects.create(
            code="partial_individuals",
            description="Partial individuals collected",
            active=True,
            individual_filters_available=True,
        )
        cls.data_collecting_type.limit_to.add(cls.business_area)
        cls.program_data = {
            "programData": {
                "name": "Test",
                "startDate": "2019-12-20",
                "endDate": "2021-12-20",
                "budget": 20000000,
                "description": "my description of program",
                "frequencyOfPayments": "REGULAR",
                "sector": "EDUCATION",
                "scope": "UNICEF",
                "cashPlus": True,
                "populationGoal": 150000,
                "administrativeAreasOfImplementation": "Lorem Ipsum",
                "businessAreaSlug": cls.business_area.slug,
                "dataCollectingTypeCode": cls.data_collecting_type.code,
            }
        }

    def test_create_program_not_authenticated(self) -> None:
        self.snapshot_graphql_request(request_string=self.CREATE_PROGRAM_MUTATION, variables=self.program_data)

    @parameterized.expand(
        [
            ("with_permission", [Permissions.PROGRAMME_CREATE], False),
            ("without_permission", [], False),
            ("with_permission_but_invalid_dates", [Permissions.PROGRAMME_CREATE], True),
        ]
    )
    def test_create_program_authenticated(
        self, _: Any, permissions: List[Permissions], should_set_wrong_date: bool
    ) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        if should_set_wrong_date:
            self.program_data["programData"]["endDate"] = "2018-12-20"

        self.snapshot_graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION, context={"user": self.user}, variables=self.program_data
        )

    def test_create_program_without_dct(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_CREATE], self.business_area)

        program_data = self.program_data
        program_data["programData"]["dataCollectingTypeCode"] = None

        self.snapshot_graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION, context={"user": self.user}, variables=program_data
        )

    def test_create_program_with_deprecated_dct(self) -> None:
        dct, _ = DataCollectingType.objects.update_or_create(
            **{"label": "Deprecated", "code": "deprecated", "description": "Deprecated", "deprecated": True}
        )
        dct.limit_to.add(self.business_area)
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_CREATE], self.business_area)

        program_data = self.program_data
        program_data["programData"]["dataCollectingTypeCode"] = "deprecated"

        self.snapshot_graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION, context={"user": self.user}, variables=program_data
        )

    def test_create_program_with_inactive_dct(self) -> None:
        dct, _ = DataCollectingType.objects.update_or_create(
            **{"label": "Inactive", "code": "inactive", "description": "Inactive", "active": False}
        )
        dct.limit_to.add(self.business_area)
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_CREATE], self.business_area)

        program_data = self.program_data
        program_data["programData"]["dataCollectingTypeCode"] = "inactive"

        self.snapshot_graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION, context={"user": self.user}, variables=program_data
        )

    def test_create_program_with_dct_from_other_ba(self) -> None:
        DataCollectingType.objects.update_or_create(
            **{"label": "Test Wrong BA", "code": "test_wrong_ba", "description": "Test Wrong BA", "active": True}
        )
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_CREATE], self.business_area)

        program_data = self.program_data
        program_data["programData"]["dataCollectingTypeCode"] = "test_wrong_ba"

        self.snapshot_graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION, context={"user": self.user}, variables=program_data
        )
