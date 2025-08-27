from django.apps import AppConfig


class PeriodicDataUpdateConfig(AppConfig):
    name = "hope.apps.periodic_data_update"

    def ready(self) -> None:
        import hope.apps.periodic_data_update.signals  # noqa: F401

        import hope.models  # noqa
