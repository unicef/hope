from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "hct_mis_api.apps.core"

    def ready(self):
        from django.contrib.admin import site

        import hct_mis_api.apps.core.tasks.admin_areas  # noqa

        site.site_title = "HOPE"
        site.site_header = "HOPE Administration"
        site.index_title = "Index"
