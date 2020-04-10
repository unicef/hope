from django.apps import AppConfig


class TargetingConfig(AppConfig):
    name = "targeting"

    # noinspection PyUnresolvedReferences
    def ready(self):
        import targeting.signals
