import datetime
import io
import json
import tempfile
from pathlib import Path
from urllib.parse import quote, unquote

from django.conf import settings
from django.core import signing
from django.core.management import call_command
from django.core.serializers import get_serializer
from django.core.signing import BadSignature
from django.db.models import Model
from django.http import Http404, HttpResponse
from django.template import loader
from django.urls.base import reverse
from django.utils.text import slugify

import requests
import reversion
from adminactions.export import ForeignKeysCollector
from constance import config

CREDENTIALS_COOKIE = "prod_credentials"
signer = signing.TimestampSigner()


def is_editor(request):
    return config.PRODUCTION_SERVER


def is_production(request):
    return not is_editor(request)


def get_data_structure(reg: Model) -> str:
    c = ForeignKeysCollector(None)
    c.collect(reg.__class__.objects.filter(pk=reg.pk))
    json = get_serializer("json")()
    return json.serialize(c.data, use_natural_foreign_keys=True, use_natural_primary_keys=True, indent=3)


def loaddata_from_url(url, auth, user=None, comment=None):
    # server = config.PRODUCTION_SERVER
    # basic = HTTPBasicAuth(*config.PRODUCTION_CREDENTIALS.split('/'))
    ret = requests.get(url, auth=auth)
    if ret.status_code == 403:
        raise PermissionError
    if ret.status_code == 404:
        raise Http404(config.PRODUCTION_SERVER + url)
    out = io.StringIO()
    payload = unwrap(ret.content)
    workdir = Path(".").absolute()
    kwargs = {"dir": workdir, "prefix": f"~LOADDATA-{slugify(url)}", "suffix": ".json", "delete": True}
    payload = payload.replace("smart_register", "aurora")
    with tempfile.NamedTemporaryFile(**kwargs) as fdst:
        assert isinstance(fdst.write, object)
        fdst.write(payload.encode())
    fixture = (workdir / fdst.name).absolute()
    with reversion.create_revision():
        if user:
            reversion.set_user(user)
            reversion.set_comment(comment)
        call_command("loaddata", fixture, stdout=out, verbosity=3)
    return out.getvalue()


def wraps(data: str) -> str:
    return json.dumps({"data": quote(data)})


def unwrap(payload: str) -> str:
    data = json.loads(payload)
    return unquote(data["data"])


def is_logged_to_prod(request):
    return request.COOKIES.get(CREDENTIALS_COOKIE, None)


def get_prod_credentials(request):
    try:
        credentials = signer.unsign_object(request.COOKIES[CREDENTIALS_COOKIE])
        return credentials
    except (BadSignature, KeyError):
        return {}


def sign_prod_credentials(username, password):
    return signer.sign_object({"username": username, "password": password})


def set_cookie(response, key, value, days_expire=7):
    if days_expire is None:
        max_age = 365 * 24 * 60 * 60  # one year
    else:
        max_age = days_expire * 24 * 60 * 60
    expires = datetime.datetime.strftime(
        datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age),
        "%a, %d-%b-%Y %H:%M:%S GMT",
    )
    response.set_cookie(
        key,
        value,
        max_age=max_age,
        expires=expires,
        domain=settings.SESSION_COOKIE_DOMAIN,
        secure=settings.SESSION_COOKIE_SECURE or None,
    )


def production_reverse(urlname):
    local = reverse(urlname)
    DJANGO_ADMIN_URL = f"/api/{settings.ADMIN_PANEL_URL}/"
    return config.PRODUCTION_SERVER + local.replace(DJANGO_ADMIN_URL, "")


def invalidate_cache():
    pass


def get_client_ip(request):
    """
    type: (WSGIRequest) -> Optional[Any]
    Naively yank the first IP address in an X-Forwarded-For header
    and assume this is correct.

    Note: Don't use this in security sensitive situations since this
    value may be forged from a client.
    """
    if request:
        for x in [
            "HTTP_X_ORIGINAL_FORWARDED_FOR",
            "HTTP_X_FORWARDED_FOR",
            "HTTP_X_REAL_IP",
            "REMOTE_ADDR",
        ]:
            ip = request.META.get(x)
            if ip:
                return ip.split(",")[0].strip()


def render(request, template_name, context=None, content_type=None, status=None, using=None, cookies=None):
    """
    Return a HttpResponse whose content is filled with the result of calling
    django.template.loader.render_to_string() with the passed arguments.
    """
    content = loader.render_to_string(template_name, context, request, using=using)
    response = HttpResponse(content, content_type, status)
    if cookies:
        for k, v in cookies.items():
            response.set_cookie(k, v)

    return response
