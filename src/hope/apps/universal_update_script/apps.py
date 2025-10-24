from django.apps import AppConfig


class Config(AppConfig):
    name = "hope.apps.universal_update_script"

    def ready(self) -> None:
        pass
