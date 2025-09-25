from django.apps import AppConfig


class TargetingConfig(AppConfig):
    name = "hope.apps.targeting"

    def ready(self) -> None:
        import hope.models  # noqa
