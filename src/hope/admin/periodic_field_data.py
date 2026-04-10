import logging

from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from hope.models import PeriodicFieldData

logger = logging.getLogger(__name__)


@admin.register(PeriodicFieldData)
class PeriodicFieldDataAdmin(UnfoldModelAdmin):
    list_filter = ("subtype", "number_of_rounds")
    list_display = ("__str__", "subtype", "number_of_rounds")
