from typing import Any

from django.http import HttpRequest
from django.utils.safestring import mark_safe


def masker(key: str, value: Any, config: dict, request: HttpRequest) -> Any:
    from django_sysinfo.utils import cleanse_setting

    from ...apps.utils.security import is_root  # noqa: ABS101

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


def filter_environment(key: str, config: dict, request: HttpRequest) -> bool:
    return key in ["ROOT_ACCESS_TOKEN"] or key.startswith("DIRENV")


SYSINFO = {
    "masked_environment": "API|TOKEN|KEY|SECRET|PASS|SIGNATURE|AUTH|_ID|SID|DATABASE_URL",
    "filter_environment": filter_environment,
    "ttl": 60,
    "masker": masker,
}
