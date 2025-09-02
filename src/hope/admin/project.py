from typing import Any

from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.mixin import AdminFiltersMixin
from django import forms
from django.contrib import admin
from django.http import HttpRequest
from smart_admin.decorators import smart_register

from hope.contrib.aurora import models
from hope.models.program import Program


@smart_register(models.Project)
class ProjectAdmin(AdminFiltersMixin, admin.ModelAdmin):
    list_display = ("name", "organization", "programme")
    list_filter = (
        ("organization", AutoCompleteFilter),
        ("programme", AutoCompleteFilter),
    )
    readonly_fields = ("name", "organization")
    search_fields = ("name",)
    raw_id_fields = ("programme",)

    def get_form(
        self, request: HttpRequest, obj: models.Project | None = None, change: bool = False, **kwargs: Any
    ) -> type[forms.ModelForm]:
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["programme"].queryset = Program.objects.filter(
            business_area=obj.organization.business_area,
            status=Program.ACTIVE,
            data_collecting_type__isnull=False,
            data_collecting_type__deprecated=False,
        ).exclude(data_collecting_type__code="unknown")
        return form
