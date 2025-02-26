from typing import Any

from rest_framework.permissions import BasePermission

from hct_mis_api.apps.account.permissions import check_permissions


class BaseRestPermission(BasePermission):
    """
    Base class for custom permissions.
    """

    ONE_OF_PERMISSIONS: bool

    def _get_permissions(self, view: Any) -> Any:
        if hasattr(view, "permissions_by_action") and view.action in view.permissions_by_action:
            return view.permissions_by_action[view.action]
        return view.PERMISSIONS

    def has_permission(self, request: Any, view: Any) -> bool:
        user = request.user
        permissions = self._get_permissions(view)
        kwargs = {
            "business_area": request.parser_context.get("kwargs", {}).get("business_area"),
            "Program": request.parser_context.get("kwargs", {}).get("program_id"),
        }

        return check_permissions(user, permissions, one_of_permissions=self.ONE_OF_PERMISSIONS, **kwargs)


class HasAllOfPermissions(BaseRestPermission):
    """
    Check if user has all of the permissions in the PERMISSIONS list
    """

    ONE_OF_PERMISSIONS = False


class HasOneOfPermissions(BaseRestPermission):
    """
    Check if user has at least one of the permissions in the PERMISSIONS list
    """

    ONE_OF_PERMISSIONS = True
