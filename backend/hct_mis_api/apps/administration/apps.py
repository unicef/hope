import django.contrib.admin
from django.contrib.admin.apps import AppConfig, SimpleAdminConfig
from django.utils.module_loading import autodiscover_modules
from django.utils.translation import gettext_lazy as _

# from hct_mis_api.apps.administration.site import site
from smart_admin.apps import SmartConfig


class TemplateConfig(AppConfig):
    name = "hct_mis_api.apps.administration"


class Config(SmartConfig):
    default_site = "hct_mis_api.apps.administration.site.HopeAdminSite"
    # verbose_name = _("Smart Admin")
    # name = 'django.contrib.admin'

    def ready(self):
        super().ready()
        django.contrib.admin.autodiscover()
        self.module.autodiscover()
        # autodiscover_modules("admin", register_to=site)
