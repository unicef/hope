from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.mixin import AdminFiltersMixin
from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from hope.contrib.aurora import models


@admin.register(models.Organization)
class OrganizationAdmin(AdminFiltersMixin, UnfoldModelAdmin):
    search_fields = ("name", "slug")
    list_display = ("name", "slug", "business_area")
    readonly_fields = (
        "name",
        "slug",
    )
    list_filter = (("business_area", AutoCompleteFilter),)
