import logging
from typing import Any, Dict, Optional, Type

from django import forms
from django.contrib import admin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import ExtraButtonsMixin
from smart_admin.decorators import smart_register

from hct_mis_api.apps.program.models import Program
from hct_mis_api.aurora import models
from hct_mis_api.aurora.forms import FetchForm
from hct_mis_api.aurora.utils import fetch_records, get_metadata

logger = logging.getLogger(__name__)


@smart_register(models.Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "business_area")
    readonly_fields = (
        "name",
        "slug",
    )


class ProjectForm(forms.ModelForm):
    def clean(self) -> Optional[Dict[str, Any]]:
        cleaned_data = self.cleaned_data
        organization = self.cleaned_data["organization"]
        programme = self.cleaned_data["programme"]

        if organization.business_area != programme.business_area:
            msg = "BusinessArea of organization is different than BusinessArea of programme."
            self.add_error("organization", msg)
        return cleaned_data


@smart_register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "organization")
    list_filter = ("organization", "programme")
    form = ProjectForm

    def get_form(
        self, request: HttpRequest, obj: Optional[models.Project] = None, change: bool = False, **kwargs: Any
    ) -> Type[forms.ModelForm]:
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["programme"].queryset = Program.objects.filter(
            status=Program.ACTIVE,
            data_collecting_type__isnull=False,
        ).exclude(data_collecting_type__code="unknown")
        return form


@smart_register(models.Registration)
class RegistrationAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    list_display = ("name", "project", "rdi_policy", "project")
    readonly_fields = ("name", "project", "slug", "extra", "metadata")
    list_filter = ("rdi_policy", "project")
    raw_id_fields = ("steficon_rule",)


class RecordMixinAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    @button()
    def fetch_aurora(self, request: HttpRequest) -> HttpResponse:
        ctx = self.get_common_context(request)
        if request.method == "POST":
            form = FetchForm(request.POST)
            aurora_token = request.user.custom_fields.get("aurora_token")
            if "detect" in request.POST:
                ctx["metadata"] = get_metadata(aurora_token)
            elif form.is_valid():
                filters = {
                    "id": form.cleaned_data.get("from_id", "") or "",
                    "after": form.cleaned_data.get("after_date", "") or "",
                }
                if form.cleaned_data["registration"]:
                    filters["registration"] = form.cleaned_data["registration"].source_id
            info = fetch_records(aurora_token, form.cleaned_data["overwrite"], **filters)
            ctx["info"] = info
        else:
            form = FetchForm()

        ctx["form"] = form
        return render(request, "admin/aurora/record/fetch.html", ctx)
