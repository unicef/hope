from django.contrib import admin
from django.contrib.admin.apps import AdminConfig


class Config(AdminConfig):
    default_site = "hope.apps.administration.admin_site.HopeAdminSite"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        super().ready()

        from django.contrib.admin.models import LogEntry
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType

        from hope.admin.compat import ContentTypeAdmin, PermissionAdmin
        from hope.admin.log_entry import LogEntryAdmin

        admin.site.register(ContentType, ContentTypeAdmin)
        admin.site.register(LogEntry, LogEntryAdmin)
        admin.site.register(Permission, PermissionAdmin)

        from adminactions import tasks  # noqa
