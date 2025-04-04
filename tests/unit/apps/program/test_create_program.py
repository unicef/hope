from typing import Any, List

import freezegun
from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import (
    BusinessAreaFactory,
    PartnerFactory,
    RoleFactory,
    UserFactory,
)
from hct_mis_api.apps.account.models import AdminAreaLimitedTo, Partner, RoleAssignment
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import (
    FlexibleAttributeForPDUFactory,
    PeriodicFieldDataFactory,
    create_afghanistan,
)
from hct_mis_api.apps.core.models import (
    BusinessArea,
    DataCollectingType,
    PeriodicFieldData,
)
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory, CountryFactory
from hct_mis_api.apps.program.fixtures import BeneficiaryGroupFactory, ProgramFactory
from hct_mis_api.apps.program.models import Program


@freezegun.freeze_time("2019-01-01")
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
          isSocialWorkerProgram
          dataCollectingType {
            code
            label
            description
            active
            individualFiltersAvailable
          }
          beneficiaryGroup {
            name
          }
          partners {
            name
            areas {
              name
            }
            areaAccess
          }
          partnerAccess
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

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
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
            type=DataCollectingType.Type.STANDARD,
        )
        cls.data_collecting_type.limit_to.add(cls.business_area)
        cls.beneficiary_group = BeneficiaryGroupFactory(name="School", master_detail=True)
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
                "partnerAccess": Program.NONE_PARTNERS_ACCESS,
                "beneficiaryGroup": str(cls.beneficiary_group.id),
            }
        }
        # partner has to be allowed in BA to be able to be assigned to program
        cls.partner.allowed_business_areas.set([cls.business_area])

        # partner with role in BA in another program - will be granted access for ALL_PARTNERS_ACCESS type because he also is allowed in BA
        # TODO: can remove the role creation after removing the temporary solution in program mutations
        cls.partner_allowed_in_BA = PartnerFactory(name="Other Partner")
        cls.partner_allowed_in_BA.allowed_business_areas.set([cls.business_area])
        role = RoleFactory(name="Role in BA")
        RoleAssignment.objects.create(
            business_area=cls.business_area,
            partner=cls.partner_allowed_in_BA,
            role=role,
            program=ProgramFactory(business_area=cls.business_area),
        )

        PartnerFactory(name="Partner not allowed in BA")

        country_afg = CountryFactory(name="Afghanistan")
        country_afg.business_areas.set([cls.business_area])
        area_type_afg = AreaTypeFactory(name="Area Type in Afg", country=country_afg)
        country_other = CountryFactory(
            name="Other Country",
            short_name="Oth",
            iso_code2="O",
            iso_code3="OTH",
            iso_num="111",
        )
        cls.area_type_other = AreaTypeFactory(name="Area Type Other", country=country_other)

        cls.area_in_afg_1 = AreaFactory(name="Area in AFG 1", area_type=area_type_afg, p_code="AREA-IN-AFG1")
        cls.area_in_afg_2 = AreaFactory(name="Area in AFG 2", area_type=area_type_afg, p_code="AREA-IN-AFG2")
        cls.area_not_in_afg = AreaFactory(
            name="Area not in AFG", area_type=cls.area_type_other, p_code="AREA-NOT-IN-AFG"
        )

        # TODO: due to temporary solution in program mutations, Partners need to already have a role in the BA to be able to be granted access to program
        # (created role in program is the same role as the Partner already held in the BA - or the BA's programs.
        # For each held role, the same role is now applied for the new program.
        # After removing this solution, below lines of setup can be deleted.
        # The Role for RoleAssignment will be passed in input.
        RoleAssignment.objects.create(
            business_area=cls.business_area,
            partner=cls.partner,
            role=RoleFactory(name="Role for Partner in BA"),
            program=ProgramFactory(business_area=cls.business_area),
        )
        RoleAssignment.objects.create(
            business_area=cls.business_area,
            partner=cls.partner,
            role=RoleFactory(name="Another Role for Partner in BA"),
            program=ProgramFactory(business_area=cls.business_area),
        )

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
        self.create_user_role_with_permissions(
            self.user, permissions, self.business_area, whole_business_area_access=True
        )

        if should_set_wrong_date:
            self.program_data["programData"]["endDate"] = "2018-12-20"

        self.snapshot_graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION, context={"user": self.user}, variables=self.program_data
        )

    def test_create_program_without_dct(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_CREATE], self.business_area, whole_business_area_access=True
        )

        program_data = self.program_data
        program_data["programData"]["dataCollectingTypeCode"] = None

        self.snapshot_graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION, context={"user": self.user}, variables=program_data
        )

    def test_create_program_without_beneficiary_group(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_CREATE], self.business_area, whole_business_area_access=True
        )

        program_data = self.program_data
        program_data["programData"]["beneficiaryGroup"] = None

        self.snapshot_graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION, context={"user": self.user}, variables=program_data
        )

    def test_create_program_with_dct_social_not_compatible_with_beneficiary_group(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_CREATE], self.business_area, whole_business_area_access=True
        )

        data_collecting_type = DataCollectingType.objects.create(
            code="dct_sw",
            label="DCT SW",
            description="DCT SW",
            active=True,
            type=DataCollectingType.Type.SOCIAL,
        )

        program_data = self.program_data
        program_data["programData"]["dataCollectingTypeCode"] = data_collecting_type.code

        self.snapshot_graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION, context={"user": self.user}, variables=program_data
        )

    def test_create_program_with_dct_standard_not_compatible_with_beneficiary_group(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_CREATE], self.business_area, whole_business_area_access=True
        )
        beneficiary_group = BeneficiaryGroupFactory(name="Social", master_detail=False)

        program_data = self.program_data
        program_data["programData"]["beneficiaryGroup"] = str(beneficiary_group.id)

        self.snapshot_graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION, context={"user": self.user}, variables=program_data
        )

    def test_create_program_with_deprecated_dct(self) -> None:
        dct, _ = DataCollectingType.objects.update_or_create(
            **{"label": "Deprecated", "code": "deprecated", "description": "Deprecated", "deprecated": True}
        )
        self.create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_CREATE], self.business_area, whole_business_area_access=True
        )

        program_data = self.program_data
        program_data["programData"]["dataCollectingTypeCode"] = "deprecated"

        self.snapshot_graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION, context={"user": self.user}, variables=program_data
        )

    def test_create_program_with_inactive_dct(self) -> None:
        dct, _ = DataCollectingType.objects.update_or_create(
            **{"label": "Inactive", "code": "inactive", "description": "Inactive", "active": False}
        )
        self.create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_CREATE], self.business_area, whole_business_area_access=True
        )

        program_data = self.program_data
        program_data["programData"]["dataCollectingTypeCode"] = "inactive"

        self.snapshot_graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION, context={"user": self.user}, variables=program_data
        )

    def test_create_program_with_dct_from_other_ba(self) -> None:
        other_ba = BusinessAreaFactory()
        dct, _ = DataCollectingType.objects.update_or_create(
            **{"label": "Test Wrong BA", "code": "test_wrong_ba", "description": "Test Wrong BA", "active": True}
        )
        dct.limit_to.add(other_ba)
        self.create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_CREATE], self.business_area, whole_business_area_access=True
        )

        program_data = self.program_data
        program_data["programData"]["dataCollectingTypeCode"] = "test_wrong_ba"

        self.snapshot_graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION, context={"user": self.user}, variables=program_data
        )

    def test_program_unique_constraints(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_CREATE], self.business_area, whole_business_area_access=True
        )

        program_count = Program.objects.count()

        # First, response is ok and program is created
        response_ok = self.graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables=self.program_data,
        )
        assert "errors" not in response_ok
        self.assertEqual(Program.objects.count(), program_count + 1)

        # Second, response has error due to unique constraints
        response_error = self.graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables=self.program_data,
        )
        self.assertEqual(Program.objects.count(), program_count + 1)
        self.assertEqual(
            response_error["data"]["createProgram"]["validationErrors"]["__all__"][0],
            f"Program for name: {self.program_data['programData']['name']} and business_area: {self.program_data['programData']['businessAreaSlug']} already exists.",
        )

        # Third, we remove program with given name and business area
        Program.objects.filter(name="Test", business_area=self.business_area).delete()
        self.assertEqual(Program.objects.count(), program_count)

        # Fourth, we can create program with the same name and business area like removed one
        response_ok = self.graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables=self.program_data,
        )
        assert "errors" not in response_ok
        self.assertEqual(Program.objects.count(), program_count + 1)

    def test_create_program_with_programme_code(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_CREATE], self.business_area, whole_business_area_access=True
        )
        self.program_data["programData"]["programmeCode"] = "ABC2"

        self.graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION, context={"user": self.user}, variables=self.program_data
        )
        program = Program.objects.get(name="Test")
        self.assertEqual(program.programme_code, "ABC2")

    @parameterized.expand(
        [
            ("valid", Program.SELECTED_PARTNERS_ACCESS),
            ("invalid_all_partner_access", Program.ALL_PARTNERS_ACCESS),
            ("invalid_none_partner_access", Program.NONE_PARTNERS_ACCESS),
        ]
    )
    def test_create_program_with_partners(self, _: Any, partner_access: str) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_CREATE], self.business_area, whole_business_area_access=True
        )
        area1 = AreaFactory(name="North Brianmouth", area_type=self.area_type_other, p_code="NORTH-B")
        area2 = AreaFactory(name="South Catherine", area_type=self.area_type_other, p_code="SOUTH-C")
        partner2 = PartnerFactory(name="New Partner")
        partner2.allowed_business_areas.set([self.business_area])
        # partner that is not allowed in BA - will not be granted access
        partner_not_allowed = PartnerFactory(name="Not Allowed Partner")

        # TODO: due to temporary solution in program mutations, Partners need to already have a role in the BA to be able to be granted access to program
        # After removing this solution, below line with role can be deleted.
        RoleAssignment.objects.create(
            business_area=self.business_area,
            partner=partner2,
            role=RoleFactory(name="Role for Partner 2"),
            program=ProgramFactory(business_area=self.business_area),
        )
        # end of temporary solution

        self.program_data["programData"]["partners"] = [
            {
                "partner": str(self.partner.id),
                "areas": [str(area1.id), str(area2.id)],
            },
            {
                "partner": str(partner2.id),
                "areas": [],
            },
            {
                "partner": str(partner_not_allowed.id),
                "areas": [],
            },
        ]
        self.program_data["programData"]["partnerAccess"] = partner_access

        self.snapshot_graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION, context={"user": self.user}, variables=self.program_data
        )

        if partner_access == Program.SELECTED_PARTNERS_ACCESS:
            program = Program.objects.get(name="Test")
            self.assertEqual(
                program.role_assignments.count(),
                3,
            )
            # role should be created for partner2,
            # self.partner (2 records - because currently 2 roles in BA - due to temporary solution),
            # UNICEF HQ has "Role with all permissions" for all programs in all BAs
            # UNICEF Partner for afghanistan has role "Role for UNICEF Partners" for all programs in this BA
            self.assertEqual(
                RoleAssignment.objects.filter(partner=partner2, program=program).first().role.name,
                "Role for Partner 2",
            )
            self.assertIn(
                "Role for Partner in BA",
                [ra.role.name for ra in RoleAssignment.objects.filter(partner=self.partner, program=program)],
            )
            self.assertIn(
                "Another Role for Partner in BA",
                [ra.role.name for ra in RoleAssignment.objects.filter(partner=self.partner, program=program)],
            )
            self.assertEqual(
                Partner.objects.get(name="UNICEF HQ")
                .role_assignments.filter(program=None, business_area=program.business_area)
                .first()
                .role.name,
                "Role with all permissions",
            )
            self.assertEqual(
                Partner.objects.get(name=f"UNICEF Partner for {self.business_area.slug}")
                .role_assignments.filter(program=None, business_area=program.business_area)
                .first()
                .role.name,
                "Role for UNICEF Partners",
            )
            self.assertEqual(
                RoleAssignment.objects.filter(partner=partner_not_allowed, program=program).count(),
                0,
            )

    def test_create_program_with_partners_all_partners_access(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_CREATE], self.business_area, whole_business_area_access=True
        )
        self.program_data["programData"]["partnerAccess"] = Program.ALL_PARTNERS_ACCESS

        self.snapshot_graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION, context={"user": self.user}, variables=self.program_data
        )

        program = Program.objects.get(name="Test")
        self.assertEqual(
            AdminAreaLimitedTo.objects.filter(program=program).count(),
            0,
        )

        self.assertEqual(
            program.role_assignments.count(),
            3,
        )
        # role should be created for self.partner (2 records - because currently 2 roles in BA - due to temporary solution),
        # and for self.partner_allowed_in_BA
        # UNICEF HQ has "Role with all permissions" for all programs in all BAs
        # UNICEF Partner for afghanistan has role "Role for UNICEF Partners" for all programs in this BA
        self.assertIn(
            "Role for Partner in BA",
            [ra.role.name for ra in RoleAssignment.objects.filter(partner=self.partner, program=program)],
        )
        self.assertIn(
            "Another Role for Partner in BA",
            [ra.role.name for ra in RoleAssignment.objects.filter(partner=self.partner, program=program)],
        )
        self.assertEqual(
            self.partner_allowed_in_BA.role_assignments.filter(program=program).first().role.name,
            "Role in BA",
        )
        self.assertEqual(
            Partner.objects.get(name="UNICEF HQ")
            .role_assignments.filter(program=None, business_area=program.business_area)
            .first()
            .role.name,
            "Role with all permissions",
        )
        self.assertEqual(
            Partner.objects.get(name=f"UNICEF Partner for {self.business_area.slug}")
            .role_assignments.filter(program=None, business_area=program.business_area)
            .first()
            .role.name,
            "Role for UNICEF Partners",
        )

    def test_create_program_with_partners_none_partners_access(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_CREATE], self.business_area, whole_business_area_access=True
        )
        self.program_data["programData"]["partnerAccess"] = Program.NONE_PARTNERS_ACCESS

        self.snapshot_graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION, context={"user": self.user}, variables=self.program_data
        )

        program = Program.objects.get(name="Test")
        self.assertEqual(
            program.role_assignments.count(),
            0,
        )

        # UNICEF HQ has "Role with all permissions" for all programs in all BAs
        # UNICEF Partner for afghanistan has role "Role for UNICEF Partners" for all programs in this BA
        self.assertEqual(
            Partner.objects.get(name="UNICEF HQ")
            .role_assignments.filter(program=None, business_area=program.business_area)
            .first()
            .role.name,
            "Role with all permissions",
        )
        self.assertEqual(
            Partner.objects.get(name=f"UNICEF Partner for {self.business_area.slug}")
            .role_assignments.filter(program=None, business_area=program.business_area)
            .first()
            .role.name,
            "Role for UNICEF Partners",
        )

    def test_programme_code_should_be_unique_among_the_same_business_area(self) -> None:
        ProgramFactory(programme_code="ABC2", business_area=self.business_area)

        self.create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_CREATE], self.business_area, whole_business_area_access=True
        )
        self.program_data["programData"]["programmeCode"] = "ABC2"

        self.snapshot_graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION, context={"user": self.user}, variables=self.program_data
        )

        program_count = Program.objects.filter(programme_code="ABC2").count()
        self.assertEqual(program_count, 1)

    def test_programme_code_can_be_reuse_in_different_business_area(self) -> None:
        business_area = BusinessAreaFactory()
        ProgramFactory(programme_code="AB-2", business_area=business_area)
        self.create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_CREATE], self.business_area, whole_business_area_access=True
        )
        self.program_data["programData"]["programmeCode"] = "AB-2"

        self.graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION, context={"user": self.user}, variables=self.program_data
        )

        program_count = Program.objects.filter(programme_code="AB-2").count()
        self.assertEqual(program_count, 2)

    def test_create_program_without_programme_code(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_CREATE], self.business_area, whole_business_area_access=True
        )

        self.graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION, context={"user": self.user}, variables=self.program_data
        )

        program = Program.objects.get(name="Test")
        self.assertIsNotNone(program.programme_code)
        self.assertEqual(len(program.programme_code), 4)

    def test_create_program_with_programme_code_as_empty_string(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_CREATE], self.business_area, whole_business_area_access=True
        )
        self.program_data["programData"]["programmeCode"] = ""

        self.graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION, context={"user": self.user}, variables=self.program_data
        )

        program = Program.objects.get(name="Test")
        self.assertIsNotNone(program.programme_code)
        self.assertEqual(len(program.programme_code), 4)

    def test_create_program_with_programme_code_lowercase(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_CREATE], self.business_area, whole_business_area_access=True
        )
        self.program_data["programData"]["programmeCode"] = "ab2-"

        self.graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION, context={"user": self.user}, variables=self.program_data
        )

        program = Program.objects.get(name="Test")
        self.assertIsNotNone(program.programme_code)
        self.assertEqual(len(program.programme_code), 4)
        self.assertEqual(program.programme_code, "AB2-")

    def test_create_program_with_programme_code_not_within_allowed_characters(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_CREATE], self.business_area, whole_business_area_access=True
        )
        self.program_data["programData"]["programmeCode"] = "A@C2"

        self.snapshot_graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION, context={"user": self.user}, variables=self.program_data
        )

    def test_create_program_with_programme_code_less_than_4_chars(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_CREATE], self.business_area, whole_business_area_access=True
        )
        self.program_data["programData"]["programmeCode"] = "Ab2"

        self.snapshot_graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION, context={"user": self.user}, variables=self.program_data
        )

    def test_create_program_with_programme_code_greater_than_4_chars(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_CREATE], self.business_area, whole_business_area_access=True
        )
        self.program_data["programData"]["programmeCode"] = "AbCd2"

        self.snapshot_graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION, context={"user": self.user}, variables=self.program_data
        )

    def test_create_program_with_pdu_fields(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_CREATE], self.business_area, whole_business_area_access=True
        )
        self.program_data["programData"]["pduFields"] = [
            {
                "label": "PDU Field 1",
                "pduData": {
                    "subtype": "DECIMAL",
                    "numberOfRounds": 3,
                    "roundsNames": ["Round 1", "Round 2", "Round 3"],
                },
            },
            {
                "label": "PDU Field 2",
                "pduData": {
                    "subtype": "STRING",
                    "numberOfRounds": 1,
                    "roundsNames": ["Round *"],
                },
            },
            {
                "label": "PDU Field 3",
                "pduData": {
                    "subtype": "DATE",
                    "numberOfRounds": 2,
                    "roundsNames": ["Round A", "Round B"],
                },
            },
            {
                "label": "PDU Field 4",
                "pduData": {
                    "subtype": "BOOL",
                    "numberOfRounds": 4,
                    "roundsNames": ["Round 1A", "Round 2B", "Round 3C", "Round 4D"],
                },
            },
        ]

        self.snapshot_graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION, context={"user": self.user}, variables=self.program_data
        )

    def test_create_program_with_pdu_fields_invalid_data(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_CREATE], self.business_area, whole_business_area_access=True
        )
        # pdu data with mismatched number of rounds and rounds names
        self.program_data["programData"]["pduFields"] = [
            {
                "label": "PDU Field 1",
                "pduData": {
                    "subtype": "DECIMAL",
                    "numberOfRounds": 3,
                    "roundsNames": ["Round 1", "Round 2", "Round 3"],
                },
            },
            {
                "label": "PDU Field 2 Invalid",
                "pduData": {
                    "subtype": "STRING",
                    "numberOfRounds": 1,
                    "roundsNames": ["Round *", "Round 2*"],
                },
            },
        ]

        self.snapshot_graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION, context={"user": self.user}, variables=self.program_data
        )

    def test_create_program_with_pdu_fields_duplicated_field_names_in_input(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_CREATE], self.business_area, whole_business_area_access=True
        )
        # pdu data with duplicated field names in the input
        self.program_data["programData"]["pduFields"] = [
            {
                "label": "PDU Field 1",
                "pduData": {
                    "subtype": "DECIMAL",
                    "numberOfRounds": 3,
                    "roundsNames": ["Round 1", "Round 2", "Round 3"],
                },
            },
            {
                "label": "PDU Field 1",
                "pduData": {
                    "subtype": "STRING",
                    "numberOfRounds": 2,
                    "roundsNames": ["Round *", "Round 2*"],
                },
            },
        ]

        self.snapshot_graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION, context={"user": self.user}, variables=self.program_data
        )

    def test_create_program_with_pdu_fields_existing_field_name_in_different_program(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_CREATE], self.business_area, whole_business_area_access=True
        )
        # pdu data with field name that already exists in the database but in different program -> no fail
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
        self.program_data["programData"]["pduFields"] = [
            {
                "label": "PDU Field 1",
                "pduData": {
                    "subtype": "DECIMAL",
                    "numberOfRounds": 3,
                    "roundsNames": ["Round 1", "Round 2", "Round 3"],
                },
            },
        ]

        self.snapshot_graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION, context={"user": self.user}, variables=self.program_data
        )
