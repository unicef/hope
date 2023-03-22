from django.apps import AppConfig


class Config(AppConfig):
    name = "hct_mis_api.aurora"

    def ready(self) -> None:
        from . import admin  # noqa
