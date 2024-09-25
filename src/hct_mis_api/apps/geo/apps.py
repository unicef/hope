from django.apps import AppConfig


class Config(AppConfig):
    name = "hct_mis_api.apps.geo"

    def ready(self) -> None:
        import hct_mis_api.apps.geo.signals  # noqa: F401
