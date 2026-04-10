from typing import TYPE_CHECKING, Any

from constance import config
from django.contrib import messages
from django.contrib.messages import add_message
from django.core.cache import cache as dj_cache, caches
from django.shortcuts import render
from django.urls import path
from unfold.sites import UnfoldAdminSite

from hope.apps.administration.forms import ClearCacheForm

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

cache = caches["default"]


def clean(v: str) -> str:
    return v.replace(r"\n", "").strip()


def site_dropdown_callback(request: Any) -> list[dict[str, Any]]:
    """Return Constance QUICK_LINKS as Unfold SITE_DROPDOWN items.

    Replaces the smart_admin SMART_ADMIN_BOOKMARKS mechanism. Each non-empty
    line in `QUICK_LINKS` becomes a dropdown entry. Supported formats:

        title,url        → entry rendered as a link
        url              → entry where title and url are the same
        --               → ignored (smart_admin used this as a separator;
                            Unfold's dropdown does not support separators)
    """
    items: list[dict[str, Any]] = []
    for raw in config.QUICK_LINKS.split("\n"):
        entry = clean(raw)
        if not entry or entry == "--":
            continue
        parts = [p.strip() for p in entry.split(",") if p.strip()]
        if not parts:
            continue
        if len(parts) == 1:
            title = link = parts[0]
        else:
            title, link = parts[0], parts[1]
        items.append(
            {
                "title": title,
                "link": link,
                "attrs": {"target": "_blank", "rel": "noopener"},
            }
        )
    return items


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
            path("panel/migrations/", self.admin_view(lambda req: panel_migrations(self, req)), name="panel_migrations"),
            path("panel/sysinfo/", self.admin_view(lambda req: panel_sysinfo(self, req)), name="panel_sysinfo"),
            path("panel/email/", self.admin_view(lambda req: email(self, req)), name="panel_email"),
            path("panel/sentry/", self.admin_view(lambda req: panel_sentry(self, req)), name="panel_sentry"),
            path("panel/error-page/", self.admin_view(lambda req: panel_error_page(self, req)), name="panel_error_page"),
            path("panel/redis/", self.admin_view(lambda req: panel_redis(self, req)), name="panel_redis"),
            path("panel/elasticsearch/", self.admin_view(lambda req: panel_elasticsearch(self, req)), name="panel_elasticsearch"),
        ]
        return custom_urls + urls
