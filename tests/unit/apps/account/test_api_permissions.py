"""Tests for BaseRestPermission class."""

from typing import Any
from unittest.mock import patch

import pytest
from rest_framework.exceptions import PermissionDenied

from extras.test_utils.factories import UserFactory
from hope.apps.account.api.permissions import BaseRestPermission
from hope.apps.account.permissions import Permissions
from hope.models import User

pytestmark = pytest.mark.django_db


class DummyView:
    def __init__(self, perms):
        self._perms = perms

    def get_permissions_for_action(self):
        return self._perms


class DummyRequest:
    def __init__(self, user):
        self.user = user
        self.parser_context = {"kwargs": {}}
        self.query_params = {}


@pytest.fixture
def user(db: Any) -> User:
    return UserFactory()


@pytest.fixture
def dummy_view_with_permissions() -> DummyView:
    perms = [Permissions.PM_VIEW_LIST, Permissions.PM_CREATE]
    return DummyView(perms)


@pytest.fixture
def dummy_view_single_permission() -> DummyView:
    return DummyView([Permissions.PM_VIEW_LIST])


@pytest.fixture
def dummy_request(user: User) -> DummyRequest:
    return DummyRequest(user)


@patch("hope.apps.account.api.permissions.check_permissions", return_value=False)
def test_permission_denied_includes_required_permissions(
    mock_check_permissions, user: User, dummy_view_with_permissions: DummyView, dummy_request: DummyRequest
):
    perms = [Permissions.PM_VIEW_LIST, Permissions.PM_CREATE]

    with pytest.raises(PermissionDenied) as excinfo:
        BaseRestPermission().has_permission(dummy_request, dummy_view_with_permissions)

    assert mock_check_permissions.called
    detail = excinfo.value.detail
    assert detail["required_permissions"] == [p.value for p in perms]
    assert detail["detail"] == "You do not have permission to perform this action."


@patch("hope.apps.account.api.permissions.check_permissions", return_value=True)
def test_permission_allowed(
    mock_check_permissions, user: User, dummy_view_single_permission: DummyView, dummy_request: DummyRequest
):
    result = BaseRestPermission().has_permission(dummy_request, dummy_view_single_permission)

    assert result is True
    assert mock_check_permissions.called
