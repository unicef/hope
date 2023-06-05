import logging

from .base import *  # noqa: ignore=F403

CACHES = {
    "default": {
        "BACKEND": "hct_mis_api.apps.core.memcache.LocMemCache",
        "TIMEOUT": 1800,
    }
}

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
        "default": {
            "level": LOG_LEVEL,
            "class": "logging.StreamHandler",
            "formatter": "standard",
        }
    },
    "loggers": {
        "": {"handlers": ["default"], "level": "DEBUG", "propagate": True},
        "registration_datahub.tasks.deduplicate": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": True,
        },
        "sanction_list.tasks.check_against_sanction_list_pre_merge": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": True,
        },
        "graphql": {"handlers": ["default"], "level": "CRITICAL", "propagate": True},
        "elasticsearch": {
            "handlers": ["default"],
            "level": "CRITICAL",
            "propagate": True,
        },
        "elasticsearch-dsl-django": {
            "handlers": ["default"],
            "level": "CRITICAL",
            "propagate": True,
        },
        "hct_mis_api.apps.registration_datahub.tasks.deduplicate": {
            "handlers": ["default"],
            "level": "CRITICAL",
            "propagate": True,
        },
        "hct_mis_api.apps.core.tasks.upload_new_template_and_update_flex_fields": {
            "handlers": ["default"],
            "level": "CRITICAL",
            "propagate": True,
        },
    },
}

logging.disable(logging.CRITICAL)

del DATABASES["read_only"]

SECURE_HSTS_SECONDS = 0
CSRF_COOKIE_SECURE = 0
CSRF_COOKIE_HTTPONLY = 0
SESSION_COOKIE_SECURE = 0
USE_DUMMY_EXCHANGE_RATES = 0
CELERY_TASK_ALWAYS_EAGER = 1
IS_TEST = 1
CYPRESS_TESTING = 1
DEBUG = 1
DOMAIN = "localhost:8000"
ELASTICSEARCH_INDEX_PREFIX = "test_"
EXCHANGE_RATE_CACHE_EXPIRY = 0
REMOTE_STORAGE_ACTIVATE = 0
