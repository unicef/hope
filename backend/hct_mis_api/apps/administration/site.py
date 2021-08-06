from django.conf import settings
from django.core.cache import caches

from constance import config
from smart_admin.site import SmartAdminSite

cache = caches["default"]


def get_bookmarks(request):
    quick_links = []
    for entry in config.QUICK_LINKS.split(";"):
        if entry:
            try:
                quick_links.append(entry.split(","))
            except ValueError:
                pass
    return quick_links


class HopeAdminSite(SmartAdminSite):
    site_title = "HOPE"
    site_header = "HOPE Administration"
    index_title = "Index"


site = HopeAdminSite()
