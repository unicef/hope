from __future__ import absolute_import

import logging

from graphql import GraphQLError
from graphql.error import GraphQLLocatedError

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
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "TIMEOUT": 1800,
    }
}

# change logging level to debug
LOGGING["loggers"]["django.request"]["level"] = "DEBUG"
def graphql_error(record):
    err_type, err_obj, traceback = record.exc_info
    if err_type == GraphQLError or err_type == GraphQLLocatedError:
        return False
    return True


logging.getLogger("graphql.execution.executor").addFilter(graphql_error)
logging.getLogger("graphql.execution.utils").addFilter(graphql_error)
logging.getLogger("graphql.execution").addFilter(graphql_error)
logging.getLogger("graphql").addFilter(graphql_error)
logging.getLogger("graphql.errors").addFilter(graphql_error)


try:
    from .local import *  # noqa: ignore=F403
except ImportError:
    pass
