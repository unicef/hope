import logging

from django.contrib import admin

from hope.admin.utils import AutocompleteForeignKeyMixin
from hope.models import PeriodicFieldData

logger = logging.getLogger(__name__)


@admin.register(PeriodicFieldData)
class PeriodicFieldDataAdmin(AutocompleteForeignKeyMixin, admin.ModelAdmin):
    list_filter = ("subtype", "number_of_rounds")
    list_display = ("__str__", "subtype", "number_of_rounds")
    search_fields = ("subtype",)
