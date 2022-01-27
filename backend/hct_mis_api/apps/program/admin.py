from django.contrib import admin
from django.template.response import TemplateResponse

from admin_extra_urls.decorators import button
from admin_extra_urls.mixins import ExtraUrlMixin
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.filters import (
    ChoicesFieldComboFilter,
    RelatedFieldComboFilter,
    TextFieldFilter,
)

from ..utils.admin import (
    HOPEModelAdminBase,
    LastSyncDateResetMixin,
    SoftDeletableAdminMixin,
)
from .models import CashPlan, Program


@admin.register(Program)
class ProgramAdmin(SoftDeletableAdminMixin, LastSyncDateResetMixin, HOPEModelAdminBase):
    list_display = ("name", "status", "start_date", "end_date", "business_area")
    date_hierarchy = "start_date"
    list_filter = (
        ("status", ChoicesFieldComboFilter),
        ("business_area", AutoCompleteFilter),
        ("scope", ChoicesFieldComboFilter),
    )
    raw_id_fields = ("business_area",)
    filter_horizontal = ("admin_areas",)


@admin.register(CashPlan)
class CashPlanAdmin(ExtraUrlMixin, HOPEModelAdminBase):
    list_display = ("name", "program", "delivery_type", "status", "verification_status")
    list_filter = (
        ("status", ChoicesFieldComboFilter),
        ("business_area", AutoCompleteFilter),
        ("delivery_type", ChoicesFieldComboFilter),
        ("verification_status", ChoicesFieldComboFilter),
        TextFieldFilter.factory("program__id", "Program ID"),
        TextFieldFilter.factory("vision_id", "Vision ID"),
    )
    raw_id_fields = ("business_area", "program", "service_provider")
    search_fields = ("name",)

    @button()
    def payments(self, request, pk):
        context = self.get_common_context(request, pk, aeu_groups=[None], action="payments")

        return TemplateResponse(request, "admin/cashplan/payments.html", context)
