from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import AutoCompleteFilter
from django.contrib import admin
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse

from hope.admin.utils import HOPEModelAdminBase
from hope.models import PaymentPlanPurpose


@admin.register(PaymentPlanPurpose)
class PaymentPlanPurposeAdmin(HOPEModelAdminBase):
    list_display = ("unicef_id", "name", "business_area", "description")
    list_filter = (("business_area", AutoCompleteFilter),)
    search_fields = ("name",)

    @button(permission="core.view_paymentplanpurpose")
    def programs(self, request: HttpRequest, pk: str) -> HttpResponseRedirect:
        url = reverse("admin:program_program_changelist")
        return HttpResponseRedirect(f"{url}?payment_plan_purposes__id__exact={pk}")

    @button(permission="core.view_paymentplanpurpose")
    def payment_plans(self, request: HttpRequest, pk: str) -> HttpResponseRedirect:
        url = reverse("admin:payment_paymentplan_changelist")
        return HttpResponseRedirect(f"{url}?payment_plan_purposes__id__exact={pk}")
