from django.contrib import admin

from adminfilters.filters import ValueFilter


from hct_mis_api.apps.sanction_list.models import (
    SanctionListIndividual,
    SanctionListIndividualDateOfBirth,
    SanctionListIndividualDocument,
)
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase


class SanctionListIndividualDateOfBirthAdmin(admin.StackedInline):
    model = SanctionListIndividualDateOfBirth
    extra = 0


@admin.register(SanctionListIndividual)
class SanctionListIndividualAdmin(HOPEModelAdminBase):
    list_display = ("full_name", "listed_on", "un_list_type", "reference_number")
    search_fields = ("full_name",)
    list_filter = ("un_list_type",)
    inlines = (SanctionListIndividualDateOfBirthAdmin,)


@admin.register(SanctionListIndividualDocument)
class SanctionListIndividualDocumentAdmin(HOPEModelAdminBase):
    list_display = ("document_number", "type_of_document", "date_of_issue", "issuing_country")
    raw_id_fields = ("individual",)
    list_filter = (("issuing_country", ValueFilter), "type_of_document")
