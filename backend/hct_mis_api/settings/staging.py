import os

from .base import *  # noqa: ignore=F403

# dev overrides
DEBUG = False
IS_STAGING = True

# domains/hosts etc.
DOMAIN_NAME = os.getenv("DOMAIN", "dev-hct.unitst.org")
WWW_ROOT = "http://{}/".format(DOMAIN_NAME)

# other
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# STORAGE
STATIC_LOCATION = "static"
MEDIA_LOCATION = "media"

AZURE_ACCOUNT_NAME = os.getenv("STORAGE_AZURE_ACCOUNT_NAME", "")
AZURE_ACCOUNT_KEY = os.getenv("STORAGE_AZURE_ACCOUNT_KEY", "")
MEDIA_STORAGE_AZURE_ACCOUNT_NAME = os.getenv("MEDIA_STORAGE_AZURE_ACCOUNT_NAME", AZURE_ACCOUNT_NAME)
MEDIA_STORAGE_AZURE_ACCOUNT_KEY = os.getenv("MEDIA_STORAGE_AZURE_ACCOUNT_KEY", AZURE_ACCOUNT_KEY)
STATIC_STORAGE_AZURE_ACCOUNT_NAME = os.getenv("STATIC_STORAGE_AZURE_ACCOUNT_NAME", AZURE_ACCOUNT_NAME)
STATIC_STORAGE_AZURE_ACCOUNT_KEY = os.getenv("STATIC_STORAGE_AZURE_ACCOUNT_KEY", AZURE_ACCOUNT_KEY)

AZURE_URL_EXPIRATION_SECS = 10800

AZURE_STATIC_CUSTOM_DOMAIN = f"{STATIC_STORAGE_AZURE_ACCOUNT_NAME}.blob.core.windows.net"
AZURE_MEDIA_CUSTOM_DOMAIN = f"{MEDIA_STORAGE_AZURE_ACCOUNT_NAME}.blob.core.windows.net"
STATIC_URL = f"https://{AZURE_STATIC_CUSTOM_DOMAIN}/{STATIC_LOCATION}/"
MEDIA_URL = f"https://{AZURE_MEDIA_CUSTOM_DOMAIN}/{MEDIA_LOCATION}/"

DEFAULT_FILE_STORAGE = "hct_mis_api.apps.core.storage.AzureMediaStorage"
STATICFILES_STORAGE = "hct_mis_api.apps.core.storage.AzureStaticStorage"
SOCIAL_AUTH_REDIRECT_IS_HTTPS = True

if os.getenv("POSTGRES_SSL", False):
    DATABASES["default"]["OPTIONS"] = {
        "sslmode": "verify-full",
        "sslrootcert": "/code/psql-cert.crt",
    }
    DATABASES["cash_assist_datahub_mis"]["OPTIONS"] = {
        "sslmode": "verify-full",
        "sslrootcert": "/code/psql-cert.crt",
        "options": "-c search_path=mis",
    }
    DATABASES["cash_assist_datahub_ca"]["OPTIONS"] = {
        "sslmode": "verify-full",
        "sslrootcert": "/code/psql-cert.crt",
        "options": "-c search_path=ca",
    }
    DATABASES["cash_assist_datahub_erp"]["OPTIONS"] = {
        "sslmode": "verify-full",
        "sslrootcert": "/code/psql-cert.crt",
        "options": "-c search_path=erp",
    }
    DATABASES["registration_datahub"]["OPTIONS"] = {
        "sslmode": "verify-full",
        "sslrootcert": "/code/psql-cert.crt",
    }

# ELASTICSEARCH SETTINGS
ELASTICSEARCH_DSL = {
    "default": {"hosts": ELASTICSEARCH_HOST, "timeout": 30},
}
