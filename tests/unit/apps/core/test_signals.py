import pytest

from extras.test_utils.factories import PartnerFactory, RoleFactory
from hope.models import BusinessArea, Partner


@pytest.fixture
def partner_unicef(db):
    return PartnerFactory(name="UNICEF")


@pytest.fixture
def role_for_unicef_partners(db):
    return RoleFactory(
        name="Role for UNICEF Partners",
        subsystem="HOPE",
        is_visible_on_ui=False,
        is_available_for_partner=False,
    )


@pytest.fixture
def unicef_hq(db, partner_unicef):
    return PartnerFactory(name="UNICEF HQ", parent=partner_unicef)


def test_create_business_area_signal_creates_partner_and_assigns_roles(
    db, partner_unicef, role_for_unicef_partners, unicef_hq
):
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

    unicef_hq.refresh_from_db()
    assert unicef_hq.allowed_business_areas.count() == 1
    assert unicef_hq.allowed_business_areas.first().name == "Test Business Area"
    assert unicef_hq.role_assignments.count() == 1
    assert unicef_hq.role_assignments.first().business_area.name == "Test Business Area"
    assert unicef_hq.role_assignments.first().role.name == "Role with all permissions"
