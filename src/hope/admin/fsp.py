from typing import TYPE_CHECKING, Any

from adminfilters.autocomplete import AutoCompleteFilter
from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db.models import Q, QuerySet
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html

from hope.admin.utils import HOPEModelAdminBase
from hope.apps.payment.models import (
    FinancialServiceProvider,
    FinancialServiceProviderXlsxTemplate,
    FspNameMapping,
    FspXlsxTemplatePerDeliveryMechanism,
    PaymentPlan,
)

if TYPE_CHECKING:
    from django.forms import Form


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
        self,
        request: HttpRequest,
        obj: FinancialServiceProviderXlsxTemplate,
        form: "Form",
        change: bool,
    ) -> None:
        for required_field in ["payment_id", "delivered_quantity"]:
            if required_field not in obj.columns:
                raise ValidationError(f"'{required_field}' must be present in columns")
        if not change:
            obj.created_by = request.user
        return super().save_model(request, obj, form, change)

    def has_change_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:
        return request.user.can_change_fsp()

    def has_delete_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:
        return request.user.can_change_fsp()

    def has_add_permission(self, request: HttpRequest) -> bool:
        return request.user.can_change_fsp()


class FspXlsxTemplatePerDeliveryMechanismForm(forms.ModelForm):
    class Meta:
        model = FspXlsxTemplatePerDeliveryMechanism
        fields = ("financial_service_provider", "delivery_mechanism", "xlsx_template")

    def clean(self) -> dict[str, Any] | None:
        cleaned_data = super().clean()
        delivery_mechanism = cleaned_data.get("delivery_mechanism")
        financial_service_provider = cleaned_data.get("financial_service_provider")

        if not delivery_mechanism or not financial_service_provider:
            return cleaned_data

        error_message = (
            f"Delivery Mechanism {delivery_mechanism} is not supported by Financial Service Provider "
            f"{financial_service_provider}"
        )
        # to work both in inline and standalone
        if delivery_mechanisms := self.data.getlist("delivery_mechanisms"):
            if delivery_mechanism and str(delivery_mechanism.id) not in delivery_mechanisms:
                raise ValidationError(error_message)
        elif delivery_mechanism and delivery_mechanism not in financial_service_provider.delivery_mechanisms.all():
            raise ValidationError(error_message)

        return cleaned_data


@admin.register(FspXlsxTemplatePerDeliveryMechanism)
class FspXlsxTemplatePerDeliveryMechanismAdmin(HOPEModelAdminBase):
    list_display = (
        "financial_service_provider",
        "delivery_mechanism",
        "xlsx_template",
        "created_by",
    )
    list_filter = (
        ("created_by", AutoCompleteFilter),
        ("financial_service_provider", AutoCompleteFilter),
        ("delivery_mechanism", AutoCompleteFilter),
        ("xlsx_template", AutoCompleteFilter),
    )
    autocomplete_fields = ("financial_service_provider", "xlsx_template")
    fields = (
        "financial_service_provider",
        "delivery_mechanism",
        "xlsx_template",
        "created_by",
    )
    form = FspXlsxTemplatePerDeliveryMechanismForm

    def get_queryset(self, request: "HttpRequest") -> "QuerySet":
        return (
            super()
            .get_queryset(request)
            .select_related(
                "financial_service_provider",
                "delivery_mechanism",
                "xlsx_template",
                "created_by",
            )
        )

    def save_model(
        self,
        request: HttpRequest,
        obj: FspXlsxTemplatePerDeliveryMechanism,
        form: "Form",
        change: bool,
    ) -> None:
        if not change:
            obj.created_by = request.user
        return super().save_model(request, obj, form, change)

    def has_change_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:
        return request.user.can_change_fsp()

    def has_delete_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:
        return request.user.can_change_fsp()

    def has_add_permission(self, request: HttpRequest) -> bool:
        return request.user.can_change_fsp()


class FinancialServiceProviderAdminForm(forms.ModelForm):
    @staticmethod
    def locked_payment_plans_for_fsp(
        obj: FinancialServiceProvider,
    ) -> QuerySet[PaymentPlan]:
        return PaymentPlan.objects.filter(
            ~Q(
                status__in=[
                    PaymentPlan.Status.OPEN,
                    PaymentPlan.Status.FINISHED,
                ],
            ),
            financial_service_provider=obj,
        ).distinct()

    def clean(self) -> dict[str, Any] | None:
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
                        f"Cannot modify {self.instance}, it is assigned to following Payment Plans:"
                        f" {list(payment_plans)}"
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
    filter_horizontal = (
        "allowed_business_areas",
        "delivery_mechanisms",
        "xlsx_templates",
    )
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
                f"<a href='{
                    reverse(
                        'admin:%s_%s_change' % (template._meta.app_label, template._meta.model_name), args=[template.id]
                    )
                }'>{template}</a>"
                for template in obj.fsp_xlsx_template_per_delivery_mechanisms.all()
            )
        )

    fsp_xlsx_templates.short_description = "FSP XLSX Templates"
    fsp_xlsx_templates.allow_tags = True

    def save_model(
        self,
        request: HttpRequest,
        obj: FinancialServiceProvider,
        form: "Form",
        change: bool,
    ) -> None:
        if not change:
            obj.created_by = request.user
        return super().save_model(request, obj, form, change)

    def has_change_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:
        return request.user.can_change_fsp()

    def has_delete_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:
        return request.user.can_change_fsp()

    def has_add_permission(self, request: HttpRequest) -> bool:
        return request.user.can_change_fsp()
