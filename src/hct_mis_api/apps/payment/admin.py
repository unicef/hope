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

from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import confirm_action
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.depot.widget import DepotManager
from adminfilters.filters import ChoicesFieldComboFilter, ValueFilter
from adminfilters.querystring import QueryStringFilter
from advanced_filters.admin import AdminAdvancedFiltersMixin
from smart_admin.mixins import LinkedObjectsMixin

from hct_mis_api.apps.payment.models import (
    DeliveryMechanism,
    DeliveryMechanismData,
    DeliveryMechanismPerPaymentPlan,
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
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase, PaymentPlanCeleryTasksMixin
from hct_mis_api.apps.utils.security import is_root

if TYPE_CHECKING:
    from uuid import UUID

    from django.forms import Form


@admin.register(PaymentVerificationPlan)
class PaymentVerificationPlanAdmin(LinkedObjectsMixin, HOPEModelAdminBase):
    list_display = ("payment_plan", "status", "verification_channel")
    list_filter = (
        ("status", ChoicesFieldComboFilter),
        ("verification_channel", ChoicesFieldComboFilter),
    )
    date_hierarchy = "updated_at"
    search_fields = ("payment_plan__name",)
    raw_id_fields = ("payment_plan",)

    @button()
    def verifications(self, request: HttpRequest, pk: "UUID") -> HttpResponseRedirect:
        list_url = reverse("admin:payment_paymentverification_changelist")
        url = f"{list_url}?payment_verification_plan__exact={pk}"
        return HttpResponseRedirect(url)

    @button()
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
class PaymentVerificationAdmin(HOPEModelAdminBase):
    list_display = ("household", "status", "received_amount", "payment_plan_name", "business_area")

    list_filter = (
        DepotManager,
        QueryStringFilter,
        ("status", ChoicesFieldComboFilter),
        ("payment__household__unicef_id", ValueFilter),
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
    list_display = ("unicef_id", "program_cycle", "status", "target_population")
    list_filter = (
        ("status", ChoicesFieldComboFilter),
        ("business_area", AutoCompleteFilter),
        ("program_cycle__program__id", ValueFilter),
        ("target_population", AutoCompleteFilter),
    )
    raw_id_fields = ("business_area", "target_population", "created_by", "program_cycle")
    search_fields = ("id", "unicef_id")

    def has_delete_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        return is_root(request)


class PaymentHouseholdSnapshotInline(admin.StackedInline):
    model = PaymentHouseholdSnapshot
    readonly_fields = ("snapshot_data", "household_id")


@admin.register(Payment)
class PaymentAdmin(AdminAdvancedFiltersMixin, HOPEModelAdminBase):
    list_display = ("unicef_id", "household", "status", "parent")
    list_filter = (
        ("status", ChoicesFieldComboFilter),
        ("business_area", AutoCompleteFilter),
        ("parent", AutoCompleteFilter),
        ("financial_service_provider", AutoCompleteFilter),
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
    )
    inlines = [PaymentHouseholdSnapshotInline]
    exclude = ("delivery_type_choice",)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("household", "parent", "business_area")

    def has_delete_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        return False


@admin.register(DeliveryMechanismPerPaymentPlan)
class DeliveryMechanismPerPaymentPlanAdmin(HOPEModelAdminBase):
    list_display = ("delivery_mechanism_order", "delivery_mechanism", "payment_plan", "status")
    raw_id_fields = ("payment_plan", "financial_service_provider", "created_by", "sent_by")


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
    fields = ("financial_service_provider", "delivery_mechanism", "xlsx_template")
    autocomplete_fields = ("financial_service_provider", "xlsx_template")
    form = FspXlsxTemplatePerDeliveryMechanismForm

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
        "created_by",
        "vision_vendor_number",
        "distribution_limit",
        "communication_channel",
    )
    search_fields = ("name",)
    # filter_horizontal = ("delivery_mechanisms",)
    filter_horizontal = ("allowed_business_areas",)
    autocomplete_fields = ("created_by",)
    list_select_related = ("created_by",)
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
    list_display = ("individual", "delivery_mechanism", "is_valid")
    raw_id_fields = ("individual", "possible_duplicate_of")
    readonly_fields = ("possible_duplicate_of", "unique_key", "signature_hash", "validation_errors")


@admin.register(DeliveryMechanism)
class DeliveryMechanismAdmin(HOPEModelAdminBase):
    list_display = ("code", "name", "is_active", "transfer_type")


@admin.register(PaymentPlanSupportingDocument)
class PaymentPlanSupportingDocumentAdmin(HOPEModelAdminBase):
    list_display = ("title", "created_by", "uploaded_at")
