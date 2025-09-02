from django.apps import AppConfig


class UtilsConfig(AppConfig):
    name = "hope.apps.utils"

    def ready(self) -> None:
        import hope.models  # noqa
