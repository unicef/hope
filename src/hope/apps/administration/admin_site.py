from typing import TYPE_CHECKING, Any

from django.contrib import messages
from django.contrib.admin.models import LogEntry
from django.contrib.messages import add_message
from django.core.cache import cache as dj_cache, caches
from django.shortcuts import render
from django.urls import path
from unfold.sites import UnfoldAdminSite

from hope.apps.administration.forms import ClearCacheForm

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

cache = caches["default"]


def dashboard_callback(request: Any, context: dict[str, Any]) -> dict[str, Any]:
    context["recent_actions"] = LogEntry.objects.select_related("content_type", "user").order_by("-action_time")[:10]
    return context


# admin view
def clear_cache_view(request: "HttpRequest") -> "HttpResponse":
    template = "admin/clear_cache.html"
    ctx = {
        "title": "Clear Cache",
        "cache_keys": [],
        "is_root": False,
        "form": ClearCacheForm(),
    }

    if hasattr(dj_cache, "keys"):
        # skip name started with numbers
        ctx["cache_keys"] = [key for key in dj_cache.keys("*") if key[0].isalpha()]

        if request.user.is_superuser:
            ctx["is_root"] = True
            if request.POST:
                form = ClearCacheForm(request.POST)
                if form.is_valid():
                    selected_keys = [k for k, v in form.cleaned_data.items() if v is True]
                    for k in [key for key in dj_cache.keys("*") if key.startswith(tuple(selected_keys))]:
                        dj_cache.delete(k)

                    ctx["cache_keys"] = [key for key in dj_cache.keys("*") if key[0].isalpha()]
                    add_message(
                        request,
                        messages.SUCCESS,
                        f"Finished remove cache for: {selected_keys}",
                    )
            return render(request, template, ctx)
        add_message(
            request,
            messages.ERROR,
            "Access Not Allowed. Only superuser have access to clear cache",
        )
        return render(request, template, ctx)
    add_message(request, messages.ERROR, "Not Possible Clear Cache For Test Settings")
    return render(request, template, ctx)


class HopeAdminSite(UnfoldAdminSite):
    site_title = "HOPE"
    site_header = "HOPE Administration"
    index_title = "Index"

    def get_urls(self) -> list:
        from hope.apps.administration.panels import (
            email,
            panel_elasticsearch,
            panel_error_page,
            panel_migrations,
            panel_redis,
            panel_sentry,
            panel_sysinfo,
        )

        urls = super().get_urls()
        custom_urls = [
            path("clear-cache/", self.admin_view(clear_cache_view), name="clear_cache"),
            path(
                "panel/migrations/", self.admin_view(lambda req: panel_migrations(self, req)), name="panel_migrations"
            ),
            path("panel/sysinfo/", self.admin_view(lambda req: panel_sysinfo(self, req)), name="panel_sysinfo"),
            path("panel/email/", self.admin_view(lambda req: email(self, req)), name="panel_email"),
            path("panel/sentry/", self.admin_view(lambda req: panel_sentry(self, req)), name="panel_sentry"),
            path(
                "panel/error-page/", self.admin_view(lambda req: panel_error_page(self, req)), name="panel_error_page"
            ),
            path("panel/redis/", self.admin_view(lambda req: panel_redis(self, req)), name="panel_redis"),
            path(
                "panel/elasticsearch/",
                self.admin_view(lambda req: panel_elasticsearch(self, req)),
                name="panel_elasticsearch",
            ),
        ]
        return custom_urls + urls

    def get_app_list(self, request: "HttpRequest", app_label: str | None = None) -> list[dict[str, Any]]:
        app_list = super().get_app_list(request, app_label)
        for app in app_list:
            if isinstance(app.get("name"), str):
                app["name"] = app["name"].upper()
        return app_list
