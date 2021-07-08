from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.safestring import mark_safe

from admin_extra_urls.decorators import button
from admin_extra_urls.mixins import ExtraUrlMixin
from adminfilters.filters import TextFieldFilter

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
class RegistrationDataImportDatahubAdmin(HOPEModelAdminBase):
    pass


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
    pass


@admin.register(ImportedHousehold)
class ImportedHouseholdAdmin(HOPEModelAdminBase):
    pass


@admin.register(ImportData)
class ImportDataAdmin(HOPEModelAdminBase):
    pass


@admin.register(ImportedDocument)
class ImportedDocumentAdmin(HOPEModelAdminBase):
    list_display = ("document_number", "type", "individual")


@admin.register(ImportedDocumentType)
class ImportedDocumentTypeAdmin(HOPEModelAdminBase):
    list_display = ("label", "country")


@admin.register(ImportedIndividualRoleInHousehold)
class ImportedIndividualRoleInHouseholdAdmin(HOPEModelAdminBase):
    pass


@admin.register(KoboImportedSubmission)
class KoboImportedSubmissionAdmin(HOPEModelAdminBase):
    pass
