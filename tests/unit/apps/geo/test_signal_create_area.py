from django.test import TestCase

from extras.test_utils.factories.account import BusinessAreaFactory, PartnerFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory, CountryFactory
from extras.test_utils.factories.program import ProgramFactory

from hct_mis_api.apps.program.models import Program, ProgramPartnerThrough


class PartnerAccessChangeSignal(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()

        cls.unicef_partner = PartnerFactory(name="UNICEF")

        cls.partner = PartnerFactory(name="Partner")

        country_afg = CountryFactory(name="Afghanistan")
        country_afg.business_areas.set([cls.business_area])
        cls.area_type_afg = AreaTypeFactory(name="Area Type in Afg", country=country_afg)
        country_other = CountryFactory(
            name="Other Country",
            short_name="Oth",
            iso_code2="O",
            iso_code3="OTH",
            iso_num="111",
        )
        cls.area_type_other = AreaTypeFactory(name="Area Type Other", country=country_other)

        cls.area_in_afg_1 = AreaFactory(name="Area in AFG 1", area_type=cls.area_type_afg, p_code="AREA-IN-AFG1")
        cls.area_in_afg_2 = AreaFactory(name="Area in AFG 2", area_type=cls.area_type_afg, p_code="AREA-IN-AFG2")

        cls.program = ProgramFactory.create(
            status=Program.DRAFT, business_area=cls.business_area, partner_access=Program.SELECTED_PARTNERS_ACCESS
        )
        cls.program_partner_through, _ = ProgramPartnerThrough.objects.get_or_create(
            program=cls.program, partner=cls.partner
        )
        cls.program_partner_through.areas.set([cls.area_in_afg_1, cls.area_in_afg_2])
        cls.program_partner_through.full_area_access = False
        cls.program_partner_through.save()
        cls.program_unicef_through, _ = ProgramPartnerThrough.objects.get_or_create(
            program=cls.program, partner=cls.unicef_partner
        )
        cls.program_unicef_through.areas.set([cls.area_in_afg_1, cls.area_in_afg_2])
        cls.program_unicef_through.full_area_access = True
        cls.program_unicef_through.save()

        other_ba = BusinessAreaFactory(name="Other Business Area")
        cls.program_other = ProgramFactory.create(
            status=Program.DRAFT, business_area=other_ba, partner_access=Program.NONE_PARTNERS_ACCESS
        )
        cls.program_other_unicef_through = ProgramPartnerThrough.objects.get(
            program=cls.program_other, partner=cls.unicef_partner
        )
        cls.program_other_unicef_through.areas.set([cls.area_in_afg_1, cls.area_in_afg_2])
        cls.program_other_unicef_through.full_area_access = True
        cls.program_other_unicef_through.save()

    def test_add_new_area_to_full_access(self) -> None:
        self.assertEqual(self.program_partner_through.areas.count(), 2)
        self.assertEqual(self.program_unicef_through.areas.count(), 2)

        self.assertEqual(self.program_other_unicef_through.areas.count(), 2)

        self.new_area_in_afg = AreaFactory(name="Area in AFG", area_type=self.area_type_afg, p_code="AREA-IN-AFG")
        self.new_area_not_in_afg = AreaFactory(
            name="Area not in AFG", area_type=self.area_type_other, p_code="AREA-NOT-IN-AFG"
        )

        self.assertEqual(self.program_partner_through.areas.count(), 2)
        self.assertEqual(self.program_unicef_through.areas.count(), 3)

        self.assertEqual(self.program_other_unicef_through.areas.count(), 2)
