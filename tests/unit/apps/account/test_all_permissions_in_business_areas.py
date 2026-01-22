"""Tests for user all_permissions_in_business_areas method."""

from datetime import timezone as dt_timezone
from typing import Any
from unittest.mock import patch

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PartnerFactory,
    RoleFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, Partner, Program, Role, RoleAssignment, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area_afg(db: Any) -> BusinessArea:
    return BusinessAreaFactory(
        slug="afghanistan",
        code="0060",
        name="Afghanistan",
        active=True,
    )


@pytest.fixture
def business_area_ukr(db: Any) -> BusinessArea:
    return BusinessAreaFactory(
        slug="ukraine",
        code="4410",
        name="Ukraine",
        active=True,
    )


@pytest.fixture
def role_rdi(db: Any) -> Role:
    return RoleFactory(
        name="RDI Role Test",
        permissions=[Permissions.RDI_VIEW_LIST.value, Permissions.RDI_VIEW_DETAILS.value],
    )


@pytest.fixture
def role_program(db: Any) -> Role:
    return RoleFactory(
        name="Program Role Test",
        permissions=[Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS.value, Permissions.PROGRAMME_CREATE.value],
    )


@pytest.fixture
def partner(db: Any) -> Partner:
    return PartnerFactory(name="Test Partner")


@pytest.fixture
def user(partner: Partner) -> User:
    return UserFactory(partner=partner)


def clear_user_cache(user: User):
    if hasattr(user, "_all_permissions_in_business_areas"):
        delattr(user, "_all_permissions_in_business_areas")
    if hasattr(user, "_program_ids_for_business_area_cache"):
        delattr(user, "_program_ids_for_business_area_cache")


def test_basic_functionality(
    user: User,
    business_area_afg: BusinessArea,
    business_area_ukr: BusinessArea,
    role_rdi: Role,
    role_program: Role,
):
    # Create role assignments for user in different business areas
    RoleAssignment.objects.create(
        role=role_rdi,
        business_area=business_area_afg,
        user=user,
        partner=None,
    )
    RoleAssignment.objects.create(
        role=role_program,
        business_area=business_area_ukr,
        user=user,
        partner=None,
    )

    clear_user_cache(user)
    permissions = user.all_permissions_in_business_areas

    # Check Afghanistan permissions
    afg_permissions = permissions[str(business_area_afg.id)]
    assert Permissions.RDI_VIEW_LIST.value in afg_permissions
    assert Permissions.RDI_VIEW_DETAILS.value in afg_permissions
    assert Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS.value not in afg_permissions

    # Check Ukraine permissions
    ukr_permissions = permissions[str(business_area_ukr.id)]
    assert Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS.value in ukr_permissions
    assert Permissions.PROGRAMME_CREATE.value in ukr_permissions
    assert Permissions.RDI_VIEW_LIST.value not in ukr_permissions


def test_multiple_roles_same_business_area(
    user: User,
    business_area_afg: BusinessArea,
    role_rdi: Role,
    role_program: Role,
):
    # Create multiple role assignments in same business area
    RoleAssignment.objects.create(
        role=role_rdi,
        business_area=business_area_afg,
        user=user,
        partner=None,
    )
    RoleAssignment.objects.create(
        role=role_program,
        business_area=business_area_afg,
        user=user,
        partner=None,
    )

    clear_user_cache(user)
    permissions = user.all_permissions_in_business_areas
    afg_permissions = permissions[str(business_area_afg.id)]

    # Should have permissions from both roles
    assert Permissions.RDI_VIEW_LIST.value in afg_permissions
    assert Permissions.RDI_VIEW_DETAILS.value in afg_permissions
    assert Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS.value in afg_permissions
    assert Permissions.PROGRAMME_CREATE.value in afg_permissions


def test_excludes_expired_roles(
    user: User,
    business_area_afg: BusinessArea,
    role_rdi: Role,
    role_program: Role,
):
    # Create active role assignment
    RoleAssignment.objects.create(
        role=role_rdi,
        business_area=business_area_afg,
        user=user,
        partner=None,
    )

    # Create expired role assignment
    expired_date = timezone.now().date() - timezone.timedelta(days=1)
    RoleAssignment.objects.create(
        role=role_program,
        business_area=business_area_afg,
        user=user,
        partner=None,
        expiry_date=expired_date,
    )

    clear_user_cache(user)
    permissions = user.all_permissions_in_business_areas
    afg_permissions = permissions[str(business_area_afg.id)]

    # Should only have permissions from active role
    assert Permissions.RDI_VIEW_LIST.value in afg_permissions
    assert Permissions.RDI_VIEW_DETAILS.value in afg_permissions
    assert Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS.value not in afg_permissions
    assert Permissions.PROGRAMME_CREATE.value not in afg_permissions


def test_includes_future_expiry_roles(
    user: User,
    business_area_afg: BusinessArea,
    role_rdi: Role,
):
    # Create role assignment with future expiry date
    future_date = timezone.now().date() + timezone.timedelta(days=30)
    RoleAssignment.objects.create(
        role=role_rdi,
        business_area=business_area_afg,
        user=user,
        partner=None,
        expiry_date=future_date,
    )

    clear_user_cache(user)
    permissions = user.all_permissions_in_business_areas
    afg_permissions = permissions[str(business_area_afg.id)]

    # Should have permissions from role with future expiry
    assert Permissions.RDI_VIEW_LIST.value in afg_permissions
    assert Permissions.RDI_VIEW_DETAILS.value in afg_permissions


def test_includes_no_expiry_roles(
    user: User,
    business_area_afg: BusinessArea,
    role_rdi: Role,
):
    # Create role assignment with no expiry
    RoleAssignment.objects.create(
        role=role_rdi,
        business_area=business_area_afg,
        user=user,
        partner=None,
        expiry_date=None,
    )

    clear_user_cache(user)
    permissions = user.all_permissions_in_business_areas
    afg_permissions = permissions[str(business_area_afg.id)]

    # Should have permissions from role with no expiry
    assert Permissions.RDI_VIEW_LIST.value in afg_permissions
    assert Permissions.RDI_VIEW_DETAILS.value in afg_permissions


def test_empty_for_no_roles():
    # User with no role assignments
    partner = PartnerFactory(name="Test Partner Empty")
    user = UserFactory(partner=partner)

    permissions = user.all_permissions_in_business_areas

    # Should be empty dict
    assert permissions == {}


def test_with_partner_roles(
    user: User,
    partner: Partner,
    business_area_afg: BusinessArea,
    role_rdi: Role,
    role_program: Role,
):
    # Add business area to partner's allowed business areas
    partner.allowed_business_areas.add(business_area_afg)

    # User role assignment
    RoleAssignment.objects.create(
        role=role_rdi,
        business_area=business_area_afg,
        user=user,
        partner=None,
    )

    # Partner role assignment
    RoleAssignment.objects.create(
        role=role_program,
        business_area=business_area_afg,
        user=None,
        partner=partner,
    )

    clear_user_cache(user)
    permissions = user.all_permissions_in_business_areas
    afg_permissions = permissions[str(business_area_afg.id)]

    # Should have permissions from both user and partner roles
    assert Permissions.RDI_VIEW_LIST.value in afg_permissions
    assert Permissions.RDI_VIEW_DETAILS.value in afg_permissions
    assert Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS.value in afg_permissions
    assert Permissions.PROGRAMME_CREATE.value in afg_permissions


def test_with_django_groups(
    user: User,
    business_area_afg: BusinessArea,
    role_rdi: Role,
):
    # Create Django group with permissions
    content_type = ContentType.objects.get_for_model(Program)

    # Try to get existing permission first
    program_permission, _ = Permission.objects.get_or_create(
        codename="view_program",
        content_type=content_type,
        defaults={"name": "Can view program"},
    )

    # Create unique group name with timestamp to avoid conflicts
    import time

    group_name = f"Program Viewers Test {int(time.time())}"
    django_group = Group.objects.create(name=group_name)
    django_group.permissions.add(program_permission)

    # Role assignment with Django group
    RoleAssignment.objects.create(
        role=role_rdi,
        business_area=business_area_afg,
        user=user,
        partner=None,
        group=django_group,
    )

    clear_user_cache(user)
    permissions = user.all_permissions_in_business_areas
    afg_permissions = permissions[str(business_area_afg.id)]

    # Should have role permissions
    assert Permissions.RDI_VIEW_LIST.value in afg_permissions
    assert Permissions.RDI_VIEW_DETAILS.value in afg_permissions

    # Should have Django group permissions
    assert "program.view_program" in afg_permissions


def test_return_types(
    user: User,
    business_area_afg: BusinessArea,
    role_rdi: Role,
):
    RoleAssignment.objects.create(
        role=role_rdi,
        business_area=business_area_afg,
        user=user,
        partner=None,
    )

    permissions = user.all_permissions_in_business_areas

    # Should return dict
    assert isinstance(permissions, dict)

    # Keys should be strings (business area IDs)
    for key in permissions:
        assert isinstance(key, str)

    # Values should be sets of strings (permissions)
    for value in permissions.values():
        assert isinstance(value, set)
        for permission in value:
            assert isinstance(permission, str)


def test_caching_behavior(
    user: User,
    business_area_afg: BusinessArea,
    role_rdi: Role,
):
    RoleAssignment.objects.create(
        role=role_rdi,
        business_area=business_area_afg,
        user=user,
        partner=None,
    )

    # First call should execute query
    permissions1 = user.all_permissions_in_business_areas

    # Second call should use cached result
    permissions2 = user.all_permissions_in_business_areas

    # Should be the same object (cached)
    assert permissions1 is permissions2

    # Should have correct permissions
    afg_permissions = permissions1[str(business_area_afg.id)]
    assert Permissions.RDI_VIEW_LIST.value in afg_permissions


@patch("hope.models.user.timezone.now")
def test_expiry_date_edge_case(
    mock_now,
    user: User,
    business_area_afg: BusinessArea,
    role_rdi: Role,
):
    # Set current time - beginning of next day so that today's date is < timezone.now()
    current_time = timezone.datetime(2024, 1, 16, 0, 0, 1, tzinfo=dt_timezone.utc)
    mock_now.return_value = current_time

    # Role assignment expiring yesterday (should be excluded)
    yesterday = timezone.datetime(2024, 1, 15, 0, 0, 0, tzinfo=dt_timezone.utc).date()
    RoleAssignment.objects.create(
        role=role_rdi,
        business_area=business_area_afg,
        user=user,
        partner=None,
        expiry_date=yesterday,
    )

    clear_user_cache(user)
    permissions = user.all_permissions_in_business_areas

    # Role expiring yesterday should NOT be included (expiry_date < timezone.now())
    assert len(permissions) == 0
