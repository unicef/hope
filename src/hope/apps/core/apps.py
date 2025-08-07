from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "hope.apps.core"

    def ready(self) -> None:
        import hope.apps.core.signals  # noqa: F401
