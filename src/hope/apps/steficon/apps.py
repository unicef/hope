from django.apps import AppConfig


class SteficonConfig(AppConfig):
    name = "hope.apps.steficon"

    def ready(self) -> None:
        import hope.models  # noqa
