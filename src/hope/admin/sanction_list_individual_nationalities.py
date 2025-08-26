from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest

from hope.admin.utils import HOPEModelAdminBase
from hope.models.sanction_list_Individual_nationalities import SanctionListIndividualNationalities


@admin.register(SanctionListIndividualNationalities)
class SanctionListIndividualNationalitiesAdmin(HOPEModelAdminBase):
    list_display = ("nationality", "individual")
    readonly_fields = ("nationality", "individual")
    list_filter = ("individual__sanction_list",)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("individual", "nationality")
