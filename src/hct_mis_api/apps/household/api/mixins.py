from typing import Any

from rest_framework.exceptions import PermissionDenied


class CreatorOrOwnerPermissionMixin:
    def check_creator_or_owner_permission(
        self,
        user: Any,
        scope: Any,
        general_permission: str,
        is_creator: bool,
        creator_permission: str,
        is_owner: bool,
        owner_permission: str,
    ) -> None:
        if not user.is_authenticated or not (
            user.has_perm(general_permission, scope)
            or (is_creator and user.has_perm(creator_permission, scope))
            or (is_owner and user.has_perm(owner_permission, scope))
        ):
            raise PermissionDenied()
