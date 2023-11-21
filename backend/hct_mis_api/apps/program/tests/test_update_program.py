from typing import Any, List

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import (
    create_afghanistan,
    generate_data_collecting_types,
)
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program


class TestUpdateProgram(APITestCase):
    UPDATE_PROGRAM_MUTATION = """
    mutation UpdateProgram($programData: UpdateProgramInput, $version: BigInt) {
      updateProgram(programData: $programData, version: $version) {
        program {
          name
          status
          dataCollectingType {
            label
            code
          }
        }
      }
    }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()
        generate_data_collecting_types()
        data_collecting_type = DataCollectingType.objects.get(code="full_collection")

        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.business_area.data_collecting_types.set(DataCollectingType.objects.all().values_list("id", flat=True))

        cls.program = ProgramFactory.create(
            name="initial name",
            status=Program.DRAFT,
            business_area=cls.business_area,
            data_collecting_type=data_collecting_type,
        )
        cls.program_finished = ProgramFactory.create(
            status=Program.FINISHED,
            business_area=cls.business_area,
        )

    def test_update_program_not_authenticated(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "name": "updated name",
                    "status": Program.ACTIVE,
                },
                "version": self.program.version,
            },
        )

    @parameterized.expand(
        [
            ("with_permissions", [Permissions.PROGRAMME_UPDATE, Permissions.PROGRAMME_ACTIVATE], True),
            (
                "with_partial_permissions",
                [
                    Permissions.PROGRAMME_UPDATE,
                ],
                False,
            ),
            ("without_permissions", [], False),
        ]
    )
    def test_update_program_authenticated(
        self, _: Any, permissions: List[Permissions], should_be_updated: bool
    ) -> None:
        user = UserFactory.create()
        self.create_user_role_with_permissions(user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "name": "updated name",
                    "status": Program.ACTIVE,
                    "dataCollectingTypeCode": "partial_individuals",
                },
                "version": self.program.version,
            },
        )

        updated_program = Program.objects.get(id=self.program.id)
        if should_be_updated:
            assert updated_program.status == Program.ACTIVE
            assert updated_program.name == "updated name"
        else:
            assert updated_program.status == Program.DRAFT
            assert updated_program.name == "initial name"

    def test_update_active_program_with_dct(self) -> None:
        user = UserFactory.create()
        self.create_user_role_with_permissions(user, [Permissions.PROGRAMME_UPDATE], self.business_area)
        data_collecting_type = DataCollectingType.objects.get(code="full_collection")
        data_collecting_type.limit_to.add(self.business_area)
        Program.objects.filter(id=self.program.id).update(
            status=Program.ACTIVE, data_collecting_type=data_collecting_type
        )

        self.program.refresh_from_db()
        self.assertEqual(self.program.status, Program.ACTIVE)
        self.assertEqual(self.program.data_collecting_type.code, "full_collection")

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "dataCollectingTypeCode": "partial_individuals",
                },
                "version": self.program.version,
            },
        )
        self.assertEqual(self.program.data_collecting_type.code, "full_collection")

    def test_update_program_with_deprecated_dct(self) -> None:
        dct, _ = DataCollectingType.objects.update_or_create(
            **{"label": "Deprecated", "code": "deprecated", "description": "Deprecated", "deprecated": True}
        )
        dct.limit_to.add(self.business_area)

        user = UserFactory.create()
        self.create_user_role_with_permissions(user, [Permissions.PROGRAMME_UPDATE], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "dataCollectingTypeCode": "deprecated",
                },
                "version": self.program.version,
            },
        )

    def test_update_program_with_inactive_dct(self) -> None:
        dct, _ = DataCollectingType.objects.update_or_create(
            **{"label": "Inactive", "code": "inactive", "description": "Inactive", "active": False}
        )
        dct.limit_to.add(self.business_area)

        user = UserFactory.create()
        self.create_user_role_with_permissions(user, [Permissions.PROGRAMME_UPDATE], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "dataCollectingTypeCode": "inactive",
                },
                "version": self.program.version,
            },
        )

    def test_update_program_with_dct_from_other_ba(self) -> None:
        DataCollectingType.objects.update_or_create(
            **{"label": "Test Wrong BA", "code": "test_wrong_ba", "description": "Test Wrong BA"}
        )
        user = UserFactory.create()
        self.create_user_role_with_permissions(user, [Permissions.PROGRAMME_CREATE], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "dataCollectingTypeCode": "test_wrong_ba",
                },
                "version": self.program.version,
            },
        )

    def test_update_program_when_finished(self) -> None:
        user = UserFactory.create()
        self.create_user_role_with_permissions(user, [Permissions.PROGRAMME_UPDATE], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": user},
            variables={
                "programData": {"id": self.id_to_base64(self.program_finished.id, "ProgramNode"), "name": "xyz"},
                "version": self.program_finished.version,
            },
        )
