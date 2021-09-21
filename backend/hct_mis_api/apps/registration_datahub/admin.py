import re

from django.contrib import admin
from django.contrib.admin import FieldListFilter, SimpleListFilter
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.safestring import mark_safe

from admin_extra_urls.decorators import button, href
from admin_extra_urls.mixins import ExtraUrlMixin
from adminactions.helpers import AdminActionPermMixin
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.filters import ChoicesFieldComboFilter, NumberFilter, TextFieldFilter
from advanced_filters.admin import AdminAdvancedFiltersMixin

from hct_mis_api.apps.registration_datahub.models import (
    ImportData,
    ImportedDocument,
    ImportedDocumentType,
    ImportedHousehold,
    ImportedIndividual,
    ImportedIndividualIdentity,
    ImportedIndividualRoleInHousehold,
    KoboImportedSubmission,
    RegistrationDataImportDatahub,
)
from hct_mis_api.apps.registration_datahub.utils import post_process_dedupe_results
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase


@admin.register(RegistrationDataImportDatahub)
class RegistrationDataImportDatahubAdmin(ExtraUrlMixin, AdminAdvancedFiltersMixin, HOPEModelAdminBase):
    list_display = ("name", "import_date", "import_done", "business_area_slug", "hct_id")
    list_filter = (
        "created_at",
        "import_done",
        ("registration_data_import", AutoCompleteFilter),
        TextFieldFilter.factory("business_area_slug__istartswith"),
    )
    advanced_filter_fields = (
        "created_at",
        "import_done",
        ("business_area__name", "business area"),
    )

    raw_id_fields = ("import_data",)
    date_hierarchy = "created_at"
    search_fields = ("name",)

    @href(
        label="RDI",
    )
    def hub(self, button):
        obj = button.context.get("original")
        if obj:
            if obj.hct_id:
                return reverse("admin:registration_data_registrationdataimport_change", args=[obj.hct_id])
            else:
                button.html_attrs = {"style": "background-color:#CCCCCC;cursor:not-allowed"}
                return "javascript:alert('RDI not imported');"
        button.visible = False

    @button()
    def inspect(self, request, pk):
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


# {"duplicates": [ {"dob": "1965-11-05",
#                  "score": 11.0,
#                  "hit_id": "266704c0-d13c-4475-9445-52ad1f6d9cb8",
#                  "location": null,
#                  "full_name": "Lavone Burnham",
#                  "proximity_to_score": 5.0}],
#                  "possible_duplicates": []}

number = r"(\d+(\.(\d+)))*"
rexx = [
    re.compile(rf"^(>=|<=|>|<|=)?([-+]?{number})$"),
    re.compile(rf"{number}"),
    # re.compile(r'(\d+)'),
    # re.compile(r'^(<>)?([-+]?[0-9]+)$')
]

rex = re.compile(r"^(?P<op>>=|<=|>|<|=)?(?P<value>\d+(\.\d+)?)")


def math_to_django(clause):
    mapping = {
        ">=": "gte",
        "<=": "lte",
        ">": "gt",
        "<": "lt",
        "=": "exact",
        "<>": "not",
    }
    # for rex in rexx:
    if match := rex.match(clause):
        groups = match.groupdict()
        op = groups.get("op", "=")
        value = groups.get("value", 0)
        return mapping[op or "="], value
    return None, None


class ScoreFilter(FieldListFilter):
    template = "adminfilters/text.html"
    title = "score"
    parameter_name = "score"

    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)
        self.original_title = self.title

    def expected_parameters(self):
        return [self.parameter_name]

    def value(self):
        return self.used_parameters.get(self.parameter_name, "")

    def queryset(self, request, queryset):
        op, value = math_to_django(self.value())
        if value:
            self.title = f"{self.original_title} {op} {value}"
            queryset = queryset.filter(**{f"{self.field_path}__score__max__{op}": float(value)})
        return queryset

    def choices(self, changelist):
        yield {
            "selected": False,
            "query_string": changelist.get_query_string(
                {},
                [
                    self.parameter_name,
                ],
            ),
            "lookup_kwarg": self.parameter_name,
            "display": "All",
            "value": self.value(),
        }


@admin.register(ImportedIndividual)
class ImportedIndividualAdmin(ExtraUrlMixin, HOPEModelAdminBase):
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
        ("deduplication_batch_results", ScoreFilter),
        ("deduplication_golden_record_results", ScoreFilter),
        TextFieldFilter.factory("registration_data_import__name__istartswith"),
        TextFieldFilter.factory("individual_id__istartswith"),
        "deduplication_batch_status",
        "deduplication_golden_record_status",
    )
    date_hierarchy = "updated_at"
    raw_id_fields = ("household", "registration_data_import")
    actions = ["enrich_deduplication"]

    def score(self, obj):
        try:
            return obj.deduplication_golden_record_results["score"]["max"]
        except KeyError:
            return ""

    def batch_score(self, obj):
        try:
            return obj.deduplication_batch_results["score"]["max"]
        except KeyError:
            return ""

    def dedupe_status(self, obj):
        lbl = f"{obj.deduplication_batch_status}/{obj.deduplication_golden_record_status}"
        url = reverse("admin:registration_datahub_importedindividual_duplicates", args=[obj.pk])
        if "duplicates" in obj.deduplication_batch_results:
            ret = f'<a href="{url}">{lbl}</a>'
        elif "duplicates" in obj.deduplication_golden_record_results:
            ret = f'<a href="{url}">{lbl}</a>'
        else:
            ret = lbl
        return mark_safe(ret)

    def enrich_deduplication(self, request, queryset):
        for record in queryset.exclude(deduplication_batch_results__has_key="score"):
            post_process_dedupe_results(record)

    @button()
    def post_process_dedupe_results(self, request, pk):
        record = self.get_queryset(request).get(id=pk)
        post_process_dedupe_results(record)
        record.save()

    @button()
    def duplicates(self, request, pk):
        ctx = self.get_common_context(request, pk, title="Duplicates")
        return TemplateResponse(request, "registration_datahub/admin/duplicates.html", ctx)


@admin.register(ImportedIndividualIdentity)
class ImportedIndividualIdentityAdmin(HOPEModelAdminBase):
    raw_id_fields = ("individual",)


@admin.register(ImportedHousehold)
class ImportedHouseholdAdmin(HOPEModelAdminBase):
    list_display = ("registration_data_import", "registration_method", "name_enumerator", "country", "country_origin")
    raw_id_fields = ("registration_data_import", "head_of_household")
    date_hierarchy = "registration_data_import__import_date"
    list_filter = (
        ("country", ChoicesFieldComboFilter),
        ("country_origin", ChoicesFieldComboFilter),
        TextFieldFilter.factory("registration_data_import__name__istartswith"),
        TextFieldFilter.factory("kobo_submission_uuid__istartswith"),
    )


@admin.register(ImportData)
class ImportDataAdmin(HOPEModelAdminBase):
    list_filter = ("data_type",)
    date_hierarchy = "created_at"


@admin.register(ImportedDocumentType)
class ImportedDocumentTypeAdmin(HOPEModelAdminBase):
    list_display = ("label", "country")
    list_filter = (("country", ChoicesFieldComboFilter),)


@admin.register(ImportedDocument)
class ImportedDocumentAdmin(HOPEModelAdminBase):
    list_display = ("document_number", "type", "individual")
    raw_id_fields = ("individual", "type")


@admin.register(ImportedIndividualRoleInHousehold)
class ImportedIndividualRoleInHouseholdAdmin(HOPEModelAdminBase):
    raw_id_fields = ("individual", "household")
    list_filter = ("role",)


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
    # date_hierarchy = "created_at"
    list_filter = (
        "amended",
        ("registration_data_import", AutoCompleteFilter),
        ("imported_household", AutoCompleteFilter),
    )
    advanced_filter_fields = (
        # "created_at",
        "amended",
        "kobo_submission_time",
        "registration_data_import_id",
    )
    raw_id_fields = ("registration_data_import", "imported_household")
