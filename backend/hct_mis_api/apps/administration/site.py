from django.conf import settings
from django.core.cache import caches

from constance import config
from smart_admin.site import SmartAdminSite

cache = caches["default"]


class HopeAdminSite(SmartAdminSite):
    def each_context(self, request):
        context = super().each_context(request)
        quick_links = {}
        for entry in config.QUICK_LINKS.split(";"):
            try:
                label, url = entry.split(",")
                quick_links[label] = url
            except ValueError:
                pass

        context["quick_links"] = quick_links
        return context


site = HopeAdminSite()
