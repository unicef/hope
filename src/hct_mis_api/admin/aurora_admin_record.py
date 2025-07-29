import base64
from typing import Any, Generator
from uuid import UUID

from django import forms
from django.contrib import admin, messages
from django.contrib.admin.views.main import ChangeList
from django.core.signing import BadSignature, Signer
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
from adminactions.mass_update import mass_update
from adminfilters.combo import ChoicesFieldComboFilter
from adminfilters.depot.widget import DepotManager
from adminfilters.json import JsonFieldFilter
from adminfilters.numbers import NumberFilter
from adminfilters.querystring import QueryStringFilter
from requests.auth import HTTPBasicAuth

from hct_mis_api.admin.utils_admin import HOPEModelAdminBase
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.utils.security import is_root
from hct_mis_api.contrib.aurora.celery_tasks import fresh_extract_records_task
from hct_mis_api.contrib.aurora.models import Record, Registration
from hct_mis_api.contrib.aurora.services.extract_record import extract
from hct_mis_api.contrib.aurora.services.flex_registration_service import (
    create_task_for_processing_records,
)
from hct_mis_api.contrib.aurora.utils import fetch_records, get_metadata


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
        queryset=Registration.objects.order_by("name"),
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
        queryset=RegistrationDataImport.objects.filter(status=RegistrationDataImport.LOADING).order_by("name"),
        help_text="can select and update existing RDI within status 'Loading'",
    )

    field_order = ["rdi", "registration", "filters"]


@admin.register(Record)
class RecordAdmin(HOPEModelAdminBase):
    list_display = ("id", "registration", "timestamp", "source_id", "status", "ignored")
    readonly_fields = (
        "id",
        "registration",
        "timestamp",
        "source_id",
        "status",
        "error_message",
    )
    exclude = ("data",)
    date_hierarchy = "timestamp"
    list_filter = (
        DepotManager,
        ("status", StatusFilter),
        ("source_id", NumberFilter),
        ("id", NumberFilter),
        ("data", JsonFieldFilter),
        QueryStringFilter,
    )
    change_form_template = "registration_datahub/admin/record/change_form.html"

    actions = [mass_update, "extract", "async_extract", "create_rdi", "count_queryset"]

    mass_update_exclude = ["pk", "data", "source_id", "registration", "timestamp"]
    mass_update_hints = []

    @button(permission="aurora.can_fetch_data")
    def fetch_aurora(self, request: HttpRequest) -> HttpResponse:
        ctx = self.get_common_context(request)
        if request.method == "POST":
            form = FetchForm(request.POST)
            aurora_token = request.user.custom_fields.get("aurora_token")
            try:
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
            except BaseException as e:
                messages.add_message(request, messages.ERROR, str(e))
        else:
            form = FetchForm()

        ctx["form"] = form
        return render(request, "admin/aurora/record/fetch.html", ctx)

    def has_add_permission(self, request: HttpRequest) -> bool:
        return is_root(request)

    def has_delete_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:
        return is_root(request)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        qs = super().get_queryset(request)
        return qs.defer("storage", "data", "files")

    @admin.action(description="Async extract")
    def async_extract(self, request: HttpRequest, queryset: QuerySet) -> None:
        try:
            records_ids = queryset.values_list("id", flat=True)
            fresh_extract_records_task.delay(list(records_ids))
            self.message_user(request, f"Extracting data for {len(records_ids)} records", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, str(e), messages.ERROR)

    @button(label="Extract", permission="aurora.view_record")
    def extract_single(self, request: HttpRequest, pk: UUID) -> None:
        records_ids = Record.objects.filter(pk=pk).values_list("pk", flat=True)
        try:
            extract(records_ids, raise_exception=True)
        except Exception as e:
            self.message_error_to_user(request, e)

    @button(permission="aurora.can_add_records")
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

    @button(permission="aurora.can_add_records")
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

    @button(permission="aurora.can_fetch_data")
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


class RemeberDataForm(forms.Form):
    SYNC_COOKIE = "fetch"
    remember = forms.BooleanField(label="Remember me", required=False)

    def get_signed_cookie(self, request: HttpRequest) -> Any:
        signer = Signer(str(request.user.password))
        return signer.sign_object(self.cleaned_data)

    @classmethod
    def get_saved_config(cls, request: HttpRequest) -> dict:
        try:
            signer = Signer(str(request.user.password))
            obj: dict = signer.unsign_object(request.COOKIES.get(cls.SYNC_COOKIE, ""))
            return obj
        except BadSignature:
            return {}


class FetchForm(RemeberDataForm):
    SYNC_COOKIE = "fetch"

    host = forms.URLField()
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    registration = forms.IntegerField()
    start = forms.IntegerField()
    end = forms.IntegerField()

    def clean(self) -> dict[str, Any] | None:
        return super().clean()
