from django.contrib import admin

from sanction_list.models import (
    SanctionListIndividual,
    SanctionListIndividualDocument,
)


@admin.register(SanctionListIndividual)
class SanctionListIndividualAdmin(admin.ModelAdmin):
    pass


@admin.register(SanctionListIndividualDocument)
class SanctionListIndividualDocumentAdmin(admin.ModelAdmin):
    pass
