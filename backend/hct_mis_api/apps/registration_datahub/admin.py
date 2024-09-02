import logging
from typing import Any, Generator, Iterable, List, Optional, Tuple, Union
from uuid import UUID

from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin, SimpleListFilter
from django.db.models import F, QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.datastructures import MultiValueDict

from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.filters import ValueFilter
from adminfilters.querystring import QueryStringFilter
from advanced_filters.admin import AdminAdvancedFiltersMixin

from hct_mis_api.apps.registration_data.models import (
    ImportData,
    KoboImportedSubmission,
    RegistrationDataImportDatahub,
)
from hct_mis_api.apps.registration_datahub.models import (
    ImportedHousehold,
    ImportedIndividual,
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


@admin.register(ImportData)
class ImportDataAdmin(HOPEModelAdminBase):
    list_filter = ("data_type", "status", ("business_area_slug", ValueFilter.factory(lookup_name="istartswith")))
    date_hierarchy = "created_at"


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
