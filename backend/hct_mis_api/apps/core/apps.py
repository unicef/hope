from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "hct_mis_api.apps.core"

    def ready(self) -> None:
        import hct_mis_api.apps.core.signals  # noqa: F401
