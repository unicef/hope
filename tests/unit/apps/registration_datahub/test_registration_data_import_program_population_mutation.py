from typing import Any, List

from parameterized import parameterized

from tests.extras.test_utils.factories.account import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from tests.extras.test_utils.factories.core import DataCollectingTypeFactory, create_afghanistan
from hct_mis_api.apps.core.models import DataCollectingType
from tests.extras.test_utils.factories.household import (
    IndividualFactory,
    create_household_and_individuals,
)
from hct_mis_api.apps.household.models import ROLE_PRIMARY, IndividualRoleInHousehold
from tests.extras.test_utils.factories.fixtures import BeneficiaryGroupFactory, ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from tests.extras.test_utils.factories.sanction_list import SanctionListFactory


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
        super().setUpTestData()
        cls.partner = PartnerFactory(name="Partner")
        cls.afghanistan = create_afghanistan()
        cls.data_collecting_type = DataCollectingTypeFactory()
        cls.import_from_program = ProgramFactory(status=Program.ACTIVE, data_collecting_type=cls.data_collecting_type)
        cls.import_to_program = ProgramFactory(status=Program.ACTIVE, data_collecting_type=cls.data_collecting_type)

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

    def test_registration_data_import_different_beneficiary_group(self) -> None:
        user = UserFactory(partner=self.partner)
        beneficiary_group1 = BeneficiaryGroupFactory()
        beneficiary_group2 = BeneficiaryGroupFactory(name="Other Group")
        self.import_to_program.beneficiary_group = beneficiary_group1
        self.import_to_program.save()
        self.import_from_program.beneficiary_group = beneficiary_group2
        self.import_from_program.save()

        self.create_user_role_with_permissions(user, [Permissions.RDI_IMPORT_DATA], self.afghanistan)
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

    def test_registration_data_import_matching_beneficiary_group(self) -> None:
        user = UserFactory(partner=self.partner)
        beneficiary_group1 = BeneficiaryGroupFactory()
        self.import_to_program.beneficiary_group = beneficiary_group1
        self.import_to_program.save()
        self.import_from_program.beneficiary_group = beneficiary_group1
        self.import_from_program.save()

        self.create_user_role_with_permissions(user, [Permissions.RDI_IMPORT_DATA], self.afghanistan)
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

    def test_registration_data_import_not_compatible_data_collecting_type(self) -> None:
        user = UserFactory(partner=self.partner)
        not_compatible_data_collecting_type = DataCollectingTypeFactory()
        self.import_to_program.data_collecting_type = not_compatible_data_collecting_type
        self.import_to_program.save()

        self.create_user_role_with_permissions(user, [Permissions.RDI_IMPORT_DATA], self.afghanistan)
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
            sanction_list = SanctionListFactory()
            sanction_list.save()
            self.import_to_program.sanction_lists.add(sanction_list)

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

    def test_registration_data_import_create_program_with_ids_filter(self) -> None:
        user = UserFactory(partner=self.partner)
        self.create_user_role_with_permissions(user, [Permissions.RDI_IMPORT_DATA], self.afghanistan)
        self.update_partner_access_to_program(self.partner, self.import_to_program)

        self.household_1, self.individuals_1 = create_household_and_individuals(
            household_data={"program": self.import_from_program},
            individuals_data=[{}],
        )
        self.household_2, self.individuals_2 = create_household_and_individuals(
            household_data={"program": self.import_from_program},
            individuals_data=[{}],
        )
        self.household_3, self.individuals_3 = create_household_and_individuals(
            household_data={"program": self.import_from_program},
            individuals_data=[{}, {}],
        )
        self.household_4, self.individuals_4 = create_household_and_individuals(
            household_data={"program": self.import_from_program},
            individuals_data=[{}, {}],
        )
        self.household_5, self.individuals_5 = create_household_and_individuals(
            household_data={"program": self.import_from_program},
            individuals_data=[{}, {}],
        )
        # create external collector for household_5
        external_collector = IndividualFactory(program=self.import_from_program)
        IndividualRoleInHousehold.objects.create(
            household=self.household_5,
            individual=external_collector,
            role=ROLE_PRIMARY,
            rdi_merge_status="MERGED",
        )

        hh_ids = f"{self.household_3.unicef_id}, {self.household_4.unicef_id}, HH-000001"
        ind_ids = f"{self.individuals_1[0].unicef_id}, {self.individuals_2[0].unicef_id}, IND-111222"

        self.snapshot_graphql_request(
            request_string=self.CREATE_REGISTRATION_DATA_IMPORT,
            context={
                "user": user,
                "headers": {"Program": self.id_to_base64(self.import_to_program.id, "ProgramNode")},
            },
            variables={
                "registrationDataImportData": {
                    "importFromProgramId": self.id_to_base64(self.import_from_program.id, "ProgramNode"),
                    "name": "New Import of Data HH Ids",
                    "businessAreaSlug": self.afghanistan.slug,
                    "importFromIds": hh_ids,
                }
            },
        )

        rdi = RegistrationDataImport.objects.filter(name="New Import of Data HH Ids").first()
        self.assertEqual(rdi.status, RegistrationDataImport.IMPORT_SCHEDULED)
        self.assertEqual(rdi.data_source, RegistrationDataImport.PROGRAM_POPULATION)
        self.assertEqual(rdi.import_from_ids, hh_ids)
        self.assertEqual(rdi.program.data_collecting_type.type, DataCollectingType.Type.STANDARD)
        self.assertEqual(rdi.number_of_individuals, 4)
        self.assertEqual(rdi.number_of_households, 2)
        self.assertEqual(rdi.program_id, self.import_to_program.id)

        # check with external collector
        self.graphql_request(
            request_string=self.CREATE_REGISTRATION_DATA_IMPORT,
            context={
                "user": user,
                "headers": {"Program": self.id_to_base64(self.import_to_program.id, "ProgramNode")},
            },
            variables={
                "registrationDataImportData": {
                    "importFromProgramId": self.id_to_base64(self.import_from_program.id, "ProgramNode"),
                    "name": "New Import of Data HH Ids with external collector",
                    "businessAreaSlug": self.afghanistan.slug,
                    "importFromIds": self.household_5.unicef_id,
                }
            },
        )

        rdi = RegistrationDataImport.objects.filter(name="New Import of Data HH Ids with external collector").first()
        self.assertEqual(rdi.status, RegistrationDataImport.IMPORT_SCHEDULED)
        self.assertEqual(rdi.data_source, RegistrationDataImport.PROGRAM_POPULATION)
        self.assertEqual(rdi.import_from_ids, self.household_5.unicef_id)
        self.assertEqual(rdi.program.data_collecting_type.type, DataCollectingType.Type.STANDARD)
        self.assertEqual(rdi.number_of_individuals, 3)  # 2 Inds and + one external collector
        self.assertEqual(rdi.number_of_households, 1)  # household_5
        self.assertEqual(rdi.program_id, self.import_to_program.id)

        # update program DCT
        self.import_to_program.data_collecting_type.type = DataCollectingType.Type.SOCIAL
        self.import_to_program.data_collecting_type.save()

        self.snapshot_graphql_request(
            request_string=self.CREATE_REGISTRATION_DATA_IMPORT,
            context={
                "user": user,
                "headers": {"Program": self.id_to_base64(self.import_to_program.id, "ProgramNode")},
            },
            variables={
                "registrationDataImportData": {
                    "importFromProgramId": self.id_to_base64(self.import_from_program.id, "ProgramNode"),
                    "name": "New Import of Data Ind ids",
                    "businessAreaSlug": self.afghanistan.slug,
                    "importFromIds": ind_ids,
                }
            },
        )

        rdi = RegistrationDataImport.objects.filter(name="New Import of Data Ind ids").first()
        self.assertEqual(rdi.status, RegistrationDataImport.IMPORT_SCHEDULED)
        self.assertEqual(rdi.data_source, RegistrationDataImport.PROGRAM_POPULATION)
        self.assertEqual(rdi.program.data_collecting_type.type, DataCollectingType.Type.SOCIAL)
        self.assertEqual(rdi.import_from_ids, ind_ids)
        self.assertEqual(rdi.number_of_individuals, 2)
        self.assertEqual(rdi.number_of_households, 2)
        self.assertEqual(rdi.program_id, self.import_to_program.id)
