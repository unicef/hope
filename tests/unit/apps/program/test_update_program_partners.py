from typing import Any, List

from parameterized import parameterized

from tests.extras.test_utils.factories.account import PartnerFactory, RoleFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from tests.extras.test_utils.factories.core import (
    create_afghanistan,
    generate_data_collecting_types,
)
from hct_mis_api.apps.core.models import (
    BusinessArea,
    BusinessAreaPartnerThrough,
    DataCollectingType,
)
from tests.extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory, CountryFactory
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program, ProgramPartnerThrough


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
        cls.unicef_partner = PartnerFactory(name="UNICEF")

        cls.program = ProgramFactory.create(
            name="initial name",
            status=Program.DRAFT,
            business_area=cls.business_area,
            data_collecting_type=data_collecting_type,
            partner_access=Program.NONE_PARTNERS_ACCESS,
            version=123,
            biometric_deduplication_enabled=True,
        )
        unicef_program, _ = ProgramPartnerThrough.objects.get_or_create(
            program=cls.program,
            partner=cls.unicef_partner,
        )

        cls.partner = PartnerFactory(name="WFP")
        cls.user = UserFactory.create(partner=cls.partner)

        # partner with role in BA - will be granted access for ALL_PARTNERS_ACCESS type
        cls.other_partner = PartnerFactory(name="Other Partner")
        cls.other_partner.allowed_business_areas.set([cls.business_area])
        role = RoleFactory(name="Role in BA")
        ba_partner_through = BusinessAreaPartnerThrough.objects.create(
            business_area=cls.business_area,
            partner=cls.other_partner,
        )
        ba_partner_through.roles.set([role])

        cls.partner_without_role_in_BA = PartnerFactory(name="Partner without role in in BA")
        cls.partner_without_role_in_BA.allowed_business_areas.set([cls.business_area])

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

        unicef_program.areas.set([cls.area_in_afg_1, cls.area_in_afg_2])

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
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

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
        program_partner = ProgramPartnerThrough.objects.create(
            program=self.program,
            partner=self.partner,
        )
        program_partner.areas.set([area1, area_to_be_unselected])
        ProgramPartnerThrough.objects.create(
            program=self.program,
            partner=self.other_partner,
        )
        partner_to_be_added = PartnerFactory(name="Partner to be added")
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.business_area,
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
                    "partnerAccess": partner_access,
                },
                "version": self.program.version,
            },
        )

    def test_update_program_partners_invalid_access_type_from_object(self) -> None:
        area1 = AreaFactory(name="Area1", area_type=self.area_type_other, p_code="AREA1")
        area2 = AreaFactory(name="Area2", area_type=self.area_type_other, p_code="AREA2")
        area_to_be_unselected = AreaFactory(
            name="AreaToBeUnselected", area_type=self.area_type_other, p_code="AREA-TO-BE-UNSELECTED"
        )
        program_partner = ProgramPartnerThrough.objects.create(
            program=self.program,
            partner=self.partner,
        )
        program_partner.areas.set([area1, area_to_be_unselected])
        ProgramPartnerThrough.objects.create(
            program=self.program,
            partner=self.other_partner,
        )
        partner_to_be_added = PartnerFactory(name="Partner to be added")
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.business_area,
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

    def test_update_full_area_access_flag(self) -> None:
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.business_area,
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

        for program_partner_through in Program.objects.get(name="initial name").program_partner_through.all():
            self.assertEqual(program_partner_through.full_area_access, True)

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
                            "partner": str(self.other_partner.id),
                            "areas": [self.area_in_afg_1.id],
                        },
                    ],
                },
                "version": self.program.version,
            },
        )

        self.assertEqual(
            ProgramPartnerThrough.objects.get(partner=self.partner, program__name="initial name").full_area_access, True
        )
        self.assertEqual(
            ProgramPartnerThrough.objects.get(
                partner=self.other_partner, program__name="initial name"
            ).full_area_access,
            False,
        )
        self.assertEqual(
            ProgramPartnerThrough.objects.get(
                partner=self.unicef_partner, program__name="initial name"
            ).full_area_access,
            True,
        )

    def test_update_program_of_other_partner_raise_error(self) -> None:
        partner = PartnerFactory(name="UHCR")
        another_partner = PartnerFactory(name="WFP")
        user = UserFactory.create(partner=partner)
        self.create_user_role_with_permissions(user, [Permissions.PROGRAMME_UPDATE], self.business_area)

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

        self.assertEqual(ProgramPartnerThrough.objects.filter(program=self.program).count(), 2)

        self.program.refresh_from_db()
        # new partner has a role in this BA
        ba_partner_through_new = BusinessAreaPartnerThrough.objects.create(
            business_area=self.business_area,
            partner=self.partner_without_role_in_BA,
        )
        role_new = RoleFactory(name="Role in BA new")
        ba_partner_through_new.roles.set([role_new])

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

        self.assertEqual(ProgramPartnerThrough.objects.filter(program=self.program).count(), 3)
