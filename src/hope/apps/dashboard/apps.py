from django.apps import AppConfig


class DashboardConfig(AppConfig):
    name = "hope.apps.dashboard"

    def ready(self) -> None:
        import hope.models  # noqa
