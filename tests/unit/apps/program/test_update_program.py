from datetime import timedelta
from typing import Any, List
from unittest.mock import Mock, patch

from parameterized import parameterized

from tests.extras.test_utils.factories.account import (
    BusinessAreaFactory,
    PartnerFactory,
    UserFactory,
)
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from tests.extras.test_utils.factories.core import (
    FlexibleAttributeForPDUFactory,
    PeriodicFieldDataFactory,
    create_afghanistan,
    generate_data_collecting_types,
)
from hct_mis_api.apps.core.models import (
    BusinessArea,
    DataCollectingType,
    FlexibleAttribute,
    PeriodicFieldData,
)
from tests.extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory, CountryFactory
from tests.extras.test_utils.factories.household import (
    create_household,
    create_household_and_individuals,
)
from hct_mis_api.apps.periodic_data_update.utils import populate_pdu_with_null_values
from tests.extras.test_utils.factories.program import BeneficiaryGroupFactory, ProgramFactory
from hct_mis_api.apps.program.models import Program, ProgramCycle, ProgramPartnerThrough
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory


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
          beneficiaryGroup {
            name
          }
          pduFields {
            name
            label
            pduData {
              subtype
              numberOfRounds
              roundsNames
            }
          }
        }
        validationErrors
      }
    }
    """

    PROGRAM_QUERY = """
        query Program($id: ID!) {
          program(id: $id) {
            name
            pduFields {
              name
              label
              pduData {
                subtype
                numberOfRounds
                roundsNames
              }
            }
          }
        }
        """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        generate_data_collecting_types()
        data_collecting_type = DataCollectingType.objects.get(code="full_collection")
        data_collecting_type.type = DataCollectingType.Type.STANDARD
        data_collecting_type.save()

        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.business_area.data_collecting_types.set(DataCollectingType.objects.all().values_list("id", flat=True))
        beneficiary_group = BeneficiaryGroupFactory()
        cls.program = ProgramFactory.create(
            name="initial name",
            status=Program.DRAFT,
            business_area=cls.business_area,
            data_collecting_type=data_collecting_type,
            partner_access=Program.NONE_PARTNERS_ACCESS,
            version=123,
            biometric_deduplication_enabled=True,
            beneficiary_group=beneficiary_group,
        )
        cls.program_finished = ProgramFactory.create(
            status=Program.FINISHED,
            business_area=cls.business_area,
            partner_access=Program.NONE_PARTNERS_ACCESS,
            beneficiary_group=beneficiary_group,
        )

        cls.partner = PartnerFactory(name="WFP")
        cls.user = UserFactory.create(partner=cls.partner)

        cls.unicef_partner = PartnerFactory(name="UNICEF")
        unicef_program, _ = ProgramPartnerThrough.objects.get_or_create(
            program=cls.program,
            partner=cls.unicef_partner,
        )

        country_afg = CountryFactory(name="Afghanistan")
        country_afg.business_areas.set([cls.business_area])
        area_type_afg = AreaTypeFactory(name="Area Type in Afg", country=country_afg)

        cls.area_in_afg_1 = AreaFactory(name="Area in AFG 1", area_type=area_type_afg, p_code="AREA-IN-AFG1")
        cls.area_in_afg_2 = AreaFactory(name="Area in AFG 2", area_type=area_type_afg, p_code="AREA-IN-AFG2")

        unicef_program.areas.set([cls.area_in_afg_1, cls.area_in_afg_2])

        # pdu fields
        cls.pdu_data_to_be_removed = PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.DECIMAL,
            number_of_rounds=3,
            rounds_names=["Round 1 To Be Removed", "Round 2 To Be Removed", "Round 3 To Be Removed"],
        )
        cls.pdu_field_to_be_removed = FlexibleAttributeForPDUFactory(
            program=cls.program,
            label="PDU Field To Be Removed",
            pdu_data=cls.pdu_data_to_be_removed,
        )
        cls.pdu_data_to_be_updated = PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.STRING,
            number_of_rounds=2,
            rounds_names=["Round 1 To Be Updated", "Round 2 To Be Updated"],
        )
        cls.pdu_field_to_be_updated = FlexibleAttributeForPDUFactory(
            program=cls.program,
            label="PDU Field To Be Updated",
            pdu_data=cls.pdu_data_to_be_updated,
        )
        cls.pdu_data_to_be_preserved = PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.DATE,
            number_of_rounds=1,
            rounds_names=["Round To Be Preserved"],
        )
        cls.pdu_field_to_be_preserved = FlexibleAttributeForPDUFactory(
            program=cls.program,
            label="PDU Field To Be Preserved",
            pdu_data=cls.pdu_data_to_be_preserved,
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
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
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
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.business_area)
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
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "dataCollectingTypeCode": "partial_individuals",
                },
                "version": self.program.version,
            },
        )
        self.assertEqual(self.program.data_collecting_type.code, "full_collection")

    def test_update_draft_not_empty_program_with_dct(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.business_area)
        data_collecting_type = DataCollectingType.objects.get(code="full_collection")
        data_collecting_type.limit_to.add(self.business_area)
        create_household(household_args={"program": self.program})

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
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

        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
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

        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "dataCollectingTypeCode": "inactive",
                },
                "version": self.program.version,
            },
        )

    def test_update_program_with_dct_from_other_ba(self) -> None:
        other_ba = BusinessAreaFactory()
        dct, _ = DataCollectingType.objects.update_or_create(
            **{"label": "Test Wrong BA", "code": "test_wrong_ba", "description": "Test Wrong BA"}
        )
        dct.limit_to.add(other_ba)
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_CREATE], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "dataCollectingTypeCode": "test_wrong_ba",
                },
                "version": self.program.version,
            },
        )

    def test_update_program_beneficiary_group(self) -> None:
        beneficiary_group2 = BeneficiaryGroupFactory(name="Other Group", master_detail=True)
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "beneficiaryGroup": str(beneficiary_group2.id),
                },
                "version": self.program.version,
            },
        )

    def test_update_program_beneficiary_group_when_imported_population(self) -> None:
        beneficiary_group2 = BeneficiaryGroupFactory(name="Other Group", master_detail=True)
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.business_area)
        RegistrationDataImportFactory(program=self.program)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "beneficiaryGroup": str(beneficiary_group2.id),
                },
                "version": self.program.version,
            },
        )

    def test_update_program_incompatible_beneficiary_group(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.business_area)

        beneficiary_group = BeneficiaryGroupFactory(name="Social", master_detail=False)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "beneficiaryGroup": str(beneficiary_group.id),
                },
                "version": self.program.version,
            },
        )

    def test_update_program_when_finished(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program_finished.id, "ProgramNode"),
                    "name": "xyz",
                },
                "version": self.program_finished.version,
            },
        )

    def test_update_program_with_programme_code(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.business_area)

        self.graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "name": "xyz",
                    "programmeCode": "ab/2",
                },
                "version": self.program.version,
            },
        )
        program = Program.objects.get(id=self.program.id)
        self.assertIsNotNone(program.programme_code)
        self.assertEqual(program.programme_code, "AB/2")

    def test_update_program_without_programme_code(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.business_area)

        self.program.programme_code = ""
        self.program.save()

        self.graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "name": "xyz",
                    "programmeCode": "",
                },
                "version": self.program.version,
            },
        )
        program = Program.objects.get(id=self.program.id)
        self.assertIsNotNone(program.programme_code)
        self.assertEqual(len(program.programme_code), 4)

    def test_update_program_with_duplicated_programme_code_among_the_same_business_area(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.business_area)

        ProgramFactory(programme_code="ABC2", business_area=self.business_area)
        self.program.programme_code = "ABC3"
        self.program.save()

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "name": "xyz",
                    "programmeCode": "abc2",
                },
                "version": self.program.version,
            },
        )
        program = Program.objects.get(id=self.program.id)
        self.assertIsNotNone(program.programme_code)
        self.assertEqual(len(program.programme_code), 4)
        self.assertEqual(program.programme_code, "ABC3")

    def test_update_program_with_pdu_fields(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_UPDATE, Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS], self.business_area
        )

        # get details to check the pdu fields
        self.snapshot_graphql_request(
            request_string=self.PROGRAM_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"id": self.id_to_base64(self.program.id, "ProgramNode")},
        )

        # update pdu fields
        update_data = {
            "programData": {
                "id": self.id_to_base64(self.program.id, "ProgramNode"),
                "name": "Program with Updated PDU Fields",
                "pduFields": [
                    {
                        "id": self.id_to_base64(self.pdu_field_to_be_preserved.id, "PeriodicFieldNode"),
                        "label": "PDU Field To Be Preserved",
                        "pduData": {
                            "subtype": "DATE",
                            "numberOfRounds": 1,
                            "roundsNames": ["Round To Be Preserved"],
                        },
                    },
                    {
                        "id": self.id_to_base64(self.pdu_field_to_be_updated.id, "PeriodicFieldNode"),
                        "label": "PDU Field - Updated",
                        "pduData": {
                            "subtype": "BOOL",
                            "numberOfRounds": 3,
                            "roundsNames": ["Round 1 Updated", "Round 2 Updated", "Round 3 Updated"],
                        },
                    },
                    {
                        "label": "PDU Field - New",
                        "pduData": {
                            "subtype": "BOOL",
                            "numberOfRounds": 4,
                            "roundsNames": ["Round 1A", "Round 2B", "Round 3C", "Round 4D"],
                        },
                    },
                ],
            }
        }
        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                **update_data,
                "version": self.program.version,
            },
        )

        # get details again to check if the pdu fields are updated
        self.snapshot_graphql_request(
            request_string=self.PROGRAM_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"id": self.id_to_base64(self.program.id, "ProgramNode")},
        )
        self.assertEqual(
            self.program.pdu_fields.count(),
            3,
        )
        self.assertIsNone(FlexibleAttribute.objects.filter(name="pdu_field_to_be_removed").first())
        self.assertIsNone(FlexibleAttribute.objects.filter(name="pdu_field_to_be_updated").first())
        self.assertEqual(FlexibleAttribute.objects.filter(name="pdu_field_updated").first().pdu_data.subtype, "BOOL")
        self.assertIsNotNone(FlexibleAttribute.objects.filter(name="pdu_field_new").first())
        self.assertIsNotNone(FlexibleAttribute.objects.filter(name="pdu_field_to_be_preserved").first())

    def test_update_program_with_pdu_fields_invalid_data(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.business_area)
        update_data = {
            "programData": {
                "id": self.id_to_base64(self.program.id, "ProgramNode"),
                "name": "Program with Updated PDU Fields",
                "pduFields": [
                    {
                        "id": self.id_to_base64(self.pdu_field_to_be_preserved.id, "PeriodicFieldNode"),
                        "label": "PDU Field To Be Preserved",
                        "pduData": {
                            "subtype": "DATE",
                            "numberOfRounds": 1,
                            "roundsNames": ["Round To Be Preserved"],
                        },
                    },
                    {
                        "id": self.id_to_base64(self.pdu_field_to_be_updated.id, "PeriodicFieldNode"),
                        "label": "PDU Field - Updated",
                        "pduData": {
                            "subtype": "BOOL",
                            "numberOfRounds": 1,
                            "roundsNames": ["Round 1 Updated", "Round 2 Updated", "Round 3 Updated"],
                        },
                    },
                    {
                        "label": "PDU Field - New",
                        "pduData": {
                            "subtype": "BOOL",
                            "numberOfRounds": 3,
                            "roundsNames": ["Round 1A", "Round 2B", "Round 3C", "Round 4D"],
                        },
                    },
                ],
            }
        }
        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                **update_data,
                "version": self.program.version,
            },
        )

    def test_update_program_with_pdu_fields_duplicated_field_names_in_input(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.business_area)
        # pdu data with duplicated field names in the input
        update_data = {
            "programData": {
                "id": self.id_to_base64(self.program.id, "ProgramNode"),
                "name": "Program with Updated PDU Fields",
                "pduFields": [
                    {
                        "id": self.id_to_base64(self.pdu_field_to_be_preserved.id, "PeriodicFieldNode"),
                        "label": "PDU Field To Be Preserved",
                        "pduData": {
                            "subtype": "DATE",
                            "numberOfRounds": 1,
                            "roundsNames": ["Round To Be Preserved"],
                        },
                    },
                    {
                        "id": self.id_to_base64(self.pdu_field_to_be_updated.id, "PeriodicFieldNode"),
                        "label": "PDU Field 1",
                        "pduData": {
                            "subtype": "BOOL",
                            "numberOfRounds": 3,
                            "roundsNames": ["Round 1 Updated", "Round 2 Updated", "Round 3 Updated"],
                        },
                    },
                    {
                        "label": "PDU Field 1",
                        "pduData": {
                            "subtype": "BOOL",
                            "numberOfRounds": 4,
                            "roundsNames": ["Round 1A", "Round 2B", "Round 3C", "Round 4D"],
                        },
                    },
                ],
            }
        }
        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                **update_data,
                "version": self.program.version,
            },
        )

    def test_update_program_with_pdu_fields_existing_field_name_for_new_field(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.business_area)
        # pdu data with NEW field with name that already exists in the database but in different program -> no fail
        pdu_data = PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.DATE,
            number_of_rounds=1,
            rounds_names=["Round 1"],
        )
        program = ProgramFactory(business_area=self.business_area, name="Test Program 1")
        FlexibleAttributeForPDUFactory(
            program=program,
            label="PDU Field 1",
            pdu_data=pdu_data,
        )
        update_data = {
            "programData": {
                "id": self.id_to_base64(self.program.id, "ProgramNode"),
                "name": "Program with Updated PDU Fields",
                "pduFields": [
                    {
                        "id": self.id_to_base64(self.pdu_field_to_be_preserved.id, "PeriodicFieldNode"),
                        "label": "PDU Field To Be Preserved",
                        "pduData": {
                            "subtype": "DATE",
                            "numberOfRounds": 1,
                            "roundsNames": ["Round To Be Preserved"],
                        },
                    },
                    {
                        "id": self.id_to_base64(self.pdu_field_to_be_updated.id, "PeriodicFieldNode"),
                        "label": "PDU Field - Updated",
                        "pduData": {
                            "subtype": "BOOL",
                            "numberOfRounds": 3,
                            "roundsNames": ["Round 1 Updated", "Round 2 Updated", "Round 3 Updated"],
                        },
                    },
                    {
                        "label": "PDU Field 1",
                        "pduData": {
                            "subtype": "BOOL",
                            "numberOfRounds": 4,
                            "roundsNames": ["Round 1A", "Round 2B", "Round 3C", "Round 4D"],
                        },
                    },
                ],
            }
        }
        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                **update_data,
                "version": self.program.version,
            },
        )

    def test_update_program_with_pdu_fields_existing_field_name_for_updated_field(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.business_area)
        # pdu data with UPDATED field with name that already exists in the database but in different program -> no fail
        pdu_data = PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.DATE,
            number_of_rounds=1,
            rounds_names=["Round 1"],
        )
        program = ProgramFactory(business_area=self.business_area, name="Test Program 1")
        FlexibleAttributeForPDUFactory(
            program=program,
            label="PDU Field 1",
            pdu_data=pdu_data,
        )
        update_data = {
            "programData": {
                "id": self.id_to_base64(self.program.id, "ProgramNode"),
                "name": "Program with Updated PDU Fields",
                "pduFields": [
                    {
                        "id": self.id_to_base64(self.pdu_field_to_be_preserved.id, "PeriodicFieldNode"),
                        "label": "PDU Field To Be Preserved",
                        "pduData": {
                            "subtype": "DATE",
                            "numberOfRounds": 1,
                            "roundsNames": ["Round To Be Preserved"],
                        },
                    },
                    {
                        "id": self.id_to_base64(self.pdu_field_to_be_updated.id, "PeriodicFieldNode"),
                        "label": "PDU Field 1",
                        "pduData": {
                            "subtype": "BOOL",
                            "numberOfRounds": 3,
                            "roundsNames": ["Round 1 Updated", "Round 2 Updated", "Round 3 Updated"],
                        },
                    },
                    {
                        "label": "PDU Field - New",
                        "pduData": {
                            "subtype": "BOOL",
                            "numberOfRounds": 4,
                            "roundsNames": ["Round 1A", "Round 2B", "Round 3C", "Round 4D"],
                        },
                    },
                ],
            }
        }
        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                **update_data,
                "version": self.program.version,
            },
        )

    def test_update_program_with_pdu_fields_program_has_RDI(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.business_area)
        RegistrationDataImportFactory(program=self.program)
        update_data = {
            "programData": {
                "id": self.id_to_base64(self.program.id, "ProgramNode"),
                "name": "Program with Updated PDU Fields",
                "pduFields": [
                    {
                        "id": self.id_to_base64(self.pdu_field_to_be_updated.id, "PeriodicFieldNode"),
                        "label": "PDU Field - NAME WILL NOT BE UPDATED",
                        "pduData": {
                            "subtype": "BOOL",  # subtype will NOT be updated
                            "numberOfRounds": 4,
                            "roundsNames": [
                                "Round 1 To Be Updated",
                                "Round 2 To Be Updated",
                                "Round 3 New",
                                "Round 4 New",
                            ],
                        },
                    },
                ],
            }
        }
        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                **update_data,
                "version": self.program.version,
            },
        )

    def test_update_program_with_pdu_fields_program_has_RDI_new_field(self) -> None:
        # new field will NOT be added
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.business_area)
        RegistrationDataImportFactory(program=self.program)
        update_data = {
            "programData": {
                "id": self.id_to_base64(self.program.id, "ProgramNode"),
                "name": "Program with Updated PDU Fields",
                "pduFields": [
                    {
                        "label": "PDU Field - New",
                        "pduData": {
                            "subtype": "BOOL",
                            "numberOfRounds": 4,
                            "roundsNames": ["Round 1A", "Round 2B", "Round 3C", "Round 4D"],
                        },
                    },
                ],
            }
        }
        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                **update_data,
                "version": self.program.version,
            },
        )

    def test_update_program_with_pdu_fields_program_has_RDI_update_pdu_field(self) -> None:
        # field will NOT be updated, no field will be removed
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.business_area)
        RegistrationDataImportFactory(program=self.program)
        update_data = {
            "programData": {
                "id": self.id_to_base64(self.program.id, "ProgramNode"),
                "name": "Program with Updated PDU Fields",
                "pduFields": [
                    {
                        "id": self.id_to_base64(self.pdu_field_to_be_updated.id, "PeriodicFieldNode"),
                        "label": "PDU Field - Updated",
                        "pduData": {
                            "subtype": "BOOL",
                            "numberOfRounds": 2,
                            "roundsNames": ["Round 1 To Be Updated", "Round 2 To Be Updated"],
                        },
                    },
                ],
            }
        }
        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                **update_data,
                "version": self.program.version,
            },
        )

    def test_update_program_with_pdu_fields_program_has_RDI_invalid_data_decrease_rounds(self) -> None:
        # round number CANNOT be decreased for Program with RDI
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.business_area)
        RegistrationDataImportFactory(program=self.program)
        update_data = {
            "programData": {
                "id": self.id_to_base64(self.program.id, "ProgramNode"),
                "name": "Program with Updated PDU Fields",
                "pduFields": [
                    {
                        "id": self.id_to_base64(self.pdu_field_to_be_updated.id, "PeriodicFieldNode"),
                        "label": self.pdu_field_to_be_updated.label,
                        "pduData": {
                            "subtype": self.pdu_field_to_be_updated.pdu_data.subtype,
                            "numberOfRounds": 1,
                            "roundsNames": ["Round 1 To Be Updated"],
                        },
                    },
                ],
            }
        }
        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                **update_data,
                "version": self.program.version,
            },
        )

    def test_update_program_with_pdu_fields_program_has_RDI_invalid_data_changed_existing_rounds_names(self) -> None:
        # names of existing rounds cannot be updated
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.business_area)
        RegistrationDataImportFactory(program=self.program)
        update_data = {
            "programData": {
                "id": self.id_to_base64(self.program.id, "ProgramNode"),
                "name": "Program with Updated PDU Fields",
                "pduFields": [
                    {
                        "id": self.id_to_base64(self.pdu_field_to_be_updated.id, "PeriodicFieldNode"),
                        "label": self.pdu_field_to_be_updated.label,
                        "pduData": {
                            "subtype": self.pdu_field_to_be_updated.pdu_data.subtype,
                            "numberOfRounds": 3,
                            "roundsNames": ["Round 1 Updated", "Round 2 Updated", "Round 3 New"],
                        },
                    },
                ],
            }
        }
        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                **update_data,
                "version": self.program.version,
            },
        )

    def test_update_program_increase_rounds_program_has_RDI(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.business_area)
        RegistrationDataImportFactory(program=self.program)
        _, individuals = create_household_and_individuals(
            household_data={"business_area": self.business_area, "program": self.program},
            individuals_data=[
                {
                    "business_area": self.business_area,
                },
            ],
        )
        individual = individuals[0]
        individual.flex_fields = populate_pdu_with_null_values(self.program, {})
        individual.save()

        self.assertEqual(
            individual.flex_fields,
            {
                "pdu_field_to_be_preserved": {"1": {"value": None}},
                "pdu_field_to_be_removed": {"1": {"value": None}, "2": {"value": None}, "3": {"value": None}},
                "pdu_field_to_be_updated": {"1": {"value": None}, "2": {"value": None}},
            },
        )
        update_data = {
            "programData": {
                "id": self.id_to_base64(self.program.id, "ProgramNode"),
                "name": "Program with Increased Rounds for PDU Field",
                "pduFields": [
                    {
                        "id": self.id_to_base64(self.pdu_field_to_be_updated.id, "PeriodicFieldNode"),
                        "label": "PDU Field To Be Updated",
                        "pduData": {
                            "subtype": "STRING",
                            "numberOfRounds": 4,
                            "roundsNames": [
                                "Round 1 To Be Updated",
                                "Round 2 To Be Updated",
                                "Round 3 New",
                                "Round 4 New",
                            ],
                        },
                    },
                ],
            }
        }
        self.graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                **update_data,
                "version": self.program.version,
            },
        )
        individual.refresh_from_db()
        self.assertEqual(
            individual.flex_fields,
            {
                "pdu_field_to_be_preserved": {"1": {"value": None}},
                "pdu_field_to_be_removed": {"1": {"value": None}, "2": {"value": None}, "3": {"value": None}},
                "pdu_field_to_be_updated": {
                    "1": {"value": None},
                    "2": {"value": None},
                    "3": {"value": None},
                    "4": {"value": None},
                },
            },
        )

    @patch.dict(
        "os.environ",
        {"DEDUPLICATION_ENGINE_API_KEY": "dedup_api_key", "DEDUPLICATION_ENGINE_API_URL": "http://dedup-fake-url.com"},
    )
    @patch(
        "hct_mis_api.apps.registration_datahub.apis.deduplication_engine.DeduplicationEngineAPI"
        ".delete_deduplication_set"
    )
    def test_finish_active_program_with_not_finished_program_cycle_or_end_date(
        self, mock_delete_deduplication_set: Mock
    ) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_FINISH], self.business_area)
        Program.objects.filter(id=self.program.id).update(status=Program.ACTIVE)
        self.program.refresh_from_db()
        self.assertEqual(self.program.status, Program.ACTIVE)
        self.assertEqual(self.program.cycles.count(), 1)
        program_cycle = self.program.cycles.first()
        program_cycle.status = ProgramCycle.ACTIVE
        program_cycle.save()
        # has active cycle
        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "status": Program.FINISHED,
                },
                "version": self.program.version,
            },
        )
        program_cycle.status = ProgramCycle.DRAFT
        program_cycle.save()
        self.program.end_date = None
        self.program.save()
        self.program.refresh_from_db()
        self.assertIsNone(self.program.end_date)
        # no program end date
        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "status": Program.FINISHED,
                },
                "version": self.program.version,
            },
        )
        # finish program
        self.program.deduplication_set_id = "12bc7994-9467-4f27-9954-d75a67d0e909"
        self.program.end_date = self.program.start_date + timedelta(days=999)
        self.program.save()
        self.program.refresh_from_db()
        self.assertIsNotNone(self.program.end_date)
        self.assertEqual(str(self.program.deduplication_set_id), "12bc7994-9467-4f27-9954-d75a67d0e909")
        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "status": Program.FINISHED,
                },
                "version": self.program.version,
            },
        )
        # check if deduplication_set_id is null
        self.program.refresh_from_db()
        self.assertIsNone(self.program.deduplication_set_id)
        mock_delete_deduplication_set.assert_called_once_with("12bc7994-9467-4f27-9954-d75a67d0e909")

    def test_update_program_end_date_validation(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.business_area)
        Program.objects.filter(id=self.program.id).update(status=Program.ACTIVE, end_date=None)
        self.program.refresh_from_db()
        self.assertEqual(self.program.status, Program.ACTIVE)
        self.assertIsNone(self.program.end_date)
        program_cycle = self.program.cycles.first()
        program_cycle.start_date = self.program.start_date
        program_cycle.end_date = self.program.start_date + timedelta(days=5)
        program_cycle.save()

        # end date before program start date
        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "endDate": self.program.start_date - timedelta(days=5),
                },
                "version": self.program.version,
            },
        )

        # end date before last cycle
        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "endDate": program_cycle.end_date - timedelta(days=2),
                },
                "version": self.program.version,
            },
        )
        # start date after cycle start date
        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "startDate": program_cycle.start_date + timedelta(days=5),
                },
                "version": self.program.version,
            },
        )
