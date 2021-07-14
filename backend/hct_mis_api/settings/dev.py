from __future__ import absolute_import

import os

from .base import *  # noqa: ignore=F403

# dev overrides
DEBUG = True
IS_DEV = True
TEMPLATES[0]["OPTIONS"]["debug"] = True

# domains/hosts etc.
DOMAIN_NAME = os.getenv("DOMAIN", "localhost:8000")
WWW_ROOT = "http://%s/" % DOMAIN_NAME
ALLOWED_HOSTS.extend(["localhost", "127.0.0.1", "10.0.2.2"])

# other
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache", "TIMEOUT": 1800}}

# change logging level to debug
LOGGING["loggers"]["django.request"]["level"] = "DEBUG"

try:
    from .local import *  # noqa: ignore=F403
except ImportError:
    pass

# ELASTICSEARCH SETTINGS
ELASTICSEARCH_DSL = {
    "default": {"hosts": ELASTICSEARCH_HOST, "timeout": 30},
    "test": {"hosts": "elasticsearch_test:9200"},
}
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")


class AnyUserBackend:
    ALLOWED = "aboncenne@unicef.org,afifield@unicef.org,gerba@unicef.org,sapostolico@unicef.org,esahin@unicef.org,nlharhoff@unicef.org"

    def get_user(self, user_id):
        from django.contrib.auth.backends import UserModel

        try:
            user = UserModel._default_manager.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
        return user if self.user_can_authenticate(user) else None

    def user_can_authenticate(self, a):
        return True

    def has_perm(self, user_obj, perm, obj=None):
        return True

    def has_module_perms(self, user_obj, app_label):
        return True

    def authenticate(self, request, username=None, password=None, **kwargs):
        from hct_mis_api.apps.account.models import User

        if username in self.ALLOWED:
            u, __ = User.objects.update_or_create(
                username=username,
                defaults={"email": username, "is_active": True, "is_staff": True, "is_superuser": True},
            )
            return u


AUTHENTICATION_BACKENDS = [
    # "django.contrib.auth.backends.ModelBackend",
    # "social_core.backends.azuread_tenant.AzureADTenantOAuth2",
    "hct_mis_api.settings.dev.AnyUserBackend",
]
