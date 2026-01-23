"""Tests for user role assignments permissions and expiry validation."""

from typing import Any

import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PartnerFactory,
    RoleFactory,
    UserFactory,
)
from hope.apps.account.permissions import (
    DEFAULT_PERMISSIONS_IS_UNICEF_PARTNER,
    Permissions,
)
from hope.models import BusinessArea, Role, RoleAssignment

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area_afg(db: Any) -> BusinessArea:
    return BusinessAreaFactory(
        slug="afghanistan",
        code="0060",
        name="Afghanistan",
    )


@pytest.fixture
def business_area_ukr(db: Any) -> BusinessArea:
    return BusinessAreaFactory(
        slug="ukraine",
        code="4410",
        name="Ukraine",
    )


def test_user_role_exclude_by_expiry_date(business_area_afg: BusinessArea, business_area_ukr: BusinessArea):
    # Create user with non-UNICEF partner
    user_not_unicef_partner = UserFactory(partner=PartnerFactory(name="Test123"))

    # Create roles with specific permissions
    role_1 = RoleFactory(name="111", permissions=[Permissions.RDI_VIEW_LIST.value])
    role_2 = RoleFactory(name="222", permissions=[Permissions.PM_EXPORT_PDF_SUMMARY.value])

    # Create active role assignment
    user_role_1 = RoleAssignment.objects.create(
        role=role_1,
        business_area=business_area_afg,
        user=user_not_unicef_partner,
        partner=None,
    )

    # Create expired role assignment
    user_role_2 = RoleAssignment.objects.create(
        role=role_2,
        business_area=business_area_afg,
        user=user_not_unicef_partner,
        partner=None,
        expiry_date="2024-02-16",
    )

    # Create active role assignment in different business area with same role as user_role_2
    RoleAssignment.objects.create(
        role=role_2,
        business_area=business_area_ukr,
        user=user_not_unicef_partner,
        partner=None,
    )

    # Verify active role permissions are present
    assert Permissions.RDI_VIEW_LIST.value in user_not_unicef_partner.permissions_in_business_area(
        business_area_afg.slug
    )
    # Expired role permissions should not be present
    assert Permissions.PM_EXPORT_PDF_SUMMARY.value not in user_not_unicef_partner.permissions_in_business_area(
        business_area_afg.slug
    )
    # Same role in different BA should be active
    assert Permissions.PM_EXPORT_PDF_SUMMARY.value in user_not_unicef_partner.permissions_in_business_area(
        business_area_ukr.slug
    )

    # Expire user_role_1
    user_role_1.expiry_date = "2024-02-02"
    user_role_1.save()
    user_role_1.refresh_from_db()

    assert str(user_role_1.expiry_date) == "2024-02-02"
    assert str(user_role_2.expiry_date) == "2024-02-16"

    # All roles in business_area_afg are now expired - empty permissions
    assert user_not_unicef_partner.permissions_in_business_area(business_area_afg.slug) == set()
    assert Permissions.RDI_VIEW_LIST.value not in user_not_unicef_partner.permissions_in_business_area(
        business_area_afg.slug
    )
    assert Permissions.PM_EXPORT_PDF_SUMMARY.value not in user_not_unicef_partner.permissions_in_business_area(
        business_area_afg.slug
    )


def test_unicef_partner_hq_has_permission_from_user_and_role_with_all_permissions(business_area_afg: BusinessArea):
    # Create UNICEF partner structure
    partner = PartnerFactory(name="UNICEF")
    unicef_hq = PartnerFactory(name="UNICEF HQ", parent=partner)
    user = UserFactory(partner=unicef_hq)

    # Create role with specific permission
    role = RoleFactory(name="111", permissions=[Permissions.GRIEVANCES_CREATE.value])
    RoleAssignment.objects.create(
        role=role,
        business_area=business_area_afg,
        user=user,
        partner=None,
    )

    # User should have the assigned permission
    assert Permissions.GRIEVANCES_CREATE.value in user.permissions_in_business_area(business_area_afg.slug)

    # Create "Role with all permissions" - UNICEF HQ gets these automatically
    role_with_all_permissions, created = Role.objects.get_or_create(
        name="Role with all permissions", subsystem="HOPE", defaults={"permissions": []}
    )
    permissions = [
        Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST,
        Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
    ]
    role_with_all_permissions.permissions = [permission.value for permission in permissions]
    role_with_all_permissions.save()

    # UNICEF HQ user should have all these permissions automatically
    for permission in permissions:
        assert permission.value in user.permissions_in_business_area(business_area_afg.slug)

    # Permission not in any role should not be present
    assert Permissions.GRIEVANCES_UPDATE.value not in user.permissions_in_business_area(business_area_afg.slug)


def test_unicef_partner_per_ba_has_permission_from_user_and_role_with_default_permissions(
    business_area_afg: BusinessArea,
):
    # Create UNICEF partner structure for specific business area
    partner = PartnerFactory(name="UNICEF")
    unicef_in_afg = PartnerFactory(name=f"UNICEF Partner for {business_area_afg.slug}", parent=partner)
    user = UserFactory(partner=unicef_in_afg)

    # Create role with specific permission
    role = RoleFactory(name="111", permissions=[Permissions.GRIEVANCES_CREATE.value])
    RoleAssignment.objects.create(
        role=role,
        business_area=business_area_afg,
        user=user,
        partner=None,
    )

    # User should have the assigned permission
    assert Permissions.GRIEVANCES_CREATE.value in user.permissions_in_business_area(business_area_afg.slug)

    # UNICEF partner (non-HQ) should have default UNICEF partner permissions
    for permission in DEFAULT_PERMISSIONS_IS_UNICEF_PARTNER:
        assert permission.value in user.permissions_in_business_area(business_area_afg.slug)

    # Permission not assigned should not be present
    assert Permissions.GRIEVANCES_UPDATE.value not in user.permissions_in_business_area(business_area_afg.slug)
