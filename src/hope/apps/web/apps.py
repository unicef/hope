from django.apps import AppConfig


class WebConfig(AppConfig):
    name = "hope.apps.web"

    def ready(self) -> None:
        import hope.models  # noqa
