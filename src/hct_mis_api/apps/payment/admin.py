from typing import TYPE_CHECKING, Any, Dict, Optional

from django import forms
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db.models import Q, QuerySet
from django.http import HttpRequest, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from admin_cursor_paginator import CursorPaginatorAdmin
from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import confirm_action
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.depot.widget import DepotManager
from adminfilters.filters import ChoicesFieldComboFilter, ValueFilter
from adminfilters.querystring import QueryStringFilter
from advanced_filters.admin import AdminAdvancedFiltersMixin
from smart_admin.mixins import LinkedObjectsMixin

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.payment.models import (
    DeliveryMechanism,
    DeliveryMechanismData,
    DeliveryMechanismPerPaymentPlan,
    FinancialInstitution,
    FinancialInstitutionMapping,
    FinancialServiceProvider,
    FinancialServiceProviderXlsxTemplate,
    FspXlsxTemplatePerDeliveryMechanism,
    Payment,
    PaymentHouseholdSnapshot,
    PaymentPlan,
    PaymentPlanSupportingDocument,
    PaymentVerification,
    PaymentVerificationPlan,
)
from hct_mis_api.apps.payment.services.verification_plan_status_change_services import (
    VerificationPlanStatusChangeServices,
)
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase, PaymentPlanCeleryTasksMixin
from hct_mis_api.apps.utils.security import is_root

if TYPE_CHECKING:
    from uuid import UUID

    from django.forms import Form


@admin.register(PaymentVerificationPlan)
class PaymentVerificationPlanAdmin(LinkedObjectsMixin, HOPEModelAdminBase):
    list_display = (
        "payment_plan",
        "status",
        "verification_channel",
        "sampling",
        "sample_size",
        "activation_date",
        "completion_date",
        "responded_count",
        "received_count",
        "not_received_count",
        "received_with_problems_count",
        "xlsx_file_exporting",
        "xlsx_file_imported",
        "error",
    )
    list_filter = (
        ("payment_plan__program_cycle__program__business_area", AutoCompleteFilter),
        ("payment_plan__program_cycle__program", AutoCompleteFilter),
        ("payment_plan", AutoCompleteFilter),
        ("status", ChoicesFieldComboFilter),
        ("verification_channel", ChoicesFieldComboFilter),
        "sampling",
        "xlsx_file_exporting",
        "xlsx_file_imported",
    )
    date_hierarchy = "updated_at"
    search_fields = ("payment_plan__name",)
    raw_id_fields = ("payment_plan",)

    @button(permission="payment.view_paymentverification")
    def verifications(self, request: HttpRequest, pk: "UUID") -> HttpResponseRedirect:
        list_url = reverse("admin:payment_paymentverification_changelist")
        url = f"{list_url}?payment_verification_plan__exact={pk}"
        return HttpResponseRedirect(url)

    @button(permission="core.execute_sync_rapid_pro")
    def execute_sync_rapid_pro(self, request: HttpRequest) -> Optional[HttpResponseRedirect]:
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
        return None

    def activate(self, request: HttpRequest, pk: "UUID") -> TemplateResponse:
        return confirm_action(
            self,
            request,
            lambda _: VerificationPlanStatusChangeServices(PaymentVerificationPlan.objects.get(pk=pk)).activate(),
            "This action will trigger Cash Plan Payment Verification activation (also sending messages via Rapid Pro).",
            "Successfully activated.",
        )


@admin.register(PaymentVerification)
class PaymentVerificationAdmin(CursorPaginatorAdmin, HOPEModelAdminBase):
    list_display = (
        "payment",
        "household",
        "business_area",
        "status",
        "status_date",
        "received_amount",
        "payment_plan_name",
        "sent_to_rapid_pro",
    )

    list_filter = (
        ("payment_verification_plan__payment_plan__program_cycle__program__business_area", AutoCompleteFilter),
        ("payment_verification_plan__payment_plan__program_cycle__program", AutoCompleteFilter),
        DepotManager,
        QueryStringFilter,
        ("status", ChoicesFieldComboFilter),
        ("payment__household__unicef_id", ValueFilter),
        "sent_to_rapid_pro",
    )
    date_hierarchy = "updated_at"
    raw_id_fields = ("payment_verification_plan", "payment")

    def payment_plan_name(self, obj: PaymentVerification) -> str:  # pragma: no cover
        payment_plan = obj.payment_verification_plan.payment_plan
        return getattr(payment_plan, "name", "~no name~")

    def household(self, obj: PaymentVerification) -> str:  # pragma: no cover
        payment = obj.payment
        return payment.household.unicef_id if payment else ""

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return (
            super()
            .get_queryset(request)
            .select_related("payment_verification_plan")
            .prefetch_related(
                "payment",
                "payment__household",
                "payment_verification_plan__payment_plan",
                "payment_verification_plan__payment_plan__business_area",
            )
        )


@admin.register(PaymentPlan)
class PaymentPlanAdmin(HOPEModelAdminBase, PaymentPlanCeleryTasksMixin):
    list_display = (
        "unicef_id",
        "name",
        "business_area",
        "program_cycle",
        "status",
        "background_action_status",
        "build_status",
        "is_follow_up",
    )
    list_filter = (
        ("business_area", AutoCompleteFilter),
        ("program_cycle__program", AutoCompleteFilter),
        ("program_cycle__program__id", ValueFilter),
        ("currency", AutoCompleteFilter),
        ("status", ChoicesFieldComboFilter),
        ("background_action_status", ChoicesFieldComboFilter),
        ("build_status", ChoicesFieldComboFilter),
        ("created_by", AutoCompleteFilter),
        "is_follow_up",
    )
    raw_id_fields = (
        "business_area",
        "targeting_criteria",
        "created_by",
        "program_cycle",
        "steficon_rule",
        "steficon_rule_targeting",
        "source_payment_plan",
        "storage_file",
        "imported_file",
        "export_file_entitlement",
        "export_file_per_fsp",
        "export_pdf_file_summary",
        "source_payment_plan",
    )
    search_fields = ("id", "unicef_id", "name")
    date_hierarchy = "updated_at"

    def has_delete_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        return is_root(request)


class PaymentHouseholdSnapshotInline(admin.StackedInline):
    model = PaymentHouseholdSnapshot
    readonly_fields = ("snapshot_data", "household_id")


@admin.register(Payment)
class PaymentAdmin(CursorPaginatorAdmin, AdminAdvancedFiltersMixin, HOPEModelAdminBase):
    search_fields = ("unicef_id",)
    list_display = (
        "unicef_id",
        "household",
        "business_area",
        "program",
        "delivery_type",
        "status",
        "parent",
        "entitlement_quantity",
        "delivered_quantity",
        "transaction_reference_id",
        "conflicted",
        "excluded",
        "is_follow_up",
        "is_cash_assist",
    )
    list_filter = (
        ("status", ChoicesFieldComboFilter),
        ("business_area", AutoCompleteFilter),
        ("program", AutoCompleteFilter),
        ("parent", AutoCompleteFilter),
        ("delivery_type", AutoCompleteFilter),
        ("financial_service_provider", AutoCompleteFilter),
        "currency",
    )
    advanced_filter_fields = (
        "status",
        "delivery_date",
        ("financial_service_provider__name", "Service Provider"),
        ("parent", "Payment Plan"),
    )
    date_hierarchy = "updated_at"
    raw_id_fields = (
        "business_area",
        "parent",
        "household",
        "collector",
        "program",
        "source_payment",
        "head_of_household",
        "financial_service_provider",
        "delivery_type",
    )
    inlines = [PaymentHouseholdSnapshotInline]
    exclude = ("delivery_type_choice",)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return (
            super()
            .get_queryset(request)
            .select_related(
                "household",
                "head_of_household",
                "parent",
                "business_area",
                "program",
                "source_payment",
                "delivery_type",
                "financial_service_provider",
            )
        )

    def has_delete_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        return False


@admin.register(DeliveryMechanismPerPaymentPlan)
class DeliveryMechanismPerPaymentPlanAdmin(HOPEModelAdminBase):
    list_display = (
        "financial_service_provider",
        "delivery_mechanism",
        "delivery_mechanism_order",
        "payment_plan",
        "status",
        "created_by",
        "sent_date",
        "sent_to_payment_gateway",
    )
    raw_id_fields = ("payment_plan", "financial_service_provider", "created_by", "sent_by", "delivery_mechanism")
    list_filter = (
        ("financial_service_provider", AutoCompleteFilter),
        ("delivery_mechanism", AutoCompleteFilter),
        ("payment_plan", AutoCompleteFilter),
        ("created_by", AutoCompleteFilter),
        "sent_to_payment_gateway",
    )
    search_fields = ("financial_service_provider__name", "payment_plan__unicef_id")

    def get_queryset(self, request: HttpRequest) -> "QuerySet":
        return (
            super()
            .get_queryset(request)
            .select_related("payment_plan", "financial_service_provider", "created_by", "sent_by", "delivery_mechanism")
        )


@admin.register(FinancialServiceProviderXlsxTemplate)
class FinancialServiceProviderXlsxTemplateAdmin(HOPEModelAdminBase):
    list_display = (
        "name",
        "total_selected_columns",
        "created_by",
    )
    list_filter = (("created_by", AutoCompleteFilter),)
    search_fields = ("name",)
    fields = ("name", "columns", "core_fields", "flex_fields", "document_types")

    def get_queryset(self, request: HttpRequest) -> "QuerySet":
        return (
            super()
            .get_queryset(request)
            .select_related(
                "created_by",
            )
        )

    def total_selected_columns(self, obj: Any) -> str:
        return f"{len(obj.columns)} of {len(FinancialServiceProviderXlsxTemplate.COLUMNS_CHOICES)}"

    total_selected_columns.short_description = "# of columns"

    def save_model(
        self, request: HttpRequest, obj: FinancialServiceProviderXlsxTemplate, form: "Form", change: bool
    ) -> None:
        for required_field in ["payment_id", "delivered_quantity"]:
            if required_field not in obj.columns:
                raise ValidationError(f"'{required_field}' must be present in columns")
        if not change:
            obj.created_by = request.user
        return super().save_model(request, obj, form, change)

    def has_change_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        return request.user.can_change_fsp()

    def has_delete_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        return request.user.can_change_fsp()

    def has_add_permission(self, request: HttpRequest) -> bool:
        return request.user.can_change_fsp()


class FspXlsxTemplatePerDeliveryMechanismForm(forms.ModelForm):
    class Meta:
        model = FspXlsxTemplatePerDeliveryMechanism
        fields = ("financial_service_provider", "delivery_mechanism", "xlsx_template")

    def clean(self) -> Optional[Dict[str, Any]]:
        cleaned_data = super().clean()
        delivery_mechanism = cleaned_data.get("delivery_mechanism")
        financial_service_provider = cleaned_data.get("financial_service_provider")
        xlsx_template = cleaned_data.get("xlsx_template")

        if not delivery_mechanism or not financial_service_provider:
            return cleaned_data

        missing_required_core_fields = [
            required_field
            for required_field in delivery_mechanism.required_fields
            if required_field not in xlsx_template.core_fields
        ]
        if missing_required_core_fields:
            raise ValidationError(
                f"{missing_required_core_fields} fields are required by delivery mechanism "
                f"{delivery_mechanism} and must be present in the template core fields"
            )

        error_message = f"Delivery Mechanism {delivery_mechanism} is not supported by Financial Service Provider {financial_service_provider}"
        # to work both in inline and standalone
        if delivery_mechanisms := self.data.get("delivery_mechanisms"):
            if delivery_mechanism and str(delivery_mechanism.id) not in delivery_mechanisms:
                raise ValidationError(error_message)
        else:
            if delivery_mechanism and delivery_mechanism not in financial_service_provider.delivery_mechanisms.all():
                raise ValidationError(error_message)

        return cleaned_data


@admin.register(FspXlsxTemplatePerDeliveryMechanism)
class FspXlsxTemplatePerDeliveryMechanismAdmin(HOPEModelAdminBase):
    list_display = ("financial_service_provider", "delivery_mechanism", "xlsx_template", "created_by")
    list_filter = (
        ("created_by", AutoCompleteFilter),
        ("financial_service_provider", AutoCompleteFilter),
        ("delivery_mechanism", AutoCompleteFilter),
        ("xlsx_template", AutoCompleteFilter),
    )
    autocomplete_fields = ("financial_service_provider", "xlsx_template")
    fields = ("financial_service_provider", "delivery_mechanism", "xlsx_template", "created_by")
    form = FspXlsxTemplatePerDeliveryMechanismForm

    def get_queryset(self, request: "HttpRequest") -> "QuerySet":
        return (
            super()
            .get_queryset(request)
            .select_related("financial_service_provider", "delivery_mechanism", "xlsx_template", "created_by")
        )

    def save_model(
        self, request: HttpRequest, obj: FspXlsxTemplatePerDeliveryMechanism, form: "Form", change: bool
    ) -> None:
        if not change:
            obj.created_by = request.user
        return super().save_model(request, obj, form, change)

    def has_change_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        return request.user.can_change_fsp()

    def has_delete_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        return request.user.can_change_fsp()

    def has_add_permission(self, request: HttpRequest) -> bool:
        return request.user.can_change_fsp()


class FinancialServiceProviderAdminForm(forms.ModelForm):
    @staticmethod
    def locked_payment_plans_for_fsp(obj: FinancialServiceProvider) -> QuerySet[PaymentPlan]:
        return PaymentPlan.objects.filter(
            ~Q(
                status__in=[
                    PaymentPlan.Status.OPEN,
                    PaymentPlan.Status.FINISHED,
                ],
            ),
            delivery_mechanisms__financial_service_provider=obj,
        ).distinct()

    def clean(self) -> Optional[Dict[str, Any]]:
        if self.instance:
            protected_fields = [
                "name",
                "vision_vendor_number",
                "distribution_limit",
                "communication_channel",
                "xlsx_templates",
            ]
            if any(x in self.changed_data for x in protected_fields):
                payment_plans = self.locked_payment_plans_for_fsp(self.instance)
                if payment_plans.exists():
                    raise ValidationError(
                        f"Cannot modify {self.instance}, it is assigned to following Payment Plans: {list(payment_plans)}"
                    )

        return super().clean()


class FspXlsxTemplatePerDeliveryMechanismAdminInline(admin.TabularInline):
    form = FspXlsxTemplatePerDeliveryMechanismForm
    model = FspXlsxTemplatePerDeliveryMechanism
    extra = 0
    readonly_fields = ("created_by",)
    raw_id_fields = ("financial_service_provider",)


@admin.register(FinancialServiceProvider)
class FinancialServiceProviderAdmin(HOPEModelAdminBase):
    form = FinancialServiceProviderAdminForm

    list_display = (
        "name",
        "vision_vendor_number",
        "communication_channel",
        "distribution_limit",
        "payment_gateway_id",
        "created_by",
    )
    search_fields = ("name", "vision_vendor_number")
    filter_horizontal = ("allowed_business_areas", "delivery_mechanisms", "xlsx_templates")
    autocomplete_fields = ("created_by",)
    list_select_related = ("created_by",)
    list_filter = (
        ("created_by", AutoCompleteFilter),
        "communication_channel",
    )
    fields = (
        ("name", "vision_vendor_number"),
        ("delivery_mechanisms",),
        ("distribution_limit",),
        ("communication_channel", "fsp_xlsx_templates"),
        ("data_transfer_configuration",),
        ("allowed_business_areas",),
    )
    readonly_fields = ("fsp_xlsx_templates", "data_transfer_configuration")
    inlines = (FspXlsxTemplatePerDeliveryMechanismAdminInline,)
    exclude = ("delivery_mechanisms_choices",)

    def fsp_xlsx_templates(self, obj: FinancialServiceProvider) -> str:
        return format_html(
            "<br>".join(
                f"<a href='{reverse('admin:%s_%s_change' % (template._meta.app_label, template._meta.model_name), args=[template.id])}'>{template}</a>"
                for template in obj.fsp_xlsx_template_per_delivery_mechanisms.all()
            )
        )

    fsp_xlsx_templates.short_description = "FSP XLSX Templates"
    fsp_xlsx_templates.allow_tags = True

    def save_model(self, request: HttpRequest, obj: FinancialServiceProvider, form: "Form", change: bool) -> None:
        if not change:
            obj.created_by = request.user
        return super().save_model(request, obj, form, change)

    def has_change_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        return request.user.can_change_fsp()

    def has_delete_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        return request.user.can_change_fsp()

    def has_add_permission(self, request: HttpRequest) -> bool:
        return request.user.can_change_fsp()


@admin.register(DeliveryMechanismData)
class DeliveryMechanismDataAdmin(HOPEModelAdminBase):
    list_display = ("individual", "get_business_area", "get_program", "delivery_mechanism", "is_valid")

    raw_id_fields = ("delivery_mechanism", "individual", "possible_duplicate_of")
    readonly_fields = ("possible_duplicate_of", "unique_key", "signature_hash", "validation_errors")
    search_fields = ("individual__unicef_id",)
    list_filter = (
        ("individual__program__business_area", AutoCompleteFilter),
        ("individual__program", AutoCompleteFilter),
        ("individual", AutoCompleteFilter),
        ("delivery_mechanism", AutoCompleteFilter),
        "is_valid",
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("individual__program__business_area")

    def get_business_area(self, obj: DeliveryMechanismData) -> BusinessArea:
        return obj.individual.program.business_area

    def get_program(self, obj: DeliveryMechanismData) -> Program:
        return obj.individual.program


@admin.register(DeliveryMechanism)
class DeliveryMechanismAdmin(HOPEModelAdminBase):
    list_display = ("code", "name", "is_active", "transfer_type")
    search_fields = ("code", "name")
    list_filter = ("is_active", "transfer_type")


@admin.register(PaymentPlanSupportingDocument)
class PaymentPlanSupportingDocumentAdmin(HOPEModelAdminBase):
    search_fields = ("title",)
    list_display = ("title", "payment_plan", "created_by", "uploaded_at")
    list_filter = (("created_by", AutoCompleteFilter),)
    raw_id_fields = (
        "payment_plan",
        "created_by",
    )


@admin.register(FinancialInstitutionMapping)
class FinancialInstitutionMappingAdmin(HOPEModelAdminBase):
    list_display = (
        "financial_institution",
        "financial_service_provider",
        "code",
    )
    search_fields = (
        "code",
        "financial_institution__code",
        "financial_institution__name",
        "financial_service_provider__name",
        "financial_service_provider__vision_vendor_number",
    )
    list_filter = (
        ("financial_institution", AutoCompleteFilter),
        ("financial_service_provider", AutoCompleteFilter),
    )
    raw_id_fields = ("financial_institution", "financial_service_provider")


@admin.register(FinancialInstitution)
class FinancialInstitutionAdmin(HOPEModelAdminBase):
    list_display = (
        "code",
        "name",
        "type",
        "country",
    )
    search_fields = ("code", "name")
    list_filter = (
        ("country", AutoCompleteFilter),
        "type",
    )
    raw_id_fields = ("country",)
