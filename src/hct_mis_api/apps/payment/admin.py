from typing import TYPE_CHECKING, Any, Dict, List, Optional

from admin_cursor_paginator import CursorPaginatorAdmin
from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import confirm_action
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.depot.widget import DepotManager
from adminfilters.filters import ChoicesFieldComboFilter, ValueFilter
from adminfilters.querystring import QueryStringFilter
from advanced_filters.admin import AdminAdvancedFiltersMixin
from django import forms
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db.models import Q, QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from smart_admin.mixins import LinkedObjectsMixin

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.payment.models import (
    Account, AccountType, DeliveryMechanism, DeliveryMechanismConfig,
    FinancialInstitution, FinancialServiceProvider,
    FinancialServiceProviderXlsxTemplate, FspNameMapping,
    FspXlsxTemplatePerDeliveryMechanism, Payment, PaymentHouseholdSnapshot,
    PaymentPlan, PaymentPlanSupportingDocument, PaymentVerification,
    PaymentVerificationPlan)
from hct_mis_api.apps.payment.models.payment import FinancialInstitutionMapping
from hct_mis_api.apps.payment.services.verification_plan_status_change_services import \
    VerificationPlanStatusChangeServices
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.utils.admin import (HOPEModelAdminBase,
                                          PaymentPlanCeleryTasksMixin)
from hct_mis_api.apps.utils.security import is_root
from hct_mis_api.contrib.vision.models import FundsCommitmentItem

if TYPE_CHECKING:
    from uuid import UUID

    from django.forms import Form


class ArrayFieldWidget(forms.Textarea):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.delimiter = kwargs.pop("delimiter", ",")
        super().__init__(*args, **kwargs)

    def format_value(self, value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, list):
            # Join list items with newline instead of comma for each value to be in a new line
            return "\n".join(str(v) for v in value)
        return value

    def value_from_datadict(self, data: Any, files: Any, name: Any) -> List[str]:
        value = data.get(name, "")
        if not value:
            return []
        # Split by newline and strip any extra spaces
        return [v.strip() for v in value.splitlines()]


class CommaSeparatedArrayField(forms.Field):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.base_field = forms.CharField()
        self.widget = ArrayFieldWidget()
        self.delimiter = kwargs.pop("delimiter", ",")
        super().__init__(*args, **kwargs)

    def prepare_value(self, value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, list):
            # Prepare value to be displayed as a newline-separated string
            return "\n".join(str(self.base_field.prepare_value(v)) for v in value)
        return value

    def to_python(self, value: Any) -> List[str]:
        if not value:
            return []
        if isinstance(value, list):
            return value
        return [self.base_field.to_python(v) for v in value.splitlines()]

    def validate(self, value: Any) -> None:
        super().validate(value)
        for item in value:
            self.base_field.validate(item)


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
            from hct_mis_api.apps.payment.tasks.CheckRapidProVerificationTask import \
                CheckRapidProVerificationTask

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


class FundsCommitmentItemInline(admin.TabularInline):  # or admin.StackedInline
    model = FundsCommitmentItem
    extra = 0
    can_delete = False
    show_change_link = True
    fields = readonly_fields = (
        "rec_serial_number",
        "funds_commitment_group",
        "funds_commitment_item",
        "fc_status",
        "commitment_amount_local",
        "commitment_amount_usd",
        "total_open_amount_local",
        "total_open_amount_usd",
    )
    raw_id_fields = ("funds_commitment_group",)

    def has_add_permission(self: Any, request: Any, obj: Any = None) -> bool:
        return False

    def has_change_permission(self: Any, request: Any, obj: Any = None) -> bool:
        return False

    def has_delete_permission(self: Any, request: Any, obj: Any = None) -> bool:
        return False


def can_sync_with_payment_gateway(payment_plan: PaymentPlan) -> bool:
    return payment_plan.is_payment_gateway and payment_plan.status == PaymentPlan.Status.ACCEPTED  # pragma: no cover


def has_payment_plan_pg_sync_permission(request: Any, payment_plan: PaymentPlan) -> bool:
    return request.user.has_permission(
        Permissions.PM_SYNC_PAYMENT_PLAN_WITH_PG.value,
        payment_plan.business_area,
        payment_plan.program_cycle.program_id,
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
    inlines = [FundsCommitmentItemInline]

    def has_delete_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        return is_root(request)

    @button(
        visible=lambda btn: can_sync_with_payment_gateway(btn.original),
        permission=lambda request, payment_plan, *args, **kwargs: has_payment_plan_pg_sync_permission(
            request, payment_plan
        ),
    )
    def sync_with_payment_gateway(self, request: HttpRequest, pk: "UUID") -> HttpResponse:
        if request.method == "POST":
            from hct_mis_api.apps.payment.services.payment_gateway import \
                PaymentGatewayService

            payment_plan = PaymentPlan.objects.get(pk=pk)
            PaymentGatewayService().sync_payment_plan(payment_plan)

            return redirect(reverse("admin:payment_paymentplan_change", args=[pk]))
        else:
            return confirm_action(
                modeladmin=self,
                request=request,
                action=self.sync_with_payment_gateway,
                message="Do you confirm to Sync with Payment Gateway?",
            )


class PaymentHouseholdSnapshotInline(admin.StackedInline):
    model = PaymentHouseholdSnapshot
    readonly_fields = ("snapshot_data", "household_id")


def has_payment_pg_sync_permission(request: Any, payment: Payment) -> bool:
    return request.user.has_permission(
        Permissions.PM_SYNC_PAYMENT_WITH_PG.value,
        payment.business_area,
        payment.parent.program_cycle.program_id,
    )


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

    @button(
        visible=lambda btn: can_sync_with_payment_gateway(btn.original.parent),
        permission=lambda request, payment, *args, **kwargs: has_payment_pg_sync_permission(request, payment),
    )
    def sync_with_payment_gateway(self, request: HttpRequest, pk: "UUID") -> HttpResponse:
        if request.method == "POST":
            from hct_mis_api.apps.payment.services.payment_gateway import \
                PaymentGatewayService

            payment = Payment.objects.get(pk=pk)
            PaymentGatewayService().sync_record(payment)

            return redirect(reverse("admin:payment_payment_change", args=[pk]))
        else:
            return confirm_action(
                modeladmin=self,
                request=request,
                action=self.sync_with_payment_gateway,
                message="Do you confirm to Sync with Payment Gateway?",
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

        if not delivery_mechanism or not financial_service_provider:
            return cleaned_data

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
            financial_service_provider=obj,
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


class FspNameMappingInline(admin.TabularInline):  # or admin.StackedInline
    model = FspNameMapping
    extra = 1
    min_num = 0
    fields = ("external_name", "hope_name", "source")
    autocomplete_fields = ("fsp",)


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
        ("payment_gateway_id",),
    )
    readonly_fields = ("fsp_xlsx_templates", "data_transfer_configuration")
    inlines = (FspXlsxTemplatePerDeliveryMechanismAdminInline, FspNameMappingInline)

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


@admin.register(Account)
class DeliveryMechanismDataAdmin(HOPEModelAdminBase):
    list_display = ("individual", "get_business_area", "get_program", "account_type", "is_unique")

    raw_id_fields = ("account_type", "individual")
    readonly_fields = ("unique_key", "signature_hash")
    search_fields = ("individual__unicef_id",)
    list_filter = (
        ("individual__program__business_area", AutoCompleteFilter),
        ("individual__program", AutoCompleteFilter),
        ("individual", AutoCompleteFilter),
        ("account_type", AutoCompleteFilter),
        "is_unique",
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("individual__program__business_area")

    def get_business_area(self, obj: Account) -> BusinessArea:
        return obj.individual.program.business_area

    def get_program(self, obj: Account) -> Program:
        return obj.individual.program


@admin.register(DeliveryMechanism)
class DeliveryMechanismAdmin(HOPEModelAdminBase):
    list_display = ("code", "name", "is_active", "transfer_type", "account_type")
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


@admin.register(AccountType)
class AccountTypeAdmin(HOPEModelAdminBase):
    list_display = ("key", "unique_fields", "payment_gateway_id")
    search_fields = ("key", "payment_gateway_id")


@admin.register(FinancialInstitution)
class FinancialInstitutionAdmin(HOPEModelAdminBase):
    list_display = (
        "code",
        "description",
        "type",
        "country",
    )
    search_fields = ("code",)
    list_filter = (
        ("country", AutoCompleteFilter),
        "type",
    )
    raw_id_fields = ("country",)


@admin.register(DeliveryMechanismConfig)
class DeliveryMechanismConfigAdmin(HOPEModelAdminBase):
    list_display = (
        "id",
        "delivery_mechanism",
        "fsp",
        "country",
    )
    search_fields = ("code",)
    list_filter = (
        ("delivery_mechanism", AutoCompleteFilter),
        ("fsp", AutoCompleteFilter),
        ("country", AutoCompleteFilter),
    )
    raw_id_fields = ("delivery_mechanism", "fsp", "country")
    readonly_fields = ("required_fields", "fsp", "delivery_mechanism", "country")


@admin.register(FinancialInstitutionMapping)
class FinancialInstitutionMappingAdmin(HOPEModelAdminBase):
    list_display = (
        "financial_institution",
        "financial_service_provider",
        "code",
    )
    search_fields = (
        "code",
        "finanacial_institution____code",
        "finanacial_institution__description",
        "financial_service_provider__name",
        "financial_service_provider__vision_vendor_number",
    )
    list_filter = (
        ("financial_institution", AutoCompleteFilter),
        ("financial_service_provider", AutoCompleteFilter),
    )
    raw_id_fields = ("financial_institution", "financial_service_provider")
