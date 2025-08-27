from django.apps import AppConfig


class ActivityLogConfig(AppConfig):
    name = "hope.apps.activity_log"

    def ready(self) -> None:
        import hope.models  # noqa
