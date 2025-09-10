from typing import Any

from rest_framework.permissions import BasePermission

from hope.apps.account.permissions import check_permissions


class BaseRestPermission(BasePermission):
    """Base class for custom permissions."""

    def has_permission(self, request: Any, view: Any) -> bool:
        user = request.user
        permissions = view.get_permissions_for_action()
        kwargs = {
            "business_area": request.parser_context.get("kwargs", {}).get("business_area_slug"),
            "program": request.parser_context.get("kwargs", {}).get("program_slug"),
            "Program": request.parser_context.get("kwargs", {}).get("program_id"),  # TODO: GraphQL - remove at the end
        }

        return check_permissions(user, permissions, **kwargs)
