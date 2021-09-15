from django.contrib import admin

from adminfilters.filters import ChoicesFieldComboFilter, RelatedFieldComboFilter

from hct_mis_api.apps.sanction_list.models import (
    SanctionListIndividual,
    SanctionListIndividualDocument,
)
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase


@admin.register(SanctionListIndividual)
class SanctionListIndividualAdmin(HOPEModelAdminBase):
    list_display = ("full_name", "listed_on", "un_list_type", "reference_number")
    search_fields = ("full_name",)


@admin.register(SanctionListIndividualDocument)
class SanctionListIndividualDocumentAdmin(HOPEModelAdminBase):
    list_display = ("document_number", "type_of_document", "date_of_issue", "issuing_country")
    raw_id_fields = ("individual",)
    list_filter = (("issuing_country", ChoicesFieldComboFilter),)
