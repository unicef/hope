from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.safestring import mark_safe

from admin_extra_urls.decorators import button
from admin_extra_urls.mixins import ExtraUrlMixin, _confirm_action
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.filters import ChoicesFieldComboFilter, TextFieldFilter
from advanced_filters.admin import AdminAdvancedFiltersMixin
from smart_admin.mixins import LinkedObjectsMixin

from hct_mis_api.apps.payment.models import (
    CashPlanPaymentVerification,
    PaymentRecord,
    PaymentVerification,
    ServiceProvider,
)
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase


@admin.register(PaymentRecord)
class PaymentRecordAdmin(AdminAdvancedFiltersMixin, HOPEModelAdminBase):
    list_display = ("household", "status", "cash_plan_name", "target_population")
    list_filter = (
        ("status", ChoicesFieldComboFilter),
        ("business_area", AutoCompleteFilter),
        ("target_population", AutoCompleteFilter),
        ("cash_plan", AutoCompleteFilter),
        ("service_provider", AutoCompleteFilter),
        # TextFieldFilter.factory("cash_plan__id", "CashPlan ID"),
        # TextFieldFilter.factory("target_population__id", "TargetPopulation ID"),
    )
    advanced_filter_fields = (
        "status",
        "delivery_date",
        ("service_provider__name", "Service Provider"),
        ("cash_plan__name", "CashPlan"),
        ("target_population__name", "TargetPopulation"),
    )
    date_hierarchy = "updated_at"
    raw_id_fields = (
        "business_area",
        "cash_plan",
        "household",
        "head_of_household",
        "target_population",
        "service_provider",
    )

    def cash_plan_name(self, obj):
        return obj.cash_plan.name

    def get_queryset(self, request):
        return (
            super().get_queryset(request).select_related("household", "cash_plan", "target_population", "business_area")
        )


@admin.register(CashPlanPaymentVerification)
class CashPlanPaymentVerificationAdmin(ExtraUrlMixin, LinkedObjectsMixin, HOPEModelAdminBase):
    list_display = ("cash_plan", "status", "verification_method")
    list_filter = (
        ("status", ChoicesFieldComboFilter),
        ("verification_method", ChoicesFieldComboFilter),
        ("cash_plan", AutoCompleteFilter),
        ("cash_plan__business_area", AutoCompleteFilter),
    )
    date_hierarchy = "updated_at"
    search_fields = ("cash_plan__name",)
    raw_id_fields = ("cash_plan",)

    @button()
    def verifications(self, request, pk):
        list_url = reverse("admin:payment_paymentverification_changelist")
        url = f"{list_url}?cash_plan_payment_verification__exact={pk}"
        return HttpResponseRedirect(url)

    @button()
    def execute_sync_rapid_pro(self, request):
        if request.method == "POST":
            from hct_mis_api.apps.payment.tasks.CheckRapidProVerificationTask import (
                CheckRapidProVerificationTask,
            )

            task = CheckRapidProVerificationTask()
            task.execute()
            self.message_user(request, "Rapid Pro synced", messages.SUCCESS)
        else:
            return _confirm_action(
                self,
                request,
                self.execute_sync_rapid_pro,
                mark_safe(
                    """<h1>DO NOT CONTINUE IF YOU ARE NOT SURE WHAT YOU ARE DOING</h1>                
                        <h3>Import will only be simulated</h3> 
                        """
                ),
                "Successfully executed",
                template="admin_extra_urls/confirm.html",
            )


@admin.register(PaymentVerification)
class PaymentVerificationAdmin(HOPEModelAdminBase):
    list_display = ("household", "status", "received_amount", "cash_plan_name")

    list_filter = (
        ("status", ChoicesFieldComboFilter),
        ("cash_plan_payment_verification__cash_plan", AutoCompleteFilter),
        ("cash_plan_payment_verification__cash_plan__business_area", AutoCompleteFilter),
        ("payment_record__household__unicef_id", TextFieldFilter.factory(title="Household ID")),
    )
    date_hierarchy = "updated_at"
    raw_id_fields = ("payment_record", "cash_plan_payment_verification")

    def cash_plan_name(self, obj):
        return obj.cash_plan_payment_verification.cash_plan.name

    def household(self, obj):
        return obj.payment_record.household.unicef_id

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "cash_plan_payment_verification",
                "cash_plan_payment_verification__cash_plan",
                "payment_record",
                "payment_record__household",
            )
        )


@admin.register(ServiceProvider)
class ServiceProviderAdmin(HOPEModelAdminBase):
    list_display = ("full_name", "short_name", "country")
    search_fields = ("full_name", "vision_id", "short_name")
    list_filter = (("business_area", AutoCompleteFilter),)
