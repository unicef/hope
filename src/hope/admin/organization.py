from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.mixin import AdminFiltersMixin
from django.contrib import admin
from smart_admin.decorators import smart_register

from hope.contrib.aurora import models


@smart_register(models.Organization)
class OrganizationAdmin(AdminFiltersMixin, admin.ModelAdmin):
    search_fields = ("name", "slug")
    list_display = ("name", "slug", "business_area")
    readonly_fields = (
        "name",
        "slug",
    )
    list_filter = (("business_area", AutoCompleteFilter),)
