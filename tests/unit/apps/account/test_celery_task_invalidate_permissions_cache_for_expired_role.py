"""Tests for account celery tasks."""

from datetime import timedelta
from typing import Any
from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase
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
from hope.apps.account.celery_tasks import (
    invalidate_permissions_cache_for_user_if_expired_role_async_task,
    invalidate_permissions_cache_for_user_if_expired_role_async_task_action,
)
from hope.apps.account.signals import _invalidate_user_permissions_cache
from hope.models import AsyncJob, BusinessArea, Partner, Program, Role, RoleAssignment, User

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
def role_for_user_1(db: Any) -> Role:
    return RoleFactory(name="Test User Role 1")


@pytest.fixture
def role_for_user_2(db: Any) -> Role:
    return RoleFactory(name="Test User Role 2")


@pytest.fixture
def role_for_partner(db: Any) -> Role:
    return RoleFactory(name="Test Partner Role")


@pytest.fixture
def role_assignment_user1(user1: User, business_area_afg: BusinessArea, role_for_user_1: Role) -> RoleAssignment:
    return RoleAssignmentFactory(
        user=user1,
        partner=None,
        business_area=business_area_afg,
        role=role_for_user_1,
    )


@pytest.fixture
def role_assignment_ok_user1(user1: User, business_area_afg: BusinessArea, role_for_user_2: Role) -> RoleAssignment:
    return RoleAssignmentFactory(
        user=user1,
        partner=None,
        business_area=business_area_afg,
        role=role_for_user_2,
    )


@pytest.fixture
def role_assignment_user2(user2: User, business_area_afg: BusinessArea, role_for_user_1: Role) -> RoleAssignment:
    return RoleAssignmentFactory(
        user=user2,
        partner=None,
        business_area=business_area_afg,
        role=role_for_user_1,
    )


@pytest.fixture
def role_assignment_partner(
    partner: Partner,
    business_area_afg: BusinessArea,
    role_for_partner: Role,
) -> RoleAssignment:
    return RoleAssignmentFactory(
        user=None,
        partner=partner,
        business_area=business_area_afg,
        role=role_for_partner,
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


@pytest.fixture
def async_job() -> RoleAssignment:
    return AsyncJob.objects.create(
        type="JOB_TASK",
        action="hope.apps.account.celery_tasks.invalidate_permissions_cache_for_user_if_expired_role_async_task_action",
        config={},
    )


def get_cache_version(user: User) -> int:
    version_key = get_user_permissions_version_key(user)
    return cache.get(version_key, 0)


@patch("hope.apps.account.celery_tasks._invalidate_user_permissions_cache")
def test_invalidate_permissions_cache_role_on_user_action(
    mock_invalidate_cache: Any,
    user1: User,
    user2: User,
    role_assignment_user1: RoleAssignment,
    async_job: AsyncJob,
    cache_versions_before: dict,
):
    mock_invalidate_cache.side_effect = _invalidate_user_permissions_cache
    with TestCase.captureOnCommitCallbacks(execute=True):
        invalidate_permissions_cache_for_user_if_expired_role_async_task_action()
    mock_invalidate_cache.assert_called_once()
    affected_users = list(mock_invalidate_cache.call_args[0][0])
    assert len(affected_users) == 0
    assert get_cache_version(user1) == cache_versions_before["user1"]
    assert get_cache_version(user2) == cache_versions_before["user2"]

    with TestCase.captureOnCommitCallbacks(execute=True):
        role_assignment_user1.expiry_date = (timezone.now() - timedelta(days=1)).date()
        role_assignment_user1.save()

    version_key_user1_after_update = get_cache_version(user1)
    assert version_key_user1_after_update == cache_versions_before["user1"] + 2

    with TestCase.captureOnCommitCallbacks(execute=True):
        result = invalidate_permissions_cache_for_user_if_expired_role_async_task_action()
    assert len(mock_invalidate_cache.call_args_list) == 2  # called second time now
    affected_users = mock_invalidate_cache.call_args[0][0]  # users from most recent call

    assert len(affected_users) == 1
    assert user1 in affected_users
    assert result is True

    assert get_cache_version(user1) == version_key_user1_after_update + 1
    assert get_cache_version(user2) == cache_versions_before["user2"]


@patch("hope.apps.account.celery_tasks._invalidate_user_permissions_cache")
def test_invalidate_permissions_cache_role_on_users_action(
    mock_invalidate_cache: Any,
    user1: User,
    user2: User,
    role_assignment_user1: RoleAssignment,
    role_assignment_user2: RoleAssignment,
    async_job: AsyncJob,
    cache_versions_before: dict,
):
    mock_invalidate_cache.side_effect = _invalidate_user_permissions_cache
    with TestCase.captureOnCommitCallbacks(execute=True):
        role_assignment_user1.expiry_date = (timezone.now() - timedelta(days=1)).date()
        role_assignment_user1.save()
        role_assignment_user2.expiry_date = (timezone.now() - timedelta(days=1)).date()
        role_assignment_user2.save()

    version_key_user1_after_update = get_cache_version(user1)
    version_key_user2_after_update = get_cache_version(user2)

    assert version_key_user1_after_update == cache_versions_before["user1"] + 2
    assert version_key_user2_after_update == cache_versions_before["user2"] + 2

    with TestCase.captureOnCommitCallbacks(execute=True):
        result = invalidate_permissions_cache_for_user_if_expired_role_async_task_action()
    mock_invalidate_cache.assert_called_once()
    affected_users = mock_invalidate_cache.call_args[0][0]

    assert len(affected_users) == 2
    assert user1 in affected_users
    assert user2 in affected_users
    assert result is True

    assert get_cache_version(user1) == version_key_user1_after_update + 1
    assert get_cache_version(user2) == version_key_user2_after_update + 1


@patch("hope.apps.account.celery_tasks._invalidate_user_permissions_cache")
def test_invalidate_permissions_cache_role_action_keeps_existing_errors_on_success(
    mock_invalidate_cache: Any,
    async_job: AsyncJob,
) -> None:
    mock_invalidate_cache.side_effect = _invalidate_user_permissions_cache
    async_job.errors = {"exception": "previous failure", "partial": "keep me"}
    async_job.save(update_fields=["errors"])

    result = invalidate_permissions_cache_for_user_if_expired_role_async_task_action(async_job)

    async_job.refresh_from_db()
    assert result is True
    assert async_job.errors == {"exception": "previous failure", "partial": "keep me"}


@patch("hope.apps.account.celery_tasks._invalidate_user_permissions_cache")
def test_invalidate_permissions_cache_role_action_failure_does_not_set_job_errors(
    mock_invalidate_cache: Any,
    async_job: AsyncJob,
) -> None:
    mock_invalidate_cache.side_effect = RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        invalidate_permissions_cache_for_user_if_expired_role_async_task_action(async_job)

    async_job.refresh_from_db()
    assert async_job.errors == {}


@patch("hope.apps.account.celery_tasks._invalidate_user_permissions_cache")
def test_invalidate_permissions_cache_role_on_partner_action(
    mock_invalidate_cache: Any,
    user1: User,
    user2: User,
    role_assignment_partner: RoleAssignment,
    async_job: AsyncJob,
    cache_versions_before: dict,
):
    mock_invalidate_cache.side_effect = _invalidate_user_permissions_cache
    with TestCase.captureOnCommitCallbacks(execute=True):
        role_assignment_partner.expiry_date = (timezone.now() - timedelta(days=1)).date()
        role_assignment_partner.save()
    version_key_user1_before = cache_versions_before["user1"] + 1  # Increased version from signal

    with TestCase.captureOnCommitCallbacks(execute=True):
        result = invalidate_permissions_cache_for_user_if_expired_role_async_task_action()
    mock_invalidate_cache.assert_called_once()
    affected_users = mock_invalidate_cache.call_args[0][0]

    assert len(affected_users) == 1
    assert user1 in affected_users
    assert result is True

    assert get_cache_version(user1) == version_key_user1_before + 1
    assert get_cache_version(user2) == cache_versions_before["user2"]


@patch("hope.apps.account.celery_tasks._invalidate_user_permissions_cache")
def test_invalidate_permissions_cache_role_on_users_and_partner_action(
    mock_invalidate_cache: Any,
    user1: User,
    user2: User,
    role_assignment_user1: RoleAssignment,
    role_assignment_user2: RoleAssignment,
    role_assignment_partner: RoleAssignment,
    async_job: AsyncJob,
    cache_versions_before: dict,
):
    mock_invalidate_cache.side_effect = _invalidate_user_permissions_cache
    with TestCase.captureOnCommitCallbacks(execute=True):
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

    with TestCase.captureOnCommitCallbacks(execute=True):
        result = invalidate_permissions_cache_for_user_if_expired_role_async_task_action()
    mock_invalidate_cache.assert_called_once()
    affected_users = mock_invalidate_cache.call_args[0][0]

    assert len(affected_users) == 2
    assert user1 in affected_users
    assert user2 in affected_users
    assert result is True

    assert get_cache_version(user1) == version_key_user1_after_update + 1
    assert get_cache_version(user2) == version_key_user2_after_update + 1


@patch.object(AsyncJob, "queue")
def test_invalidate_permissions_cache_role_task_schedules_async_job(mock_queue: Any) -> None:
    result = invalidate_permissions_cache_for_user_if_expired_role_async_task()

    job = AsyncJob.objects.get()

    assert result is True
    assert job.owner is None
    assert job.type == "JOB_TASK"
    assert (
        job.action
        == "hope.apps.account.celery_tasks.invalidate_permissions_cache_for_user_if_expired_role_async_task_action"
    )
    assert job.config == {}
    assert job.group_key == "invalidate_permissions_cache_for_user_if_expired_role_async_task"
    assert job.description == "Invalidate permissions cache for users with expired roles"
    mock_queue.assert_called_once_with()
