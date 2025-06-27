import os
from pathlib import Path
from typing import Any, Dict, List

from django.utils.text import slugify

from single_source import get_version

from hct_mis_api.config.env import env

DEBUG: bool = env("DEBUG")

PROJECT_NAME = "hct_mis_api"
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
VERSION = get_version(__name__, Path(PROJECT_ROOT).parent, default_return=None)

DOMAIN_NAME = env("DOMAIN")
WWW_ROOT = "http://{}/".format(DOMAIN_NAME)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")
FRONTEND_HOST = env("DOMAIN")
ADMIN_PANEL_URL = env("ADMIN_PANEL_URL")

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

STATIC_URL = "/api/static/"
STATIC_ROOT = f"{DATA_VOLUME}/staticserve"

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
)
MANIFEST_FILE = "web/.vite/manifest.json"


ENV = env("ENV")

RO_CONN = env.db("REP_DATABASE_URL")
RO_CONN.update(
    {
        "OPTIONS": {"options": "-c default_transaction_read_only=on"},
        "TEST": {
            "READ_ONLY": True,
            "MIRROR": "default",
        },  # Do not manage this database during tests
    }
)
DATABASES = {
    "default": env.db(),
    "read_only": RO_CONN,
}
DATABASES["default"].update({"CONN_MAX_AGE": 60})
DATABASE_APPS_MAPPING: Dict[str, str] = {}

DATABASE_ROUTERS = ("hct_mis_api.apps.core.dbrouters.DbRouter",)

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "social_core.backends.azuread_tenant.AzureADTenantOAuth2",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "hijack.middleware.HijackUserMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    # "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Replace the default XFrameOptionsMiddleware with the custom one to enable Dashboard iframe
    "hct_mis_api.middlewares.xframe.AllowSpecificIframeDomainsMiddleware",
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
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
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
    "hct_mis_api.apps.dashboard.apps.DashboardConfig",
    "hct_mis_api.apps.accountability.apps.AccountabilityConfig",
    "hct_mis_api.apps.web.apps.WebConfig",
    "hct_mis_api.apps.periodic_data_update.apps.PeriodicDataUpdateConfig",
    "hct_mis_api.contrib.aurora.apps.Config",
    "hct_mis_api.contrib.vision.apps.Config",
    "hct_mis_api.apps.universal_update_script.apps.Config",
]

DJANGO_APPS = [
    "hct_mis_api.apps.administration.apps.TemplateConfig",
    "advanced_filters",
    "smart_admin.logs",
    "smart_admin.apps.SmartTemplateConfig",
    "hct_mis_api.apps.administration.apps.Config",
    "admin_sync.apps.Config",
    "smart_env",
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

CACHE_ENABLED = env("CACHE_ENABLED")

CACHES: Dict[str, Any]  # TODO use cache_url from smartenv
if CACHE_ENABLED:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": env("CACHE_LOCATION"),
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

AUTH_USER_MODEL = "account.User"
SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE")
SESSION_COOKIE_HTTPONLY = env.bool("SESSION_COOKIE_HTTPONLY")
SESSION_COOKIE_NAME = env("SESSION_COOKIE_NAME")
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

CSRF_COOKIE_HTTPONLY = env.bool("CSRF_COOKIE_HTTPONLY")
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE")

SECURE_CONTENT_TYPE_NOSNIFF = env.bool("SECURE_CONTENT_TYPE_NOSNIFF")
SECURE_REFERRER_POLICY = env("SECURE_REFERRER_POLICY")
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS")


LOGIN_URL = "/api/login/azuread-tenant-oauth2/"

X_FRAME_OPTIONS = "SAMEORIGIN"

MAX_STORAGE_FILE_SIZE = 30
FILE_UPLOAD_MAX_MEMORY_SIZE = 25 * 1024 * 1024  # 25mb
DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024
DATA_UPLOAD_MAX_NUMBER_FIELDS = None

GDAL_LIBRARY_PATH = env("GDAL_LIBRARY_PATH")
GEOS_LIBRARY_PATH = env("GEOS_LIBRARY_PATH")

GIT_VERSION = env("GIT_VERSION")

ALLOWED_IFRAME_DOMAINS = env.list("ALLOWED_IFRAME_DOMAINS")

PROFILING = env("PROFILING") == "on"
if PROFILING:
    # SILK
    INSTALLED_APPS.append("silk")
    MIDDLEWARE.append("hct_mis_api.middlewares.silk.DynamicSilkyMiddleware")
    SILKY_PYTHON_PROFILER = True

IS_TEST = False

from hct_mis_api.config.fragments.admin_sync import *  # noqa: F403, F401, E402
from hct_mis_api.config.fragments.celery import *  # noqa: F403, F401, E402
from hct_mis_api.config.fragments.concurrency import *  # noqa: F403, F401, E402
from hct_mis_api.config.fragments.constance import *  # noqa: F403, F401, E402
from hct_mis_api.config.fragments.countries import *  # noqa: F403, F401, E402
from hct_mis_api.config.fragments.csp import *  # noqa: F403, F401, E402
from hct_mis_api.config.fragments.debug_toolbar import *  # noqa: F403, F401, E402
from hct_mis_api.config.fragments.drf import *  # noqa: F403, F401, E402
from hct_mis_api.config.fragments.email import *  # noqa: F403, F401, E402
from hct_mis_api.config.fragments.es import *  # noqa: F403, F401, E402
from hct_mis_api.config.fragments.explorer import *  # noqa: F403, F401, E402
from hct_mis_api.config.fragments.flags import *  # noqa: F403, F401, E402
from hct_mis_api.config.fragments.graph import *  # noqa: F403, F401, E402
from hct_mis_api.config.fragments.graphene import *  # noqa: F403, F401, E402
from hct_mis_api.config.fragments.hope import *  # noqa: F403, F401, E402
from hct_mis_api.config.fragments.kobo import *  # noqa: F403, F401, E402
from hct_mis_api.config.fragments.loggers import *  # noqa: F403, F401, E402
from hct_mis_api.config.fragments.markdownify import *  # noqa: F403, F401, E402
from hct_mis_api.config.fragments.matomo import *  # noqa: F403, F401, E402
from hct_mis_api.config.fragments.permissions import *  # noqa: F403, F401, E402
from hct_mis_api.config.fragments.phone_numbers import *  # noqa: F403, F401, E402
from hct_mis_api.config.fragments.rapidpro import *  # noqa: F403, F401, E402
from hct_mis_api.config.fragments.sentry import *  # noqa: F403, F401, E402
from hct_mis_api.config.fragments.smart_admin import *  # noqa: F403, F401, E402
from hct_mis_api.config.fragments.social_auth import *  # noqa: F403, F401, E402
from hct_mis_api.config.fragments.storages import *  # noqa: F403, F401, E402
from hct_mis_api.config.fragments.sysinfo import *  # noqa: F403, F401, E402
from hct_mis_api.config.fragments.test import *  # noqa: F403, F401, E402
