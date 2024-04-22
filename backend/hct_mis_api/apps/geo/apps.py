from django.apps import AppConfig


class Config(AppConfig):
    name = "hct_mis_api.apps.geo"

    def ready(self):
        from hct_mis_api.apps.geo import signals as area_signals
