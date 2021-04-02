import uuid
from pathlib import Path

from environ import Env

DEFAULTS = {
    "ADMINS": (parse_emails, ""),
    "TEST_USERS": (parse_emails, ""),
    "ALLOWED_HOSTS": (list, ""),
    "BITCASTER_API": (str, "https://app.bitcaster.io/api/"),
}


env = Env(**DEFAULTS)
