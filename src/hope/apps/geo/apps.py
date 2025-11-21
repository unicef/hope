from django.apps import AppConfig


class Config(AppConfig):
    name = "hope.apps.geo"

    def ready(self) -> None:
        import hope.apps.geo.signals  # noqa: F401
        import hope.models  # noqa
