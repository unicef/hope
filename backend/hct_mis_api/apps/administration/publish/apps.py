from django.contrib.admin.apps import AppConfig

from smart_admin.apps import SmartConfig


class TemplateConfig(AppConfig):
    name = "hct_mis_api.apps.administration"


class Config(SmartConfig):
    name = "hct_mis_api.apps.administration.publish"

    def ready(self):
        pass
