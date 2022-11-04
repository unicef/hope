import base64
import logging
from typing import Any, Dict, Generator, Iterable, Optional, Tuple

from django import forms
from django.contrib import admin, messages
from django.contrib.admin import SimpleListFilter
from django.core.signing import BadSignature, Signer
from django.db.models import F, QuerySet
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe

import requests
from admin_cursor_paginator import CursorPaginatorAdmin
from admin_extra_buttons.decorators import button, link
from adminactions.mass_update import mass_update
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.depot.widget import DepotManager
from adminfilters.filters import ChoicesFieldComboFilter, NumberFilter, ValueFilter
from adminfilters.json import JsonFieldFilter
from adminfilters.querystring import QueryStringFilter
from advanced_filters.admin import AdminAdvancedFiltersMixin
from requests.auth import HTTPBasicAuth

from hct_mis_api.apps.registration_datahub.celery_tasks import (
    fresh_extract_records_task,
    process_flex_records_task,
)
from hct_mis_api.apps.registration_datahub.models import (
    DiiaHousehold,
    DiiaIndividual,
    ImportData,
    ImportedBankAccountInfo,
    ImportedDocument,
    ImportedDocumentType,
    ImportedHousehold,
    ImportedIndividual,
    ImportedIndividualIdentity,
    ImportedIndividualRoleInHousehold,
    KoboImportedSubmission,
    Record,
    RegistrationDataImportDatahub,
)
from hct_mis_api.apps.registration_datahub.services.extract_record import extract
from hct_mis_api.apps.registration_datahub.services.flex_registration_service import (
    FlexRegistrationService,
)
from hct_mis_api.apps.registration_datahub.utils import (
    post_process_dedupe_results as _post_process_dedupe_results,
)
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase
from hct_mis_api.apps.utils.security import is_root

logger = logging.getLogger(__name__)


@admin.register(RegistrationDataImportDatahub)
class RegistrationDataImportDatahubAdmin(HOPEModelAdminBase):
    list_display = ("name", "import_date", "import_done", "business_area_slug", "hct_id")
    list_filter = ("created_at", "import_done", ("business_area_slug", ValueFilter.factory(lookup_name="istartswith")))
    advanced_filter_fields = (
        "created_at",
        "import_done",
        ("business_area__name", "business area"),
    )

    raw_id_fields = ("import_data",)
    date_hierarchy = "created_at"
    search_fields = ("name",)

    @link(
        href=None,
        label="RDI",
    )
    def hub(self, button) -> Optional[str]:
        obj = button.context.get("original")
        if obj:
            if obj.hct_id:
                return reverse("admin:registration_data_registrationdataimport_change", args=[obj.hct_id])
            else:
                button.html_attrs = {"style": "background-color:#CCCCCC;cursor:not-allowed"}
                return "javascript:alert('RDI not imported');"
        button.visible = False
        return None

    @button()
    def inspect(self, request, pk) -> TemplateResponse:
        context = self.get_common_context(request, pk)
        obj: RegistrationDataImportDatahub = context["original"]
        context["title"] = f"Import {obj.name} - {obj.import_done}"
        context["data"] = {}
        has_content = False
        for model in [ImportedIndividual, ImportedHousehold]:
            count = model.objects.filter(registration_data_import=obj).count()
            has_content = has_content or count
            context["data"][model] = {"count": count, "warnings": [], "errors": [], "meta": model._meta}

        return TemplateResponse(request, "registration_datahub/admin/inspect.html", context)


class ImportedBankAccountInfoStackedInline(admin.StackedInline):
    model = ImportedBankAccountInfo

    exclude = ("debit_card_number",)
    extra = 0


@admin.register(ImportedIndividual)
class ImportedIndividualAdmin(HOPEModelAdminBase):
    list_display = (
        "registration_data_import",
        "individual_id",
        "full_name",
        "sex",
        "dedupe_status",
        "score",
        "batch_score",
    )
    list_filter = (
        ("deduplication_batch_results", NumberFilter),
        ("deduplication_golden_record_results", NumberFilter),
        ("registration_data_import__name", ValueFilter.factory(lookup_name="istartswith")),
        ("individual_id", ValueFilter.factory(lookup_name="istartswith")),
        "deduplication_batch_status",
        "deduplication_golden_record_status",
    )
    date_hierarchy = "updated_at"
    # raw_id_fields = ("household", "registration_data_import")
    autocomplete_fields = ("household", "registration_data_import")
    actions = ["enrich_deduplication"]
    inlines = (ImportedBankAccountInfoStackedInline,)

    def score(self, obj) -> Any:
        try:
            return obj.deduplication_golden_record_results["score"]["max"]
        except KeyError:
            return ""

    def batch_score(self, obj) -> Any:
        try:
            return obj.deduplication_batch_results["score"]["max"]
        except KeyError:
            return ""

    def dedupe_status(self, obj) -> str:
        lbl = f"{obj.deduplication_batch_status}/{obj.deduplication_golden_record_status}"
        url = reverse("admin:registration_datahub_importedindividual_duplicates", args=[obj.pk])
        if "duplicates" in obj.deduplication_batch_results:
            ret = f'<a href="{url}">{lbl}</a>'
        elif "duplicates" in obj.deduplication_golden_record_results:
            ret = f'<a href="{url}">{lbl}</a>'
        else:
            ret = lbl
        return mark_safe(ret)

    def enrich_deduplication(self, request, queryset) -> None:
        for record in queryset.exclude(deduplication_batch_results__has_key="score"):
            _post_process_dedupe_results(record)

    @button()
    def post_process_dedupe_results(self, request, pk) -> None:
        record = self.get_queryset(request).get(id=pk)
        _post_process_dedupe_results(record)
        record.save()

    @button()
    def duplicates(self, request, pk) -> TemplateResponse:
        ctx = self.get_common_context(request, pk, title="Duplicates")
        return TemplateResponse(request, "registration_datahub/admin/duplicates.html", ctx)


@admin.register(ImportedIndividualIdentity)
class ImportedIndividualIdentityAdmin(HOPEModelAdminBase):
    list_display = ("individual", "agency", "document_number")
    raw_id_fields = ("individual",)


@admin.register(ImportedHousehold)
class ImportedHouseholdAdmin(HOPEModelAdminBase):
    search_fields = ("id", "registration_data_import")
    list_display = ("registration_data_import", "registration_method", "name_enumerator", "country", "country_origin")
    raw_id_fields = ("registration_data_import", "head_of_household")
    date_hierarchy = "registration_data_import__import_date"
    list_filter = (
        DepotManager,
        ("country", ChoicesFieldComboFilter),
        ("country_origin", ChoicesFieldComboFilter),
        "registration_method",
        ("registration_data_import__name", ValueFilter.factory(lookup_name="istartswith")),
        ("kobo_submission_uuid", ValueFilter.factory(lookup_name="istartswith", title="Kobo Submission UUID")),
    )


@admin.register(ImportData)
class ImportDataAdmin(HOPEModelAdminBase):
    list_filter = ("data_type", "status", ("business_area_slug", ValueFilter.factory(lookup_name="istartswith")))
    date_hierarchy = "created_at"


@admin.register(ImportedDocumentType)
class ImportedDocumentTypeAdmin(HOPEModelAdminBase):
    list_display = ("label",)
    list_filter = ("label", QueryStringFilter)


@admin.register(ImportedDocument)
class ImportedDocumentAdmin(HOPEModelAdminBase):
    list_display = ("document_number", "type", "country", "individual")
    raw_id_fields = ("individual", "type")
    list_filter = (("type", AutoCompleteFilter), ("country", ChoicesFieldComboFilter), QueryStringFilter)
    date_hierarchy = "created_at"


@admin.register(ImportedIndividualRoleInHousehold)
class ImportedIndividualRoleInHouseholdAdmin(HOPEModelAdminBase):
    raw_id_fields = ("individual", "household")
    list_filter = ("role", QueryStringFilter)


@admin.register(KoboImportedSubmission)
class KoboImportedSubmissionAdmin(AdminAdvancedFiltersMixin, HOPEModelAdminBase):
    list_display = (
        "created_at",
        "kobo_submission_time",
        "kobo_submission_uuid",
        "kobo_asset_id",
        "amended",
        "imported_household_id",
        "registration_data_import_id",
    )
    list_filter = (
        "amended",
        ("registration_data_import", AutoCompleteFilter),
        ("imported_household", AutoCompleteFilter),
        QueryStringFilter,
    )
    advanced_filter_fields = (
        # "created_at",
        "amended",
        "kobo_submission_time",
        "registration_data_import_id",
    )
    raw_id_fields = ("registration_data_import", "imported_household")


class RemeberDataForm(forms.Form):
    SYNC_COOKIE = "fetch"
    remember = forms.BooleanField(label="Remember me", required=False)

    def get_signed_cookie(self, request) -> Any:
        signer = Signer(request.user.password)
        return signer.sign_object(self.cleaned_data)

    @classmethod
    def get_saved_config(cls, request) -> Dict:
        try:
            signer = Signer(request.user.password)
            obj: Dict = signer.unsign_object(request.COOKIES.get(cls.SYNC_COOKIE, {}))
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

    def clean(self) -> Optional[Dict[str, Any]]:
        return super().clean()


class ValidateForm(RemeberDataForm):
    SYNC_COOKIE = "ocr"
    picture_field = forms.CharField()
    number_field = forms.CharField()


class AlexisFilter(SimpleListFilter):
    template = "adminfilters/alexis.html"
    title = "Alexis"
    parameter_name = "alexis"

    def __init__(self, request, params, model, model_admin) -> None:
        super().__init__(request, params, model, model_admin)
        self.lookup_kwarg = self.parameter_name
        self.lookup_val = request.GET.getlist(self.lookup_kwarg, [])

    def queryset(self, request, queryset) -> QuerySet:
        if "1" in self.lookup_val:
            queryset = queryset.filter(data__w_counters__individuals_num=F("data__household__0__size_h_c"))
        if "2" in self.lookup_val:
            queryset = queryset.filter(data__w_counters__collectors_num=1)
        if "3" in self.lookup_val:
            queryset = queryset.filter(data__w_counters__head=1)
        if "4" in self.lookup_val:
            queryset = queryset.filter(data__w_counters__valid_phones__gt=0)
        if "5" in self.lookup_val:
            queryset = queryset.filter(data__w_counters__valid_taxid__gt=0)
        if "6" in self.lookup_val:
            queryset = queryset.filter(data__w_counters__birth_certificate__gt=0)
        if "7" in self.lookup_val:
            queryset = queryset.filter(data__w_counters__disability_certificate=True)
        if "8" in self.lookup_val:
            queryset = queryset.filter(data__w_counters__valid_payment__gt=0)
        if "9" in self.lookup_val:
            queryset = queryset.filter(data__w_counters__collector_bank_account=True)
        return queryset

    def lookups(self, request, model_admin) -> Optional[Iterable[Tuple[Any, str]]]:
        return (
            ("1", "Household size match"),
            ("2", "Only one collector"),
            ("3", "One and only one head"),
            ("4", "More than 1 phone number"),
            ("5", "At least 1 HoH has TaxId ans BankAccount"),
            ("6", "at least one birth certificate picture"),
            ("7", "disability certificate for each disabled"),
            ("8", "At least 1 member has TaxId ans BankAccount"),
            ("9", "Collector has BankAccount"),
        )

    def choices(self, changelist) -> Generator:
        for lookup, title in self.lookup_choices:
            qs = changelist.get_query_string(remove=[self.parameter_name]) + "&"
            qs += "&".join([f"{self.parameter_name}={v}" for v in self.lookup_val if v != lookup])
            if str(lookup) not in self.lookup_val:
                qs += f"&{self.parameter_name}={lookup}"
            yield {
                "selected": str(lookup) in self.lookup_val,
                "query_string": qs,
                "display": title,
            }


@admin.register(Record)
class RecordDatahubAdmin(CursorPaginatorAdmin, HOPEModelAdminBase):
    list_display = ("id", "registration", "timestamp", "source_id", "status", "ignored")
    readonly_fields = (
        "id",
        "registration",
        "timestamp",
        "source_id",
        "registration_data_import",
        "status",
        "error_message",
    )
    # list_editable = ("ignored",)
    exclude = ("data",)
    date_hierarchy = "timestamp"
    list_filter = (
        DepotManager,
        ("registration_data_import", AutoCompleteFilter),
        "status",
        ("source_id", NumberFilter),
        ("id", NumberFilter),
        ("data", JsonFieldFilter),
        QueryStringFilter,
    )
    change_form_template = "registration_datahub/admin/record/change_form.html"
    # change_list_template = "registration_datahub/admin/record/change_list.html"

    actions = [mass_update, "extract", "async_extract", "create_rdi", "count_queryset"]

    mass_update_exclude = ["pk", "data", "source_id", "registration", "timestamp"]
    mass_update_hints = []

    def get_queryset(self, request) -> QuerySet:
        qs = super().get_queryset(request)
        qs = qs.defer("storage", "data")
        return qs

    @admin.action(description="Create RDI")
    def create_rdi(self, request, queryset) -> None:
        service = FlexRegistrationService()
        try:
            records_ids = queryset.values_list("id", flat=True)
            rdi = service.create_rdi(request.user, f"ukraine rdi {timezone.now()}")

            process_flex_records_task.delay(rdi.id, list(records_ids))
            url = reverse("admin:registration_data_registrationdataimport_change", args=[rdi.pk])
            self.message_user(
                request, mark_safe(f"RDI Import with name: <a href='{url}'>{rdi.name}</a> started"), messages.SUCCESS
            )
        except Exception as e:
            self.message_user(request, str(e), messages.ERROR)

    @admin.action(description="Async extract")
    def async_extract(self, request, queryset) -> None:
        try:
            records_ids = queryset.values_list("id", flat=True)
            fresh_extract_records_task.delay(list(records_ids))
            self.message_user(request, f"Extracting data for {len(records_ids)} records", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, str(e), messages.ERROR)

    @button(permission=is_root)
    def fetch(self, request) -> TemplateResponse:
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

    @button(label="Extract")
    def extract_single(self, request, pk) -> None:
        records_ids = Record.objects.filter(pk=pk).values_list("pk", flat=True)
        try:
            extract(records_ids, raise_exception=True)
        except Exception as e:
            self.message_error_to_user(request, e)

    def has_add_permission(self, request) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return is_root(request)


@admin.register(DiiaIndividual)
class DiiaIndividualAdmin(HOPEModelAdminBase):
    list_display = ("registration_data_import", "individual_id", "full_name", "sex", "disability")
    list_filter = (
        ("registration_data_import__name", ValueFilter.factory(lookup_name="istartswith")),
        ("individual_id", ValueFilter.factory(lookup_name="istartswith")),
        "disability",
    )


@admin.register(DiiaHousehold)
class DiiaHouseholdAdmin(HOPEModelAdminBase):
    search_fields = ("id", "registration_data_import", "rec_id")
    list_display = ("registration_data_import", "status", "rec_id")
    raw_id_fields = ("registration_data_import",)
    date_hierarchy = "registration_data_import__import_date"
    list_filter = (
        ("registration_data_import__name", ValueFilter.factory(lookup_name="istartswith")),
        (
            "rec_id",
            ValueFilter.factory(
                lookup_name="istartswith",
            ),
        ),
    )
