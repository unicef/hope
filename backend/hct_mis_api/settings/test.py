import logging
import os

from .base import *  # noqa: ignore=F403

# dev overrides
DEBUG = True
IS_DEV = True
TEMPLATES[0]["OPTIONS"]["debug"] = True

# domains/hosts etc.
DOMAIN_NAME = "localhost:8000"
WWW_ROOT = "http://{}/".format(DOMAIN_NAME)
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "10.0.2.2", os.getenv("DOMAIN", "")]

# other


CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
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

# ELASTICSEARCH SETTINGS
ELASTICSEARCH_DSL = {
    "default": {"hosts": "elasticsearch:9200"},
    "test": {"hosts": "elasticsearch:9200"},
}
ELASTICSEARCH_INDEX_PREFIX = "test_"

logging.disable(logging.CRITICAL)

EXCHANGE_RATE_CACHE_EXPIRY = 0
del DATABASES["read_only"]
CELERY_TASK_ALWAYS_EAGER = True