"""Tests for account celery tasks."""

from datetime import timedelta
from typing import Any
from unittest.mock import patch

from django.core.cache import cache
from django.utils import timezone
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PartnerFactory,
    ProgramFactory,
    RoleFactory,
    UserFactory,
)
from hope.apps.account.caches import get_user_permissions_version_key
from hope.apps.account.celery_tasks import (
    invalidate_permissions_cache_for_user_if_expired_role,
)
from hope.apps.account.signals import _invalidate_user_permissions_cache
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
def partner(db: Any) -> Partner:
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def user1(partner: Partner) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def user2(db: Any) -> User:
    return UserFactory(partner=None)


@pytest.fixture
def program(business_area_afg: BusinessArea) -> Program:
    return ProgramFactory(
        status=Program.ACTIVE,
        name="Test Program",
        business_area=business_area_afg,
    )


@pytest.fixture
def role_expired(db: Any) -> Role:
    return RoleFactory(name="Test Expired Role")


@pytest.fixture
def role_ok(db: Any) -> Role:
    return RoleFactory(name="Test OK Role")


@pytest.fixture
def role_partner_expired(db: Any) -> Role:
    return RoleFactory(name="Test Partner Expired Role")


@pytest.fixture
def role_assignment_user1(user1: User, business_area_afg: BusinessArea, role_expired: Role) -> RoleAssignment:
    return RoleAssignment.objects.create(
        user=user1,
        partner=None,
        business_area=business_area_afg,
        role=role_expired,
    )


@pytest.fixture
def role_assignment_ok_user1(user1: User, business_area_afg: BusinessArea, role_ok: Role) -> RoleAssignment:
    return RoleAssignment.objects.create(
        user=user1,
        partner=None,
        business_area=business_area_afg,
        role=role_ok,
    )


@pytest.fixture
def role_assignment_user2(user2: User, business_area_afg: BusinessArea) -> RoleAssignment:
    return RoleAssignment.objects.create(
        user=user2,
        partner=None,
        business_area=business_area_afg,
        role=None,
    )


@pytest.fixture
def role_assignment_partner(
    partner: Partner,
    business_area_afg: BusinessArea,
    role_partner_expired: Role,
) -> RoleAssignment:
    partner.allowed_business_areas.add(business_area_afg)
    return RoleAssignment.objects.create(
        user=None,
        partner=partner,
        business_area=business_area_afg,
        role=role_partner_expired,
    )


@pytest.fixture
def cache_versions_before(
    user1: User,
    user2: User,
    role_assignment_user1: RoleAssignment,
    role_assignment_ok_user1: RoleAssignment,
    role_assignment_user2: RoleAssignment,
    role_assignment_partner: RoleAssignment,
):
    # Ensure all setup is complete and get initial cache versions
    return {
        "user1": get_cache_version(user1),
        "user2": get_cache_version(user2),
    }


def get_cache_version(user: User) -> int:
    version_key = get_user_permissions_version_key(user)
    return cache.get(version_key)


@patch("hope.apps.account.celery_tasks._invalidate_user_permissions_cache")
def test_invalidate_permissions_cache_role_on_user(
    mock_invalidate_cache: Any,
    user1: User,
    user2: User,
    role_assignment_user1: RoleAssignment,
    cache_versions_before: dict,
):
    mock_invalidate_cache.side_effect = _invalidate_user_permissions_cache
    invalidate_permissions_cache_for_user_if_expired_role()
    mock_invalidate_cache.assert_called_once()
    affected_users = list(mock_invalidate_cache.call_args[0][0])
    assert len(affected_users) == 0
    assert get_cache_version(user1) == cache_versions_before["user1"]
    assert get_cache_version(user2) == cache_versions_before["user2"]

    role_assignment_user1.expiry_date = (timezone.now() - timedelta(days=1)).date()
    role_assignment_user1.save()

    version_key_user1_after_update = get_cache_version(user1)
    assert version_key_user1_after_update == cache_versions_before["user1"] + 2

    result = invalidate_permissions_cache_for_user_if_expired_role()
    assert len(mock_invalidate_cache.call_args_list) == 2  # called second time now
    affected_users = mock_invalidate_cache.call_args[0][0]  # users from most recent call

    assert len(affected_users) == 1
    assert user1 in affected_users
    assert result is True

    assert get_cache_version(user1) == version_key_user1_after_update + 1
    assert get_cache_version(user2) == cache_versions_before["user2"]


@patch("hope.apps.account.celery_tasks._invalidate_user_permissions_cache")
def test_invalidate_permissions_cache_role_on_users(
    mock_invalidate_cache: Any,
    user1: User,
    user2: User,
    role_assignment_user1: RoleAssignment,
    role_assignment_user2: RoleAssignment,
    cache_versions_before: dict,
):
    mock_invalidate_cache.side_effect = _invalidate_user_permissions_cache
    role_assignment_user1.expiry_date = (timezone.now() - timedelta(days=1)).date()
    role_assignment_user1.save()
    role_assignment_user2.expiry_date = (timezone.now() - timedelta(days=1)).date()
    role_assignment_user2.save()

    version_key_user1_after_update = get_cache_version(user1)
    version_key_user2_after_update = get_cache_version(user2)

    assert version_key_user1_after_update == cache_versions_before["user1"] + 2
    assert version_key_user2_after_update == cache_versions_before["user2"] + 2

    result = invalidate_permissions_cache_for_user_if_expired_role()
    mock_invalidate_cache.assert_called_once()
    affected_users = mock_invalidate_cache.call_args[0][0]

    assert len(affected_users) == 2
    assert user1 in affected_users
    assert user2 in affected_users
    assert result is True

    assert get_cache_version(user1) == version_key_user1_after_update + 1
    assert get_cache_version(user2) == version_key_user2_after_update + 1


@patch("hope.apps.account.celery_tasks._invalidate_user_permissions_cache")
def test_invalidate_permissions_cache_role_on_partner(
    mock_invalidate_cache: Any,
    user1: User,
    user2: User,
    role_assignment_partner: RoleAssignment,
    cache_versions_before: dict,
):
    mock_invalidate_cache.side_effect = _invalidate_user_permissions_cache
    role_assignment_partner.expiry_date = (timezone.now() - timedelta(days=1)).date()
    role_assignment_partner.save()
    version_key_user1_before = cache_versions_before["user1"] + 1  # Increased version from signal

    result = invalidate_permissions_cache_for_user_if_expired_role()
    mock_invalidate_cache.assert_called_once()
    affected_users = mock_invalidate_cache.call_args[0][0]

    assert len(affected_users) == 1
    assert user1 in affected_users
    assert result is True

    assert get_cache_version(user1) == version_key_user1_before + 1
    assert get_cache_version(user2) == cache_versions_before["user2"]


@patch("hope.apps.account.celery_tasks._invalidate_user_permissions_cache")
def test_invalidate_permissions_cache_role_on_users_and_partner(
    mock_invalidate_cache: Any,
    user1: User,
    user2: User,
    role_assignment_user1: RoleAssignment,
    role_assignment_user2: RoleAssignment,
    role_assignment_partner: RoleAssignment,
    cache_versions_before: dict,
):
    mock_invalidate_cache.side_effect = _invalidate_user_permissions_cache
    role_assignment_partner.expiry_date = (timezone.now() - timedelta(days=1)).date()
    role_assignment_partner.save()
    role_assignment_user1.expiry_date = (timezone.now() - timedelta(days=1)).date()
    role_assignment_user1.save()
    role_assignment_user2.expiry_date = (timezone.now() - timedelta(days=1)).date()
    role_assignment_user2.save()

    version_key_user1_before = cache_versions_before["user1"] + 1  # Increased version from signal on partner

    version_key_user1_after_update = get_cache_version(user1)
    version_key_user2_after_update = get_cache_version(user2)
    assert version_key_user1_after_update == version_key_user1_before + 2
    assert version_key_user2_after_update == cache_versions_before["user2"] + 2

    result = invalidate_permissions_cache_for_user_if_expired_role()
    mock_invalidate_cache.assert_called_once()
    affected_users = mock_invalidate_cache.call_args[0][0]

    assert len(affected_users) == 2
    assert user1 in affected_users
    assert user2 in affected_users
    assert result is True

    assert get_cache_version(user1) == version_key_user1_after_update + 1
    assert get_cache_version(user2) == version_key_user2_after_update + 1

