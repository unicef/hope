from django.apps import AppConfig


class GrievanceConfig(AppConfig):
    name = "hope.apps.grievance"

    def ready(self) -> None:
        import hope.apps.grievance.signals  # noqa: F401
