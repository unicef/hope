from django.contrib import admin

from hct_mis_api.apps.activity_log.models import LogEntry


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    pass
