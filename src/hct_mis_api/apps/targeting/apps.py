from django.apps import AppConfig


class TargetingConfig(AppConfig):
    name = "hct_mis_api.apps.targeting"

    def ready(self) -> None:
        import hct_mis_api.apps.targeting.signals  # noqa: F401
