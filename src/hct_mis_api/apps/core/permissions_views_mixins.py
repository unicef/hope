from typing import Any

from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest

from hct_mis_api.apps.account.permissions import Permissions


class ViewPermissionsMixinBase(AccessMixin):
    def has_permissions(self) -> bool:
        raise NotImplementedError()

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not self.has_permissions():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class UploadFilePermissionMixin(ViewPermissionsMixinBase):
    def has_permissions(self) -> bool:
        roles = self.request.user.user_roles.all()

        return any(
            self.request.user.has_permission(Permissions.UPLOAD_STORAGE_FILE.name, role.business_area) for role in roles
        )
