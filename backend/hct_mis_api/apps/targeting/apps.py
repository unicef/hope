from django.apps import AppConfig


class TargetingConfig(AppConfig):
    name = "hct_mis_api.apps.targeting"

    # noinspection PyUnresolvedReferences
    def ready(self):
        import hct_mis_api.apps.targeting.signals  # noqa: F401
