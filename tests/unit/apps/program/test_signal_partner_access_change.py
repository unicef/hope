from django.test import TestCase

from hct_mis_api.apps.account.fixtures import PartnerFactory, RoleFactory
from hct_mis_api.apps.account.models import AdminAreaLimitedTo, RoleAssignment
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory, CountryFactory
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program


class TestPartnerAccessChangeSignal(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()

        cls.unicef_partner = PartnerFactory(name="UNICEF")

        role = RoleFactory(name="Role for Partner")
        cls.partner_with_role_in_afg_1 = PartnerFactory(name="Partner with role in Afg 1")
        cls.partner_with_role_in_afg_1.allowed_business_areas.set([cls.business_area])
        # TODO: Due to temporary solution on program mutation, partner has to hold a role in business area.
        # After temporary solution is removed, partners will just need to be allowed in business area.
        RoleAssignment.objects.create(
            partner=cls.partner_with_role_in_afg_1,
            role=role,
            business_area=cls.business_area,
            program=ProgramFactory(business_area=cls.business_area),
        )

        cls.partner_with_role_in_afg_2 = PartnerFactory(name="Partner with role in Afg 2")
        cls.partner_with_role_in_afg_2.allowed_business_areas.set([cls.business_area])
        RoleAssignment.objects.create(
            partner=cls.partner_with_role_in_afg_2,
            role=role,
            business_area=cls.business_area,
            program=ProgramFactory(business_area=cls.business_area),
        )

        cls.partner_not_allowed_in_BA = PartnerFactory(name="Partner without role in Afg")

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

        cls.program = ProgramFactory.create(
            status=Program.DRAFT, business_area=cls.business_area, partner_access=Program.NONE_PARTNERS_ACCESS
        )

    def test_none_partners_access(self) -> None:
        self.assertEqual(self.program.partner_access, Program.NONE_PARTNERS_ACCESS)
        self.assertEqual(self.program.role_assignments.count(), 0)
        self.assertEqual(
            RoleAssignment.objects.filter(business_area=self.business_area, program=None).count(),
            2,
        )  # UNICEF HQ and UNICEF Partner for afghanistan
        self.assertEqual(
            RoleAssignment.objects.filter(
                business_area=self.business_area, program=None, partner__name="UNICEF HQ"
            ).count(),
            1,
        )
        self.assertEqual(
            RoleAssignment.objects.filter(
                business_area=self.business_area,
                program=None,
                partner__name=f"UNICEF Partner for {self.business_area.slug}",
            ).count(),
            1,
        )

        self.assertEqual(self.program.admin_area_limits.count(), 0)

        self.program.partner_access = Program.NONE_PARTNERS_ACCESS
        self.program.save()

        self.assertEqual(self.program.partner_access, Program.NONE_PARTNERS_ACCESS)
        self.assertEqual(self.program.role_assignments.count(), 0)
        self.assertEqual(
            RoleAssignment.objects.filter(business_area=self.business_area, program=None).count(),
            2,
        )  # UNICEF HQ and UNICEF Partner for afghanistan

        self.assertEqual(self.program.admin_area_limits.count(), 0)

    def test_all_partners_access(self) -> None:
        self.assertEqual(self.program.role_assignments.count(), 0)

        self.program.partner_access = Program.ALL_PARTNERS_ACCESS
        self.program.save()

        self.assertEqual(self.program.partner_access, Program.ALL_PARTNERS_ACCESS)

        self.assertEqual(self.program.role_assignments.count(), 2)
        self.assertEqual(self.program.role_assignments.filter(partner=self.partner_with_role_in_afg_1).count(), 1)
        self.assertEqual(self.program.role_assignments.filter(partner=self.partner_with_role_in_afg_2).count(), 1)

        self.assertEqual(self.program.admin_area_limits.count(), 0)

    def test_selected_into_all_and_none_partners_access(self) -> None:
        self.assertEqual(self.program.role_assignments.count(), 0)

        self.program.partner_access = Program.SELECTED_PARTNERS_ACCESS
        self.program.save()

        self.assertEqual(self.program.role_assignments.count(), 0)

        RoleAssignment.objects.create(
            partner=self.partner_with_role_in_afg_1,
            role=RoleFactory(name="Role for Partner"),
            business_area=self.business_area,
            program=self.program,
        )
        area_limits = AdminAreaLimitedTo.objects.create(partner=self.partner_with_role_in_afg_1, program=self.program)
        area_limits.areas.set([self.area_in_afg_1])

        self.assertEqual(self.program.role_assignments.count(), 1)
        self.assertEqual(self.program.admin_area_limits.count(), 1)
        self.assertEqual(self.program.admin_area_limits.first().areas.count(), 1)
        self.assertEqual(self.program.admin_area_limits.first().areas.first(), self.area_in_afg_1)

        self.program.partner_access = Program.ALL_PARTNERS_ACCESS
        self.program.save()

        self.assertEqual(self.program.role_assignments.count(), 2)

        self.assertEqual(self.program.role_assignments.filter(partner=self.partner_with_role_in_afg_1).count(), 1)
        self.assertEqual(self.program.role_assignments.filter(partner=self.partner_with_role_in_afg_2).count(), 1)

        self.assertEqual(self.program.admin_area_limits.count(), 0)

        self.program.partner_access = Program.NONE_PARTNERS_ACCESS
        self.program.save()

        self.assertEqual(self.program.role_assignments.count(), 0)
        self.assertEqual(
            RoleAssignment.objects.filter(business_area=self.business_area, program=None).count(),
            2,
        )  # UNICEF HQ and UNICEF Partner for afghanistan
        self.assertEqual(
            RoleAssignment.objects.filter(
                business_area=self.business_area, program=None, partner__name="UNICEF HQ"
            ).count(),
            1,
        )
        self.assertEqual(
            RoleAssignment.objects.filter(
                business_area=self.business_area,
                program=None,
                partner__name=f"UNICEF Partner for {self.business_area.slug}",
            ).count(),
            1,
        )
