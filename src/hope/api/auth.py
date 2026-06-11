from typing import TYPE_CHECKING, Any

from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import SAFE_METHODS, BasePermission, IsAuthenticated
from rest_framework.request import Request

from hope.models import User
from hope.models.business_area import ALL_EXCEPT_CW_INGEST_REJECT_MSG, CW_ONLY_INGEST_REJECT_MSG

if TYPE_CHECKING:
    from hope.models import APIToken


class HOPEAuthentication(TokenAuthentication):
    keyword = "Token"

    def authenticate_credentials(self, key: str) -> tuple[User, "APIToken"]:
        from hope.models import APIToken

        try:
            token = (
                APIToken.objects.select_related("user")
                .filter(valid_from__lte=timezone.now())
                .filter(Q(valid_to__gte=timezone.now()) | Q(valid_to__isnull=True))
                .get(key=key)
            )
        except APIToken.DoesNotExist:
            raise exceptions.AuthenticationFailed(_("Invalid token."))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_("User inactive or deleted."))

        return (token.user, token)


class HOPEPermission(IsAuthenticated):
    def has_permission(self, request: Request, view: Any) -> bool:
        if bool(request.auth):
            if view.permission == "any":
                return True
            if view.permission:
                return view.permission.name in request.auth.grants
        return False


class BusinessAreaIngestCWOnlyPermission(BasePermission):
    message = CW_ONLY_INGEST_REJECT_MSG

    def has_permission(self, request: Request, view: Any) -> bool:
        return view.selected_business_area.is_rdi_ingest_source_country_workspace_only


class BusinessAreaIngestAllExceptCWPermission(BasePermission):
    message = ALL_EXCEPT_CW_INGEST_REJECT_MSG

    def has_permission(self, request: Request, view: Any) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return not view.business_area.is_rdi_ingest_source_country_workspace_only
