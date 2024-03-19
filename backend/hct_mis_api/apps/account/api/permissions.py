from typing import Type

from hct_mis_api.apps.account.permissions import Permissions, check_permissions
from hct_mis_api.apps.core.utils import get_program_id_from_headers


class BaseRestPermission:
    def has_permission(self, request, view) -> bool:
        return False


def hopeRestPermissionClass(permission: Permissions) -> Type[BaseRestPermission]:
    class PermissionClass(BaseRestPermission):
        def has_permission(self, request, view) -> bool:
            user = request.user
            permissions = [permission]
            return check_permissions(user, permissions, **request.headers)

    return PermissionClass


def hopeRestPermissionNoGPFClass(permission: Permissions) -> Type[BaseRestPermission]:
    class PermissionClass(BaseRestPermission):
        def has_permission(self, request, view) -> bool:
            user = request.user
            permissions = [permission]
            if get_program_id_from_headers(request.headers):
                return True
            return check_permissions(user, permissions, **request.headers)

    return PermissionClass
