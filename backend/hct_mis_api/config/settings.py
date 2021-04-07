import logging
import os
import sys
from pathlib import Path

####
# Change per project
####
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from sentry_sdk.integrations.celery import CeleryIntegration

from .defaults import env

PROJECT_NAME = "hct_mis_api"
PROJECT_ROOT = Path(__file__).parent.parent

# domains/hosts etc.
DOMAIN_NAME = env("DOMAIN")
ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS") + [DOMAIN_NAME]
FRONTEND_HOST = env("HCT_MIS_FRONTEND_HOST")

####
# Other settings
####
ADMINS = env("ADMINS") + (
    ("Alerts", os.getenv("ALERTS_EMAIL") or "admin@hct-mis.com"),
    ("Tivix", f"unicef-hct-mis+{slugify(DOMAIN_NAME)}@tivix.com"),
)

SITE_ID = 1
TIME_ZONE = "UTC"
LANGUAGE_CODE = "en-us"
USE_I18N = True
SECRET_KEY = env("SECRET_KEY")
DEFAULT_CHARSET = "utf-8"
ROOT_URLCONF = "hct_mis_api.config.urls"

DATA_VOLUME = env("DATA_VOLUME")

ALLOWED_EXTENSIONS = (
    "pdf",
    "doc",
    "docx",
    "xls",
    "xlsx",
    "img",
    "png",
    "jpg",
    "jpeg",
    "csv",
    "zip",
)
UPLOADS_DIR_NAME = "uploads"
MEDIA_URL = f"/api/{UPLOADS_DIR_NAME}/"
MEDIA_ROOT = env("HCT_MIS_UPLOADS_PATH") or os.path.join(DATA_VOLUME, UPLOADS_DIR_NAME)

FILE_UPLOAD_MAX_MEMORY_SIZE = 25 * 1024 * 1024  # 25mb
DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024

# static resources related. See documentation at: http://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/
STATIC_URL = "/api/static/"
STATIC_ROOT = f"{DATA_VOLUME}/staticserve"

# static serving
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
)

DEBUG = True
IS_DEV = False
IS_STAGING = False
IS_PROD = False

EMAIL_CONFIG = env.email_url("EMAIL_URL", default="smtp://user@:password@localhost:25")

vars().update(EMAIL_CONFIG)

DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")
# EMAIL_HOST = env("EMAIL_HOST")
# EMAIL_PORT = env("EMAIL_PORT")
# EMAIL_HOST_USER = env("EMAIL_HOST_USER")
# EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
# EMAIL_USE_TLS = env("EMAIL_USE_TLS")

DATABASES = {
    "default": env.db("DATABASE_URL"),
    "cash_assist_datahub_mis": env.db("DATABASE_URL_HUB_MIS"),
    "cash_assist_datahub_ca": env.db("DATABASE_URL_HUB_CA"),
    "cash_assist_datahub_erp": env.db("DATABASE_URL_HUB_ERP"),
    "registration_datahub": env.db("DATABASE_URL_HUB_REGISTRATION"),
}

# If app is not specified here it will use default db
DATABASE_APPS_MAPPING = {
    "cash_assist_datahub": "cash_assist_datahub_ca",
    "mis_datahub": "cash_assist_datahub_mis",
    "erp_datahub": "cash_assist_datahub_erp",
    "registration_datahub": "registration_datahub",
}

DATABASE_ROUTERS = ("hct_mis_api.apps.core.dbrouters.DbRouter",)

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "hct_mis_api.middlewares.sentry.SentryScopeMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.media",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.static",
                "django.template.context_processors.request",
                # Social auth context_processors
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
            ],
        },
    },
]
PROJECT_APPS = [
    "hct_mis_api.apps.account",
    "hct_mis_api.apps.core",
    "hct_mis_api.apps.grievance",
    "hct_mis_api.apps.household",
    "hct_mis_api.apps.id_management",
    "hct_mis_api.apps.intervention",
    "hct_mis_api.apps.payment",
    "hct_mis_api.apps.program",
    # "hct_mis_api.apps.targeting",
    "hct_mis_api.apps.targeting.apps.TargetingConfig",
    "hct_mis_api.apps.utils",
    "hct_mis_api.apps.registration_datahub",
    "hct_mis_api.apps.registration_data",
    "hct_mis_api.apps.cash_assist_datahub",
    "hct_mis_api.apps.mis_datahub",
    "hct_mis_api.apps.erp_datahub",
    "hct_mis_api.apps.sanction_list",
    "hct_mis_api.apps.steficon",
    "hct_mis_api.apps.reporting",
    "hct_mis_api.apps.activity_log",
]

DJANGO_APPS = [
    "smart_admin.templates",
    "smart_admin",
    "django_sysinfo",
    "django.contrib.auth",
    "django.contrib.humanize",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "django.contrib.staticfiles",
    "django.contrib.gis",
]

OTHER_APPS = [
    "django_countries",
    "phonenumber_field",
    "compressor",
    "graphene_django",
    "social_django",
    "corsheaders",
    "django_elasticsearch_dsl",
    "constance.backends.database",
    "constance",
    "admin_extra_urls",
    "adminfilters",
    "multiselectfield",
    "mptt",
    "django_extensions",
    "django_celery_results",
    "django_celery_beat",
]

INSTALLED_APPS = DJANGO_APPS + OTHER_APPS + PROJECT_APPS

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 12}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

PASSWORD_RESET_TIMEOUT_DAYS = 31

ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 7

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "social_core.backends.azuread_tenant.AzureADTenantOAuth2",
]

NOSE_ARGS = ["--with-timer", "--nocapture", "--nologcapture"]


# helper function to extend all the common lists
def extend_list_avoid_repeats(list_to_extend, extend_with):
    """Extends the first list with the elements in the second one, making sure its elements are not already there in the
    original list."""
    list_to_extend.extend(filter(lambda x: not list_to_extend.count(x), extend_with))


LOG_LEVEL = "DEBUG" if DEBUG and "test" not in sys.argv else "INFO"
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s line %(lineno)d: %(message)s"},
        "verbose": {
            "format": "[%(asctime)s][%(levelname)s][%(name)s] %(filename)s.%(funcName)s:%(lineno)d %(message)s",
        },
    },
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "handlers": {
        "default": {"level": LOG_LEVEL, "class": "logging.StreamHandler", "formatter": "standard"},
        "file": {"level": LOG_LEVEL, "class": "logging.FileHandler", "filename": "debug.log"},
    },
    "loggers": {
        "": {"handlers": ["default"], "level": "INFO", "propagate": True},
        "console": {"handlers": ["default"], "level": "DEBUG", "propagate": True},
        "django.request": {"handlers": ["default"], "level": "ERROR", "propagate": False},
        "django.security.DisallowedHost": {
            # Skip "SuspiciousOperation: Invalid HTTP_HOST" e-mails.
            "handlers": ["default"],
            "propagate": False,
        },
        "elasticsearch": {"handlers": ["file"], "level": "CRITICAL", "propagate": True},
    },
}

GIT_VERSION = env("GIT_VERSION")

REDIS_INSTANCE = os.getenv("REDIS_INSTANCE", "redis")
CACHES = {"default": env.cache("CACHE_URL")}

SESSION_COOKIE_HTTPONLY = True
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
AUTH_USER_MODEL = "account.User"

GRAPHENE = {
    "SCHEMA": "hct_mis_api.schema.schema",
    "SCHEMA_OUTPUT": "schema.json",
    "SCHEMA_INDENT": 2,
}

# Social Auth settings.
AZURE_CLIENT_ID = env("AZURE_CLIENT_ID")
AZURE_CLIENT_SECRET = env("AZURE_CLIENT_SECRET")
AZURE_TENANT_KEY = env("AZURE_TENANT_KEY")
SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_KEY = AZURE_CLIENT_ID
SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_SECRET = AZURE_CLIENT_SECRET
SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_TENANT_ID = AZURE_TENANT_KEY
SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = [
    "username",
    "first_name",
    "last_name",
    "email",
]
SOCIAL_AUTH_POSTGRES_JSONFIELD = True

SOCIAL_AUTH_PIPELINE = (
    "hct_mis_api.apps.account.authentication.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "social_core.pipeline.social_auth.social_user",
    "social_core.pipeline.user.get_username",
    "hct_mis_api.apps.account.authentication.require_email",
    "social_core.pipeline.social_auth.associate_by_email",
    "hct_mis_api.apps.account.authentication.create_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "hct_mis_api.apps.account.authentication.user_details",
)
SOCIAL_AUTH_AZUREAD_B2C_OAUTH2_USER_FIELDS = [
    "email",
    "fullname",
]

SOCIAL_AUTH_AZUREAD_B2C_OAUTH2_SCOPE = [
    "openid",
    "email",
    "profile",
]

SOCIAL_AUTH_SANITIZE_REDIRECTS = True

LOGIN_URL = "/api/login/azuread-tenant-oauth2"

TEST_RUNNER = "hct_mis_api.apps.core.mis_test_runner.PostgresTestRunner"

GRAPH_MODELS = {
    "all_applications": True,
    "group_models": True,
}

PHONENUMBER_DEFAULT_REGION = "US"

SANCTION_LIST_CC_MAIL = env("SANCTION_LIST_CC_MAIL")

# ELASTICSEARCH SETTINGS
ELASTICSEARCH_DSL_AUTOSYNC = False
ELASTICSEARCH_HOST = env("ELASTICSEARCH_HOST")
ELASTICSEARCH_DSL = {
    "default": {"hosts": ELASTICSEARCH_HOST, "timeout": 30},
}

RAPID_PRO_URL = env("RAPID_PRO_URL")

# DJANGO CONSTANCE settings
CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"

CONSTANCE_ADDITIONAL_FIELDS = {
    "percentages": (
        "django.forms.fields.IntegerField",
        {"widget": "django.forms.widgets.NumberInput", "validators": [MinValueValidator(0), MaxValueValidator(100)]},
    ),
    "positive_integers": (
        "django.forms.fields.IntegerField",
        {"widget": "django.forms.widgets.NumberInput", "validators": [MinValueValidator(0)]},
    ),
    "positive_floats": (
        "django.forms.fields.FloatField",
        {"widget": "django.forms.widgets.NumberInput", "validators": [MinValueValidator(0)]},
    ),
}

CONSTANCE_CONFIG = {
    # BATCH SETTINGS
    "DEDUPLICATION_BATCH_DUPLICATE_SCORE": (
        6.0,
        "Results equal or above this score are considered duplicates",
        "positive_floats",
    ),
    # "DEDUPLICATION_BATCH_MIN_SCORE": (
    #     15.0,
    #     "Results below the minimum score will not be taken into account",
    #     "positive_integers",
    # ),
    "DEDUPLICATION_BATCH_DUPLICATES_PERCENTAGE": (
        50,
        "If percentage of duplicates is higher or equal to this setting, deduplication is aborted",
        "percentages",
    ),
    "DEDUPLICATION_BATCH_DUPLICATES_ALLOWED": (
        5,
        "If amount of duplicates for single individual exceeds this limit deduplication is aborted",
        "positive_integers",
    ),
    # GOLDEN RECORDS SETTINGS
    "DEDUPLICATION_GOLDEN_RECORD_MIN_SCORE": (
        6.0,
        "Results below the minimum score will not be taken into account",
        "positive_floats",
    ),
    "DEDUPLICATION_GOLDEN_RECORD_DUPLICATE_SCORE": (
        11.0,
        "Results equal or above this score are considered duplicates",
        "positive_floats",
    ),
    "DEDUPLICATION_GOLDEN_RECORD_DUPLICATES_PERCENTAGE": (
        50,
        "If percentage of duplicates is higher or equal to this setting, deduplication is aborted",
        "percentages",
    ),
    "DEDUPLICATION_GOLDEN_RECORD_DUPLICATES_ALLOWED": (
        5,
        "If amount of duplicates for single individual exceeds this limit deduplication is aborted",
        "positive_integers",
    ),
    # SANCTION LIST
    "SANCTION_LIST_MATCH_SCORE": (
        4.8,
        "Results equal or above this score are considered possible matches",
        "positive_floats",
    ),
    # RAPID PRO
    "RAPID_PRO_PROVIDER": ("tel", "Rapid pro messages provider (telegram/tel)"),
    # CASH ASSIST
    "CASH_ASSIST_URL_PREFIX": ("", "Cash Assist base url used to generate url to cash assist"),
}

CONSTANCE_DBS = ("default",)

# MICROSOFT GRAPH
AZURE_GRAPH_API_BASE_URL = "https://graph.microsoft.com"
AZURE_GRAPH_API_VERSION = "v1.0"
AZURE_TOKEN_URL = "https://login.microsoftonline.com/unicef.org/oauth2/token"

TEST_OUTPUT_DIR = "./test-results"
TEST_OUTPUT_FILE_NAME = "result.xml"

DATAMART_USER = env("DATAMART_USER")
DATAMART_PASSWORD = env("DATAMART_PASSWORD")
DATAMART_URL = env("DATAMART_URL")


AZURE_ACCOUNT_NAME = env("STORAGE_AZURE_ACCOUNT_NAME")
AZURE_ACCOUNT_KEY = env("STORAGE_AZURE_ACCOUNT_KEY")
AZURE_URL_EXPIRATION_SECS = 10800

AZURE_CUSTOM_DOMAIN = f"{AZURE_ACCOUNT_NAME}.blob.core.windows.net"
STATIC_URL = env("STATIC_URL")
MEDIA_URL = env("MEDIA_URL")

DEFAULT_FILE_STORAGE = env("STORAGE_DEFAULT")
STATICFILES_STORAGE = env("STORAGE_STATICFILES")
SOCIAL_AUTH_REDIRECT_IS_HTTPS = env.bool("SOCIAL_AUTH_REDIRECT_IS_HTTPS")


KOBO_MASTER_API_TOKEN = env("KOBO_MASTER_API_TOKEN")

COUNTRIES_OVERRIDE = {
    "U": {
        "name": _("Unknown or Not Applicable"),
        "alpha3": "U",
        "ioc_code": "U",
    },
}

SENTRY_DSN = env("SENTRY_DSN")
SENTRY_URL = env("SENTRY_URL")
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration

    from hct_mis_api import get_full_version

    sentry_logging = LoggingIntegration(
        level=logging.INFO, event_level=logging.ERROR  # Capture info and above as breadcrumbs  # Send errors as events
    )

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(transaction_style="url"),
            sentry_logging,
            CeleryIntegration()
            # RedisIntegration(),
        ],
        release=get_full_version(),
        send_default_pii=True,
    )

CORS_ALLOWED_ORIGIN_REGEXES = [r"https://\w+.blob.core.windows.net$"]

CELERY_BROKER_URL = env("CELERY_BROKER_URL")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_TASK_ALWAYS_EAGER = env.bool("CELERY_TASK_ALWAYS_EAGER")

from smart_admin.utils import match, regex

SMART_ADMIN_SECTIONS = {
    "HOPE": [
        "program",
        match("household.H*"),
        regex(r"household\.I.*"),
        "targeting",
        "payment",
    ],
    "Grievance": ["grievance"],
    "Configuration": ["core", "constance", "household", "household.agency"],
    "Rule Engine": [
        "steficon",
    ],
    "Security": ["account", "auth"],
    "Logs": [
        "admin.LogEntry",
    ],
    "Kobo": [
        "core.FlexibleAttributeChoice",
        "core.XLSXKoboTemplate",
        "core.FlexibleAttribute",
        "core.FlexibleAttributeGroup",
    ],
    "HUBs": [
        "cash_assist_datahub",
        "erp_datahub",
        "mis_datahub",
        "registration_datahub",
    ],
    "System": [
        "social_django",
        "constance",
        "sites",
    ],
}
