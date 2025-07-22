from django.test import TestCase

from extras.test_utils.factories.account import PartnerFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory, CountryFactory
from extras.test_utils.factories.program import ProgramFactory

from hct_mis_api.apps.program.models import Program, ProgramPartnerThrough


class TestPartnerFullAreaAccessSignal(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()

        cls.unicef_partner = PartnerFactory(name="UNICEF")
        cls.partner = PartnerFactory(name="Partner")

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
            status=Program.DRAFT, business_area=cls.business_area, partner_access=Program.SELECTED_PARTNERS_ACCESS
        )
        program_partner_through = ProgramPartnerThrough.objects.create(
            program=cls.program,
            partner=cls.partner,
        )
        program_partner_through.areas.set([cls.area_in_afg_1])

    def test_create_program_full_access_area_flag(self) -> None:
        new_partner = PartnerFactory(name="New Partner")
        new_program_partner_through = ProgramPartnerThrough.objects.create(
            program=self.program,
            partner=new_partner,
            full_area_access=True,
        )

        self.assertEqual(new_program_partner_through.full_area_access, True)
        self.assertEqual(self.program.program_partner_through.filter(partner=new_partner).first().areas.count(), 2)
        self.assertIn(
            self.area_in_afg_1, self.program.program_partner_through.filter(partner=new_partner).first().areas.all()
        )
        self.assertIn(
            self.area_in_afg_2, self.program.program_partner_through.filter(partner=new_partner).first().areas.all()
        )
        self.assertNotIn(
            self.area_not_in_afg, self.program.program_partner_through.filter(partner=new_partner).first().areas.all()
        )

    def test_update_program_full_access_area_flag(self) -> None:
        self.assertEqual(
            self.program.program_partner_through.filter(partner=self.partner).first().full_area_access, False
        )
        self.assertEqual(self.program.program_partner_through.filter(partner=self.partner).first().areas.count(), 1)
        self.assertIn(
            self.area_in_afg_1, self.program.program_partner_through.filter(partner=self.partner).first().areas.all()
        )
        self.assertNotIn(
            self.area_in_afg_2, self.program.program_partner_through.filter(partner=self.partner).first().areas.all()
        )
        self.assertNotIn(
            self.area_not_in_afg, self.program.program_partner_through.filter(partner=self.partner).first().areas.all()
        )

        program_partner_through = self.program.program_partner_through.filter(partner=self.partner).first()
        program_partner_through.full_area_access = True
        program_partner_through.save(update_fields=["full_area_access"])

        self.assertEqual(
            self.program.program_partner_through.filter(partner=self.partner).first().full_area_access, True
        )
        self.assertEqual(self.program.program_partner_through.filter(partner=self.partner).first().areas.count(), 2)
        self.assertIn(
            self.area_in_afg_1, self.program.program_partner_through.filter(partner=self.partner).first().areas.all()
        )
        self.assertIn(
            self.area_in_afg_2, self.program.program_partner_through.filter(partner=self.partner).first().areas.all()
        )
        self.assertNotIn(
            self.area_not_in_afg, self.program.program_partner_through.filter(partner=self.partner).first().areas.all()
        )
