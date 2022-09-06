from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.template.response import TemplateResponse

from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import ExtraButtonsMixin, confirm_action
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.filters import ChoicesFieldComboFilter, ValueFilter
from advanced_filters.admin import AdminAdvancedFiltersMixin
from smart_admin.mixins import LinkedObjectsMixin

from hct_mis_api.apps.payment.models import (
    CashPlanPaymentVerification,
    FinancialServiceProvider,
    FinancialServiceProviderXlsxReport,
    FinancialServiceProviderXlsxTemplate,
    PaymentRecord,
    PaymentVerification,
    ServiceProvider,
    CashPlan,
    PaymentPlan,
    Payment,
    DeliveryMechanismPerPaymentPlan,
    PaymentChannel,
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
        # ValueFilter.factory("cash_plan__id", "CashPlan ID"),
        # ValueFilter.factory("target_population__id", "TargetPopulation ID"),
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
class CashPlanPaymentVerificationAdmin(ExtraButtonsMixin, LinkedObjectsMixin, HOPEModelAdminBase):
    list_display = ("cash_plan", "status", "verification_channel")
    list_filter = (
        ("status", ChoicesFieldComboFilter),
        ("verification_channel", ChoicesFieldComboFilter),
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
            return confirm_action(
                self,
                request,
                self.execute_sync_rapid_pro,
                mark_safe(
                    """<h1>DO NOT CONTINUE IF YOU ARE NOT SURE WHAT YOU ARE DOING</h1>
                        <h3>Import will only be simulated</h3>
                        """
                ),
                "Successfully executed",
                template="admin_extra_buttons/confirm.html",
            )


@admin.register(PaymentVerification)
class PaymentVerificationAdmin(HOPEModelAdminBase):
    list_display = ("household", "status", "received_amount", "cash_plan_name")

    list_filter = (
        ("status", ChoicesFieldComboFilter),
        ("cash_plan_payment_verification__cash_plan", AutoCompleteFilter),
        ("cash_plan_payment_verification__cash_plan__business_area", AutoCompleteFilter),
        ("payment_record__household__unicef_id", ValueFilter),
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


@admin.register(CashPlan)
class CashPlanAdmin(ExtraButtonsMixin, HOPEModelAdminBase):
    list_display = ("name", "program", "delivery_type", "status", "verification_status", "ca_id")
    list_filter = (
        ("status", ChoicesFieldComboFilter),
        ("business_area", AutoCompleteFilter),
        ("delivery_type", ChoicesFieldComboFilter),
        ("cash_plan_payment_verification_summary__status", ChoicesFieldComboFilter),
        ("program__id", ValueFilter),
        ("vision_id", ValueFilter),
    )
    raw_id_fields = ("business_area", "program", "service_provider")
    search_fields = ("name",)

    def verification_status(self, obj):
        return obj.cash_plan_payment_verification_summary.status

    @button()
    def payments(self, request, pk):
        context = self.get_common_context(request, pk, aeu_groups=[None], action="payments")

        return TemplateResponse(request, "admin/cashplan/payments.html", context)


@admin.register(PaymentPlan)
class PaymentPlanAdmin(HOPEModelAdminBase):
    list_display = ("unicef_id", "program", "status", "target_population")
    list_filter = (
        ("status", ChoicesFieldComboFilter),
        ("business_area", AutoCompleteFilter),
        ("program__id", ValueFilter),
        ("target_population", AutoCompleteFilter),
    )
    raw_id_fields = ("business_area", "program", "target_population")
    search_fields = ("id", "unicef_id")


@admin.register(Payment)
class PaymentAdmin(AdminAdvancedFiltersMixin, HOPEModelAdminBase):
    list_display = ("unicef_id", "household", "status", "payment_plan")
    list_filter = (
        ("status", ChoicesFieldComboFilter),
        ("business_area", AutoCompleteFilter),
        ("payment_plan", AutoCompleteFilter),
        ("financial_service_provider", AutoCompleteFilter),
    )
    advanced_filter_fields = (
        "status",
        "delivery_date",
        ("financial_service_provider__name", "Service Provider"),
        ("payment_plan", "PaymentPlan"),
    )
    date_hierarchy = "updated_at"
    raw_id_fields = (
        "business_area",
        "payment_plan",
        "household",
        "head_of_household",
        "financial_service_provider",
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("household", "payment_plan", "business_area")


@admin.register(DeliveryMechanismPerPaymentPlan)
class DeliveryMechanismPerPaymentPlanAdmin(HOPEModelAdminBase):
    list_display = ("delivery_mechanism_order", "delivery_mechanism", "payment_plan", "status")


@admin.register(PaymentChannel)
class PaymentChannelAdmin(HOPEModelAdminBase):
    list_display = ("individual", "delivery_mechanism_display_name")

    def delivery_mechanism_display_name(self, obj):
        return obj.delivery_mechanism


@admin.register(FinancialServiceProviderXlsxTemplate)
class FinancialServiceProviderXlsxTemplateAdmin(HOPEModelAdminBase):
    list_display = (
        "name",
        "total_selected_columns",
        "created_by",
    )
    list_filter = (("created_by", AutoCompleteFilter),)
    search_fields = ("name",)
    fields = (
        "name",
        "columns",
    )

    def total_selected_columns(self, obj):
        return f"{len(obj.columns)} of {len(FinancialServiceProviderXlsxTemplate.COLUMNS_TO_CHOOSE)}"

    total_selected_columns.short_description = "# of columns"

    def save_model(self, request, obj: FinancialServiceProviderXlsxTemplate, form, change: bool) -> None:
        if not change:
            obj.created_by = request.user
        return super().save_model(request, obj, form, change)


@admin.register(FinancialServiceProvider)
class FinancialServiceProviderAdmin(HOPEModelAdminBase):
    list_display = (
        "name",
        "created_by",
        "vision_vendor_number",
        "distribution_limit",
        "communication_channel",
    )
    search_fields = ("name",)
    list_filter = ("delivery_mechanisms",)
    autocomplete_fields = ("created_by", "fsp_xlsx_template")
    list_select_related = ("created_by", "fsp_xlsx_template")
    fields = (
        ("name", "vision_vendor_number"),
        ("delivery_mechanisms", "distribution_limit"),
        ("communication_channel", "fsp_xlsx_template"),
        ("data_transfer_configuration",),
    )

    def save_model(self, request, obj: FinancialServiceProvider, form, change: bool) -> None:
        if not change:
            obj.created_by = request.user
        return super().save_model(request, obj, form, change)


@admin.register(FinancialServiceProviderXlsxReport)
class FinancialServiceProviderXlsxReportAdmin(HOPEModelAdminBase):
    list_display = ("id", "status", "file")
    list_filter = ("status",)
    list_select_related = ("financial_service_provider",)
    # search_fields = ("id",)
    readonly_fields = ("file", "status", "financial_service_provider")

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False
