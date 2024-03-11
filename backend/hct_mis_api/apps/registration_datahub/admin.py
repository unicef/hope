import logging
from typing import Any, Dict, Generator, Iterable, List, Optional, Tuple, Union
from uuid import UUID

from django import forms
from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin, SimpleListFilter
from django.core.signing import BadSignature, Signer
from django.db.models import F, QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.datastructures import MultiValueDict
from django.utils.safestring import mark_safe

from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.depot.widget import DepotManager
from adminfilters.filters import ChoicesFieldComboFilter, NumberFilter, ValueFilter
from adminfilters.querystring import QueryStringFilter
from advanced_filters.admin import AdminAdvancedFiltersMixin

from hct_mis_api.apps.registration_datahub.models import (
    ImportData,
    ImportedBankAccountInfo,
    ImportedDocument,
    ImportedDocumentType,
    ImportedHousehold,
    ImportedIndividual,
    ImportedIndividualIdentity,
    ImportedIndividualRoleInHousehold,
    KoboImportedSubmission,
    RegistrationDataImportDatahub,
)
from hct_mis_api.apps.registration_datahub.utils import (
    post_process_dedupe_results as _post_process_dedupe_results,
)
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase

logger = logging.getLogger(__name__)


@admin.register(RegistrationDataImportDatahub)
class RegistrationDataImportDatahubAdmin(HOPEModelAdminBase):
    list_display = ("name", "import_date", "import_done", "business_area_slug", "hct_id")
    list_filter = (
        QueryStringFilter,
        "created_at",
        "import_done",
        ("business_area_slug", ValueFilter.factory(lookup_name="istartswith")),
    )
    advanced_filter_fields = (
        "created_at",
        "import_done",
        ("business_area__name", "business area"),
    )

    raw_id_fields = ("import_data",)
    date_hierarchy = "created_at"
    search_fields = ("name",)

    @button(label="RDI")
    def hub(self, request: HttpRequest, pk: UUID) -> Union[HttpResponseRedirect, HttpResponse]:  # type: ignore[return]
        obj = self.get_object(request, str(pk))
        if obj.hct_id:
            url = reverse("admin:registration_data_registrationdataimport_change", args=[obj.hct_id])
            return HttpResponseRedirect(url)
        else:
            self.message_user(request, "No RDI linked", messages.ERROR)

    @button()
    def inspect(self, request: HttpRequest, pk: UUID) -> TemplateResponse:
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
        "program_id",
    )
    list_filter = (
        QueryStringFilter,
        ("deduplication_batch_results", NumberFilter),
        ("deduplication_golden_record_results", NumberFilter),
        ("registration_data_import__name", ValueFilter.factory(lookup_name="istartswith")),
        ("individual_id", ValueFilter.factory(lookup_name="istartswith")),
        "deduplication_batch_status",
        "deduplication_golden_record_status",
        ("program_id", ValueFilter.factory(lookup_name="istartswith", title="Program ID")),
    )
    date_hierarchy = "updated_at"
    # raw_id_fields = ("household", "registration_data_import")
    autocomplete_fields = ("household", "registration_data_import")
    actions = ["enrich_deduplication"]
    inlines = (ImportedBankAccountInfoStackedInline,)

    def score(self, obj: ImportedIndividual) -> Union[int, str]:
        try:
            return obj.deduplication_golden_record_results["score"]["max"]
        except KeyError:
            return ""

    def batch_score(self, obj: ImportedIndividual) -> Union[int, str]:
        try:
            return obj.deduplication_batch_results["score"]["max"]
        except KeyError:
            return ""

    def dedupe_status(self, obj: ImportedIndividual) -> str:
        lbl = f"{obj.deduplication_batch_status}/{obj.deduplication_golden_record_status}"
        url = reverse("admin:registration_datahub_importedindividual_duplicates", args=[obj.pk])
        if "duplicates" in obj.deduplication_batch_results:
            ret = f'<a href="{url}">{lbl}</a>'
        elif "duplicates" in obj.deduplication_golden_record_results:
            ret = f'<a href="{url}">{lbl}</a>'
        else:
            ret = lbl
        return mark_safe(ret)

    def enrich_deduplication(self, request: HttpRequest, queryset: QuerySet) -> None:
        for record in queryset.exclude(deduplication_batch_results__has_key="score"):
            _post_process_dedupe_results(record)

    @button()
    def post_process_dedupe_results(self, request: HttpRequest, pk: UUID) -> None:
        record = self.get_queryset(request).get(id=pk)
        _post_process_dedupe_results(record)
        record.save()

    @button()
    def duplicates(self, request: HttpRequest, pk: UUID) -> TemplateResponse:
        ctx = self.get_common_context(request, pk, title="Duplicates")
        return TemplateResponse(request, "registration_datahub/admin/duplicates.html", ctx)


@admin.register(ImportedIndividualIdentity)
class ImportedIndividualIdentityAdmin(HOPEModelAdminBase):
    list_display = ("individual", "document_number")
    raw_id_fields = ("individual",)


@admin.register(ImportedHousehold)
class ImportedHouseholdAdmin(HOPEModelAdminBase):
    search_fields = ("id", "registration_data_import")
    list_display = (
        "registration_data_import",
        "registration_method",
        "program_id",
        "name_enumerator",
        "country",
        "country_origin",
    )
    raw_id_fields = ("registration_data_import", "head_of_household")
    date_hierarchy = "registration_data_import__import_date"
    list_filter = (
        QueryStringFilter,
        DepotManager,
        ("country", ChoicesFieldComboFilter),
        ("country_origin", ChoicesFieldComboFilter),
        "registration_method",
        ("registration_data_import__name", ValueFilter.factory(lookup_name="istartswith")),
        ("kobo_submission_uuid", ValueFilter.factory(lookup_name="istartswith", title="Kobo Submission UUID")),
        ("program_id", ValueFilter.factory(lookup_name="istartswith", title="Program ID")),
    )


@admin.register(ImportData)
class ImportDataAdmin(HOPEModelAdminBase):
    list_filter = ("data_type", "status", ("business_area_slug", ValueFilter.factory(lookup_name="istartswith")))
    date_hierarchy = "created_at"


@admin.register(ImportedDocumentType)
class ImportedDocumentTypeAdmin(HOPEModelAdminBase):
    list_display = ("label", "key", "is_identity_document")
    list_filter = ("label", QueryStringFilter)


@admin.register(ImportedDocument)
class ImportedDocumentAdmin(HOPEModelAdminBase):
    list_display = ("document_number", "type", "country", "individual")
    raw_id_fields = ("individual", "type")
    list_filter = (("type", AutoCompleteFilter), ("country", ChoicesFieldComboFilter), QueryStringFilter)
    date_hierarchy = "created_at"


@admin.register(ImportedBankAccountInfo)
class ImportedBankAccountInfoAdmin(HOPEModelAdminBase):
    list_display = ("individual", "bank_name", "bank_account_number", "debit_card_number")
    raw_id_fields = ("individual",)
    search_fields = ("bank_name", "bank_account_number")
    list_filter = (QueryStringFilter,)
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

    def get_signed_cookie(self, request: HttpRequest) -> Any:
        signer = Signer(str(request.user.password))
        return signer.sign_object(self.cleaned_data)

    @classmethod
    def get_saved_config(cls, request: HttpRequest) -> Dict:
        try:
            signer = Signer(str(request.user.password))
            obj: Dict = signer.unsign_object(request.COOKIES.get(cls.SYNC_COOKIE, ""))
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

    def __init__(
        self, request: HttpRequest, params: MultiValueDict[str, str], model: Any, model_admin: ModelAdmin
    ) -> None:
        super().__init__(request, params, model, model_admin)
        self.lookup_kwarg = self.parameter_name
        self.lookup_val = request.GET.getlist(self.lookup_kwarg, [])

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
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

    def lookups(self, request: HttpRequest, model_admin: ModelAdmin) -> Optional[Iterable[Tuple[Any, str]]]:
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

    def choices(self, changelist: List) -> Generator:
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
