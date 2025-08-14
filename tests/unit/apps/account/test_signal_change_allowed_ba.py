from django.test import TestCase

from extras.test_utils.factories.account import PartnerFactory, RoleFactory
from extras.test_utils.factories.core import create_afghanistan, create_ukraine
from extras.test_utils.factories.program import ProgramFactory

from hope.apps.account.models import AdminAreaLimitedTo, RoleAssignment
from hope.apps.program.models import Program


class TestSignalChangeAllowedBusinessAreas(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area_afg = create_afghanistan()
        cls.business_area_ukr = create_ukraine()

        cls.partner = PartnerFactory(name="Partner")

        cls.partner.allowed_business_areas.add(cls.business_area_afg)
        role = RoleFactory(name="Role for Partner")

        RoleAssignment.objects.create(
            partner=cls.partner,
            role=role,
            business_area=cls.business_area_afg,
            program=None,
        )

        cls.partner.allowed_business_areas.add(cls.business_area_ukr)

        cls.program_afg = ProgramFactory.create(
            status=Program.DRAFT, business_area=cls.business_area_afg, partner_access=Program.ALL_PARTNERS_ACCESS
        )
        cls.program_ukr = ProgramFactory.create(
            status=Program.DRAFT, business_area=cls.business_area_ukr, partner_access=Program.SELECTED_PARTNERS_ACCESS
        )
        cls.program_ukr_2 = ProgramFactory.create(
            status=Program.DRAFT, business_area=cls.business_area_ukr, partner_access=Program.SELECTED_PARTNERS_ACCESS
        )

        RoleAssignment.objects.create(
            partner=cls.partner,
            role=role,
            business_area=cls.business_area_ukr,
            program=cls.program_ukr_2,
        )

    def test_signal_change_allowed_business_areas(self) -> None:
        assert (
            self.program_afg.role_assignments.count() == 1
        )  # ALL_PARTNERS_ACCESS - Partner that has access to AFG (signal on program)
        assert self.program_afg.role_assignments.first().partner == self.partner

        assert (
            RoleAssignment.objects.filter(business_area=self.business_area_afg, program=None).count() == 3
        )  # UNICEF HQ, UNICEF for afg, self.partner

        assert self.program_ukr.role_assignments.count() == 0  # SELECTED_PARTNERS_ACCESS

        assert (
            RoleAssignment.objects.filter(business_area=self.business_area_ukr, program=None).count() == 2
        )  # UNICEF HQ, UNICEF for afg, self.partner

        assert self.program_ukr_2.role_assignments.count() == 1  # SELECTED_PARTNERS_ACCESS
        assert self.program_ukr_2.role_assignments.first().partner == self.partner

        assert self.partner.role_assignments.count() == 3
        self.assertIsNotNone(self.partner.role_assignments.filter(program=self.program_afg).first())
        self.assertIsNotNone(
            self.partner.role_assignments.filter(program=None, business_area=self.business_area_afg).first()
        )
        self.assertIsNotNone(self.partner.role_assignments.filter(program=self.program_ukr_2).first())

        assert AdminAreaLimitedTo.objects.filter(partner=self.partner).count() == 0

        self.partner.allowed_business_areas.remove(self.business_area_afg)
        # removing from allowed BA -> removing roles in this BA
        self.assertIsNone(self.partner.role_assignments.filter(program=self.program_afg).first())
        self.assertIsNone(
            self.partner.role_assignments.filter(program=None, business_area=self.business_area_afg).first()
        )
        self.assertIsNotNone(self.partner.role_assignments.filter(program=self.program_ukr_2).first())
