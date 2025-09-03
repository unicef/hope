from typing import TYPE_CHECKING, Any

from admin_cursor_paginator import CursorPaginatorAdmin
from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import confirm_action
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.filters import ChoicesFieldComboFilter, ValueFilter
from advanced_filters.admin import AdminAdvancedFiltersMixin
from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse

from hope.admin.utils import HOPEModelAdminBase, PaymentPlanCeleryTasksMixin
from hope.apps.account.permissions import Permissions
from hope.apps.payment.forms import TemplateSelectForm
from hope.apps.payment.models import (
    Payment,
    PaymentHouseholdSnapshot,
    PaymentPlan,
    PaymentPlanSupportingDocument,
)
from hope.apps.utils.security import is_root
from hope.contrib.vision.models import FundsCommitmentItem

if TYPE_CHECKING:
    from uuid import UUID


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


def can_regenerate_export_file_per_fsp(payment_plan: PaymentPlan) -> bool:
    return payment_plan.can_regenerate_export_file_per_fsp


def has_payment_plan_pg_sync_permission(request: Any, payment_plan: PaymentPlan) -> bool:
    return request.user.has_permission(
        Permissions.PM_SYNC_PAYMENT_PLAN_WITH_PG.value,
        payment_plan.business_area,
        payment_plan.program_cycle.program_id,
    )


def has_payment_plan_export_per_fsp_permission(request: Any, payment_plan: PaymentPlan) -> bool:
    return request.user.has_permission(
        Permissions.PM_VIEW_LIST.value,
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
        "financial_service_provider",
        "delivery_mechanism",
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

    def has_delete_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:
        return is_root(request)

    @button(
        visible=lambda btn: can_sync_with_payment_gateway(btn.original),
        permission=lambda request, payment_plan, *args, **kwargs: has_payment_plan_pg_sync_permission(
            request, payment_plan
        ),
    )
    def sync_with_payment_gateway(self, request: HttpRequest, pk: "UUID") -> HttpResponse:
        if request.method == "POST":
            from hope.apps.payment.services.payment_gateway import PaymentGatewayService

            payment_plan = PaymentPlan.objects.get(pk=pk)
            PaymentGatewayService().sync_payment_plan(payment_plan)

            return redirect(reverse("admin:payment_paymentplan_change", args=[pk]))
        return confirm_action(
            modeladmin=self,
            request=request,
            action=self.sync_with_payment_gateway,
            message="Do you confirm to Sync with Payment Gateway?",
        )

    @button(
        visible=lambda btn: can_sync_with_payment_gateway(btn.original),
        permission=lambda request, payment_plan, *args, **kwargs: has_payment_plan_pg_sync_permission(
            request, payment_plan
        ),
    )
    def sync_missing_records_with_payment_gateway(self, request: HttpRequest, pk: "UUID") -> HttpResponse:
        if request.method == "POST":
            from hope.apps.payment.services.payment_gateway import PaymentGatewayService

            payment_plan = PaymentPlan.objects.get(pk=pk)
            PaymentGatewayService().add_missing_records_to_payment_instructions(payment_plan)

            return redirect(reverse("admin:payment_paymentplan_change", args=[pk]))
        return confirm_action(
            modeladmin=self,
            request=request,
            action=self.sync_missing_records_with_payment_gateway,
            message="Do you confirm to Sync with Payment Gateway missing Records?",
        )

    @button(
        visible=lambda btn: btn.original.can_regenerate_export_file_per_fsp,
        permission=lambda request, payment_plan, *args, **kwargs: has_payment_plan_export_per_fsp_permission(
            request, payment_plan
        ),
    )
    def regenerate_export_xlsx(self, request: HttpRequest, pk: "UUID") -> HttpResponse:
        payment_plan = PaymentPlan.objects.get(pk=pk)

        if request.method == "POST":
            from hope.apps.payment.services.payment_plan_services import (
                PaymentPlanService,
            )

            form = TemplateSelectForm(request.POST, payment_plan=payment_plan)
            if form.is_valid():
                template_obj = form.cleaned_data.get("template")
                fsp_xlsx_template_id = str(template_obj.id) if template_obj else None
                PaymentPlanService(payment_plan=payment_plan).export_xlsx_per_fsp(request.user.pk, fsp_xlsx_template_id)
                messages.success(request, "Celery task for export regenerate file successfully started.")
                return redirect(reverse("admin:payment_paymentplan_change", args=[pk]))
        else:
            form = TemplateSelectForm(payment_plan=payment_plan)

        return render(
            request,
            "admin/payment/regenerate_export_xlsx_form.html",
            {
                "form": form,
                "payment_plan": payment_plan,
                "title": "Select a template if you want the export to include the FSP Auth Code",
            },
        )

    @button(permission="payment.view_paymentplan")
    def related_configs(self, request: HttpRequest, pk: "UUID") -> HttpResponse:
        obj = PaymentPlan.objects.get(pk=pk)
        url = reverse("admin:payment_deliverymechanismconfig_changelist")
        flt = f"delivery_mechanism__exact={obj.delivery_mechanism.id}&fsp__exact={obj.financial_service_provider.id}"
        return HttpResponseRedirect(f"{url}?{flt}")


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

    def has_delete_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:
        return False

    @button(
        visible=lambda btn: can_sync_with_payment_gateway(btn.original.parent),
        permission=lambda request, payment, *args, **kwargs: has_payment_pg_sync_permission(request, payment),
    )
    def sync_with_payment_gateway(self, request: HttpRequest, pk: "UUID") -> HttpResponse:
        if request.method == "POST":
            from hope.apps.payment.services.payment_gateway import PaymentGatewayService

            payment = Payment.objects.get(pk=pk)
            PaymentGatewayService().sync_record(payment)

            return redirect(reverse("admin:payment_payment_change", args=[pk]))
        return confirm_action(
            modeladmin=self,
            request=request,
            action=self.sync_with_payment_gateway,
            message="Do you confirm to Sync with Payment Gateway?",
        )


@admin.register(PaymentPlanSupportingDocument)
class PaymentPlanSupportingDocumentAdmin(HOPEModelAdminBase):
    search_fields = ("title",)
    list_display = ("title", "payment_plan", "created_by", "uploaded_at")
    list_filter = (("created_by", AutoCompleteFilter),)
    raw_id_fields = (
        "payment_plan",
        "created_by",
    )
