from django.test import TestCase

from hct_mis_api.apps.account.fixtures import PartnerFactory
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory, CountryFactory
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program, ProgramPartnerThrough


class TestPartnerAccessChangeSignal(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.business_area = create_afghanistan()

        cls.unicef_partner = PartnerFactory(name="UNICEF")

        cls.partner_allowed_in_afg_1 = PartnerFactory(name="Partner Allowed in Afg 1")
        cls.partner_allowed_in_afg_1.allowed_business_areas.set([cls.business_area])

        cls.partner_allowed_in_afg_2 = PartnerFactory(name="Partner Allowed in Afg 2")
        cls.partner_allowed_in_afg_2.allowed_business_areas.set([cls.business_area])

        cls.partner_not_allowed_in_BA = PartnerFactory(name="Partner not allowed in Afg")

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
        self.assertEqual(self.program.partners.count(), 1)
        self.assertEqual(self.program.partners.first(), self.unicef_partner)
        self.assertEqual(self.program.program_partner_through.first().areas.count(), 2)
        self.assertIn(self.area_in_afg_1, self.program.program_partner_through.first().areas.all())
        self.assertIn(self.area_in_afg_2, self.program.program_partner_through.first().areas.all())

        self.program.partner_access = Program.NONE_PARTNERS_ACCESS
        self.program.save()

        self.assertEqual(self.program.partner_access, Program.NONE_PARTNERS_ACCESS)
        self.assertEqual(self.program.partners.count(), 1)
        self.assertEqual(self.program.partners.first(), self.unicef_partner)
        self.assertEqual(self.program.program_partner_through.first().areas.count(), 2)
        self.assertIn(self.area_in_afg_1, self.program.program_partner_through.first().areas.all())
        self.assertIn(self.area_in_afg_2, self.program.program_partner_through.first().areas.all())

    def test_all_partners_access(self) -> None:
        self.assertEqual(self.program.partners.count(), 1)

        self.program.partner_access = Program.ALL_PARTNERS_ACCESS
        self.program.save()

        self.assertEqual(self.program.partner_access, Program.ALL_PARTNERS_ACCESS)
        self.assertEqual(self.program.partners.count(), 3)
        self.assertSetEqual(
            set(self.program.partners.all()),
            {self.unicef_partner, self.partner_allowed_in_afg_1, self.partner_allowed_in_afg_2},
        )
        for program_partner_through in self.program.program_partner_through.all():
            self.assertEqual(program_partner_through.areas.count(), 2)
            self.assertIn(self.area_in_afg_1, program_partner_through.areas.all())
            self.assertIn(self.area_in_afg_2, program_partner_through.areas.all())

    def test_selected_into_all_and_none_partners_access(self) -> None:
        self.assertEqual(self.program.partners.count(), 1)

        self.program.partner_access = Program.SELECTED_PARTNERS_ACCESS
        self.program.save()

        self.assertEqual(self.program.partners.count(), 1)

        program_partner_through = ProgramPartnerThrough.objects.create(
            program=self.program, partner=self.partner_allowed_in_afg_1
        )
        program_partner_through.areas.set([self.area_in_afg_1])

        self.assertEqual(self.program.partners.count(), 2)

        self.program.partner_access = Program.ALL_PARTNERS_ACCESS
        self.program.save()

        self.assertEqual(self.program.partners.count(), 3)
        self.assertSetEqual(
            set(self.program.partners.all()),
            {self.unicef_partner, self.partner_allowed_in_afg_1, self.partner_allowed_in_afg_2},
        )
        for program_partner_through in self.program.program_partner_through.all():
            self.assertEqual(program_partner_through.areas.count(), 2)
            self.assertIn(self.area_in_afg_1, program_partner_through.areas.all())
            self.assertIn(self.area_in_afg_2, program_partner_through.areas.all())

        self.program.partner_access = Program.NONE_PARTNERS_ACCESS
        self.program.save()

        self.assertEqual(self.program.partners.count(), 1)
        self.assertEqual(self.program.partners.first(), self.unicef_partner)
