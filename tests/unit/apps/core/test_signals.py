from django.test import TestCase
from extras.test_utils.factories.account import PartnerFactory, RoleFactory

from hope.apps.account.models import Partner
from hope.apps.core.models import BusinessArea


class TestSignalCreateBusinessArea(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()

        cls.partner_unicef = PartnerFactory(name="UNICEF")
        RoleFactory(
            name="Role for UNICEF Partners",
            subsystem="HOPE",
            is_visible_on_ui=False,
            is_available_for_partner=False,
        )
        cls.unicef_hq = PartnerFactory(name="UNICEF HQ", parent=cls.partner_unicef)

    def test_signal_add_partner_role(self) -> None:
        partner_count = Partner.objects.count()
        new_ba = BusinessArea.objects.create(name="Test Business Area", code="TBA", active=True)
        assert Partner.objects.count() == partner_count + 1

        new_partner = Partner.objects.filter(name=f"UNICEF Partner for {new_ba.slug}").first()
        assert new_partner is not None
        assert new_partner.allowed_business_areas.count() == 1
        assert new_partner.allowed_business_areas.first().name == "Test Business Area"
        assert new_partner.role_assignments.count() == 1
        assert new_partner.role_assignments.first().business_area.name == "Test Business Area"
        assert new_partner.role_assignments.first().role.name == "Role for UNICEF Partners"

        # UNICEF HQ is granted role "Role with all permissions" in the new business area
        assert self.unicef_hq.allowed_business_areas.count() == 1
        assert self.unicef_hq.allowed_business_areas.first().name == "Test Business Area"
        assert self.unicef_hq.role_assignments.count() == 1
        assert self.unicef_hq.role_assignments.first().business_area.name == "Test Business Area"
        assert self.unicef_hq.role_assignments.first().role.name == "Role with all permissions"
