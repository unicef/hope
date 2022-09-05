import io
import json
import logging
import tempfile
from pathlib import Path
from urllib.parse import quote_plus, unquote_plus

from django.contrib import messages
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.core.management import call_command
from django.core.serializers import get_serializer
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls.base import reverse as local_reverse
from django.views.decorators.csrf import csrf_exempt

import requests
import reversion
from admin_extra_buttons.decorators import button, view
from admin_extra_buttons.mixins import ExtraButtonsMixin
from concurrency.api import disable_concurrency
from constance import config
from requests.auth import HTTPBasicAuth

from ...utils.security import is_root
from .forms import ProductionLoginForm
from .perms import check_load_permission, check_publish_permission
from .utils import (
    CREDENTIALS_COOKIE,
    get_client_ip,
    get_data_structure,
    get_prod_credentials,
    invalidate_cache,
    is_editor,
    is_logged_to_prod,
    is_production,
    loaddata_from_url,
    production_reverse,
    render,
    set_cookie,
    sign_prod_credentials,
    unwrap,
    wraps,
)

logger = logging.getLogger(__name__)


class PublishMixin(ExtraButtonsMixin):
    def get_serializer(self, fmt):
        return get_serializer(fmt)()

    def _get_data(self, record) -> str:
        return get_data_structure(record)

    @view(decorators=[csrf_exempt], http_basic_auth=True, enabled=is_production)
    def check_login(self, request):
        response = JsonResponse({"user": request.user.username})
        set_cookie(response, "editor_logged", "1")
        return response

    @view(decorators=[csrf_exempt], http_basic_auth=True, enabled=is_production)
    def production_logout(self, request):
        redir_url = request.build_absolute_uri(unquote_plus(request.GET.get("from", "..")))
        response = HttpResponseRedirect(redir_url)
        response.set_cookie(CREDENTIALS_COOKIE, "")
        return response

    def get_common_context(self, request, pk=None, **kwargs):
        kwargs["server"] = config.PRODUCTION_SERVER
        kwargs["prod_logout"] = local_reverse(admin_urlname(self.model._meta, "production_logout"))
        kwargs["prod_credentials"] = get_prod_credentials(request)
        kwargs["prod_login"] = local_reverse(admin_urlname(self.model._meta, "login_to_prod"))
        return super().get_common_context(request, pk, **kwargs)

    @view(enabled=is_editor)
    def login_to_prod(self, request):
        context = self.get_common_context(request, title=f"Login to production ({config.PRODUCTION_SERVER})")
        cookies = {}
        if request.method == "POST":
            form = ProductionLoginForm(data=request.POST)
            if form.is_valid():
                basic = HTTPBasicAuth(**form.cleaned_data)
                url = production_reverse(admin_urlname(self.model._meta, "check_login"))
                ret = requests.post(url, auth=basic)
                if ret.status_code == 200:
                    cookies[CREDENTIALS_COOKIE] = sign_prod_credentials(**form.cleaned_data)
                    data = ret.json()
                    self.message_user(request, f"Logged in to {config.PRODUCTION_SERVER} as {data['user']}")
                    if "from" in request.GET:
                        redir_url = request.build_absolute_uri(unquote_plus(request.GET["from"]))
                        response = HttpResponseRedirect(redir_url)
                        response.set_cookie(CREDENTIALS_COOKIE, cookies[CREDENTIALS_COOKIE])
                        return response
                else:
                    self.message_user(request, f"Login failed {ret} - {url}", messages.ERROR)
        else:
            form = ProductionLoginForm()
        context["form"] = form
        context["login_url"] = production_reverse(admin_urlname(self.model._meta, "check_login"))
        return render(request, "admin/publish/login_prod.html", context, cookies=cookies)

    @button(enabled=is_editor, change_list=True, order=999, permission=check_load_permission)
    def get_data(self, request):
        context = self.get_common_context(request, title="Load data from PRODUCTION", server=config.PRODUCTION_SERVER)
        if request.method == "POST":
            try:
                if not is_logged_to_prod(request):
                    raise PermissionError
                url = production_reverse(admin_urlname(self.model._meta, "dumpdata"))
                basic = HTTPBasicAuth(**get_prod_credentials(request))

                info = loaddata_from_url(url, basic, request.user, f"loaddata from {config.PRODUCTION_SERVER}")

                context["stdout"] = {"details": info}
                invalidate_cache()
                self.message_user(request, "Success", messages.SUCCESS)
                return render(request, "admin/publish/get_data_done.html", context)
            except PermissionError:
                url = local_reverse(admin_urlname(self.model._meta, "login_to_prod"))
                return HttpResponseRedirect(f"{url}?from={quote_plus(request.path)}")
            except Exception as e:
                logger.exception(e)
                self.message_error_to_user(request, e)
        else:
            if not is_logged_to_prod(request):
                url = local_reverse(admin_urlname(self.model._meta, "login_to_prod"))
                return HttpResponseRedirect(f"{url}?from={quote_plus(request.path)}")
            return render(request, "admin/publish/get_data.html", context)

    @view(decorators=[csrf_exempt], http_basic_auth=True, enabled=is_production)
    def dumpdata(self, request):
        try:
            data = []
            for r in self.model.objects.all():
                data.extend(json.loads(self._get_data(r)))
            return HttpResponse(wraps(json.dumps(data)), content_type="application/json")
        except Exception as e:
            logger.exception(e)
            self.message_error_to_user(request, e)
            return HttpResponseRedirect("..")

    @button(enabled=is_editor, order=999, permission=check_publish_permission)
    def publish(self, request, pk):
        context = self.get_common_context(request, pk, title="Publish to PRODUCTION", server=config.PRODUCTION_SERVER)
        if request.method == "POST":
            try:
                if not is_logged_to_prod(request):
                    raise PermissionError
                url = production_reverse(admin_urlname(self.model._meta, "receive"))
                basic = HTTPBasicAuth(**get_prod_credentials(request))
                record = self.get_object(request, pk)
                payload = self._get_data(record)

                ret = requests.post(url, data=wraps(payload), auth=basic)
                result = ret.json()
                context["stdout"] = result
                if ret.status_code == 200:
                    self.message_user(request, "Success", messages.SUCCESS)
                else:
                    self.message_user(request, "Error", messages.ERROR)
                return HttpResponseRedirect("../publish_done/done/")
                # return render(request, "admin/publish/publish_done.html", context)
            except PermissionError:
                url = local_reverse(admin_urlname(self.model._meta, "login_to_prod"))
                return HttpResponseRedirect(f"{url}?from={quote_plus(request.path)}")
            except Exception as e:
                logger.exception(e)
                self.message_error_to_user(request, e)
        else:
            return render(request, "admin/publish/publish.html", context)

    @view(decorators=[csrf_exempt], http_basic_auth=True)
    def receive(self, request):
        opts = self.model._meta
        out = io.StringIO()
        remote_ip = get_client_ip(request)
        try:
            data = unwrap(request.body.decode())
            workdir = Path(".").absolute()
            kwargs = {"dir": workdir, "prefix": f"~GET-{opts.model_name}", "suffix": ".json", "delete": False}
            with tempfile.NamedTemporaryFile(**kwargs) as fdst:
                assert isinstance(fdst.write, object)
                fdst.write(data.encode())
            fixture = (workdir / fdst.name).absolute()
            with disable_concurrency():
                with reversion.create_revision():
                    reversion.set_user(request.user)
                    reversion.set_comment(f"loaddata from {remote_ip}")
                    call_command("loaddata", fixture, stdout=out, stderr=out, verbosity=3)
            invalidate_cache()
            return JsonResponse(
                {
                    "message": "Done",
                    "details": out.getvalue(),
                },
                status=200,
            )
        except Exception as e:
            logger.exception(e)
            return JsonResponse(
                {
                    "error": str(e),
                    "details": out.getvalue(),
                },
                status=400,
            )

    @view(decorators=[csrf_exempt], http_basic_auth=True)
    def done(self, request, pk, tpl):
        context = self.get_common_context(request, pk)
        return render(request, f"admin/publish/{tpl}.html", context)

    def check_publish_permission(self, request, obj=None):
        return is_root(request.user)

    def check_load_permission(self, request, obj=None):
        return request.user.is_staff
