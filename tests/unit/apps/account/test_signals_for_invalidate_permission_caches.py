"""Tests for signals that invalidate permission caches."""

from datetime import timedelta
from typing import Any

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
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
from hope.apps.account.caches import get_user_permissions_version_key
from hope.models import BusinessArea, Partner, Program, Role, RoleAssignment, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area_afg(db: Any) -> BusinessArea:
    return BusinessAreaFactory(
        slug="afghanistan",
        code="0060",
        name="Afghanistan",
    )


@pytest.fixture
def partner1(db: Any) -> Partner:
    return PartnerFactory(name="Partner")


@pytest.fixture
def partner2(db: Any) -> Partner:
    return PartnerFactory(name="Partner 2")


@pytest.fixture
def user1_partner1(partner1: Partner) -> User:
    return UserFactory(partner=partner1)


@pytest.fixture
def user2_partner1(partner1: Partner) -> User:
    return UserFactory(partner=partner1)


@pytest.fixture
def user1_partner2(partner2: Partner) -> User:
    return UserFactory(partner=partner2)


@pytest.fixture
def user2_partner2(partner2: Partner) -> User:
    return UserFactory(partner=partner2)


@pytest.fixture
def role1(db: Any) -> Role:
    return RoleFactory(name="Role 1")


@pytest.fixture
def role2(db: Any) -> Role:
    return RoleFactory(name="Role 2")


@pytest.fixture
def program(business_area_afg: BusinessArea) -> Program:
    return ProgramFactory(
        status=Program.DRAFT,
        business_area=business_area_afg,
        partner_access=Program.SELECTED_PARTNERS_ACCESS,
    )


@pytest.fixture
def role_assignment1(user1_partner1: User, role1: Role, business_area_afg: BusinessArea) -> RoleAssignment:
    return RoleAssignmentFactory(
        user=user1_partner1,
        partner=None,
        role=role1,
        business_area=business_area_afg,
    )


@pytest.fixture
def role_assignment2(user1_partner2: User, role1: Role, business_area_afg: BusinessArea) -> RoleAssignment:
    return RoleAssignmentFactory(
        user=user1_partner2,
        partner=None,
        role=role1,
        business_area=business_area_afg,
    )


@pytest.fixture
def role_assignment3(partner1: Partner, role2: Role, business_area_afg: BusinessArea) -> RoleAssignment:
    return RoleAssignmentFactory(
        user=None,
        partner=partner1,
        role=role2,
        business_area=business_area_afg,
    )


@pytest.fixture
def content_type(db: Any) -> ContentType:
    return ContentType.objects.get_for_model(BusinessArea)


@pytest.fixture
def group1(user1_partner1: User, content_type: ContentType) -> Group:
    # Group on a user
    group = Group.objects.create(name="Test Group")
    permission = Permission.objects.create(
        codename="test_permission",
        name="Test Permission",
        content_type=content_type,
    )
    group.permissions.add(permission)
    user1_partner1.groups.add(group)
    return group


@pytest.fixture
def group2(role_assignment2: RoleAssignment, content_type: ContentType) -> Group:
    # Group on a user's role assignment
    group = Group.objects.create(name="Test Group 2")
    role_assignment2.group = group
    role_assignment2.save()
    return group


@pytest.fixture
def group3(role_assignment3: RoleAssignment, content_type: ContentType) -> Group:
    # Group on a partner's role assignment
    group = Group.objects.create(name="Test Group 3")
    role_assignment3.group = group
    role_assignment3.save()
    return group


@pytest.fixture
def cache_versions_before(
    user1_partner1: User,
    user2_partner1: User,
    user1_partner2: User,
    user2_partner2: User,
    role_assignment1: RoleAssignment,
    role_assignment2: RoleAssignment,
    role_assignment3: RoleAssignment,
    group1: Group,
    group2: Group,
    group3: Group,
):
    # Ensure all setup is complete and get initial cache versions
    return {
        "user1_partner1": get_cache_version(user1_partner1),
        "user2_partner1": get_cache_version(user2_partner1),
        "user1_partner2": get_cache_version(user1_partner2),
        "user2_partner2": get_cache_version(user2_partner2),
    }


def get_cache_version(user: User) -> int:
    version_key = get_user_permissions_version_key(user)
    return cache.get(version_key)


def test_invalidate_cache_on_user_change(
    user1_partner1: User,
    user2_partner1: User,
    user1_partner2: User,
    user2_partner2: User,
    partner2: Partner,
    cache_versions_before: dict,
):
    user1_partner1.is_superuser = True
    user1_partner1.save()
    assert get_cache_version(user1_partner1) == cache_versions_before["user1_partner1"] + 1

    user1_partner1.partner = partner2
    user1_partner1.save()
    assert get_cache_version(user1_partner1) == cache_versions_before["user1_partner1"] + 2

    # No invalidation for the rest of the users
    assert get_cache_version(user1_partner2) == cache_versions_before["user1_partner2"]
    assert get_cache_version(user2_partner1) == cache_versions_before["user2_partner1"]
    assert get_cache_version(user2_partner2) == cache_versions_before["user2_partner2"]


def test_invalidate_cache_on_role_change_for_user(
    role1: Role,
    user1_partner1: User,
    user2_partner1: User,
    user1_partner2: User,
    user2_partner2: User,
    cache_versions_before: dict,
):
    role1.permissions = ["PROGRAMME_CREATE", "PROGRAMME_FINISH"]
    role1.save()

    # Users with role_assignments connected to the role should have their cache invalidated
    assert get_cache_version(user1_partner1) == cache_versions_before["user1_partner1"] + 1
    assert get_cache_version(user1_partner2) == cache_versions_before["user1_partner2"] + 1

    # No invalidation for the rest of the users
    assert get_cache_version(user2_partner1) == cache_versions_before["user2_partner1"]
    assert get_cache_version(user2_partner2) == cache_versions_before["user2_partner2"]


def test_invalidate_cache_on_role_change_for_partner(
    role2: Role,
    user1_partner1: User,
    user2_partner1: User,
    user1_partner2: User,
    user2_partner2: User,
    cache_versions_before: dict,
):
    role2.permissions = ["PROGRAMME_CREATE", "PROGRAMME_FINISH"]
    role2.save()

    # Users with partner's role_assignments connected to the role should have their cache invalidated
    assert get_cache_version(user1_partner1) == cache_versions_before["user1_partner1"] + 1
    assert get_cache_version(user2_partner1) == cache_versions_before["user2_partner1"] + 1

    # No invalidation for the rest of the users
    assert get_cache_version(user1_partner2) == cache_versions_before["user1_partner2"]
    assert get_cache_version(user2_partner2) == cache_versions_before["user2_partner2"]


def test_invalidate_cache_on_group_permissions_change_for_user(
    group1: Group,
    content_type: ContentType,
    user1_partner1: User,
    user2_partner1: User,
    user1_partner2: User,
    user2_partner2: User,
    cache_versions_before: dict,
):
    permission = Permission.objects.create(
        codename="test_permission_new_1",
        name="Test Permission 2",
        content_type=content_type,
    )
    group1.permissions.add(permission)

    # Users connected with the group should have their cache invalidated
    assert get_cache_version(user1_partner1) == cache_versions_before["user1_partner1"] + 1

    # No invalidation for the rest of the users
    assert get_cache_version(user2_partner1) == cache_versions_before["user2_partner1"]
    assert get_cache_version(user1_partner2) == cache_versions_before["user1_partner2"]
    assert get_cache_version(user2_partner2) == cache_versions_before["user2_partner2"]

    # Remove permission from the group
    group1.permissions.remove(permission)

    # Users connected with the group should have their cache invalidated
    assert get_cache_version(user1_partner1) == cache_versions_before["user1_partner1"] + 2

    # No invalidation for the rest of the users
    assert get_cache_version(user2_partner1) == cache_versions_before["user2_partner1"]
    assert get_cache_version(user1_partner2) == cache_versions_before["user1_partner2"]
    assert get_cache_version(user2_partner2) == cache_versions_before["user2_partner2"]


def test_invalidate_cache_on_group_permissions_change_for_user_role_assignment(
    group2: Group,
    content_type: ContentType,
    user1_partner1: User,
    user2_partner1: User,
    user1_partner2: User,
    user2_partner2: User,
    cache_versions_before: dict,
):
    permission = Permission.objects.create(
        codename="test_permission_new_2",
        name="Test Permission 2",
        content_type=content_type,
    )
    group2.permissions.add(permission)

    # Users with role_assignments connected with the group should have their cache invalidated
    assert get_cache_version(user1_partner2) == cache_versions_before["user1_partner2"] + 1

    # No invalidation for the rest of the users
    assert get_cache_version(user1_partner1) == cache_versions_before["user1_partner1"]
    assert get_cache_version(user2_partner1) == cache_versions_before["user2_partner1"]
    assert get_cache_version(user2_partner2) == cache_versions_before["user2_partner2"]

    # Remove permission from the group
    group2.permissions.remove(permission)

    # Users with role_assignments connected with the group should have their cache invalidated
    assert get_cache_version(user1_partner2) == cache_versions_before["user1_partner2"] + 2

    # No invalidation for the rest of the users
    assert get_cache_version(user1_partner1) == cache_versions_before["user1_partner1"]
    assert get_cache_version(user2_partner1) == cache_versions_before["user2_partner1"]
    assert get_cache_version(user2_partner2) == cache_versions_before["user2_partner2"]


def test_invalidate_cache_on_group_permissions_change_for_partner_role_assignment(
    group3: Group,
    content_type: ContentType,
    user1_partner1: User,
    user2_partner1: User,
    user1_partner2: User,
    user2_partner2: User,
    cache_versions_before: dict,
):
    permission = Permission.objects.create(
        codename="test_permission_new_3",
        name="Test Permission 2",
        content_type=content_type,
    )
    group3.permissions.add(permission)

    # Users with partner with role_assignments connected with the group should have their cache invalidated
    assert get_cache_version(user1_partner1) == cache_versions_before["user1_partner1"] + 1
    assert get_cache_version(user2_partner1) == cache_versions_before["user2_partner1"] + 1

    # No invalidation for the rest of the users
    assert get_cache_version(user1_partner2) == cache_versions_before["user1_partner2"]
    assert get_cache_version(user2_partner2) == cache_versions_before["user2_partner2"]

    # Remove permission from the group
    group3.permissions.remove(permission)

    # Users with partner with role_assignments connected with the group should have their cache invalidated
    assert get_cache_version(user1_partner1) == cache_versions_before["user1_partner1"] + 2
    assert get_cache_version(user2_partner1) == cache_versions_before["user2_partner1"] + 2

    # No invalidation for the rest of the users
    assert get_cache_version(user1_partner2) == cache_versions_before["user1_partner2"]
    assert get_cache_version(user2_partner2) == cache_versions_before["user2_partner2"]


def test_invalidate_cache_on_group_change_for_user(
    group1: Group,
    user1_partner1: User,
    user2_partner1: User,
    user1_partner2: User,
    user2_partner2: User,
    cache_versions_before: dict,
):
    user1_partner1.groups.remove(group1)

    # User with changed group should have their cache invalidated
    assert get_cache_version(user1_partner1) == cache_versions_before["user1_partner1"] + 1

    # No invalidation for the rest of the users
    assert get_cache_version(user2_partner1) == cache_versions_before["user2_partner1"]
    assert get_cache_version(user1_partner2) == cache_versions_before["user1_partner2"]
    assert get_cache_version(user2_partner2) == cache_versions_before["user2_partner2"]


def test_invalidate_cache_on_group_delete_for_user(
    group1: Group,
    user1_partner1: User,
    user2_partner1: User,
    user1_partner2: User,
    user2_partner2: User,
    cache_versions_before: dict,
):
    group1.delete()

    # Users connected with the group should have their cache invalidated
    assert get_cache_version(user1_partner1) == cache_versions_before["user1_partner1"] + 1

    # No invalidation for the rest of the users
    assert get_cache_version(user2_partner1) == cache_versions_before["user2_partner1"]
    assert get_cache_version(user1_partner2) == cache_versions_before["user1_partner2"]
    assert get_cache_version(user2_partner2) == cache_versions_before["user2_partner2"]


def test_invalidate_cache_on_group_delete_for_user_role_assignment(
    group2: Group,
    user1_partner1: User,
    user2_partner1: User,
    user1_partner2: User,
    user2_partner2: User,
    cache_versions_before: dict,
):
    group2.delete()

    # Users with role_assignments connected with the group should have their cache invalidated
    # Increased by additional 2 signals:
    # * signal on the RoleAssignment
    # * signal on User update triggered because of cascade delete of the RoleAssignment
    assert get_cache_version(user1_partner2) == cache_versions_before["user1_partner2"] + 3

    # No invalidation for the rest of the users
    assert get_cache_version(user1_partner1) == cache_versions_before["user1_partner1"]
    assert get_cache_version(user2_partner1) == cache_versions_before["user2_partner1"]
    assert get_cache_version(user2_partner2) == cache_versions_before["user2_partner2"]


def test_invalidate_cache_on_group_delete_for_partner_role_assignment(
    group3: Group,
    user1_partner1: User,
    user2_partner1: User,
    user1_partner2: User,
    user2_partner2: User,
    cache_versions_before: dict,
):
    group3.delete()

    # Users with partner with role_assignments connected with the group should have their cache invalidated
    # Increased by 2 because of the signal on the RoleAssignment as well
    assert get_cache_version(user1_partner1) == cache_versions_before["user1_partner1"] + 2
    assert get_cache_version(user2_partner1) == cache_versions_before["user2_partner1"] + 2

    # No invalidation for the rest of the users
    assert get_cache_version(user1_partner2) == cache_versions_before["user1_partner2"]
    assert get_cache_version(user2_partner2) == cache_versions_before["user2_partner2"]


def test_invalidate_cache_on_role_assignment_change_for_user(
    role_assignment1: RoleAssignment,
    role2: Role,
    group3: Group,
    user1_partner1: User,
    user2_partner1: User,
    user1_partner2: User,
    user2_partner2: User,
    cache_versions_before: dict,
):
    role_assignment1.expiry_date = (timezone.now() - timedelta(days=1)).date()
    role_assignment1.save()

    role_assignment1.group = group3
    role_assignment1.save()

    role_assignment1.role = role2
    role_assignment1.save()

    # Users connected to the role_assignment should have their cache invalidated
    # +6: 3 signals on RoleAssignment and 3 signals on User to update modify_date because of role_assignment change
    assert get_cache_version(user1_partner1) == cache_versions_before["user1_partner1"] + 6

    # No invalidation for the rest of the users
    assert get_cache_version(user2_partner1) == cache_versions_before["user2_partner1"]
    assert get_cache_version(user1_partner2) == cache_versions_before["user1_partner2"]
    assert get_cache_version(user2_partner2) == cache_versions_before["user2_partner2"]


def test_invalidate_cache_on_role_assignment_change_for_partner(
    role_assignment3: RoleAssignment,
    role1: Role,
    program: Program,
    user1_partner1: User,
    user2_partner1: User,
    user1_partner2: User,
    user2_partner2: User,
    cache_versions_before: dict,
):
    role_assignment3.expiry_date = (timezone.now() - timedelta(days=1)).date()
    role_assignment3.save()

    role_assignment3.program = program
    role_assignment3.save()

    role_assignment3.role = role1
    role_assignment3.save()

    # Users with partner connected to the role_assignment should have their cache invalidated
    assert get_cache_version(user1_partner1) == cache_versions_before["user1_partner1"] + 3
    assert get_cache_version(user2_partner1) == cache_versions_before["user2_partner1"] + 3

    # No invalidation for the rest of the users
    assert get_cache_version(user1_partner2) == cache_versions_before["user1_partner2"]
    assert get_cache_version(user2_partner2) == cache_versions_before["user2_partner2"]
