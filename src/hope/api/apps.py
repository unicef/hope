from django.apps import AppConfig


class ApiConfig(AppConfig):
    name = "hope.api"

    def ready(self) -> None:
        import hope.models  # noqa
