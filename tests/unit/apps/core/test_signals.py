from django.test import TestCase

from hct_mis_api.apps.account.fixtures import PartnerFactory
from hct_mis_api.apps.account.models import Partner, Role
from hct_mis_api.apps.core.models import BusinessArea


class TestSignalCreateBusinessArea(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()

        cls.partner_unicef = PartnerFactory(name="UNICEF")
        Role.objects.get_or_create(name="Role for UNICEF Partners", subsystem="HOPE")
        cls.unicef_hq = PartnerFactory(name="UNICEF HQ", parent=cls.partner_unicef)

    def test_signal_add_partner_role(self) -> None:
        partner_count = Partner.objects.count()
        new_ba = BusinessArea.objects.create(name="Test Business Area", code="TBA", active=True)
        self.assertEqual(Partner.objects.count(), partner_count + 1)

        new_partner = Partner.objects.filter(name=f"UNICEF Partner for {new_ba.slug}").first()
        self.assertIsNotNone(new_partner)
        self.assertEqual(new_partner.allowed_business_areas.count(), 1)
        self.assertEqual(new_partner.allowed_business_areas.first().name, "Test Business Area")
        self.assertEqual(new_partner.role_assignments.count(), 1)
        self.assertEqual(new_partner.role_assignments.first().business_area.name, "Test Business Area")
        self.assertEqual(new_partner.role_assignments.first().role.name, "Role for UNICEF Partners")

        # UNICEF HQ is granted role "Role with all permissions" in the new business area
        self.assertEqual(self.unicef_hq.allowed_business_areas.count(), 1)
        self.assertEqual(self.unicef_hq.allowed_business_areas.first().name, "Test Business Area")
        self.assertEqual(self.unicef_hq.role_assignments.count(), 1)
        self.assertEqual(self.unicef_hq.role_assignments.first().business_area.name, "Test Business Area")
        self.assertEqual(self.unicef_hq.role_assignments.first().role.name, "Role with all permissions")
