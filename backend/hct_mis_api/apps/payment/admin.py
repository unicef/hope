from admin_extra_urls.decorators import button
from admin_extra_urls.mixins import ExtraUrlMixin, _confirm_action
from adminfilters.filters import ChoicesFieldComboFilter, TextFieldFilter
from django.contrib import admin, messages
from django.utils.safestring import mark_safe

from hct_mis_api.apps.payment.models import (
    CashPlanPaymentVerification,
    PaymentRecord,
    PaymentVerification,
)
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase


@admin.register(PaymentRecord)
class PaymentRecordAdmin(HOPEModelAdminBase):
    list_display = ("household", "status", "cash_plan_name", "target_population")
    list_filter = (
        ("status", ChoicesFieldComboFilter),
        TextFieldFilter.factory("cash_plan__id", "CashPlan ID"),
        TextFieldFilter.factory("target_population__id", "TargetPopulation ID"),
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
class CashPlanPaymentVerificationAdmin(ExtraUrlMixin, HOPEModelAdminBase):
    list_display = ("cash_plan", "status", "verification_method")
    list_filter = (
        ("status", ChoicesFieldComboFilter),
        ("verification_method", ChoicesFieldComboFilter),
    )
    date_hierarchy = "updated_at"
    raw_id_fields = ("cash_plan",)

    @button()
    def execute_sync_rapid_pro(self, request):
        if request.method == "POST":
            from hct_mis_api.apps.payment.tasks.CheckRapidProVerificationTask import CheckRapidProVerificationTask

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
    list_display = ("payment_record", "household", "status", "cash_plan_id")

    list_filter = (
        ("status", ChoicesFieldComboFilter),
        TextFieldFilter.factory("cash_plan_payment_verification__cash_plan__id", "CashPlan ID"),
        TextFieldFilter.factory("payment_record__household__unicef_id", "Household ID"),
    )
    date_hierarchy = "updated_at"
    raw_id_fields = ("payment_record", "cash_plan_payment_verification")

    def cash_plan_id(self, obj):
        return obj.cash_plan_payment_verification.cash_plan.id

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
