from typing import TYPE_CHECKING, Any

from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q
from django.http import Http404
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import SAFE_METHODS, BasePermission, IsAuthenticated
from rest_framework.request import Request

from hope.models import User
from hope.models.business_area import ALL_EXCEPT_CW_INGEST_REJECT_MSG, CW_ONLY_INGEST_REJECT_MSG

if TYPE_CHECKING:
    from hope.models import APIToken, BusinessArea


def _view_business_area(view: Any) -> "BusinessArea":
    """Resolve the business area the ingest permissions should check.

    The token API resolves it from the token scope (`selected_business_area`, see
    `SelectedBusinessAreaMixin`), the internal API from the URL or the program
    (`business_area`, see `BusinessAreaMixin` / `ProgramMixin`). Prefer the
    token-scoped one: it is the stricter source.
    """
    for attr in ("selected_business_area", "business_area"):
        if (business_area := getattr(view, attr, None)) is not None:
            return business_area
    raise ImproperlyConfigured(
        f"{type(view).__name__} exposes neither `selected_business_area` nor `business_area`, "
        "so RDI ingest permissions cannot resolve the business area to check."
    )


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

        return token.user, token


class HOPEPermission(IsAuthenticated):
    def has_permission(self, request: Request, view: Any) -> bool:
        if not bool(request.auth):
            return False
        if not view.permission or view.permission.name not in request.auth.grants:
            return False
        # token must be valid for the business area in the URL (skipped when there is none)
        ba_slug = view.kwargs.get("business_area_slug")
        if ba_slug and not request.auth.valid_for.filter(slug=ba_slug).exists():
            raise Http404
        return True


class BusinessAreaIngestCWOnlyPermission(BasePermission):
    message = CW_ONLY_INGEST_REJECT_MSG

    def has_permission(self, request: Request, view: Any) -> bool:
        return _view_business_area(view).is_rdi_ingest_source_country_workspace_only


class BusinessAreaIngestAllExceptCWPermission(BasePermission):
    message = ALL_EXCEPT_CW_INGEST_REJECT_MSG

    def has_permission(self, request: Request, view: Any) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return not _view_business_area(view).is_rdi_ingest_source_country_workspace_only
