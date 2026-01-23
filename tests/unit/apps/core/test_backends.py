from typing import Any
from unittest.mock import patch

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PartnerFactory,
    ProgramFactory,
    RoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)
from hope.apps.core.backends import PermissionsBackend
from hope.models import BusinessArea, Program


def get_permission_name(permission: Permission) -> str:
    return f"{permission.content_type.app_label}.{permission.codename}"


@pytest.fixture
def business_area(db):
    return BusinessAreaFactory()


@pytest.fixture
def partner(db):
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def user(partner):
    return UserFactory(partner=partner)


@pytest.fixture
def content_type(db):
    return ContentType.objects.get_for_model(BusinessArea)


@pytest.fixture
def permission(content_type):
    return Permission.objects.create(
        codename="test_permission",
        name="Test Permission",
        content_type=content_type,
    )


@pytest.fixture
def group(permission):
    group = Group.objects.create(name="TestGroup")
    group.permissions.add(permission)
    return group


@pytest.fixture
def program(business_area):
    return ProgramFactory(
        status=Program.ACTIVE,
        name="Test Program",
        business_area=business_area,
    )


@pytest.fixture
def role_assignment_user(user, business_area):
    return RoleAssignmentFactory(
        user=user,
        business_area=business_area,
        role=None,
        partner=None,
    )


@pytest.fixture
def role_assignment_partner(partner, business_area):
    partner.allowed_business_areas.add(business_area)
    return RoleAssignmentFactory(
        partner=partner,
        business_area=business_area,
        role=None,
        user=None,
    )


@pytest.fixture
def backend():
    return PermissionsBackend()


def test_get_all_permissions_caches_result(
    backend,
    user,
    business_area,
    group,
    permission,
    role_assignment_user,
    role_assignment_partner,
    django_assert_num_queries,
):
    group.permissions.add(permission)
    user.groups.add(group)

    with django_assert_num_queries(4):
        permissions = backend.get_all_permissions(user, business_area)
    with django_assert_num_queries(0):
        cached_permissions = backend.get_all_permissions(user, business_area)

    assert permissions == cached_permissions


@patch("hope.apps.core.backends.cache.get")
def test_cache_get_returns_cached_permissions(mock_cache_get: Any, backend, user, business_area, permission):
    mock_cache_get.return_value = {get_permission_name(permission)}
    permissions = backend.get_all_permissions(user, business_area)
    mock_cache_get.assert_called()
    assert mock_cache_get.call_count == 2
    assert get_permission_name(permission) in permissions


def test_user_group_permissions_included(
    backend, user, business_area, group, permission, role_assignment_user, role_assignment_partner
):
    group.permissions.add(permission)
    user.groups.add(group)

    permissions = backend.get_all_permissions(user, business_area)

    assert get_permission_name(permission) in permissions


def test_role_assignment_user_role_permissions(backend, user, business_area, role_assignment_user):
    role = RoleFactory(name="Role for User", permissions=["PROGRAMME_CREATE", "PROGRAMME_UPDATE"])
    role_assignment_user.role = role
    role_assignment_user.save()

    permissions = backend.get_all_permissions(user, business_area)

    assert "PROGRAMME_CREATE" in permissions
    assert "PROGRAMME_UPDATE" in permissions


def test_role_assignment_user_group_permissions(backend, user, business_area, group, permission, role_assignment_user):
    role_assignment_user.group = group
    role_assignment_user.save()

    permissions = backend.get_all_permissions(user, business_area)

    assert get_permission_name(permission) in permissions


def test_role_assignment_partner_role_permissions(backend, user, business_area, role_assignment_partner):
    role = RoleFactory(name="Role for Partner", permissions=["PROGRAMME_FINISH"])
    role_assignment_partner.role = role
    role_assignment_partner.save()

    permissions = backend.get_all_permissions(user, business_area)

    assert "PROGRAMME_FINISH" in permissions


def test_role_assignment_partner_group_permissions(
    backend, user, business_area, group, permission, role_assignment_partner
):
    role_assignment_partner.group = group
    role_assignment_partner.save()

    permissions = backend.get_all_permissions(user, business_area)

    assert get_permission_name(permission) in permissions


def test_superuser_has_all_permissions(backend, user, content_type, permission, program):
    user.is_superuser = True
    user.save()

    assert backend.has_perm(user, f"{content_type.app_label}.{permission.codename}")
    assert backend.has_perm(user, "PROGRAMME_FINISH", program)


def test_expired_role_assignment_excludes_permissions(
    backend, user, business_area, group, permission, role_assignment_user
):
    role_assignment_user.group = group
    role_assignment_user.save()

    permissions = backend.get_all_permissions(user, business_area)
    assert get_permission_name(permission) in permissions

    role_assignment_user.expiry_date = timezone.now() - timezone.timedelta(days=1)
    role_assignment_user.save()

    permissions = backend.get_all_permissions(user, business_area)
    assert get_permission_name(permission) not in permissions


def test_partner_role_assignment_grants_permission_for_specific_program(
    backend, user, business_area, program, role_assignment_partner
):
    role = RoleFactory(name="Role for Partner", permissions=["PROGRAMME_FINISH"])
    role_assignment_partner.role = role
    role_assignment_partner.program = program
    role_assignment_partner.save()

    permissions = backend.get_all_permissions(user, program)

    assert "PROGRAMME_FINISH" in permissions


def test_no_permissions_for_program_without_role_assignment(backend, user, business_area):
    program_other = ProgramFactory(
        status=Program.ACTIVE,
        name="Test Program Other",
        business_area=business_area,
    )

    permissions = backend.get_all_permissions(user, program_other)

    assert set() == permissions


def test_user_role_assignment_grants_permission_for_specific_program(
    backend, user, business_area, role_assignment_user
):
    program_empty = ProgramFactory(
        status=Program.ACTIVE,
        name="Test Program Empty",
        business_area=business_area,
    )
    role = RoleFactory(name="Role for User", permissions=["PROGRAMME_CREATE", "PROGRAMME_UPDATE"])
    role_assignment_user.role = role
    role_assignment_user.program = program_empty
    role_assignment_user.save()

    permissions = backend.get_all_permissions(user, program_empty)

    assert "PROGRAMME_CREATE" in permissions
    assert "PROGRAMME_UPDATE" in permissions


def test_partner_loses_permission_when_assigned_to_different_program(
    backend, user, business_area, program, role_assignment_partner
):
    program_other = ProgramFactory(
        status=Program.ACTIVE,
        name="Test Program Other",
        business_area=business_area,
    )
    role = RoleFactory(name="Role for Partner", permissions=["PROGRAMME_FINISH"])
    role_assignment_partner.role = role
    role_assignment_partner.program = program
    role_assignment_partner.save()

    permissions_in_program = backend.get_all_permissions(user, program)
    assert "PROGRAMME_FINISH" in permissions_in_program

    role_assignment_partner.program = program_other
    role_assignment_partner.save()

    permissions_in_program = backend.get_all_permissions(user, program)
    assert set() == permissions_in_program

    permissions_in_other = backend.get_all_permissions(user, program_other)
    assert "PROGRAMME_FINISH" in permissions_in_other


def test_user_loses_permission_when_assigned_to_different_program(backend, user, business_area, role_assignment_user):
    program_a = ProgramFactory(
        status=Program.ACTIVE,
        name="Test Program A",
        business_area=business_area,
    )
    program_b = ProgramFactory(
        status=Program.ACTIVE,
        name="Test Program B",
        business_area=business_area,
    )
    role = RoleFactory(name="Role for User", permissions=["PROGRAMME_CREATE"])
    role_assignment_user.role = role
    role_assignment_user.program = program_a
    role_assignment_user.save()

    permissions_a = backend.get_all_permissions(user, program_a)
    assert "PROGRAMME_CREATE" in permissions_a

    role_assignment_user.program = program_b
    role_assignment_user.save()

    permissions_a = backend.get_all_permissions(user, program_a)
    assert set() == permissions_a

    permissions_b = backend.get_all_permissions(user, program_b)
    assert "PROGRAMME_CREATE" in permissions_b


def test_partner_with_null_program_has_access_to_all_programs(
    backend, user, business_area, program, role_assignment_partner
):
    program_other = ProgramFactory(
        status=Program.ACTIVE,
        name="Test Program Other",
        business_area=business_area,
    )
    role = RoleFactory(name="Role for Partner", permissions=["PROGRAMME_FINISH"])
    role_assignment_partner.role = role
    role_assignment_partner.program = None
    role_assignment_partner.save()

    permissions_in_program = backend.get_all_permissions(user, program)
    assert "PROGRAMME_FINISH" in permissions_in_program

    permissions_in_other = backend.get_all_permissions(user, program_other)
    assert "PROGRAMME_FINISH" in permissions_in_other


def test_user_with_null_program_has_access_to_all_programs(backend, user, business_area, program, role_assignment_user):
    program_other = ProgramFactory(
        status=Program.ACTIVE,
        name="Test Program Other",
        business_area=business_area,
    )
    role = RoleFactory(name="Role for User", permissions=["PROGRAMME_CREATE", "PROGRAMME_UPDATE"])
    role_assignment_user.role = role
    role_assignment_user.program = None
    role_assignment_user.save()

    permissions_in_program = backend.get_all_permissions(user, program)
    assert "PROGRAMME_CREATE" in permissions_in_program
    assert "PROGRAMME_UPDATE" in permissions_in_program

    permissions_in_other = backend.get_all_permissions(user, program_other)
    assert "PROGRAMME_CREATE" in permissions_in_other
    assert "PROGRAMME_UPDATE" in permissions_in_other


def test_outside_ba_permissions_only_from_user_group(backend, user, content_type):
    permission1 = Permission.objects.create(
        codename="test_permission1",
        name="Test Permission 1",
        content_type=content_type,
    )
    group_user = Group.objects.create(name="TestGroupUser")
    group_user.permissions.add(permission1)
    user.groups.add(group_user)

    permissions = backend.get_all_permissions(user)

    assert {get_permission_name(permission1)} == permissions


def test_permissions_for_business_area_from_all_sources(
    backend,
    user,
    business_area,
    content_type,
    role_assignment_user,
    role_assignment_partner,
):
    permission1 = Permission.objects.create(
        codename="test_permission1",
        name="Test Permission 1",
        content_type=content_type,
    )
    permission2 = Permission.objects.create(
        codename="test_permission2",
        name="Test Permission 2",
        content_type=content_type,
    )
    permission3 = Permission.objects.create(
        codename="test_permission3",
        name="Test Permission 3",
        content_type=content_type,
    )

    group_user = Group.objects.create(name="TestGroupUser")
    group_user.permissions.add(permission1)
    user.groups.add(group_user)

    group_role_assignment_user = Group.objects.create(name="TestGroupRoleAssignmentUser")
    group_role_assignment_user.permissions.add(permission2)
    role_assignment_user.group = group_role_assignment_user
    role_assignment_user.save()

    group_role_assignment_partner = Group.objects.create(name="TestGroupRoleAssignmentPartner")
    group_role_assignment_partner.permissions.add(permission3)
    role_assignment_partner.group = group_role_assignment_partner
    role_assignment_partner.save()

    role_user = RoleFactory(name="Test Role User", permissions=["PROGRAMME_CREATE"])
    role_assignment_user.role = role_user
    role_assignment_user.save()

    role_partner = RoleFactory(name="Test Role Partner", permissions=["PROGRAMME_FINISH"])
    role_assignment_partner.role = role_partner
    role_assignment_partner.save()

    permissions = backend.get_all_permissions(user, business_area)

    assert get_permission_name(permission1) in permissions
    assert get_permission_name(permission2) in permissions
    assert get_permission_name(permission3) in permissions
    assert "PROGRAMME_CREATE" in permissions
    assert "PROGRAMME_FINISH" in permissions


def test_no_permissions_for_other_business_area(backend, user):
    business_area_other = BusinessAreaFactory()

    permissions = backend.get_all_permissions(user, business_area_other)

    assert set() == permissions


def test_program_permissions_from_partner_role_assignment(
    backend, user, business_area, program, content_type, role_assignment_partner
):
    permission1 = Permission.objects.create(
        codename="test_permission1",
        name="Test Permission 1",
        content_type=content_type,
    )
    permission3 = Permission.objects.create(
        codename="test_permission3",
        name="Test Permission 3",
        content_type=content_type,
    )

    group_user = Group.objects.create(name="TestGroupUser")
    group_user.permissions.add(permission1)
    user.groups.add(group_user)

    group_role_assignment_partner = Group.objects.create(name="TestGroupRoleAssignmentPartner")
    group_role_assignment_partner.permissions.add(permission3)
    role_assignment_partner.group = group_role_assignment_partner
    role_assignment_partner.program = program
    role_assignment_partner.save()

    role_partner = RoleFactory(name="Test Role Partner", permissions=["PROGRAMME_FINISH"])
    role_assignment_partner.role = role_partner
    role_assignment_partner.save()

    permissions = backend.get_all_permissions(user, program)

    assert get_permission_name(permission1) in permissions
    assert get_permission_name(permission3) in permissions
    assert "PROGRAMME_FINISH" in permissions


def test_program_permissions_from_user_role_assignment(
    backend, user, business_area, content_type, role_assignment_user
):
    program_for_user = ProgramFactory(
        status=Program.ACTIVE,
        name="Test Program For User",
        business_area=business_area,
    )
    permission1 = Permission.objects.create(
        codename="test_permission1",
        name="Test Permission 1",
        content_type=content_type,
    )
    permission2 = Permission.objects.create(
        codename="test_permission2",
        name="Test Permission 2",
        content_type=content_type,
    )

    group_user = Group.objects.create(name="TestGroupUser")
    group_user.permissions.add(permission1)
    user.groups.add(group_user)

    group_role_assignment_user = Group.objects.create(name="TestGroupRoleAssignmentUser")
    group_role_assignment_user.permissions.add(permission2)
    role_assignment_user.group = group_role_assignment_user
    role_assignment_user.program = program_for_user
    role_assignment_user.save()

    role_user = RoleFactory(name="Test Role User", permissions=["PROGRAMME_CREATE"])
    role_assignment_user.role = role_user
    role_assignment_user.save()

    permissions = backend.get_all_permissions(user, program_for_user)

    assert get_permission_name(permission1) in permissions
    assert get_permission_name(permission2) in permissions
    assert "PROGRAMME_CREATE" in permissions


def test_no_permissions_for_program_without_any_role_assignment(
    backend, user, business_area, role_assignment_user, role_assignment_partner
):
    program_for_user = ProgramFactory(
        status=Program.ACTIVE,
        name="Test Program For User",
        business_area=business_area,
    )
    role_assignment_user.program = program_for_user
    role_assignment_user.save()

    role_assignment_partner.program = ProgramFactory(
        status=Program.ACTIVE,
        name="Test Program For Partner",
        business_area=business_area,
    )
    role_assignment_partner.save()

    program_other = ProgramFactory(
        status=Program.ACTIVE,
        name="Test Program Other",
        business_area=business_area,
    )

    permissions = backend.get_all_permissions(user, program_other)

    assert set() == permissions
