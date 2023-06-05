import base64
import hashlib
import inspect
import json
from datetime import datetime
from typing import Any, Callable, Dict

from django.conf import settings
from django.contrib.auth import authenticate
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.utils.safestring import mark_safe

import tablib
from concurrency.utils import get_classname


def fqn(o: Any) -> str:
    parts = []

    if inspect.isclass(o):
        cls = o
    else:
        cls = type(o)
    if hasattr(o, "__module__"):
        parts.append(o.__module__)
        parts.append(get_classname(o))
    elif inspect.ismodule(o):
        return o.__name__
    else:
        parts.append(cls.__name__)
    if not parts:
        raise ValueError("Invalid argument `{}`".format(o))
    return ".".join(parts)


def to_dataset(result: Any) -> tablib.Dataset:
    if isinstance(result, QuerySet):
        data = tablib.Dataset()
        fields = result.__dict__["_fields"]
        if not fields:
            fields = [field.name for field in result.model._meta.concrete_fields]
        data.headers = fields
        try:
            for obj in result.all():
                data.append([obj[f] if isinstance(obj, dict) else str(getattr(obj, f)) for f in fields])
        except Exception:
            raise ValueError("Results can't be rendered as a tablib Dataset")
    elif isinstance(result, (list, tuple)):
        data = tablib.Dataset()
        fields = set().union(*(d.keys() for d in list(result)))
        data.headers = fields
        try:
            for obj in result:
                data.append([obj[f] for f in fields])
        except Exception:
            raise ValueError("Results can't be rendered as a tablib Dataset")
    elif isinstance(result, (tablib.Dataset, dict)):
        data = result
    else:
        raise ValueError(f"{result} ({type(result)}")
    return data


def get_sentry_url(event_id: int, html: bool = False) -> str:
    url = f"{settings.SENTRY_URL}?query={event_id}"
    if html:
        return mark_safe('<a href="{url}" target="_sentry" >View on Sentry<a/>')
    return url


def basicauth(view: Callable) -> Callable:
    def wrap(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_authenticated:
            return view(request, *args, **kwargs)

        if "HTTP_AUTHORIZATION" in request.META:
            auth = request.headers["Authorization"].split()
            if len(auth) == 2:
                if auth[0].lower() == "basic":
                    uname, passwd = base64.b64decode(auth[1].encode()).decode().split(":")
                    user = authenticate(username=uname, password=passwd)
                    if user is not None and user.is_active:
                        request.user = user
                        return view(request, *args, **kwargs)

        response = HttpResponse()
        response.status_code = 401
        response["WWW-Authenticate"] = 'Basic realm="HOPE"'
        return response

    return wrap


def sizeof(num: float, suffix: str = "") -> str:
    for unit in ["&nbsp;&nbsp;", "Kb", "Mb", "Gb", "Tb", "Pb", "Eb", "Zb"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f} {unit}{suffix} "
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


def dict_hash(dictionary: Dict[str, Any]) -> str:
    """MD5 hash of a dictionary."""
    dhash = hashlib.md5()
    # We need to sort arguments so {'a': 1, 'b': 2} is
    # the same as {'b': 2, 'a': 1}
    encoded = json.dumps(dictionary, sort_keys=True).encode()
    dhash.update(encoded)
    return dhash.hexdigest()


def should_run(expression: str) -> bool:
    match_expressions = expression.split(",")
    today = datetime.today()

    for exp in match_expressions:
        if exp.lower() in ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]:
            if exp.lower() == datetime.today().strftime("%a").lower():
                return True
        elif exp.isnumeric():
            if today.day == int(exp):
                return True
        elif exp.count("/") == 1:
            day, month = exp.split("/")
            if day.isnumeric() and month.isnumeric() and int(day) == today.day and int(month) == today.month:
                return True
        else:
            raise ValueError(f"Invalid expression '{expression}'")
    return False
