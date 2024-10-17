import os
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from django.http import HttpRequest
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from single_source import get_version

from hct_mis_api.config.env import env

DEBUG: bool = env("DEBUG")
IS_TEST = False

PROJECT_NAME = "hct_mis_api"
# project root and add "apps" to the path
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))

# domains/hosts etc.
DOMAIN_NAME = env("DOMAIN")
WWW_ROOT = "http://{}/".format(DOMAIN_NAME)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[DOMAIN_NAME])
FRONTEND_HOST = env("HCT_MIS_FRONTEND_HOST", default=DOMAIN_NAME)
ADMIN_PANEL_URL = env("ADMIN_PANEL_URL")

####
# Other settings
####
ADMINS = (
    ("Alerts", env("ALERTS_EMAIL")),
    ("Kellton", f"unicef-hct-mis+{slugify(DOMAIN_NAME)}@kellton.com"),
)

SITE_ID = 1
TIME_ZONE = "UTC"
LANGUAGE_CODE = "en-us"
USE_I18N = True
USE_TZ = True
SECRET_KEY = env("SECRET_KEY")
DEFAULT_CHARSET = "utf-8"
ROOT_URLCONF = "hct_mis_api.urls"

DATA_VOLUME = env("DATA_VOLUME")
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
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

GRIEVANCE_ONE_UPLOAD_MAX_MEMORY_SIZE = 3 * 1024 * 1024
GRIEVANCE_UPLOAD_CONTENT_TYPES = (
    "image/jpeg",
    "image/png",
    "image/tiff",
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
)

# static resources related. See documentation at: http://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/
STATIC_URL = "/api/static/"
STATIC_ROOT = f"{DATA_VOLUME}/staticserve"

# static serving
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
)
MANIFEST_FILE = "web/.vite/manifest.json"

DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")

EMAIL_BACKEND = env("EMAIL_BACKEND") if not DEBUG else "django.core.mail.backends.console.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env("EMAIL_PORT")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS")

KOBO_KF_URL = env("KOBO_KF_URL")
KOBO_KC_URL = env("KOBO_KC_URL")
KOBO_MASTER_API_TOKEN = env("KOBO_MASTER_API_TOKEN")

# Get the ENV setting. Needs to be set in .bashrc or similar.
ENV = env("ENV")

# prefix all non-production emails
if ENV != "prod":
    EMAIL_SUBJECT_PREFIX = f"{ENV}"
else:
    EMAIL_SUBJECT_PREFIX = ""

RO_CONN = dict(**env.db("DATABASE_URL")).copy()
RO_CONN.update(
    {
        "OPTIONS": {"options": "-c default_transaction_read_only=on"},
        "TEST": {
            "READ_ONLY": True,  # Do not manage this database during tests
        },
    }
)
DATABASES = {
    "default": env.db(),
    "read_only": RO_CONN,
}
DATABASES["default"].update({"CONN_MAX_AGE": 60})

if env("POSTGRES_SSL", default=False):
    DATABASES["default"]["OPTIONS"] = {
        "sslmode": "verify-full",
        "sslrootcert": "/certs/psql-cert.crt",
    }

# If app is not specified here it will use default db
DATABASE_APPS_MAPPING: Dict[str, str] = {}

DATABASE_ROUTERS = ("hct_mis_api.apps.core.dbrouters.DbRouter",)

MIDDLEWARE = [
    # "hct_mis_api.middlewares.deployment.DisableTrafficDuringMigrationsMiddleware",
] + [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "hijack.middleware.HijackUserMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "hct_mis_api.middlewares.sentry.SentryScopeMiddleware",
    "hct_mis_api.middlewares.version.VersionMiddleware",
]
if not DEBUG:
    MIDDLEWARE.append("csp.contrib.rate_limiting.RateLimitedCSPMiddleware")

TEMPLATES: List[Dict[str, Any]] = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(PROJECT_ROOT, "../apps", "core", "templates"),
        ],
        "OPTIONS": {
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
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
                # Matomo
                "hct_mis_api.apps.core.context_processors.matomo",
            ],
            "debug": DEBUG,
        },
    },
]
PROJECT_APPS = [
    "hct_mis_api.api",
    "hct_mis_api.apps.geo.apps.Config",
    "hct_mis_api.apps.account.apps.AccountConfig",
    "hct_mis_api.apps.core.apps.CoreConfig",
    "hct_mis_api.apps.grievance.apps.GrievanceConfig",
    "hct_mis_api.apps.household.apps.HouseholdConfig",
    "hct_mis_api.apps.payment.apps.PaymentConfig",
    "hct_mis_api.apps.program.apps.ProgramConfig",
    "hct_mis_api.apps.changelog.apps.ChangelogConfig",
    "hct_mis_api.apps.targeting.apps.TargetingConfig",
    "hct_mis_api.apps.utils.apps.UtilsConfig",
    "hct_mis_api.apps.registration_datahub.apps.Config",
    "hct_mis_api.apps.registration_data.apps.RegistrationDataConfig",
    "hct_mis_api.apps.sanction_list.apps.SanctionListConfig",
    "hct_mis_api.apps.steficon.apps.SteficonConfig",
    "hct_mis_api.apps.reporting.apps.ReportingConfig",
    "hct_mis_api.apps.activity_log.apps.ActivityLogConfig",
    "hct_mis_api.apps.accountability.apps.AccountabilityConfig",
    "hct_mis_api.apps.web.apps.WebConfig",
    "hct_mis_api.apps.periodic_data_update.apps.PeriodicDataUpdateConfig",
    "hct_mis_api.contrib.aurora.apps.Config",
    "hct_mis_api.contrib.vision.apps.Config",
]

DJANGO_APPS = [
    "hct_mis_api.apps.administration.apps.TemplateConfig",
    "advanced_filters",
    "smart_admin.logs",
    "smart_admin.apps.SmartTemplateConfig",
    "hct_mis_api.apps.administration.apps.Config",
    "admin_sync.apps.Config",
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
    "django.contrib.postgres",
]

OTHER_APPS = [
    "hijack",
    "jsoneditor",
    "django_countries",
    "phonenumber_field",
    "compressor",
    "graphene_django",
    "social_django",
    "corsheaders",
    "django_elasticsearch_dsl",
    "constance",
    "admin_extra_buttons",
    "adminfilters",
    "adminfilters.depot",
    "adminactions",
    "multiselectfield",
    "mptt",
    "django_extensions",
    "django_celery_results",
    "django_celery_beat",
    "django_filters",
    "explorer",
    "import_export",
    "rest_framework",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "flags",
    "admin_cursor_paginator",
    "markdownify.apps.MarkdownifyConfig",
]

INSTALLED_APPS = DJANGO_APPS + OTHER_APPS + PROJECT_APPS
# LOGIN_REDIRECT_URL = f'/api/{ADMIN_PANEL_URL}/'

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 12},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

PASSWORD_RESET_TIMEOUT = 60 * 60 * 24 * 31

ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 7

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "social_core.backends.azuread_tenant.AzureADTenantOAuth2",
]

NOSE_ARGS = ["--with-timer", "--nocapture", "--nologcapture"]


# helper function to extend all the common lists
def extend_list_avoid_repeats(list_to_extend: List, extend_with: List) -> None:
    """Extends the first list with the elements in the second one, making sure its elements are not already there in the
    original list."""
    list_to_extend.extend(filter(lambda x: not list_to_extend.count(x), extend_with))


GIT_VERSION = env("GIT_VERSION", default="UNKNOWN")
HIJACK_PERMISSION_CHECK = "hct_mis_api.apps.utils.security.can_hijack"

REDIS_INSTANCE = env("REDIS_INSTANCE", default="redis:6379")

CACHE_ENABLED = env("CACHE_ENABLED", default=True)

CACHES: Dict[str, Any]
if CACHE_ENABLED:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": env("CACHE_LOCATION", default=f"redis://{REDIS_INSTANCE}/1"),
            "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "hct_mis_api.apps.core.memcache.LocMemCache",
            "TIMEOUT": 1800,
        }
    }

SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE")
SESSION_COOKIE_HTTPONLY = env.bool("SESSION_COOKIE_HTTPONLY")
SESSION_COOKIE_NAME = env("SESSION_COOKIE_NAME")
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
AUTH_USER_MODEL = "account.User"
DEFAULT_EMPTY_PARTNER = "Default Empty Partner"

GRAPHENE = {
    "SCHEMA": "hct_mis_api.schema.schema",
    "SCHEMA_OUTPUT": "schema.json",
    "SCHEMA_INDENT": 2,
}

# Social Auth settings.


LOGIN_URL = "/api/login/azuread-tenant-oauth2/"

GRAPH_MODELS = {
    "all_applications": True,
    "group_models": True,
}

PHONENUMBER_DEFAULT_REGION = "US"

SANCTION_LIST_CC_MAIL = env("SANCTION_LIST_CC_MAIL")

RAPID_PRO_URL = env("RAPID_PRO_URL")

DATA_UPLOAD_MAX_NUMBER_FIELDS = None

# DJANGO CONSTANCE settings


# MICROSOFT GRAPH
AZURE_GRAPH_API_BASE_URL = "https://graph.microsoft.com"
AZURE_GRAPH_API_VERSION = "v1.0"
AZURE_TOKEN_URL = "https://login.microsoftonline.com/unicef.org/oauth2/token"

TEST_OUTPUT_DIR = "./test-results"
TEST_OUTPUT_FILE_NAME = "result.xml"

DATAMART_USER = env("DATAMART_USER")
DATAMART_PASSWORD = env("DATAMART_PASSWORD")
DATAMART_URL = env("DATAMART_URL")

COUNTRIES_OVERRIDE = {
    "U": {
        "name": _("Unknown or Not Applicable"),
        "alpha3": "U",
        "ioc_code": "U",
    },
}

ROOT_TOKEN = env.str("ROOT_ACCESS_TOKEN", uuid4().hex)

CORS_ALLOWED_ORIGIN_REGEXES = [r"https://\w+.blob.core.windows.net$"]

EXCHANGE_RATE_CACHE_EXPIRY = env.int("EXCHANGE_RATE_CACHE_EXPIRY", default=1 * 60 * 60 * 24)

VERSION = get_version(__name__, Path(PROJECT_ROOT).parent, default_return=None)

# see adminactions.perms
# set handker to AA_PERMISSION_CREATE_USE_COMMAND
AA_PERMISSION_HANDLER = 3


def filter_environment(key: str, config: Dict, request: HttpRequest) -> bool:
    return key in ["ROOT_ACCESS_TOKEN"] or key.startswith("DIRENV")


def masker(key: str, value: Any, config: Dict, request: HttpRequest) -> Any:
    from django_sysinfo.utils import cleanse_setting

    from ..apps.utils.security import is_root  # noqa: ABS101

    if key in ["PATH", "PYTHONPATH"]:
        return mark_safe(value.replace(":", r":<br>"))
    if not is_root(request):
        if key.startswith("DATABASE_URL"):
            from urllib.parse import urlparse

            try:
                c = urlparse(value)
                value = f"{c.scheme}://****:****@{c.hostname}{c.path}?{c.query}"
            except Exception:
                value = "<wrong url>"
            return value
        return cleanse_setting(key, value, config, request)
    return value


SYSINFO = {
    "masked_environment": "API|TOKEN|KEY|SECRET|PASS|SIGNATURE|AUTH|_ID|SID|DATABASE_URL",
    "filter_environment": filter_environment,
    "ttl": 60,
    "masker": masker,
}

EXPLORER_CONNECTIONS = {
    "default": "default",
}
EXPLORER_DEFAULT_CONNECTION = "default"
EXPLORER_PERMISSION_VIEW = lambda r: r.user.has_perm("explorer.view_query")
EXPLORER_PERMISSION_CHANGE = lambda r: r.user.has_perm("explorer.change_query")

IMPERSONATE = {
    "REDIRECT_URL": f"/api/{ADMIN_PANEL_URL}/",
    "PAGINATE_COUNT": 50,
    "DISABLE_LOGGING": False,
}

POWER_QUERY_DB_ALIAS = env("POWER_QUERY_DB_ALIAS")
POWER_QUERY_EXTRA_CONNECTIONS = [
    "core.businessarea",
]

CONCURRENCY_ENABLED = False

PROFILING = env("PROFILING", default="off") == "on"
if PROFILING:
    # SILK
    INSTALLED_APPS.append("silk")
    MIDDLEWARE.append("hct_mis_api.middlewares.silk.DynamicSilkyMiddleware")
    SILKY_PYTHON_PROFILER = True

ADMIN_SYNC_USE_REVERSION = False

SWAGGER_SETTINGS = {
    "LOGOUT_URL": reverse_lazy("logout"),
    "LOGIN_URL": "/",
    "SECURITY_DEFINITIONS": {"DRF Token": {"type": "apiKey", "name": "Authorization", "in": "header"}},
}

MAX_STORAGE_FILE_SIZE = 30
USE_DUMMY_EXCHANGE_RATES = env("USE_DUMMY_EXCHANGE_RATES", default="no") == "yes"

FLAGS_STATE_LOGGING = DEBUG
FLAGS = {
    "DEVELOP_DEBUG_TOOLBAR": [],
    "SILK_MIDDLEWARE": [],
    "FRONT_DOOR_BYPASS": [],
    "ALLOW_ACCOUNTABILITY_MODULE": [{"condition": "boolean", "value": False}],
    "NEW_RECORD_MODEL": [{"condition": "boolean", "value": False}],
}

MARKDOWNIFY = {
    "default": {
        "WHITELIST_TAGS": ["a", "abbr", "acronym", "b", "blockquote", "em", "i", "li", "ol", "p", "strong", "ul" "br"]
    }
}

CYPRESS_TESTING = env("CYPRESS_TESTING", default="no") == "yes"

if CYPRESS_TESTING and ENV != "dev":
    from django.core.exceptions import ImproperlyConfigured

    raise ImproperlyConfigured(f"CYPRESS_TESTING can only be used in development env: ENV={ENV}")

CSRF_COOKIE_HTTPONLY = env.bool("CSRF_COOKIE_HTTPONLY")
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE")

SECURE_CONTENT_TYPE_NOSNIFF = env.bool("SECURE_CONTENT_TYPE_NOSNIFF")
SECURE_REFERRER_POLICY = env("SECURE_REFERRER_POLICY")
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS")

FLOWER_ADDRESS = env("FLOWER_ADDRESS")

ADMIN_SYNC_CONFIG = "admin_sync.conf.DjangoConstance"
DEFAULT_EMPTY_PARTNER = "Default Empty Partner"

from hct_mis_api.config.fragments.celery import *  # noqa: F403, F401, E402
from hct_mis_api.config.fragments.constance import *  # noqa: F403, F401, E402
from hct_mis_api.config.fragments.csp import *  # noqa: F403, F401, E402
from hct_mis_api.config.fragments.debug_toolbar import *  # noqa: F403, F401, E402
from hct_mis_api.config.fragments.drf import *  # noqa: F403, F401, E402
from hct_mis_api.config.fragments.drf_spectacular import *  # noqa: F403, F401, E402
from hct_mis_api.config.fragments.es import *  # noqa: F403, F401, E402
from hct_mis_api.config.fragments.loggers import *  # noqa: F403, F401, E402
from hct_mis_api.config.fragments.mailjet import *  # noqa: F403, F401, E402
from hct_mis_api.config.fragments.matomo import *  # noqa: F403, F401, E402
from hct_mis_api.config.fragments.sentry import *  # noqa: F403, F401, E402
from hct_mis_api.config.fragments.smart_admin import *  # noqa: F403, F401, E402
from hct_mis_api.config.fragments.social_auth import *  # noqa: F403, F401, E402
from hct_mis_api.config.fragments.storages import *  # noqa: F403, F401, E402

LIBRARY_PATHS: bool = env("LIBRARY_PATHS", default=False)
if LIBRARY_PATHS:
    GDAL_LIBRARY_PATH = "/opt/homebrew/opt/gdal/lib/libgdal.dylib"
    GEOS_LIBRARY_PATH = "/opt/homebrew/opt/geos/lib/libgeos_c.dylib"
