import ast
import base64
import inspect

from django.conf import settings
from django.contrib.auth import authenticate
from django.db.models import QuerySet
from django.http import HttpResponse
from django.utils.safestring import mark_safe

import tablib
from concurrency.utils import get_classname


def fqn(o):

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
        raise ValueError("Invalid argument `%s`" % o)
    return ".".join(parts)


def to_dataset(result):
    if isinstance(result, QuerySet):
        data = tablib.Dataset()
        fields = [field.name for field in result.model._meta.fields]
        data.headers = fields
        for obj in result.all():
            data.append([getattr(obj, f) for f in fields])
    elif isinstance(result, tablib.Dataset):
        data = result
    elif isinstance(result, dict):
        data = result
    else:
        raise ValueError(f"{result} ({type(result)}")
    return data


def get_sentry_url(event_id, html=False):
    url = f"{settings.SENTRY_URL}?query={event_id}"
    if html:
        return mark_safe('<a href="{url}" target="_sentry" >View on Sentry<a/>')
    return url


def basicauth(view):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view(request, *args, **kwargs)

        if "HTTP_AUTHORIZATION" in request.META:
            auth = request.META["HTTP_AUTHORIZATION"].split()
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
