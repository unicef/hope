from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "hct_mis_api.apps.core"

    def ready(self):
        import hct_mis_api.apps.core.tasks.admin_areas  # noqa
