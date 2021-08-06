from django.conf import settings
from django.core.cache import caches

from constance import config
from smart_admin.site import SmartAdminSite

cache = caches["default"]


def clean(v):
    return v.replace(r"\n", "").strip()


def get_bookmarks(request):
    quick_links = []
    for entry in config.QUICK_LINKS.split(";"):
        if clean(entry):
            try:
                label, url = entry.split(",")
                quick_links.append([clean(label), clean(url)])
            except ValueError:
                pass
    return quick_links


class HopeAdminSite(SmartAdminSite):
    site_title = "HOPE"
    site_header = "HOPE Administration"
    index_title = "Index"


site = HopeAdminSite()
