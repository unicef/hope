from django.apps import AppConfig


class Config(AppConfig):
    name = "hct_mis_api.apps.ba_admin"

    def ready(self):
        from hct_mis_api.apps.core.models import BusinessArea

        from .models import BusinessAreaAdmin
        from .options import model_admin_registry
        from .site import ba_site

        for opt in model_admin_registry:
            ba_site.register(opt)
