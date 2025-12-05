from django.apps import AppConfig


class Config(AppConfig):
    name = "hope.apps.generic_import"

    def ready(self) -> None:
        pass
