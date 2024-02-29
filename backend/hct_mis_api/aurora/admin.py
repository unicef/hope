import base64
from typing import Any, Generator, Optional, Type
from uuid import UUID

from django import forms
from django.contrib import admin, messages
from django.contrib.admin.views.main import ChangeList
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

import requests
from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import ExtraButtonsMixin
from adminactions.mass_update import mass_update
from adminfilters.combo import ChoicesFieldComboFilter
from adminfilters.depot.widget import DepotManager
from adminfilters.json import JsonFieldFilter
from adminfilters.numbers import NumberFilter
from adminfilters.querystring import QueryStringFilter
from requests.auth import HTTPBasicAuth
from smart_admin.decorators import smart_register

from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase
from hct_mis_api.apps.utils.security import is_root
from hct_mis_api.aurora import models
from hct_mis_api.aurora.celery_tasks import fresh_extract_records_task
from hct_mis_api.aurora.forms import FetchForm
from hct_mis_api.aurora.models import Record, Registration
from hct_mis_api.aurora.services.extract_record import extract
from hct_mis_api.aurora.services.flex_registration_service import (
    create_task_for_processing_records,
)
from hct_mis_api.aurora.utils import fetch_records, get_metadata


class StatusFilter(ChoicesFieldComboFilter):
    def choices(self, changelist: ChangeList) -> Generator:
        yield {
            "selected": self.lookup_val is None,
            "query_string": changelist.get_query_string(remove=[self.lookup_kwarg, self.lookup_kwarg_isnull]),
            "display": _("All"),
        }
        for lookup, title in self.field.flatchoices:
            if lookup == Record.STATUS_TO_IMPORT:
                yield {
                    "selected": bool(self.lookup_val_isnull),
                    "query_string": changelist.get_query_string(
                        {self.lookup_kwarg_isnull: "True"}, [self.lookup_kwarg]
                    ),
                    "display": title,
                }
            else:
                yield {
                    "selected": str(lookup) == self.lookup_val,
                    "query_string": changelist.get_query_string(
                        {self.lookup_kwarg: lookup}, [self.lookup_kwarg_isnull]
                    ),
                    "display": title,
                }


@smart_register(models.Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "business_area")
    readonly_fields = (
        "name",
        "slug",
    )


@smart_register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "organization")
    list_filter = ("organization", "programme")
    readonly_fields = ("name", "organization")

    def get_form(
        self, request: HttpRequest, obj: Optional[models.Project] = None, change: bool = False, **kwargs: Any
    ) -> Type[forms.ModelForm]:
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["programme"].queryset = Program.objects.filter(
            business_area=obj.organization.business_area,
            status=Program.ACTIVE,
            data_collecting_type__isnull=False,
            data_collecting_type__deprecated=False,
        ).exclude(data_collecting_type__code="unknown")
        return form


@smart_register(models.Registration)
class RegistrationAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    list_display = ("name", "project", "rdi_policy", "project")
    readonly_fields = ("name", "project", "slug", "extra", "metadata")
    list_filter = ("rdi_policy", "project")
    raw_id_fields = ("steficon_rule",)


class BaseRDIForm(forms.Form):
    STATUS_TO_IMPORT = "TO_IMPORT"
    STATUS_IMPORTED = "IMPORTED"
    STATUS_ERROR = "ERROR"
    ANY = "ANY"

    STATUSES_CHOICES = (
        (STATUS_TO_IMPORT, "To import"),
        (STATUS_ERROR, "Error"),
    )
    STATUSES_ROOT_CHOICES = (
        (STATUS_IMPORTED, "Imported"),
        (ANY, "Any"),
    )
    registration = forms.ModelChoiceField(
        label="Registration",
        required=True,
        queryset=Registration.objects.all(),
        help_text="Registration to be used",
    )
    filters = forms.CharField(
        widget=forms.Textarea,
        required=False,
        help_text="filters to use to select the records (Uses Django filtering syntax)",
    )
    status = forms.ChoiceField(label="Record status", required=True, choices=STATUSES_CHOICES)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if request := kwargs.pop("request", None):
            if is_root(request):
                self.base_fields["status"].choices = self.STATUSES_CHOICES + self.STATUSES_ROOT_CHOICES
        super().__init__(*args, **kwargs)

    def clean_filters(self) -> QueryStringFilter:
        filter = QueryStringFilter(None, {}, Record, None)
        return filter.get_filters(self.cleaned_data["filters"])

    def clean(self) -> None:
        super().clean()
        filters, excludes = self.cleaned_data["filters"]
        if self.cleaned_data["status"] == Record.STATUS_TO_IMPORT:
            filters["status__isnull"] = True
        elif self.cleaned_data["status"] in [Record.STATUS_IMPORTED, Record.STATUS_ERROR]:
            filters["status"] = self.cleaned_data["status"]

        self.cleaned_data["filters"] = filters, excludes


class CreateRDIForm(BaseRDIForm):
    name = forms.CharField(label="RDI name", max_length=100, required=False, help_text="[Business Area] RDI Name")
    is_open = forms.BooleanField(label="Is open?", help_text="Is the RDI open for amend", required=False)
    field_order = ["name", "registration", "is_open", "filters", "status"]


class AmendRDIForm(BaseRDIForm):
    rdi = forms.ModelChoiceField(
        label="RDI",
        required=False,
        queryset=RegistrationDataImport.objects.filter(status=RegistrationDataImport.LOADING),
        help_text="can select and update existing RDI within status 'Loading'",
    )

    field_order = ["rdi", "registration", "filters"]


class RecordMixinAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    list_display = ("id", "registration", "timestamp", "source_id", "status", "ignored")
    readonly_fields = (
        "id",
        "registration",
        "timestamp",
        "source_id",
        # "registration_data_import",
        "status",
        "error_message",
    )
    # list_editable = ("ignored",)
    exclude = ("data",)
    date_hierarchy = "timestamp"
    list_filter = (
        DepotManager,
        # ("registration_data_import", AutoCompleteFilter),
        ("status", StatusFilter),
        ("source_id", NumberFilter),
        ("id", NumberFilter),
        ("data", JsonFieldFilter),
        QueryStringFilter,
    )
    change_form_template = "registration_datahub/admin/record/change_form.html"
    # change_list_template = "registration_datahub/admin/record/change_list.html"

    actions = [mass_update, "extract", "async_extract", "create_rdi", "create_sr_lanka_rdi", "count_queryset"]

    mass_update_exclude = ["pk", "data", "source_id", "registration", "timestamp"]
    mass_update_hints = []

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

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        return is_root(request)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        qs = super().get_queryset(request)
        qs = qs.defer("storage", "data", "files")
        return qs

    @admin.action(description="Async extract")
    def async_extract(self, request: HttpRequest, queryset: QuerySet) -> None:
        try:
            records_ids = queryset.values_list("id", flat=True)
            fresh_extract_records_task.delay(list(records_ids))
            self.message_user(request, f"Extracting data for {len(records_ids)} records", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, str(e), messages.ERROR)

    @button(label="Extract")
    def extract_single(self, request: HttpRequest, pk: UUID) -> None:
        records_ids = Record.objects.filter(pk=pk).values_list("pk", flat=True)
        try:
            extract(records_ids, raise_exception=True)
        except Exception as e:
            self.message_error_to_user(request, e)

    @button()
    def create_new_rdi(self, request: HttpRequest) -> HttpResponse:
        ctx = self.get_common_context(request, title="Create RDI")
        if request.method == "POST":
            form = CreateRDIForm(request.POST, request=request)
            if form.is_valid():
                registration = form.cleaned_data["registration"]
                name = form.cleaned_data["name"]
                is_open = form.cleaned_data["is_open"]
                filters, exclude = form.cleaned_data["filters"]
                ctx["filters"] = filters
                ctx["exclude"] = exclude
                if service := registration.rdi_parser:
                    qs = (
                        Record.objects.defer("storage", "counters", "files", "fields")
                        .filter(**filters)
                        .exclude(**exclude)
                    )
                    if records_ids := qs.values_list("id", flat=True):
                        try:
                            project = registration.project
                            organization = project.organization
                            rdi_name = name or {timezone.now()}
                            rdi = service.create_rdi(
                                imported_by=request.user,
                                rdi_name=f"{organization.slug} rdi {rdi_name}",
                                is_open=is_open,
                            )
                            create_task_for_processing_records(service, registration.pk, rdi.pk, list(records_ids))
                            url = reverse("admin:registration_data_registrationdataimport_change", args=[rdi.pk])
                            self.message_user(
                                request,
                                mark_safe("Started RDI Import with name: <a href='{}'>{}</a>").format(url, rdi.name),
                                messages.SUCCESS,
                            )
                        except Exception as e:
                            self.message_error_to_user(request, e)

                    else:
                        self.message_user(request, "There are no Records by filtering criteria", messages.ERROR)
                else:
                    self.message_user(
                        request,
                        "Selected registration doesn't have any strategy service associated.",
                        messages.ERROR,
                    )
        else:
            form = CreateRDIForm(request=request)

        ctx["form"] = form
        return render(request, "registration_datahub/admin/record/create_rdi.html", ctx)

    @button()
    def add_to_existing_rdi(self, request: HttpRequest) -> HttpResponse:
        ctx = self.get_common_context(request, title="Add to existing RDI")

        if request.method == "POST":
            form = AmendRDIForm(request.POST, request=request)
            if form.is_valid():
                registration = form.cleaned_data["registration"]
                rdi = form.cleaned_data.get("rdi")
                filters, exclude = form.cleaned_data["filters"]
                ctx["filters"] = filters
                ctx["exclude"] = exclude
                if service := registration.rdi_parser:
                    qs = (
                        Record.objects.defer("storage", "counters", "files", "fields")
                        .filter(**filters)
                        .exclude(**exclude)
                    )
                    if records_ids := qs.values_list("id", flat=True):
                        try:
                            create_task_for_processing_records(service, registration.pk, rdi.pk, list(records_ids))
                            url = reverse("admin:registration_data_registrationdataimport_change", args=[rdi.pk])
                            self.message_user(
                                request,
                                mark_safe(f"Adding to RDI Import with name: <a href='{url}'>{rdi.name}</a>"),
                                messages.SUCCESS,
                            )
                        except Exception as e:
                            self.message_error_to_user(request, e)

                    else:
                        self.message_user(request, "There are no Records by filtering criteria", messages.ERROR)
                else:
                    self.message_user(
                        request,
                        "Selected registration doesn't have any strategy service associated.",
                        messages.ERROR,
                    )
        else:
            form = AmendRDIForm(request=request)

        ctx["form"] = form
        return render(request, "registration_datahub/admin/record/create_rdi.html", ctx)

    @button(permission=is_root)
    def fetch(self, request: HttpRequest) -> TemplateResponse:
        ctx = self.get_common_context(request)
        cookies = {}
        if request.method == "POST":
            form = FetchForm(request.POST)
            if form.is_valid():
                if form.cleaned_data["remember"]:
                    cookies = {form.SYNC_COOKIE: form.get_signed_cookie(request)}

                auth = HTTPBasicAuth(form.cleaned_data["username"], form.cleaned_data["password"])
                url = "{host}api/data/{registration}/{start}/{end}/".format(**form.cleaned_data)
                with requests.get(url, stream=True, auth=auth) as res:
                    if res.status_code != 200:
                        raise Exception(str(res))
                    payload = res.json()
                    for record in payload["data"]:
                        Record.objects.update_or_create(
                            source_id=record["id"],
                            registration=2,
                            defaults={"timestamp": record["timestamp"], "storage": base64.b64decode(record["storage"])},
                        )
        else:
            form = FetchForm(initial=FetchForm.get_saved_config(request))

        ctx["form"] = form
        response = TemplateResponse(request, "registration_datahub/admin/record/fetch.html", ctx)
        if cookies:
            for k, v in cookies.items():
                response.set_cookie(k, v)
        return response


@admin.register(Record)
class RecordDatahubAdmin(RecordMixinAdmin, HOPEModelAdminBase):
    pass
