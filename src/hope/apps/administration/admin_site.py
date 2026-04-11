from collections import OrderedDict
from typing import TYPE_CHECKING, Any

from constance import config
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.models import LogEntry
from django.contrib.messages import add_message
from django.core.cache import cache as dj_cache, caches
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.urls import path
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from unfold.sites import UnfoldAdminSite

from hope.apps.administration.forms import ClearCacheForm
from hope.apps.administration.section_utils import SmartList, as_bool

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

cache = caches["default"]


def dashboard_callback(request: Any, context: dict[str, Any]) -> dict[str, Any]:
    context["recent_actions"] = LogEntry.objects.select_related("content_type", "user").order_by("-action_time")[:10]
    return context


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
    smart_index_template = "admin/smart_index.html"

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
            path("smart/<str:on_off>/", self.admin_view(self.smart_toggle), name="smart_toggle"),
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

    def each_context(self, request: "HttpRequest") -> dict[str, Any]:
        context = super().each_context(request)
        context["smart"] = self.is_smart_enabled(request)
        return context

    def is_smart_enabled(self, request: "HttpRequest") -> bool:
        return as_bool(request.COOKIES.get("smart", "0"))

    def smart_toggle(self, request: "HttpRequest", on_off: str) -> HttpResponseRedirect:
        destination = request.GET.get("from", request.path)
        response = HttpResponseRedirect(destination)
        response.set_cookie("smart", str(int(as_bool(on_off))))
        return response

    @method_decorator(never_cache)
    def index(self, request: "HttpRequest", extra_context: dict[str, Any] | None = None) -> "HttpResponse":
        extra_context = {"show_changelinks": True, **(extra_context or {})}
        if self.is_smart_enabled(request):
            context = {
                **self.each_context(request),
                "groups": dict(self._get_menu(request)),
                "recent_actions": LogEntry.objects.select_related("content_type", "user").order_by("-action_time")[:10],
                **extra_context,
            }
            request.current_app = self.name
            return TemplateResponse(request, self.smart_index_template, context)
        return super().index(request, extra_context)

    def get_app_list(self, request: "HttpRequest", app_label: str | None = None) -> list[dict[str, Any]]:
        app_list = super().get_app_list(request, app_label)
        for app in app_list:
            if isinstance(app.get("name"), str):
                app["name"] = app["name"].upper()
        return app_list

    def _get_menu(self, request: "HttpRequest") -> "OrderedDict[str, list[dict[str, Any]]]":
        sections_source = getattr(settings, "HOPE_ADMIN_SECTIONS", {})
        sections: dict[str, SmartList] = {"_hidden_": SmartList()}
        for name, entries in sections_source.items():
            sections[name] = SmartList(entries)
        if "Other" not in sections:
            sections["Other"] = SmartList()

        groups: OrderedDict[str, list[dict[str, Any]]] = OrderedDict((k, []) for k in sections)
        app_list = self.get_app_list(request)

        def get_section(model_info: dict[str, Any], app: dict[str, Any]) -> str:
            fqn = f"{app['app_label']}.{model_info['object_name']}"
            if fqn in sections["_hidden_"] or app["app_label"] in sections["_hidden_"]:
                return "_hidden_"
            for sec_name, sec_entries in sections.items():
                if fqn in sec_entries or app["app_label"] in sec_entries:
                    return sec_name
            return "Other"

        for app in app_list:
            for model_info in app["models"]:
                section_name = get_section(model_info, app)
                groups[section_name].append(
                    {
                        "app_label": str(app["app_label"]),
                        "app_name": str(app["name"]),
                        "app_url": app["app_url"],
                        "label": f"{app['name']} - {model_info['name']}",
                        "model_name": str(model_info["name"]),
                        "admin_url": model_info["admin_url"],
                        "perms": model_info["perms"],
                    }
                )

        for items in groups.values():
            items.sort(key=lambda x: x["label"])

        return groups
