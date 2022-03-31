import re

from django.contrib import admin
from django.contrib.admin import FieldListFilter, SimpleListFilter
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.safestring import mark_safe

from admin_extra_buttons.decorators import button, link
from admin_extra_buttons.mixins import ExtraButtonsMixin
from adminactions.helpers import AdminActionPermMixin
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.filters import ChoicesFieldComboFilter, NumberFilter, ValueFilter
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

from hct_mis_api.apps.registration_datahub.models import Record


@admin.register(RegistrationDataImportDatahub)
class RegistrationDataImportDatahubAdmin(ExtraButtonsMixin, AdminAdvancedFiltersMixin, HOPEModelAdminBase):
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


@admin.register(ImportedIndividual)
class ImportedIndividualAdmin(ExtraButtonsMixin, HOPEModelAdminBase):
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
    search_fields = ("id", "registration_data_import")
    list_display = ("registration_data_import", "registration_method", "name_enumerator", "country", "country_origin")
    raw_id_fields = ("registration_data_import", "head_of_household")
    date_hierarchy = "registration_data_import__import_date"
    list_filter = (
        ("country", ChoicesFieldComboFilter),
        ("country_origin", ChoicesFieldComboFilter),
        ("registration_data_import__name", ValueFilter.factory(lookup_name="istartswith")),
        ("kobo_submission_uuid", ValueFilter.factory(lookup_name="istartswith")),
        ("kobo_submission_uuid", ValueFilter.factory(lookup_name="istartswith")),
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
    list_filter = (("type", AutoCompleteFilter),)


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


@admin.register(Record)
class RegistrationDataImportDatahubAdmin(ExtraButtonsMixin, AdminAdvancedFiltersMixin, HOPEModelAdminBase):
    list_display = ("id", "registration", "timestamp", "ignored")
