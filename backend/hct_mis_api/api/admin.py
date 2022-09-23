from django.contrib import admin

from adminfilters.autocomplete import AutoCompleteFilter
from smart_admin.modeladmin import SmartModelAdmin

from hct_mis_api.api.models import APIToken


@admin.register(APIToken)
class APITokenAdmin(SmartModelAdmin):
    list_display = ("user", "valid_from", "valid_to")
    list_filter = (("user", AutoCompleteFilter),)
    filter_horizontal = ("valid_for",)
    readonly_fields = ("key",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")
