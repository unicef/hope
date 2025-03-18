from typing import Any

from rest_framework.permissions import BasePermission

from hct_mis_api.apps.account.permissions import check_permissions


class BaseRestPermission(BasePermission):
    """
    Base class for custom permissions.
    """

    def _get_permissions(self, view: Any) -> Any:
        if hasattr(view, "permissions_by_action"):
            if view.action in view.permissions_by_action:
                return view.permissions_by_action[view.action]
            elif view.action == "count":
                return view.permissions_by_action["list"]
        return view.PERMISSIONS

    def has_permission(self, request: Any, view: Any) -> bool:
        user = request.user
        permissions = self._get_permissions(view)
        kwargs = {
            "business_area": request.parser_context.get("kwargs", {}).get("business_area_slug"),
            "program": request.parser_context.get("kwargs", {}).get("program_slug"),
            "Program": request.parser_context.get("kwargs", {}).get("program_id"),  # TODO: GraphQL - remove at the end
        }

        return check_permissions(user, permissions, **kwargs)
