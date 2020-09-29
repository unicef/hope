from __future__ import absolute_import

from .base import *  # noqa: ignore=F403

# dev overrides
DEBUG = True
IS_DEV = True
TEMPLATES[0]["OPTIONS"]["debug"] = True

# domains/hosts etc.
DOMAIN_NAME = "localhost:8000"
WWW_ROOT = "http://%s/" % DOMAIN_NAME
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "10.0.2.2", os.getenv("DOMAIN", "")]

# other


CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache", "TIMEOUT": 1800}}

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
    "handlers": {"default": {"level": LOG_LEVEL, "class": "logging.StreamHandler", "formatter": "standard"}},
    "loggers": {
        "": {"handlers": ["default"], "level": "DEBUG", "propagate": True},
        "graphql": {"handlers": ["default"], "level": "CRITICAL", "propagate": True},
    },
}

# ELASTICSEARCH SETTINGS
ELASTICSEARCH_DSL = {
    "default": {"hosts": "elasticsearch:9200"},
}

try:
    from .local import *  # noqa: ignore=F403
except ImportError:
    pass
