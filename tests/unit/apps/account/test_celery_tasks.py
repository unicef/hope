from datetime import timedelta
from typing import Any
from unittest.mock import patch

import pytest
from django.core.cache import cache
from django.utils import timezone
from extras.test_utils.factories.account import (
    BusinessAreaFactory,
    PartnerFactory,
    RoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)
from extras.test_utils.factories.program import ProgramFactory

from hope.apps.account.caches import get_user_permissions_version_key
from hope.apps.account.celery_tasks import (
    invalidate_permissions_cache_for_user_if_expired_role,
)
from hope.apps.account.models import User
from hope.apps.account.signals import _invalidate_user_permissions_cache
from hope.apps.program.models import Program

pytestmark = pytest.mark.django_db()


class TestInvalidatePermissionsCacheForUserIfExpiredRoleTask:
    @pytest.fixture(autouse=True)
    def set_up(self, afghanistan: BusinessAreaFactory) -> None:
        self.partner = PartnerFactory(name="TestPartner")
        self.user1 = UserFactory(partner=self.partner)
        self.user2 = UserFactory(partner=None)
        self.afghanistan = afghanistan
        self.program = ProgramFactory(status=Program.ACTIVE, name="Test Program", business_area=self.afghanistan)
        role1 = RoleFactory(name="Test Expired Role")
        role2 = RoleFactory(name="Test OK Role")
        role3 = RoleFactory(name="Test Partner Expired Role")

        self.role_assignment_user1 = RoleAssignmentFactory(
            user=self.user1,
            business_area=self.afghanistan,
            role=role1,
        )
        self.role_assignment_ok_user1 = RoleAssignmentFactory(
            user=self.user1,
            business_area=self.afghanistan,
            role=role2,
        )
        self.role_assignment_user2 = RoleAssignmentFactory(
            user=self.user2,
            business_area=self.afghanistan,
            role=None,
        )
        self.partner.allowed_business_areas.add(self.afghanistan)
        self.role_assignment_partner = RoleAssignmentFactory(
            partner=self.partner,
            business_area=self.afghanistan,
            role=role3,
        )

        self.version_key_user1_before = self._get_cache_version(self.user1)
        self.version_key_user2_before = self._get_cache_version(self.user2)

    @patch("hope.apps.account.celery_tasks._invalidate_user_permissions_cache")
    def test_invalidate_permissions_cache_role_on_user(self, mock_invalidate_cache: Any) -> None:
        mock_invalidate_cache.side_effect = _invalidate_user_permissions_cache
        invalidate_permissions_cache_for_user_if_expired_role()
        mock_invalidate_cache.assert_called_once()
        affected_users = list(mock_invalidate_cache.call_args[0][0])
        assert len(affected_users) == 0
        assert self._get_cache_version(self.user1) == self.version_key_user1_before
        assert self._get_cache_version(self.user2) == self.version_key_user2_before

        self.role_assignment_user1.expiry_date = (timezone.now() - timedelta(days=1)).date()
        self.role_assignment_user1.save()

        version_key_user1_after_update = self._get_cache_version(self.user1)
        assert version_key_user1_after_update == self.version_key_user1_before + 2

        result = invalidate_permissions_cache_for_user_if_expired_role()
        assert len(mock_invalidate_cache.call_args_list) == 2  # called second time now
        affected_users = mock_invalidate_cache.call_args[0][0]  # users from most recent call

        assert len(affected_users) == 1
        assert self.user1 in affected_users
        assert result is True

        assert self._get_cache_version(self.user1) == version_key_user1_after_update + 1
        assert self._get_cache_version(self.user2) == self.version_key_user2_before

    @patch("hope.apps.account.celery_tasks._invalidate_user_permissions_cache")
    def test_invalidate_permissions_cache_role_on_users(self, mock_invalidate_cache: Any) -> None:
        mock_invalidate_cache.side_effect = _invalidate_user_permissions_cache
        self.role_assignment_user1.expiry_date = (timezone.now() - timedelta(days=1)).date()
        self.role_assignment_user1.save()
        self.role_assignment_user2.expiry_date = (timezone.now() - timedelta(days=1)).date()
        self.role_assignment_user2.save()

        version_key_user1_after_update = self._get_cache_version(self.user1)
        version_key_user2_after_update = self._get_cache_version(self.user2)

        assert version_key_user1_after_update == self.version_key_user1_before + 2
        assert version_key_user2_after_update == self.version_key_user2_before + 2
        # increased by additional 2 signals:
        # * signal on the  RoleAssignment
        # * signal on User update triggered because of cascade delete of the RoleAssignment

        result = invalidate_permissions_cache_for_user_if_expired_role()
        mock_invalidate_cache.assert_called_once()
        affected_users = mock_invalidate_cache.call_args[0][0]

        assert len(affected_users) == 2
        assert self.user1 in affected_users
        assert self.user2 in affected_users
        assert result is True

        assert self._get_cache_version(self.user1) == version_key_user1_after_update + 1
        assert self._get_cache_version(self.user2) == version_key_user2_after_update + 1

    @patch("hope.apps.account.celery_tasks._invalidate_user_permissions_cache")
    def test_invalidate_permissions_cache_role_on_partner(self, mock_invalidate_cache: Any) -> None:
        mock_invalidate_cache.side_effect = _invalidate_user_permissions_cache
        self.role_assignment_partner.expiry_date = (timezone.now() - timedelta(days=1)).date()
        self.role_assignment_partner.save()
        self.version_key_user1_before += 1  # increased version from signal

        result = invalidate_permissions_cache_for_user_if_expired_role()
        mock_invalidate_cache.assert_called_once()
        affected_users = mock_invalidate_cache.call_args[0][0]

        assert len(affected_users) == 1
        assert self.user1 in affected_users
        assert result is True

        assert self._get_cache_version(self.user1) == self.version_key_user1_before + 1
        assert self._get_cache_version(self.user2) == self.version_key_user2_before

    @patch("hope.apps.account.celery_tasks._invalidate_user_permissions_cache")
    def test_invalidate_permissions_cache_role_on_users_and_partner(self, mock_invalidate_cache: Any) -> None:
        mock_invalidate_cache.side_effect = _invalidate_user_permissions_cache
        self.role_assignment_partner.expiry_date = (timezone.now() - timedelta(days=1)).date()
        self.role_assignment_partner.save()
        self.role_assignment_user1.expiry_date = (timezone.now() - timedelta(days=1)).date()
        self.role_assignment_user1.save()
        self.role_assignment_user2.expiry_date = (timezone.now() - timedelta(days=1)).date()
        self.role_assignment_user2.save()

        self.version_key_user1_before += 1  # increased version from signal on partner

        version_key_user1_after_update = self._get_cache_version(self.user1)
        version_key_user2_after_update = self._get_cache_version(self.user2)
        assert version_key_user1_after_update == self.version_key_user1_before + 2
        assert version_key_user2_after_update == self.version_key_user2_before + 2

        result = invalidate_permissions_cache_for_user_if_expired_role()
        mock_invalidate_cache.assert_called_once()
        affected_users = mock_invalidate_cache.call_args[0][0]

        assert len(affected_users) == 2
        assert self.user1 in affected_users
        assert self.user2 in affected_users
        assert result is True

        assert self._get_cache_version(self.user1) == version_key_user1_after_update + 1
        assert self._get_cache_version(self.user2) == version_key_user2_after_update + 1

    def _get_cache_version(self, user: User) -> int:
        version_key = get_user_permissions_version_key(user)
        return cache.get(version_key)
