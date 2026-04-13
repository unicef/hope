"""Console panel views — local replacements for smart_admin.console panels.

Each function is an admin view callable with signature:
    (admin_site, request, extra_context=None) -> HttpResponse
They are registered on HopeAdminSite.get_urls().
"""

from functools import partial
import io
import logging
from urllib.parse import ParseResult, urlparse

from admin_extra_buttons.utils import HttpResponseRedirectToReferrer
from django import forms
from django.conf import settings
from django.conf.urls import handler400, handler403, handler404, handler500
from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.management import call_command
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.html import urlize
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import cache_page

logger = logging.getLogger(__name__)


# ── Migrations ──────────────────────────────────────────────


def panel_migrations(self, request):
    out = io.StringIO()
    call_command("showmigrations", stdout=out, no_color=True, format="list")
    context = self.each_context(request)
    context["list"] = out.getvalue()
    out = io.StringIO()
    call_command("showmigrations", stdout=out, no_color=True, format="plan")
    context["plan"] = out.getvalue()
    return render(request, "administration/panels/migrations.html", context)


panel_migrations.verbose_name = _("Migrations")
panel_migrations.url_name = "migrations"


# ── Sysinfo ─────────────────────────────────────────────────


def panel_sysinfo(self, request) -> HttpResponse:
    @cache_page(0)
    def _sysinfo(request):
        from django_sysinfo.api import get_sysinfo

        infos = get_sysinfo(request)
        infos.setdefault("extra", {})
        infos.setdefault("checks", {})
        context = self.each_context(request)
        context.update(
            {
                "title": "sysinfo",
                "infos": infos,
                "enable_switch": True,
                "has_permission": True,
            }
        )
        return render(request, "administration/panels/sysinfo.html", context)

    return _sysinfo(request)


panel_sysinfo.verbose_name = _("System Info")
panel_sysinfo.url_name = "sysinfo"


# ── Redis ───────────────────────────────────────────────────


class RedisCLIForm(forms.Form):
    command = forms.CharField()
    connection = forms.ChoiceField(choices=zip(settings.CACHES.keys(), settings.CACHES.keys(), strict=False))


def panel_redis(self, request, extra_context=None):
    try:
        from django_redis import get_redis_connection
        from redis import ResponseError
    except ImportError as exc:
        messages.add_message(request, messages.ERROR, f"{exc.__class__.__name__}: {exc}. Please remove `panel_redis`")
        return HttpResponseRedirectToReferrer(request)

    context = self.each_context(request)
    context["title"] = "Redis CLI"
    if request.method == "POST":
        form = RedisCLIForm(request.POST)
        if form.is_valid():
            r = get_redis_connection(form.cleaned_data["connection"])
            kwargs = r.get_connection_kwargs()
            context["redis"] = r
            context["connection_kwargs"] = kwargs
            try:
                stdout = r.execute_command(form.cleaned_data["command"])
                context["stdout"] = stdout
            except ResponseError as e:
                messages.add_message(request, messages.ERROR, str(e))
            except Exception as e:
                logger.exception(e)
                messages.add_message(request, messages.ERROR, f"{e.__class__.__name__}: {e}")
    else:
        form = RedisCLIForm()
    context["form"] = form
    return render(request, "administration/panels/redis.html", context)


panel_redis.verbose_name = _("Redis CLI")


# ── Sentry ──────────────────────────────────────────────────


def get_sentry_host():
    result: ParseResult = urlparse(settings.SENTRY_DSN)
    host = f"{result.scheme}://{result.hostname}"
    if result.port:
        host = f"{host}:{result.port}"
    return host


def get_sentry_dashboard():
    if getattr(settings, "SENTRY_PROJECT", None):
        return f"{get_sentry_host()}/{settings.SENTRY_PROJECT}"
    return "N/A"


def get_event_url(event_id):
    try:
        return f"{get_sentry_host()}/{settings.SENTRY_PROJECT}/?query={event_id}"
    except AttributeError as e:
        logger.exception(e)


def make_sentry_link(event_id):
    if getattr(settings, "SENTRY_PROJECT", "") and (url := get_event_url(event_id)):
        return f'<a href="{url}">{event_id}</a>'
    return event_id


class SentryForm(forms.Form):
    ACTIONS = [
        ("capture_event", "capture_event()"),
        ("capture_exception", "capture_exception"),
        ("capture_message", "capture_message"),
        ("logging_integration", "logging_integration"),
        ("400", "Error 400"),
        ("403", "Error 403"),
        ("404", "Error 404"),
        ("500", "Error 500"),
    ]
    action = forms.ChoiceField(choices=ACTIONS, widget=forms.RadioSelect)


def panel_sentry(self, request, extra_context=None):
    try:
        import sentry_sdk
    except ImportError as exc:
        messages.add_message(request, messages.ERROR, f"{exc.__class__.__name__}: {exc}. Please remove `panel_sentry`.")
        return HttpResponseRedirectToReferrer(request)
    context = self.each_context(request)
    context["title"] = "Sentry"
    try:
        context["info"] = {
            "SENTRY_DSN": settings.SENTRY_DSN,
            "SENTRY_SERVER_URL": mark_safe(urlize(get_sentry_host())),  # noqa: S308
            "SENTRY_DASHBOARD": mark_safe(urlize(get_sentry_dashboard())),  # noqa: S308
            "SENTRY_PROJECT": getattr(settings, "SENTRY_PROJECT", "N/A") or "N/A",
            "SENTRY_ENVIRONMENT": getattr(settings, "SENTRY_ENVIRONMENT", "N/A") or "N/A",
        }
    except AttributeError:
        messages.add_message(request, messages.ERROR, "Sentry not configured. Please remove 'panel_sentry'.")
        return HttpResponseRedirect(reverse("admin:index"))

    if request.method == "POST":
        form = SentryForm(request.POST)
        if form.is_valid():
            last_event_id = None
            opt = form.cleaned_data["action"]
            if opt == "capture_event":
                last_event_id = sentry_sdk.capture_event({"capture_event() Test": 1})
            elif opt == "capture_exception":
                last_event_id = sentry_sdk.capture_exception(Exception("capture_exception() Test"))
            elif opt == "capture_message":
                last_event_id = sentry_sdk.capture_message("capture_message() Test")
            elif opt == "logging_integration":
                try:
                    raise Exception("Logging Integration/last_event_id() Test")
                except Exception as e:
                    logger.exception(e)
                    last_event_id = sentry_sdk.last_event_id()
            else:
                mapping = {
                    "400": (ValidationError, handler400),
                    "403": (PermissionDenied, handler403),
                    "404": (Http404, handler404),
                    "500": (Exception, handler500),
                }
                error, handler = mapping[opt]
                try:
                    raise error(f"Error {opt} Test")
                except Exception as e:
                    logger.exception(e)
                    last_event_id = sentry_sdk.last_event_id()
                    handler(request, e)
            messages.add_message(request, messages.SUCCESS, mark_safe(f"Sentry ID: {make_sentry_link(last_event_id)}"))  # noqa: S308
    else:
        form = SentryForm()
    context["form"] = form
    return render(request, "administration/panels/sentry.html", context)


panel_sentry.verbose_name = _("Sentry")
panel_sentry.url_name = "sentry"


# ── Error Pages ─────────────────────────────────────────────


class ErrorPageForm(forms.Form):
    ACTIONS = [
        ("400", "Error 400"),
        ("403", "Error 403"),
        ("404", "Error 404"),
        ("500", "Error 500"),
    ]
    action = forms.ChoiceField(choices=ACTIONS, widget=forms.RadioSelect)


def panel_error_page(self, request, extra_context=None):
    context = self.each_context(request)
    context["title"] = _("Error Pages")
    if request.method == "POST":
        form = ErrorPageForm(request.POST)
        if form.is_valid():
            opt = form.cleaned_data["action"]
            if opt in ["400", "403", "404", "500"]:
                mapping = {
                    "400": (ValidationError, partial(handler400, exception=ValidationError("Test Error"))),
                    "403": (ValidationError, partial(handler403, exception=PermissionDenied())),
                    "404": (ValidationError, partial(handler404, exception=Http404())),
                    "500": (ValidationError, partial(handler500)),
                }
                error, handler = mapping[opt]
                return handler(request)
    else:
        form = ErrorPageForm()
    context["form"] = form
    return render(request, "administration/panels/sentry.html", context)


panel_error_page.verbose_name = _("Error Pages")
panel_error_page.url_name = "error_page"
