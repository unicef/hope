from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.safestring import mark_safe

from admin_extra_urls.decorators import button, href
from admin_extra_urls.mixins import ExtraUrlMixin
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.filters import ChoicesFieldComboFilter, TextFieldFilter

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
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase


@admin.register(RegistrationDataImportDatahub)
class RegistrationDataImportDatahubAdmin(ExtraUrlMixin, HOPEModelAdminBase):
    list_display = ("name", "import_date", "import_done", "business_area_slug", "hct_id")
    list_filter = (
        "import_done",
        TextFieldFilter.factory("business_area_slug__istartswith"),
    )
    raw_id_fields = ("import_data",)
    date_hierarchy = "import_date"
    search_fields = ("name",)

    @href(
        label="RDI",
    )
    def hub(self, button):
        obj = button.context.get("original")
        if obj and obj.hct_id:
            return reverse("admin:registration_data_registrationdataimport_change", args=[obj.hct_id])
        else:
            button.html_attrs = {"style": "background-color:#CCCCCC;cursor:not-allowed"}
            return "javascript:alert('RDI not imported');"

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


@admin.register(ImportedIndividual)
class ImportedIndividualAdmin(ExtraUrlMixin, HOPEModelAdminBase):
    list_display = (
        "registration_data_import",
        "individual_id",
        "full_name",
        "sex",
        "dedupe_status",
    )
    list_filter = (
        TextFieldFilter.factory("registration_data_import__name__istartswith"),
        TextFieldFilter.factory("individual_id__istartswith"),
        "deduplication_batch_status",
        "deduplication_golden_record_status",
    )
    date_hierarchy = "updated_at"
    raw_id_fields = ("household", "registration_data_import")

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
class KoboImportedSubmissionAdmin(HOPEModelAdminBase):
    list_display = (
        "kobo_submission_time",
        "kobo_submission_uuid",
        "kobo_asset_id",
        "imported_household_id",
        "registration_data_import_id",
    )
    date_hierarchy = "kobo_submission_time"
    list_filter = (
        ("registration_data_import", AutoCompleteFilter),
        ("imported_household", AutoCompleteFilter),
    )
    raw_id_fields = ("registration_data_import", "imported_household")
