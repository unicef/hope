from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication, get_authorization_header
from rest_framework.permissions import IsAuthenticated

from .models import APIToken


class HOPEAuthentication(TokenAuthentication):
    keyword = "Token"
    model = APIToken

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = _("Invalid token header. No credentials provided.")
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _("Invalid token header. Token string should not contain spaces.")
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = _("Invalid token header. Token string should not contain invalid characters.")
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):
        try:
            token = (
                APIToken.objects.select_related("user")
                .filter(valid_from__gte=timezone.now())
                .filter(Q(valid_from__lte=timezone.now()) | Q(valid_from__isnull=True))
                .get(key=key)
            )
        except APIToken.DoesNotExist:
            raise exceptions.AuthenticationFailed(_("Invalid token."))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_("User inactive or deleted."))

        return (token.user, token)


class HOPEPermission(IsAuthenticated):
    def has_permission(self, request, view):
        if bool(request.user and request.user.is_authenticated):
            if view.permission == "any":
                return True
            return request.user.user_roles.filter(role__permissions__contains=[view.permission]).exists()
        return False
