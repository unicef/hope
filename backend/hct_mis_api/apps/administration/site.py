from django.core.cache import caches
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from constance import config
from smart_admin.site import SmartAdminSite

cache = caches["default"]


def clean(v):
    return v.replace(r"\n", "").strip()


def get_bookmarks(request):
    quick_links = []
    for entry in config.QUICK_LINKS.split("\n"):
        if entry := clean(entry):
            try:
                if entry == "--":
                    quick_links.append(mark_safe("<li><hr/></li>"))
                elif parts := entry.split(","):
                    args = None
                    if len(parts) == 1:
                        args = parts[0], "viewlink", parts[0], parts[0]
                    elif len(parts) == 2:
                        args = parts[0], "viewlink", parts[1], parts[0]
                    elif len(parts) == 3:
                        args = parts[0], "viewlink", parts[1], parts[0]
                    elif len(parts) == 4:
                        args = parts.reverse()
                    if args:
                        quick_links.append(format_html('<li><a target="{}" class="{}" href="{}">{}</a></li>', *args))
            except ValueError:
                pass
    return quick_links


class HopeAdminSite(SmartAdminSite):
    site_title = "HOPE"
    site_header = "HOPE Administration"
    index_title = "Index"


site = HopeAdminSite()
