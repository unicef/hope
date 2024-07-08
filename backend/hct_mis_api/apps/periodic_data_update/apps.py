from django.apps import AppConfig


class PeriodicDataUpdateConfig(AppConfig):
    name = "hct_mis_api.apps.periodic_data_update"

    def ready(self) -> None:
        import hct_mis_api.apps.periodic_data_update.signals  # noqa: F401
