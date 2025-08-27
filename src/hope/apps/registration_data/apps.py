from django.apps import AppConfig


class RegistrationDataConfig(AppConfig):
    name = "hope.apps.registration_data"

    def ready(self) -> None:
        import hope.apps.registration_data.signals  # noqa: F401

        import hope.models  # noqa
