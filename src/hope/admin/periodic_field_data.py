import logging

from django.contrib import admin

from hope.models.core import PeriodicFieldData

logger = logging.getLogger(__name__)


@admin.register(PeriodicFieldData)
class PeriodicFieldDataAdmin(admin.ModelAdmin):
    list_filter = ("subtype", "number_of_rounds")
    list_display = ("__str__", "subtype", "number_of_rounds")
