from django.test import TestCase

from hct_mis_api.apps.account.fixtures import PartnerFactory
from hct_mis_api.apps.core.fixtures import create_afghanistan, create_ukraine
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program


class TestSignalChangeAllowedBusinessAreas(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.business_area_afg = create_afghanistan()
        cls.business_area_ukr = create_ukraine()
        cls.program_afg = ProgramFactory.create(
            status=Program.DRAFT, business_area=cls.business_area_afg, partner_access=Program.ALL_PARTNERS_ACCESS
        )
        cls.program_ukr = ProgramFactory.create(
            status=Program.DRAFT, business_area=cls.business_area_ukr, partner_access=Program.ALL_PARTNERS_ACCESS
        )
        cls.partner = PartnerFactory(name="Partner")
        cls.partner_unicef = PartnerFactory(name="UNICEF")  # UNICEF partner has access to all programs

    def test_signal_change_allowed_business_areas(self) -> None:
        self.partner.allowed_business_areas.add(self.business_area_afg)

        self.assertEqual(self.program_afg.partners.count(), 2)
        self.assertEqual(self.program_ukr.partners.count(), 1)
        self.assertEqual(self.partner.programs.count(), 1)
        self.assertEqual(self.partner.program_partner_through.first().full_area_access, True)

        self.partner.allowed_business_areas.add(self.business_area_ukr)

        self.assertEqual(self.program_afg.partners.count(), 2)
        self.assertEqual(self.program_ukr.partners.count(), 2)
        self.assertEqual(self.partner.programs.count(), 2)
        self.assertEqual(self.partner.program_partner_through.first().full_area_access, True)
        self.assertEqual(self.partner.program_partner_through.last().full_area_access, True)

        self.partner.allowed_business_areas.remove(self.business_area_afg)

        self.assertEqual(self.program_afg.partners.count(), 1)
        self.assertEqual(self.program_ukr.partners.count(), 2)
        self.assertEqual(self.partner.programs.count(), 1)
        self.assertEqual(self.partner.program_partner_through.first().full_area_access, True)

        self.partner.allowed_business_areas.clear()

        self.assertEqual(self.program_afg.partners.count(), 1)
        self.assertEqual(self.program_ukr.partners.count(), 1)
        self.assertEqual(self.partner.programs.count(), 0)
