from typing import Any, List

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.models import RegistrationDataImport


class TestRegistrationDataProgramPopulationImportMutations(APITestCase):
    databases = "__all__"

    CREATE_REGISTRATION_DATA_IMPORT = """
    mutation CreateRegistrationProgramPopulationImport(
      $registrationDataImportData: RegistrationProgramPopulationImportMutationInput!
    ) {
      registrationProgramPopulationImport(
        registrationDataImportData: $registrationDataImportData
      ) {
        registrationDataImport {
          name
          dataSource
          screenBeneficiary
        }
      }
    }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        cls.partner = PartnerFactory(name="Partner")
        cls.afghanistan = create_afghanistan()
        cls.import_from_program = ProgramFactory(status=Program.ACTIVE)
        cls.import_to_program = ProgramFactory(status=Program.ACTIVE)

    def _create_user_with_permissions(self) -> Any:
        user = UserFactory(partner=self.partner)
        self.create_user_role_with_permissions(user, [Permissions.RDI_IMPORT_DATA], self.afghanistan)
        self.update_partner_access_to_program(self.partner, self.import_to_program)
        return user

    def test_registration_data_import_create_nothing_to_import(self) -> None:
        user = self._create_user_with_permissions()
        self.snapshot_graphql_request(
            request_string=self.CREATE_REGISTRATION_DATA_IMPORT,
            context={
                "user": user,
                "headers": {"Program": self.id_to_base64(self.import_to_program.id, "ProgramNode")},
            },
            variables={
                "registrationDataImportData": {
                    "importFromProgramId": self.id_to_base64(self.import_from_program.id, "ProgramNode"),
                    "name": "New Import of Data 123",
                    "businessAreaSlug": self.afghanistan.slug,
                }
            },
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.RDI_IMPORT_DATA],
            ),
            (
                "without_permission",
                [],
            ),
        ]
    )
    def test_registration_data_import_create(self, _: Any, permissions: List[Permissions]) -> None:
        user = UserFactory(partner=self.partner)
        self.create_user_role_with_permissions(user, permissions, self.afghanistan)
        self.update_partner_access_to_program(self.partner, self.import_to_program)
        self.household, self.individuals = create_household_and_individuals(
            household_data={"program": self.import_from_program},
            individuals_data=[{}, {}],
        )

        self.snapshot_graphql_request(
            request_string=self.CREATE_REGISTRATION_DATA_IMPORT,
            context={
                "user": user,
                "headers": {"Program": self.id_to_base64(self.import_to_program.id, "ProgramNode")},
            },
            variables={
                "registrationDataImportData": {
                    "importFromProgramId": self.id_to_base64(self.import_from_program.id, "ProgramNode"),
                    "name": "New Import of Data 123",
                    "businessAreaSlug": self.afghanistan.slug,
                }
            },
        )
        if permissions:
            rdi = RegistrationDataImport.objects.filter(imported_by=user).first()
            self.assertEqual(rdi.status, RegistrationDataImport.IMPORT_SCHEDULED)
            self.assertEqual(rdi.data_source, RegistrationDataImport.PROGRAM_POPULATION)
            self.assertEqual(rdi.number_of_individuals, 2)
            self.assertEqual(rdi.number_of_households, 1)
            self.assertEqual(rdi.program_id, self.import_to_program.id)

    def test_registration_data_import_create_program_finished(self) -> None:
        user = self._create_user_with_permissions()
        self.household, self.individuals = create_household_and_individuals(
            household_data={"program": self.import_from_program},
            individuals_data=[{}, {}],
        )
        self.import_to_program.status = Program.FINISHED
        self.import_to_program.save()

        self.snapshot_graphql_request(
            request_string=self.CREATE_REGISTRATION_DATA_IMPORT,
            context={
                "user": user,
                "headers": {"Program": self.id_to_base64(self.import_to_program.id, "ProgramNode")},
            },
            variables={
                "registrationDataImportData": {
                    "importFromProgramId": self.id_to_base64(self.import_from_program.id, "ProgramNode"),
                    "name": "New Import of Data 123",
                    "businessAreaSlug": self.afghanistan.slug,
                }
            },
        )

    @parameterized.expand(
        [
            (
                "can_check_against_sanction_list",
                True,
            ),
            (
                "cannot_check_against_sanction_list",
                False,
            ),
        ]
    )
    def test_registration_data_import_create_cannot_check_against_sanction_list(
        self, _: Any, sanction_list: bool
    ) -> None:
        user = self._create_user_with_permissions()
        self.household, self.individuals = create_household_and_individuals(
            household_data={"program": self.import_from_program},
            individuals_data=[{}, {}],
        )
        if sanction_list:
            self.afghanistan.screen_beneficiary = True
            self.afghanistan.save()

        self.snapshot_graphql_request(
            request_string=self.CREATE_REGISTRATION_DATA_IMPORT,
            context={
                "user": user,
                "headers": {"Program": self.id_to_base64(self.import_to_program.id, "ProgramNode")},
            },
            variables={
                "registrationDataImportData": {
                    "importFromProgramId": self.id_to_base64(self.import_from_program.id, "ProgramNode"),
                    "name": "New Import of Data 123",
                    "businessAreaSlug": self.afghanistan.slug,
                    "screenBeneficiary": True,
                }
            },
        )
