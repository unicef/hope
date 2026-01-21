from unittest.mock import patch

import pytest
from rest_framework.exceptions import PermissionDenied

from extras.test_utils.old_factories.account import UserFactory
from hope.apps.account.api.permissions import BaseRestPermission
from hope.apps.account.permissions import Permissions


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


class TestBaseRestPermission:
    @patch("hope.apps.account.api.permissions.check_permissions", return_value=False)
    def test_permission_denied_includes_required_permissions(self, mock_check_permissions):
        user = UserFactory()
        perms = [Permissions.PM_VIEW_LIST, Permissions.PM_CREATE]
        view = DummyView(perms)
        request = DummyRequest(user)

        with pytest.raises(PermissionDenied) as excinfo:
            BaseRestPermission().has_permission(request, view)

        assert mock_check_permissions.called
        detail = excinfo.value.detail
        assert detail["required_permissions"] == [p.value for p in perms]
        assert detail["detail"] == "You do not have permission to perform this action."

    @patch("hope.apps.account.api.permissions.check_permissions", return_value=True)
    def test_permission_allowed(self, mock_check_permissions):
        user = UserFactory()
        view = DummyView([Permissions.PM_VIEW_LIST])
        request = DummyRequest(user)

        assert BaseRestPermission().has_permission(request, view) is True
        assert mock_check_permissions.called
