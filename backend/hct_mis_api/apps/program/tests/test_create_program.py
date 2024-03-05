from typing import Any, List

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import (
    BusinessAreaFactory,
    PartnerFactory,
    UserFactory,
)
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program


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
          cashPlus
          populationGoal
          administrativeAreasOfImplementation
          dataCollectingType {
            code
            label
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
        cls.partner = PartnerFactory(name="WFP")
        cls.user = UserFactory.create(partner=cls.partner)
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.data_collecting_type = DataCollectingType.objects.create(
            code="partial_individuals",
            label="Partial",
            description="Partial individuals collected",
            active=True,
            individual_filters_available=True,
        )
        cls.data_collecting_type.available_for.add(cls.business_area)
        cls.program_data = {
            "programData": {
                "name": "Test",
                "startDate": "2019-12-20",
                "endDate": "2021-12-20",
                "budget": 20000000,
                "description": "my description of program",
                "frequencyOfPayments": "REGULAR",
                "sector": "EDUCATION",
                "cashPlus": True,
                "populationGoal": 150000,
                "administrativeAreasOfImplementation": "Lorem Ipsum",
                "businessAreaSlug": cls.business_area.slug,
                "dataCollectingTypeCode": cls.data_collecting_type.code,
                "partners": [{"id": str(cls.partner.id), "areaAccess": "BUSINESS_AREA"}],
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

    def test_program_unique_constraints(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_CREATE], self.business_area)

        self.assertEqual(Program.objects.count(), 0)

        # First, response is ok and program is created
        response_ok = self.graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables=self.program_data,
        )
        assert "errors" not in response_ok
        self.assertEqual(Program.objects.count(), 1)

        # Second, response has error due to unique constraints
        response_error = self.graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables=self.program_data,
        )
        self.assertEqual(Program.objects.count(), 1)
        self.assertEqual(
            response_error["data"]["createProgram"]["validationErrors"]["__all__"][0],
            f"Program for name: {self.program_data['programData']['name']} and business_area: {self.program_data['programData']['businessAreaSlug']} already exists.",
        )

        # Third, we remove program with given name and business area
        Program.objects.first().delete()
        self.assertEqual(Program.objects.count(), 0)

        # Fourth, we can create program with the same name and business area like removed one
        response_ok = self.graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables=self.program_data,
        )
        assert "errors" not in response_ok
        self.assertEqual(Program.objects.count(), 1)

    def test_create_program_with_programme_code(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_CREATE], self.business_area)
        self.program_data["programData"]["programmeCode"] = "ABC2"

        self.graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION, context={"user": self.user}, variables=self.program_data
        )

        program = Program.objects.get(name="Test")
        self.assertEqual(program.programme_code, "ABC2")

    def test_programme_code_should_be_unique_among_the_same_business_area(self) -> None:
        ProgramFactory(programme_code="ABC2", business_area=self.business_area)

        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_CREATE], self.business_area)
        self.program_data["programData"]["programmeCode"] = "ABC2"

        self.snapshot_graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION, context={"user": self.user}, variables=self.program_data
        )

        program_count = Program.objects.filter(programme_code="ABC2").count()
        self.assertEqual(program_count, 1)

    def test_programme_code_can_be_reuse_in_different_business_area(self) -> None:
        business_area = BusinessAreaFactory()
        ProgramFactory(programme_code="AB.2", business_area=business_area)
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_CREATE], self.business_area)
        self.program_data["programData"]["programmeCode"] = "AB.2"

        self.graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION, context={"user": self.user}, variables=self.program_data
        )

        program_count = Program.objects.filter(programme_code="AB.2").count()
        self.assertEqual(program_count, 2)

    def test_create_program_without_programme_code(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_CREATE], self.business_area)

        self.graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION, context={"user": self.user}, variables=self.program_data
        )

        program = Program.objects.get(name="Test")
        self.assertIsNotNone(program.programme_code)
        self.assertEqual(len(program.programme_code), 4)

    def test_create_program_with_programme_code_as_empty_string(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_CREATE], self.business_area)
        self.program_data["programData"]["programmeCode"] = ""

        self.graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION, context={"user": self.user}, variables=self.program_data
        )

        program = Program.objects.get(name="Test")
        self.assertIsNotNone(program.programme_code)
        self.assertEqual(len(program.programme_code), 4)

    def test_create_program_with_programme_code_lowercase(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_CREATE], self.business_area)
        self.program_data["programData"]["programmeCode"] = "ab2-"

        self.graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION, context={"user": self.user}, variables=self.program_data
        )

        program = Program.objects.get(name="Test")
        self.assertIsNotNone(program.programme_code)
        self.assertEqual(len(program.programme_code), 4)
        self.assertEqual(program.programme_code, "AB2-")

    def test_create_program_with_programme_code_not_within_allowed_characters(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_CREATE], self.business_area)
        self.program_data["programData"]["programmeCode"] = "A@C2"

        self.snapshot_graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION, context={"user": self.user}, variables=self.program_data
        )

    def test_create_program_with_programme_code_less_than_4_chars(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_CREATE], self.business_area)
        self.program_data["programData"]["programmeCode"] = "Ab2"

        self.snapshot_graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION, context={"user": self.user}, variables=self.program_data
        )

    def test_create_program_with_programme_code_greater_than_4_chars(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_CREATE], self.business_area)
        self.program_data["programData"]["programmeCode"] = "AbCd2"

        self.snapshot_graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION, context={"user": self.user}, variables=self.program_data
        )
