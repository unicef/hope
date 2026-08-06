from enum import StrEnum
from pathlib import Path
import sys


class ProcessRole(StrEnum):
    WEB = "hope-web"
    CELERY = "hope-celery"
    MIGRATE = "hope-migrate"
    RUNSERVER = "hope-runserver"
    SHELL = "hope-shell"
    MANAGE = "hope-manage"
    UNKNOWN = "hope-unknown"


MANAGEMENT_COMMAND_ROLES = {
    "migrate": ProcessRole.MIGRATE,
    "runserver": ProcessRole.RUNSERVER,
    "shell": ProcessRole.SHELL,
    "shell_plus": ProcessRole.SHELL,
}


def get_process_role() -> ProcessRole:
    argv0 = Path(sys.argv[0]).name if sys.argv else ""
    if argv0 == "gunicorn":
        return ProcessRole.WEB
    if argv0 == "celery":
        return ProcessRole.CELERY
    if argv0 in ("manage.py", "django-admin"):
        command = sys.argv[1] if len(sys.argv) > 1 else ""
        return MANAGEMENT_COMMAND_ROLES.get(command, ProcessRole.MANAGE)
    return ProcessRole.UNKNOWN
