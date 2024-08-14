from django.apps import AppConfig


class RegistrationDataConfig(AppConfig):
    name = "hct_mis_api.apps.registration_data"

    def ready(self) -> None:
        import hct_mis_api.apps.registration_data.signals  # noqa: F401
