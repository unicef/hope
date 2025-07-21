from django.test import TestCase

from tests.extras.test_utils.factories.account import PartnerFactory, RoleFactory
from tests.extras.test_utils.factories.core import create_afghanistan, create_ukraine
from hct_mis_api.apps.core.models import BusinessAreaPartnerThrough
from tests.extras.test_utils.factories.program import ProgramFactory
from hct_mis_api.apps.program.models import Program, ProgramPartnerThrough


class TestSignalChangeAllowedBusinessAreas(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area_afg = create_afghanistan()
        cls.business_area_ukr = create_ukraine()

        cls.partner = PartnerFactory(name="Partner")
        cls.partner_unicef = PartnerFactory(name="UNICEF")  # UNICEF partner has access to all programs

        cls.partner.allowed_business_areas.add(cls.business_area_afg)
        role = RoleFactory(name="Role for Partner")
        afg_partner_through = BusinessAreaPartnerThrough.objects.create(
            business_area=cls.business_area_afg,
            partner=cls.partner,
        )
        afg_partner_through.roles.set([role])
        cls.partner.allowed_business_areas.add(cls.business_area_ukr)
        ukr_partner_through = BusinessAreaPartnerThrough.objects.create(
            business_area=cls.business_area_ukr,
            partner=cls.partner,
        )
        ukr_partner_through.roles.set([role])

        cls.program_afg = ProgramFactory.create(
            status=Program.DRAFT, business_area=cls.business_area_afg, partner_access=Program.ALL_PARTNERS_ACCESS
        )
        cls.program_ukr = ProgramFactory.create(
            status=Program.DRAFT, business_area=cls.business_area_ukr, partner_access=Program.SELECTED_PARTNERS_ACCESS
        )

    def test_signal_change_allowed_business_areas(self) -> None:
        self.assertEqual(
            self.program_afg.partners.count(), 2
        )  # ALL_PARTNERS_ACCESS - UNICEF and Partner that has access to AFG (signal on program)
        self.assertEqual(self.program_ukr.partners.count(), 1)  # SELECTED_PARTNERS_ACCESS - only UNICEF
        self.assertEqual(self.partner.programs.count(), 1)

        self.assertEqual(self.partner.program_partner_through.first().full_area_access, True)

        # grant access to program in ukr
        ProgramPartnerThrough.objects.create(
            program=self.program_ukr,
            partner=self.partner,
        )

        self.assertEqual(self.program_ukr.partners.count(), 2)
        self.assertEqual(self.partner.programs.count(), 2)

        self.assertEqual(self.partner.program_partner_through.get(program=self.program_ukr).full_area_access, False)

        self.partner.allowed_business_areas.remove(self.business_area_afg)
        # removing from allowed BA -> removing roles in this BA
        self.assertIsNone(
            self.partner.business_area_partner_through.filter(business_area=self.business_area_afg).first()
        )
        self.assertIsNotNone(
            self.partner.business_area_partner_through.filter(business_area=self.business_area_ukr).first()
        )
        # removing the role -> removing access to the program
        self.assertEqual(self.program_afg.partners.count(), 1)  # only UNICEF left
        self.assertEqual(self.partner.programs.count(), 1)

        self.partner.allowed_business_areas.remove(self.business_area_ukr)
        # removing from allowed BA -> removing roles in this BA
        self.assertIsNone(
            self.partner.business_area_partner_through.filter(business_area=self.business_area_ukr).first()
        )
        # removing the role -> removing access to the program
        self.assertEqual(self.program_ukr.partners.count(), 1)  # only UNICEF left

        self.assertEqual(self.partner.programs.count(), 0)
