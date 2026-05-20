from adminfilters.autocomplete import AutoCompleteFilter
from django.contrib import admin

from hope.admin.utils import AutocompleteForeignKeyMixin, HOPEModelAdminBase
from hope.models import FinancialInstitution, FinancialInstitutionMapping


class FinancialInstitutionMappingInline(AutocompleteForeignKeyMixin, admin.TabularInline):
    model = FinancialInstitutionMapping
    extra = 0


@admin.register(FinancialInstitution)
class FinancialInstitutionAdmin(HOPEModelAdminBase):
    list_display = (
        "id",
        "name",
        "type",
        "country",
    )
    search_fields = ("id", "name")
    list_filter = (
        ("country", AutoCompleteFilter),
        "type",
    )

    inlines = [FinancialInstitutionMappingInline]


@admin.register(FinancialInstitutionMapping)
class FinancialInstitutionMappingAdmin(HOPEModelAdminBase):
    list_display = (
        "financial_institution",
        "financial_service_provider",
        "code",
    )
    search_fields = (
        "code",
        "financial_institution__id",
        "financial_institution__name",
        "financial_service_provider__name",
        "financial_service_provider__vision_vendor_number",
    )
    list_filter = (
        ("financial_institution", AutoCompleteFilter),
        ("financial_service_provider", AutoCompleteFilter),
    )
