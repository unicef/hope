from typing import TYPE_CHECKING, Any

from django.db.models import Q
from django.http import Http404
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request

from hope.models import User

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
        if not bool(request.auth):
            return False
        if view.permission == "any":
            return True
        if not view.permission or view.permission.name not in request.auth.grants:
            return False
        # token must be valid for the business area in the URL (skipped when there is none)
        ba_slug = view.kwargs.get("business_area_slug")
        if ba_slug and not request.auth.valid_for.filter(slug=ba_slug).exists():
            raise Http404
        return True
