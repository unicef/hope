import os

from .base import *  # noqa: ignore=F403

# dev overrides
DEBUG = True
IS_DEV = True
TEMPLATES[0]["OPTIONS"]["debug"] = True

# domains/hosts etc.
DOMAIN_NAME = os.getenv("DOMAIN", "localhost:8000")
WWW_ROOT = "http://{}/".format(DOMAIN_NAME)
ALLOWED_HOSTS.extend(["localhost", "127.0.0.1", "10.0.2.2"])

# change logging level to debug
LOGGING["loggers"]["django.request"]["level"] = "DEBUG"

# ELASTICSEARCH SETTINGS
ELASTICSEARCH_DSL = {
    "default": {"hosts": ELASTICSEARCH_HOST, "timeout": 30},
}

EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
