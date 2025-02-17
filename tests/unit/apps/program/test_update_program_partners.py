from typing import Any, List

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import PartnerFactory, RoleFactory, UserFactory
from hct_mis_api.apps.account.models import AdminAreaLimitedTo, Partner, RoleAssignment
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import (
    create_afghanistan,
    generate_data_collecting_types,
)
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory, CountryFactory
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program


class TestUpdateProgramPartners(APITestCase):
    UPDATE_PROGRAM_PARTNERS_MUTATION = """
    mutation UpdateProgramPartners($programData: UpdateProgramPartnersInput, $version: BigInt) {
      updateProgramPartners(programData: $programData, version: $version) {
        program {
          partners {
            name
            areas {
              name
            }
            areaAccess
          }
          partnerAccess
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

        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.business_area.data_collecting_types.set(DataCollectingType.objects.all().values_list("id", flat=True))

        cls.program = ProgramFactory.create(
            name="initial name",
            status=Program.DRAFT,
            business_area=cls.business_area,
            data_collecting_type=data_collecting_type,
            partner_access=Program.NONE_PARTNERS_ACCESS,
            version=123,
            biometric_deduplication_enabled=True,
        )

        cls.partner = PartnerFactory(name="WFP")
        cls.user = UserFactory.create(partner=cls.partner)

        # partner has to be allowed in BA to be able to be assigned to program
        cls.partner.allowed_business_areas.set([cls.business_area])

        # partner with role in BA - will be granted access for ALL_PARTNERS_ACCESS type because he also is allowed in BA
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

        cls.partner_not_allowed_in_ba = PartnerFactory(name="Partner not allowed in BA")

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
            name="Area not in AFG", area_type=cls.area_type_other, p_code="AREA-NOT-IN-AFG2"
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

    def test_update_program_partners_not_authenticated(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_PARTNERS_MUTATION,
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "partnerAccess": Program.NONE_PARTNERS_ACCESS,
                },
                "version": self.program.version,
            },
        )

    @parameterized.expand(
        [
            ("with_permissions", [Permissions.PROGRAMME_UPDATE]),
            ("without_permissions", []),
        ]
    )
    def test_update_program_partners_authenticated(
        self,
        _: Any,
        permissions: List[Permissions],
    ) -> None:
        self.create_user_role_with_permissions(
            self.user, permissions, self.business_area, whole_business_area_access=True
        )

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_PARTNERS_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "partnerAccess": Program.NONE_PARTNERS_ACCESS,
                },
                "version": self.program.version,
            },
        )

    @parameterized.expand(
        [
            ("valid", Program.SELECTED_PARTNERS_ACCESS),
            ("invalid_all_partner_access", Program.ALL_PARTNERS_ACCESS),
            ("invalid_none_partner_access", Program.NONE_PARTNERS_ACCESS),
        ]
    )
    def test_update_program_partners(self, _: Any, partner_access: str) -> None:
        area1 = AreaFactory(name="Area1", area_type=self.area_type_other, p_code="AREA1")
        area2 = AreaFactory(name="Area2", area_type=self.area_type_other, p_code="AREA2")
        area_to_be_unselected = AreaFactory(
            name="AreaToBeUnselected", area_type=self.area_type_other, p_code="AREA-TO-BE-UNSELECTED"
        )
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.business_area,
            whole_business_area_access=True,
        )

        # update program partners #1
        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_PARTNERS_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "partners": [
                        {
                            "partner": str(self.partner.id),
                            "areas": [str(area1.id), str(area_to_be_unselected.id)],
                        },
                        {
                            "partner": str(self.partner_allowed_in_BA.id),
                            "areas": [area1.id],
                        },
                    ],
                    "partnerAccess": partner_access,
                },
                "version": self.program.version,
            },
        )
        self.program.refresh_from_db()

        if partner_access == Program.SELECTED_PARTNERS_ACCESS:
            # check access after initial update
            self.assertEqual(
                self.program.role_assignments.count(),
                3,
            )
            self.assertIn(
                "Role for Partner in BA",
                [ra.role.name for ra in RoleAssignment.objects.filter(partner=self.partner, program=self.program)],
            )
            self.assertIn(
                "Another Role for Partner in BA",
                [ra.role.name for ra in RoleAssignment.objects.filter(partner=self.partner, program=self.program)],
            )
            self.assertIn(
                "Role in BA",
                [
                    ra.role.name
                    for ra in RoleAssignment.objects.filter(partner=self.partner_allowed_in_BA, program=self.program)
                ],
            )
            self.assertEqual(
                AdminAreaLimitedTo.objects.filter(program=self.program).count(),
                2,
            )
            self.assertEqual(
                AdminAreaLimitedTo.objects.filter(program=self.program, partner=self.partner_allowed_in_BA).count(),
                1,
            )
            self.assertEqual(
                AdminAreaLimitedTo.objects.filter(program=self.program, partner=self.partner_allowed_in_BA)
                .first()
                .areas.count(),
                1,
            )
            self.assertEqual(
                AdminAreaLimitedTo.objects.filter(program=self.program, partner=self.partner_allowed_in_BA)
                .first()
                .areas.first(),
                area1,
            )
            self.assertEqual(
                AdminAreaLimitedTo.objects.filter(program=self.program, partner=self.partner).count(),
                1,
            )
            self.assertEqual(
                AdminAreaLimitedTo.objects.filter(program=self.program, partner=self.partner).first().areas.count(),
                2,
            )
            self.assertIn(
                area1,
                AdminAreaLimitedTo.objects.filter(program=self.program, partner=self.partner).first().areas.all(),
            )
            self.assertIn(
                area_to_be_unselected,
                AdminAreaLimitedTo.objects.filter(program=self.program, partner=self.partner).first().areas.all(),
            )

            # update program partners #2
            partner_to_be_added = PartnerFactory(name="Partner to be added")
            partner_to_be_added.allowed_business_areas.set([self.business_area])
            # TODO: due to temporary solution in program mutations, Partners need to already have a role in the BA to be able to be granted access to program
            # After removing this solution, below line with role can be deleted.
            RoleAssignment.objects.create(
                business_area=self.business_area,
                partner=partner_to_be_added,
                role=RoleFactory(name="Role for Partner to be added"),
                program=ProgramFactory(business_area=self.business_area),
            )
            # end of temporary solution

            self.snapshot_graphql_request(
                request_string=self.UPDATE_PROGRAM_PARTNERS_MUTATION,
                context={"user": self.user},
                variables={
                    "programData": {
                        "id": self.id_to_base64(self.program.id, "ProgramNode"),
                        "partners": [
                            {
                                "partner": str(self.partner.id),
                                "areas": [str(area1.id), str(area2.id)],
                            },
                            {
                                "partner": str(partner_to_be_added.id),
                                "areas": [str(area1.id), str(area2.id)],
                            },
                            {
                                "partner": str(self.partner_allowed_in_BA.id),
                                "areas": [],
                            },
                        ],
                        "partnerAccess": partner_access,
                    },
                    "version": self.program.version,
                },
            )

            self.program.refresh_from_db()
            self.assertEqual(
                self.program.role_assignments.count(),
                4,
            )
            self.assertIn(
                "Role for Partner in BA",
                [ra.role.name for ra in RoleAssignment.objects.filter(partner=self.partner, program=self.program)],
            )
            self.assertIn(
                "Another Role for Partner in BA",
                [ra.role.name for ra in RoleAssignment.objects.filter(partner=self.partner, program=self.program)],
            )
            self.assertIn(
                "Role in BA",
                [
                    ra.role.name
                    for ra in RoleAssignment.objects.filter(partner=self.partner_allowed_in_BA, program=self.program)
                ],
            )
            self.assertIn(
                "Role for Partner to be added",
                [
                    ra.role.name
                    for ra in RoleAssignment.objects.filter(partner=partner_to_be_added, program=self.program)
                ],
            )
            self.assertEqual(
                AdminAreaLimitedTo.objects.filter(program=self.program).count(),
                2,
            )
            self.assertEqual(
                AdminAreaLimitedTo.objects.filter(program=self.program, partner=self.partner_allowed_in_BA).count(),
                0,
            )
            self.assertEqual(
                AdminAreaLimitedTo.objects.filter(program=self.program, partner=self.partner).count(),
                1,
            )
            self.assertEqual(
                AdminAreaLimitedTo.objects.filter(program=self.program, partner=self.partner).first().areas.count(),
                2,
            )
            self.assertIn(
                area1,
                AdminAreaLimitedTo.objects.filter(program=self.program, partner=self.partner).first().areas.all(),
            )
            self.assertNotIn(
                area_to_be_unselected,
                AdminAreaLimitedTo.objects.filter(program=self.program, partner=self.partner).first().areas.all(),
            )
            self.assertIn(
                area2,
                AdminAreaLimitedTo.objects.filter(program=self.program, partner=self.partner).first().areas.all(),
            )
            self.assertEqual(
                AdminAreaLimitedTo.objects.filter(program=self.program, partner=partner_to_be_added).count(),
                1,
            )
            self.assertEqual(
                AdminAreaLimitedTo.objects.filter(program=self.program, partner=partner_to_be_added)
                .first()
                .areas.count(),
                2,
            )
            self.assertIn(
                area1,
                AdminAreaLimitedTo.objects.filter(program=self.program, partner=partner_to_be_added)
                .first()
                .areas.all(),
            )
            self.assertNotIn(
                area_to_be_unselected,
                AdminAreaLimitedTo.objects.filter(program=self.program, partner=partner_to_be_added)
                .first()
                .areas.all(),
            )
            self.assertIn(
                area2,
                AdminAreaLimitedTo.objects.filter(program=self.program, partner=partner_to_be_added)
                .first()
                .areas.all(),
            )

            # update program partners #3 - remove partner

            self.snapshot_graphql_request(
                request_string=self.UPDATE_PROGRAM_PARTNERS_MUTATION,
                context={"user": self.user},
                variables={
                    "programData": {
                        "id": self.id_to_base64(self.program.id, "ProgramNode"),
                        "partners": [
                            {
                                "partner": str(self.partner.id),
                                "areas": [str(area1.id), str(area2.id)],
                            },
                            {
                                "partner": str(self.partner_allowed_in_BA.id),
                                "areas": [],
                            },
                        ],
                        "partnerAccess": partner_access,
                    },
                    "version": self.program.version,
                },
            )

            self.program.refresh_from_db()
            self.assertEqual(
                self.program.role_assignments.count(),
                3,
            )
            self.assertIsNone(
                self.program.role_assignments.filter(partner=partner_to_be_added).first(),
            )

            # update program partners #4 - change to NONE_PARTNERS_ACCESS

            self.snapshot_graphql_request(
                request_string=self.UPDATE_PROGRAM_PARTNERS_MUTATION,
                context={"user": self.user},
                variables={
                    "programData": {
                        "id": self.id_to_base64(self.program.id, "ProgramNode"),
                        "partnerAccess": Program.NONE_PARTNERS_ACCESS,
                    },
                    "version": self.program.version,
                },
            )

            self.program.refresh_from_db()
            self.assertEqual(
                self.program.role_assignments.count(),
                0,
            )

    def test_update_program_partners_invalid_access_type_from_object(self) -> None:
        self.program.partner_access = Program.SELECTED_PARTNERS_ACCESS
        self.program.save()
        area1 = AreaFactory(name="Area1", area_type=self.area_type_other, p_code="AREA1")
        area2 = AreaFactory(name="Area2", area_type=self.area_type_other, p_code="AREA2")
        area_to_be_unselected = AreaFactory(
            name="AreaToBeUnselected", area_type=self.area_type_other, p_code="AREA-TO-BE-UNSELECTED"
        )
        RoleAssignment.objects.create(
            business_area=self.business_area,
            partner=self.partner,
            role=RoleFactory(name="Role for Partner"),
            program=self.program,
        )
        area_limits = AdminAreaLimitedTo.objects.create(
            partner=self.partner,
            program=self.program,
        )
        area_limits.areas.set([area1, area_to_be_unselected])

        RoleAssignment.objects.create(
            business_area=self.business_area,
            partner=self.partner_allowed_in_BA,
            role=RoleFactory(name="Role for Partner Allowed in BA"),
            program=self.program,
        )
        area_limits_2 = AdminAreaLimitedTo.objects.create(
            partner=self.partner_allowed_in_BA,
            program=self.program,
        )
        area_limits_2.areas.set([area1])

        partner_to_be_added = PartnerFactory(name="Partner to be added")
        partner_to_be_added.allowed_business_areas.set([self.business_area])
        # TODO: due to temporary solution in program mutations, Partners need to already have a role in the BA to be able to be granted access to program
        # After removing this solution, below line with role can be deleted.
        RoleAssignment.objects.create(
            business_area=self.business_area,
            partner=partner_to_be_added,
            role=RoleFactory(name="Role for Partner to be added"),
            program=ProgramFactory(business_area=self.business_area),
        )
        # end of temporary solution

        self.create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.business_area,
            whole_business_area_access=True,
        )

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_PARTNERS_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "partners": [
                        {
                            "partner": str(self.partner.id),
                            "areas": [str(area1.id), str(area2.id)],
                        },
                        {
                            "partner": str(partner_to_be_added.id),
                            "areas": [str(area1.id), str(area2.id)],
                        },
                    ],
                },
                "version": self.program.version,
            },
        )

    def test_update_program_partners_all_partners_access(self) -> None:
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.business_area,
            whole_business_area_access=True,
        )

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_PARTNERS_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "partnerAccess": Program.ALL_PARTNERS_ACCESS,
                },
                "version": self.program.version,
            },
        )

        self.program.refresh_from_db()
        self.assertEqual(
            AdminAreaLimitedTo.objects.filter(program=self.program).count(),
            0,
        )
        self.assertEqual(
            self.program.role_assignments.count(),
            3,
        )
        # role should be created for self.partner (2 records - because currently 2 roles in BA - due to temporary solution),
        # and for self.partner_allowed_in_BA
        # UNICEF HQ has "Role with all permissions" for all programs in all BAs
        # UNICEF Partner for afghanistan has role "Role for UNICEF Partners" for all programs in this BA
        self.assertIn(
            "Role for Partner in BA",
            [ra.role.name for ra in RoleAssignment.objects.filter(partner=self.partner, program=self.program)],
        )
        self.assertIn(
            "Another Role for Partner in BA",
            [ra.role.name for ra in RoleAssignment.objects.filter(partner=self.partner, program=self.program)],
        )
        self.assertEqual(
            self.partner_allowed_in_BA.role_assignments.filter(program=self.program).first().role.name,
            "Role in BA",
        )
        self.assertEqual(
            Partner.objects.get(name="UNICEF HQ")
            .role_assignments.filter(program=None, business_area=self.program.business_area)
            .first()
            .role.name,
            "Role with all permissions",
        )
        self.assertEqual(
            Partner.objects.get(name=f"UNICEF Partner for {self.business_area.slug}")
            .role_assignments.filter(program=None, business_area=self.program.business_area)
            .first()
            .role.name,
            "Role for UNICEF Partners",
        )

    def test_update_full_area_access_flag(self) -> None:
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.business_area,
            whole_business_area_access=True,
        )
        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_PARTNERS_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "partnerAccess": Program.ALL_PARTNERS_ACCESS,
                },
                "version": self.program.version,
            },
        )

        self.program.refresh_from_db()
        self.assertEqual(AdminAreaLimitedTo.objects.filter(program=self.program).count(), 0)

        self.program.refresh_from_db()

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_PARTNERS_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "partnerAccess": Program.SELECTED_PARTNERS_ACCESS,
                    "partners": [
                        {
                            "partner": str(self.partner.id),
                            "areas": [],
                        },
                        {
                            "partner": str(self.partner_allowed_in_BA.id),
                            "areas": [self.area_in_afg_1.id],
                        },
                    ],
                },
                "version": self.program.version,
            },
        )

        self.program.refresh_from_db()

        self.assertEqual(AdminAreaLimitedTo.objects.filter(program=self.program).count(), 1)
        self.assertEqual(AdminAreaLimitedTo.objects.filter(program=self.program, partner=self.partner).count(), 0)
        self.assertEqual(
            AdminAreaLimitedTo.objects.filter(program=self.program, partner=self.partner_allowed_in_BA).count(),
            1,
        )
        self.assertEqual(
            AdminAreaLimitedTo.objects.filter(program=self.program, partner=self.partner_allowed_in_BA)
            .first()
            .areas.count(),
            1,
        )
        self.assertEqual(
            AdminAreaLimitedTo.objects.filter(program=self.program, partner=self.partner_allowed_in_BA)
            .first()
            .areas.first(),
            self.area_in_afg_1,
        )

    def test_update_program_of_other_partner_raise_error(self) -> None:
        partner = PartnerFactory(name="UHCR")
        another_partner = PartnerFactory(name="WFP")
        user = UserFactory.create(partner=partner)
        self.create_user_role_with_permissions(
            user, [Permissions.PROGRAMME_UPDATE], self.business_area, whole_business_area_access=True
        )

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_PARTNERS_MUTATION,
            context={"user": user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "partnerAccess": Program.SELECTED_PARTNERS_ACCESS,
                    "partners": [
                        {
                            "partner": str(another_partner.id),
                            "areas": [],
                        },
                    ],
                },
                "version": self.program.version,
            },
        )

    def test_update_program_partners_all_partners_access_refresh_partners_after_update(self) -> None:
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.business_area,
            whole_business_area_access=True,
        )

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_PARTNERS_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "partnerAccess": Program.ALL_PARTNERS_ACCESS,
                },
                "version": self.program.version,
            },
        )

        self.assertEqual(self.program.role_assignments.count(), 3)
        self.assertIn(
            "Role for Partner in BA",
            [ra.role.name for ra in RoleAssignment.objects.filter(partner=self.partner, program=self.program)],
        )
        self.assertIn(
            "Another Role for Partner in BA",
            [ra.role.name for ra in RoleAssignment.objects.filter(partner=self.partner, program=self.program)],
        )
        self.assertEqual(
            self.partner_allowed_in_BA.role_assignments.filter(program=self.program).first().role.name,
            "Role in BA",
        )

        self.program.refresh_from_db()
        # new partner has a role in this BA
        self.partner_not_allowed_in_ba.allowed_business_areas.set([self.business_area])
        role_new = RoleFactory(name="Role in BA new")
        RoleAssignment.objects.create(
            business_area=self.business_area,
            partner=self.partner_not_allowed_in_ba,
            role=role_new,
            program=ProgramFactory(business_area=self.business_area),
        )

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_PARTNERS_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "partnerAccess": Program.ALL_PARTNERS_ACCESS,
                },
                "version": self.program.version,
            },
        )

        self.assertEqual(RoleAssignment.objects.filter(program=self.program).count(), 4)
        self.assertIsNotNone(
            self.program.role_assignments.filter(partner=self.partner_not_allowed_in_ba).first(),
        )
        self.assertEqual(
            self.partner_not_allowed_in_ba.role_assignments.filter(program=self.program).first().role.name,
            "Role in BA new",
        )
