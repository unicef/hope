from __future__ import absolute_import
from .base import *  # noqa: ignore=F403


# dev overrides
DEBUG = False
IS_STAGING = False

DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL", "HCT-MIS <noreply@hct-mis.org>"
)

# Sentry Configs
INSTALLED_APPS += ("raven.contrib.django.raven_compat",)

RAVEN_CONFIG = {
    "dsn": os.environ.get("SENTRY_DSN"),
}

# django-storages: https://django-storages.readthedocs.io/en/latest/backends/azure.html
AZURE_ACCOUNT_NAME = os.environ.get("AZURE_ACCOUNT_NAME", None)  # noqa: F405
AZURE_ACCOUNT_KEY = os.environ.get("AZURE_ACCOUNT_KEY", None)  # noqa: F405
AZURE_CONTAINER = os.environ.get("AZURE_CONTAINER", None)  # noqa: F405

AZURE_URL_EXPIRATION_SECS = 10800

if AZURE_ACCOUNT_NAME and AZURE_ACCOUNT_KEY and AZURE_CONTAINER:
    DEFAULT_FILE_STORAGE = "storages.backends.azure_storage.AzureStorage"
