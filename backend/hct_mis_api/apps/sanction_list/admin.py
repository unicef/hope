from django.contrib import admin

from hct_mis_api.apps.utils.admin import HOPEModelAdminBase
from hct_mis_api.apps.sanction_list.models import (
    SanctionListIndividual,
    SanctionListIndividualDocument,
)


@admin.register(SanctionListIndividual)
class SanctionListIndividualAdmin(HOPEModelAdminBase):
    list_display = ("full_name", "listed_on", "un_list_type", "reference_number")
    search_fields = ("full_name",)


@admin.register(SanctionListIndividualDocument)
class SanctionListIndividualDocumentAdmin(HOPEModelAdminBase):
    pass
