from django.apps import AppConfig


class Config(AppConfig):
    name = "hct_mis_api.apps.universal_update_script"

    def ready(self) -> None:
        pass
