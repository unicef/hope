from __future__ import absolute_import
from .base import *  # noqa: ignore=F403


# dev overrides
DEBUG = False
IS_STAGING = True

# domains/hosts etc.
DOMAIN_NAME = 'localhost:8000'
WWW_ROOT = 'http://%s/' % DOMAIN_NAME
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "10.0.2.2", os.getenv("DOMAIN", "")]

# other
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# CACHE
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'TIMEOUT': 1800,
    }
}
