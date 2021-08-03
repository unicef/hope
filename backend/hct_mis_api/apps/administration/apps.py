import django.contrib.admin
from django.contrib.admin.apps import SimpleAdminConfig
from django.utils.module_loading import autodiscover_modules
from django.utils.translation import gettext_lazy as _

from hct_mis_api.apps.administration.site import site


class Config(SimpleAdminConfig):
    default_site = "hct_mis_api.apps.administration.site.HopeAdminSite"
    verbose_name = _("Smart Admin")

    def ready(self):
        super().ready()
        django.contrib.admin.autodiscover()
        autodiscover_modules("admin", register_to=site)
