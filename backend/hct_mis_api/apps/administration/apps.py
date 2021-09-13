import django.contrib.admin
from django.contrib.admin.apps import AppConfig, SimpleAdminConfig
from django.utils.module_loading import autodiscover_modules
from django.utils.translation import gettext_lazy as _

# from hct_mis_api.apps.administration.site import site
from smart_admin.apps import SmartConfig
from smart_admin.decorators import smart_register


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
        from django.contrib.admin.models import LogEntry
        from django.contrib.contenttypes.models import ContentType

        from smart_admin.smart_auth.admin import ContentTypeAdmin

        from .admin import LogEntryAdmin

        smart_register(ContentType)(ContentTypeAdmin)
        smart_register(LogEntry)(LogEntryAdmin)
