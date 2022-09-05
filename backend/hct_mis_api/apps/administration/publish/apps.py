import django.contrib.admin
from django.contrib.admin.apps import AppConfig

from smart_admin.apps import SmartConfig
from smart_admin.decorators import smart_register


class TemplateConfig(AppConfig):
    name = "hct_mis_api.apps.administration"


class Config(SmartConfig):
    name = "hct_mis_api.apps.administration.publish"

    def ready(self):
        pass
