from django.apps import AppConfig


class GrievanceConfig(AppConfig):
    name = "hope.apps.grievance"

    def ready(self) -> None:
        import hope.models  # noqa
